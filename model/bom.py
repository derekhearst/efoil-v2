"""Complete itemised bill of materials.

Quantities that CAN be derived are derived - sheet counts from the live cut
list, fastener counts and cord lengths from the model - so this cannot drift
from the design. Everything else carries a tag saying where the number is from.

Usage:  python model/bom.py [n_boards]
"""
import json
import math
import os
import sys


# --- the model's report, not a copy of it ---------------------------------
# blender_board.py writes model/report.json on every run. Reading it is the
# whole point: a hand-typed copy of a number cannot fail when the model
# changes, it can only be wrong. That is how fleet_cost.py ended up costing a
# board from two redesigns ago and performance.py ended up 1.2 kg heavy.
def _report():
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "report.json")
    src = os.path.join(here, "blender_board.py")
    if not os.path.exists(path):
        raise SystemExit(
            "model/report.json is missing. Run blender_board.py in Blender "
            "first - this script reads the model rather than duplicating it.")
    if os.path.getmtime(src) > os.path.getmtime(path):
        raise SystemExit(
            "model/report.json is OLDER than blender_board.py. Re-run the "
            "model. Refusing to report numbers from a stale build.")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cnc_drawings as C                                    # noqa: E402
# fleet_cost is NOT imported any more. It was a second, parallel cost model
# that duplicated this file and drifted: it still had an H-200 mast block, a
# DALY 200 A, a $629 foil and three sheets of G10. Two scripts costing the
# same board is one script too many. The only things this needed from it were
# the cell-case constants, so they live here now.
CELL_CASE_N, CELL_CASE_USD = 130, 260.00

N = int(sys.argv[1]) if len(sys.argv) > 1 else 2
FREE_PACKS = 1                       # packs' worth of cells already on hand

# Counts read straight out of blender_board.py's report.
R = _report()
M = dict(seal_blank=R["module_seal_blank_mm"],
         mod_handle_bolts=R["bom_mod_handle_bolts"],
         hatch_bolts=R["bom_hatch_bolts"],
         mod_inserts=R["bom_mod_inserts"],
         mast_bushings=R["bom_mast_bolts"],
         hatch_cord_mm=R["bom_hatch_cord_mm"],
         mod_cord_mm=R["bom_mod_cord_mm"],
         bay_glands=R["bom_bay_glands"],
         cells=R["pack"]["cells"],
         conduit_mm=R["bom_conduit_mm"],
         pad_pieces=R["deck_pad_pieces_per_board"],
         pad_roll_mm=R["deck_pad_roll_mm_per_board"],
         pack_series=R["pack_series"],
         pack_parallel=R["pack_parallel"],
         # ROW to ROW - the series boundaries are between rows, and that is
         # what a nickel bridge spans. pack_pitch_mm is now a (within-row,
         # row-to-row) pair, so taking it whole put a list here.
         pack_pitch=R["pack_pitch_row_to_row_mm"],
         holder_bricks=R["cell_holder_bricks"],
         holder_positions=R["cell_holder_positions"],
         # nickel_m is not geometry - it is a build estimate, so it stays
         # here. 8.0 not 7.0: the edge strips get a second welded layer.
         nickel_m=8.0)
         # strips get a second welded layer, which V1 did and the 7.0 figure
         # (copied from V1's COPPER-jumper design) never paid for.

OK, EST, OWNED = "verified", "estimate", "on hand"
try:
    from links import LINKS, LINK_VENDOR
except ImportError:               # importable as a package too
    from .links import LINKS, LINK_VENDOR

ROWS = []
DRIFT = []                        # (item, believed, listed, qty)


def add(sec, item, qty, unit, price, conf, note="", tool=False,
        vendor=None, url=None):
    """tool=True marks a ONE-TIME cost - a tool, jig or template that is
    bought once and still exists after the build. It is real money out the
    door, but it is not the cost of a board, and it does not repeat on the
    next one. Keeping the two apart is the difference between "a board costs
    $4,100" and "a board costs $3,700 and I now own a vacuum rig".
    """
    # THE LISTING IS THE PRICE. Where a line is linked to a real listing,
    # that listing's price wins over the literal written below - the literal
    # is what we BELIEVED before anyone looked. Disagreements go into DRIFT
    # and are printed at the end of the build, so an override is never
    # silent. A big one usually means the line is specced wrong rather than
    # merely mispriced - pack goods costed as loose units, A2 quoted for A4.
    if item in LINKS:
        _ref, _listed, _t = LINKS[item]
        if url is None:
            # a bare 10-char ASIN expands to an Amazon URL; anything else is
            # already a full URL at whatever vendor actually stocks the part
            url = _ref if _ref.startswith("http")                 else "https://www.amazon.com/dp/" + _ref
        if _listed and abs(_listed - price) > 0.005:
            DRIFT.append((item, price, _listed, qty))
            price = _listed
    ROWS.append(dict(sec=sec, item=item, qty=qty, unit=unit, price=price,
                     conf=conf, note=note, ext=qty * price, tool=tool,
                     vendor=vendor, url=url))


def linked(r):
    """Item name as a markdown link when we know the exact listing."""
    return ("[" + r["item"] + "](" + r["url"] + ")") if r.get("url")         else r["item"]


# What the makerspace covers, and therefore is NOT in this BOM.
# Maker Shop Boise tool list: SawStop table saws, Powermatic jointers and
# planers, Laguna/Powermatic bandsaws, drill press, belt/disc/spindle/edge
# sanders, two Supermax drum sanders, the Axiom CNC, a Shaper Origin, several
# DeWalt routers and Jet/JessEm router tables, Festool tracksaws and Dominos.
#
# So none of the following are budgeted: table saw, bandsaw, planer, router,
# router table, sanders, tracksaw, drill press. What IS budgeted is the stuff
# a woodshop will not have or will not lend as a consumable - the vacuum pump
# and regulator, the lug crimper, and the router CUTTERS.
SHOP_PROVIDES = ("table saw", "bandsaw", "planer", "router", "router table",
                 "drum sander", "spindle sander", "tracksaw", "drill press",
                 "Shaper Origin")



def build():
    ROWS.clear()

    # ------------------------------------------------------------ 1 core
    # MACHINE ACCESS WAS NOT ON THIS LIST AT ALL. It lived in fleet_cost.py -
    # "4 day passes @ $200 = $800" - and went out with that file when it was
    # retired as a stale duplicate. Every total quoted since has been missing
    # it, which also made the shaping-service comparison look worse than it is.
    # $150 for a month at the makerspace, which settles the comparison:
    #   makerspace   EPS 110.72 + 150            = $261
    #   shaping svc  ~180-250 a blank x 2        = $360-500
    # The month pass wins on cost, and it is the only route that also covers
    # the lid trimming and the MDF templates rather than just the cores.
    # WHAT IT BUYS IS A DEADLINE. Everything that needs the machine has to
    # happen inside those 30 days: 4 core halves, 2 hatch lids, 2 module lids,
    # the caul, the groove guide and 21 MDF templates. Cut ALL of it in the
    # month and let the layups follow the weather afterwards - the machine
    # work and the wet work do not have to be in the same season, and given a
    # Boise winter they should not be.
    # NO LINE HERE. There was already a "Maker Shop Boise Basic month" at
    # $150 further down, and I added this as a second one - so the pass was
    # billed TWICE for four commits. The surviving line is the original.
    add("1  Core and shaping",
        "EPS rigid foam 2in x 48in x 8ft (HD 202532856)",
        # 2 * N, not 1.5 * N. FOUR layers a board, not three: three is 152.4
        # mm of stack and the blank envelope is 163.8 - the board is 153.8
        # thick and the ROCKER adds another 10 that the old figure never
        # accounted for. Three sheets physically cannot make this board, and
        # it got worse when the module grew to clear the pack past the lid
        # flange. 39.4 mm machines away, which is foam and roughing time, not
        # money. If CNC hours matter more than a sheet, 3 x 2in + 1 x 1in is
        # 177.8 and skims only 14 - but 1 in EPS is a special trip.
        2 * N, "sheet", 27.68, OK,
        "HD Meridian, 30 in stock, aisle 29 bay 020; $23.53 at 32+. EPS, not "
        "the XPS V1 used - deliberate, ~$90 cheaper across both boards, and "
        "the shear it gives up is covered by H-80 at the hardpoints. See the "
        "note at RHO_EPS in blender_board.py", vendor="Home Depot / hardware")
    add("1  Core and shaping", "PL300 / Gorilla Glue, layer glue-up",
        N, "tube", 8.00, EST)
    # Maker Shop Boise, Overland & Cole: day pass $99, 5-day punch $250,
    # Basic month $150. My $200/day was wrong by half. The punch pass is the
    # sane buy for two cores - and a month at $150 is cheaper still if the
    # builds land close together.
    # UNVERIFIED: their CNC bed size is not published, and the job needs
    # 1030 x 560 mm for the longer core half. Call (208) 254-6151 before
    # counting on it.
    # Basic month beats the 5-day punch if both cores get cut inside one
    # month. Their page says month-to-month, so it should cancel cleanly -
    # worth confirming when you ask about the bed size.
    add("1  Core and shaping", "Maker Shop Boise Basic month",
        1, "month", 150.00, OK,
        "month-to-month; confirm it cancels cleanly. Only ONE part truly "
        "wants a CNC - the EPS core - but the pass covers the lids and the "
        "MDF gauges too, so cut everything inside the 30 days and let the "
        "layups follow the weather afterwards", tool=True)

    # ---------------------------------------------------- 2 G10: NONE
    # There is no G10 on this board any more. It went in three steps:
    #   module walls + flange -> printed ASA   (-1 sheet of 1/8", $133.86)
    #   module floor -> 1/8" 5052 alu          (-the rest of the 1/8", $0)
    #   mast plate -> 1/2" 6061, tapped        (-3/4" sheet, $200.75)
    #   rim ring -> printed ASA                (-1/2" sheet, $267.62)
    # $736.09 of G10 at the start of today, $0 now, and the board came out
    # LIGHTER at every step except the module floor, which was taken on
    # purpose to give the ESC something to dump heat into.

    # ------------------------------------------------------ 2b aluminium
    # Both of these are VERIFIED prices, which is rare in this BOM: the 5052
    # is off Derek's own April receipt and the 6061 is Speedy Metals' list.
    add("2b Aluminium", "5052 1/8in x 12 x 24, 2-pack - module floors",
        1, "pk", 61.99, OK,
        "your Apr 2026 receipt (MorningRo/Huaiian). One sheet is one floor, "
        "so this pack does both boards")
    # CHECKED ON AMAZON, STAYS HERE, AND THE REASON IS TEMPER. Amazon has
    # 1/2in "6061" at 11.8 x 11.8 for $41.99, and since a plate is 250 x 175
    # one nests per sheet - two sheets is $83.98, under this line, with free
    # delivery. But that listing states no temper anywhere: not T6, not T651,
    # just "high-quality aluminum alloy". 6061-O yields about 55 MPa against
    # T6's 276. This plate carries 6293 N of bolt demand at a margin of 2.62
    # ON THE ASSUMPTION OF T6; at O temper it becomes the weak link by 5x,
    # and the failure is the foil leaving the board at speed. $5 is not the
    # price of finding out. Speedy Metals states T651.
    add("2b Aluminium", "6061-T651 1/2in x 12 x 18 - mast plates",
        1, "sheet", 88.92, OK,
        "speedymetals.com 61p.5; both plates nest, 2 x 6.89in of 18, 4.2 "
        "spare. Saw-cut edge, +/-1/4in - profile it yourself")

    # -------------------------------------------------- 3 structural foam
    # H-200 is NOT STOCKED anywhere normal - Fiberglass Supply Depot carries
    # H60/H80, Fiberglass Supply carries H80/H100. Everything dense is now
    # H-100, which holds every margin and halves the mass.
    # Quarter sheets are 21 x 42 in = 533 x 1067 mm; the hatch lid core is
    # 584 x 379, which fits rotated.
    # Quarter sheets are 21 x 42 in = 533 x 1067 mm. Hatch lid core is
    # 584 x 379 - fits rotated. One sheet does both boards.
    # No 1/2in H-100 exists - only 1/8, 1/4 and 1in. Two 1/4in sheets bonded
    # give 12.7 mm at full H-100 crush strength, because crush is a SURFACE
    # effect and the bond line sits mid-core where it does nothing.
    add("3  Structural foam", "Divinycell H-100 1/4in quarter 21x42, hatch "
        "lid cores - 2 sheets bonded to 1/2in", 2, "sheet", 49.59, OK,
        "fiberglasssupply.com; no 1/2in H-100 is made")
    add("3  Structural foam", "Divinycell H-80 1/4in quarter 24x48, module "
        "lid cores", 1, "sheet", 53.94, OK,
        "L18-1070; nobody stands on this one")
    # 3/4in is H-80 only, and H-80 carries the block fine - 17.7x on plate
    # bearing. Leash and handle pads come out of the same offcut.
    # 2 sheets, not 1. Worked from the actual parts at 80% nesting:
    #   mast block slab  430 x 355 x 29.5  = 2 plies  473 in2/board
    #   2 shear ribs     355 x 118 each    = 1 ply    130 in2/board
    #   handle pads      190 x 46, 2 sides = 3 plies   81 in2/board
    #   leash pad        70 x 70                        8 in2/board
    # 692 in2 a board, 1384 for two, 1730 with nesting. An H-80 quarter sheet
    # is 24 x 48 = 1152 in2, NOT the 21 x 42 = 882 that H-100 quarters are -
    # the two grades ship in different sizes and this line had H-100's. Two
    # sheets is 2304 in2, so 574 in2 spare: the ribs were already free and a
    # third and fourth would be too. Two is what the load case asked for.
    # ONE sheet, not two - the two shear ribs are gone. They took the side-load
    # limit from 1.22 g to 1.81 g, i.e. 51 deg of bank to 61, and were measured
    # against nothing. V1's own capacity is 0.44 g (24 deg) and it is in
    # service, so the block alone at 2.8x V1 is the honest bar. They also cost
    # more than foam: the aft rib landed under the rim board and the mast
    # conduit ran straight through it.
    # CHECKED ON AMAZON, STAYS HERE. Amazon does carry Divinycell - H-80
    # 3/4in 24x48 is $112.99 there against $100.26 here - but ONLY in 1/2in
    # and 3/4in. There is no 1/4in Divinycell on Amazon at all, and both lid
    # cores below are 1/4in. So the Fiberglass Supply order and its freight
    # happen regardless, and moving just this sheet would pay $12.73 more to
    # save nothing. Do not re-open this without checking 1/4in stock first.
    add("3  Structural foam", "Divinycell H-80 3/4in quarter sheet 24x48, "
        "mast block + leash pad", 1, "sheet", 100.26, OK,
        "L18-1112, 24x48. Was 2 sheets when it carried 2 shear ribs")

    # ---------------------------------------------------------- 4 laminate
    add("4  Laminate", "E-glass 6 oz, 50in x 12ft, 2-pack",
        N, "pack", 19.07, OK, "your receipt", vendor="Amazon")
    # 6 yd needed for the pair. Fibre Glast sells it by the yard at $12.50
    # and then freights it; Amazon has the 50in x 10 yd roll at $79.99, which
    # is $8.00/yd, arrives free, and leaves 4 yd of margin on a part where
    # the biax is the structural layer you do not want to be short of.
    add("4  Laminate", "1708 biax, 50in x 10 yd roll", 1, "roll", 79.99, OK,
        "6 yd needed across both boards; $8.00/yd against Fibre Glast's "
        "$12.50 and no freight", vendor="Amazon")
    # HARDENER FOLLOWS THE SHOP TEMPERATURE, and this build runs autumn into
    # spring in a Boise garage, so it is not one choice for the whole job:
    #     SLOW  minimum 60 F.   pot life 20 min at 75 F
    #     FAST  minimum 40 F (45 to be safe).  shorter at the same temp, but
    #           in a 50 F shop the cold hands the working time back
    # Below about 35-40 F epoxy cannot generate enough heat to cure AT ALL -
    # it does not just go slowly, it stays soft for ever. A cold laminate is
    # not a slow laminate, it is a ruined one.
    # Buy BOTH hardeners. Which one goes in the pot is a thermometer decision
    # on the morning, not a decision made now.
    # TotalBoat sells 5:1 hardener on its own, sized to the RESIN volume it
    # will catalyse: 6 oz does a quart ($27.99), 25 oz does a gallon ($61.99).
    # Buying the 6 oz because this is a contingency, not the primary system -
    # the gallon kit is slow and does the warm sessions.
    add("4  Laminate", "TotalBoat 5:1 FAST hardener 6 oz, cold days",
        1, "ea", 27.99, OK,
        "min 40-45 F against slow's 60. In a cold shop this is the one that "
        "cures, and the cold gives the pot life back. 6 oz catalyses ONE "
        "QUART of resin, which is about a single hull session - if the shop "
        "turns out to be cold for the whole build, the 25 oz at $61.99 does "
        "a full gallon and is the cheaper way to get there",
        vendor="Amazon")
    # $149 off Amazon, not $159.99, AND the gallon kit ships with cups,
    # stirrers and spreaders - so the separate spreader line goes with it.
    add("4  Laminate", "TotalBoat 5:1 gallon kit, slow hardener",
        N, "kit", 149.00, OK, "2.51 m2 laminate = 4.8 kg mixed = 1 kit/board")
    add("4  Laminate", "TotalBoat 5:1 quart kit, fillets and bonding",
        1, "kit", 68.99, OK)
    add("4  Laminate", "Fumed silica thickener", 0, "off", 0.00, OWNED,
        "plenty on hand from V1")
    # No separate microballoons: TotalFair IS the fairing compound and doing
    # both is buying the same job twice.

    # ---------------------------------------------------- 5 vacuum bagging
    # SINGLE-STAGE, and not as a saving - as the right spec. A 2-stage pump
    # buys ULTIMATE vacuum, measured in microns, and this build must never go
    # anywhere near full vacuum: EPS crushes around 130-200 kPa and full
    # vacuum is 101, so the core is bedded at 5-10 inHg with the regulator
    # doing the work. Depth was never the constraint. FLOW is - 4.5 CFM pulls
    # a 1.5 m bag down faster than 3 CFM does, and that is the number that
    # matters when the epoxy has already started.
    # Oil is included with it, which deletes the separate oil line as well.
    #
    # WHY NOT A HAND PUMP - asked, and checked against foil.zone rather than
    # guessed. The "Very cheap vacuum pump for vacuum bagging" thread (Apr 25,
    # /t/23468) laminated a whole board and a foil wing on a $10 DIAPHRAGM
    # pump: 6 L/min, several minutes to pull a mattress-bag down, max -70 kPa.
    # Two things fall out of that, and they point opposite ways.
    #  1. PULL-DOWN IS NOT THE PROBLEM. 6 L/min did it, which is 1/21st of
    #     this pump. A hand pump would do it too - a 1.4 m bag holds roughly
    #     23 litres of loose air, so about 900 strokes at 25 cc. Tedious, not
    #     impossible.
    #  2. HOLDING IS THE PROBLEM, and it is what kills the hand pump. That
    #     thread's pump still cycles "a couple of seconds every 10-20 minutes"
    #     once sealed - a bag always leaks a little. Over a 6 hour epoxy cure
    #     that is ~24 top-ups, and you have to be standing there for all of
    #     them. Miss a few and the laminate cures at partial pressure.
    # So: electric, but this is NOT bought for capacity. It is bought so that
    # nobody has to babysit a cure, across the 8-10 bagging sessions two hulls
    # plus four lids need. The thing being protected is the hull - the single
    # most expensive and most labour-intensive part on the board - against a
    # bag that sags at hour three.
    # A $10 diaphragm pump plus a vacuum SWITCH would genuinely work and is
    # what the forum does. Note it needs a switch, not the VR20 bleed
    # regulator below: a bleed regulator holds level by admitting air, which
    # means the pump runs continuously, and cheap diaphragm pumps are not
    # continuous-duty. That swap saves ~$25 and adds a failure mode.
    add("5  Vacuum bagging", "VECOTOOLS 4.5 CFM single-stage pump, oil incl.",
        1, "ea", 57.99, OK,
        "your listing, ASIN B0GZVLP3PL. Was a $139.99 Pittsburgh 2-stage "
        "plus $15 of oil - $97 for ultimate vacuum we must not use",
        tool=True)
    # TWO CORRECTIONS HERE, both worth keeping.
    # 1. THE VR20 IS AN EASY COMPOSITES PART, NOT FIBRE GLAST. This line sat
    #    under Fibre Glast for the whole project; fibreglast.com returns ZERO
    #    results for "VR20" - their part numbers are numeric. Their nearest
    #    equivalent is the Bleedoff Valve Assembly 902-A at $70.97, which is
    #    a manual needle valve: it bleeds vacuum down but does not HOLD a
    #    setpoint as the pump and the bag's leak rate change.
    # 2. "NO VACUUM REGULATOR ON AMAZON" WAS WRONG. Amazon does sell genuine
    #    IRV-pattern negative-pressure regulators, just not marketed for
    #    composites. The cheap ones ($24-30) are Rc 1/8 with ~0.6 L/min
    #    intake - fine on a tight bag, marginal against the VR20's 1/4 in
    #    ports. The correctly sized IRV20-C10/C12 is $60-66, i.e. MORE than
    #    the real VR20, and without its integrated gauge or bracket.
    # So the VR20 still wins - but on price and completeness, not because
    # nothing else exists.
    add("5  Vacuum bagging", "VR20 vacuum regulator", 1, "ea", 52.00, OK,
        "one-time. Holds the bag at 5-10 inHg, which is the whole ball game: "
        "EPS crushes around 150 kPa and full vacuum is 101. Hose tails are "
        "+$4.70 if you want them", tool=True)
    # THE "BAGGING STARTER KIT" IS DELETED. This line was wrong three ways.
    # It was costed at $127.40 and described as "film, peel ply, tape,
    # breather, connector" - consumables. Fibre Glast's actual Vacuum Bagging
    # Starter Kit (02227-A) is $506.42 and contains NO consumables at all:
    # it is a regulator/filter, a venturi vacuum GENERATOR, two air hoses, a
    # gauge, tubing, clamps and a connector. Its own page says "you supply
    # the air source and consumables".
    #   - wrong price, by 4x
    #   - wrong contents, so it never covered the consumables it was
    #     supposedly covering (those are all bought per-item below anyway)
    #   - wrong ARCHITECTURE: it is a venturi that runs off a shop air
    #     compressor. We bought a $57.99 ELECTRIC vacuum pump. Buying the kit
    #     means buying a second vacuum source we cannot feed, plus a second
    #     regulator and a second gauge on top of the VR20 and the gauge below.
    # What the kit had that we genuinely still need is only the plumbing:
    # a through-bag connector, tubing and clamps. Those are the two lines
    # that replace it, for $54 instead of $506.
    add("5  Vacuum bagging", "Bag connector w/ ball valve, 1/4 in QD",
        2, "ea", 19.59, OK,
        "THE BALL VALVE IS THE POINT: shut it and the bag is isolated from "
        "the pump, so leak-down is a real measurement and not a guess about "
        "whether the pump is keeping up. Two of them - a 1400 mm hull bag "
        "pulls down far faster from both ends, and one is a spare",
        vendor="Amazon", tool=True)
    add("5  Vacuum bagging", "Vacuum hose + hose clamps", 1, "set", 15.00,
        EST, "1/2 in tubing pump-to-bag plus clamps; the other half of what "
        "the deleted kit was actually carrying", vendor="Amazon", tool=True)
    # Fibre Glast, per-item rather than a kit: film 5 yd $24.95, breather
    # 1 yd $13.95, release film 1 yd $11.28.
    # A VACUUM GAUGE, which was missing, and on this build it is not an
    # accessory - it is the thing that stops the bag crushing the core. EPS
    # goes at 130-200 kPa and full vacuum is 101, so the target is 5-10 inHg
    # and "as much as it will pull" is the wrong answer. Without a gauge you
    # cannot tell 7 inHg from 25.
    # --- what V1 actually taught us about water ---------------------------
    # V1 flooded its cavity three times and then, more recently, got water
    # into the ESC and battery enclosures too. Its own leak notes name the
    # mechanism: "cured laminate is NOT waterproof at a cut edge" - exposed
    # fibre ends wick, and XPS/EPS carries it onward. V2 repeats two of those
    # cut edges (the routed seal groove, the machined lid perimeter and its 12
    # holes) and adds a new one V1 also hit: PRINTED plastic is porous.
    add("6  Hatch and seal", "Neat epoxy, sealing every cut laminate edge",
        0, "off", 0.00, OWNED,
        "off the laminating kit. Groove walls, lid perimeter, all 12 lid "
        "bores, every machined edge. This is V1's Test 2 verbatim - water "
        "came in through unsealed fibre ends at the cavity ledge, and its own "
        "note reads: cured laminate is NOT waterproof at a cut edge")
    # THIS IS THE ONE. Derek's read on the V1 failure is that water seeped
    # through the PETG itself, and that is entirely consistent with how FDM
    # parts behave: an extruded wall is beads laid side by side, and the
    # valleys between them are a connected path straight through. More
    # perimeters lengthens the path, it does not close it - V1 ran FOUR wall
    # loops and still wetted through.
    # Wall thickness is not the fix. A CONTINUOUS BARRIER is, and the cheapest
    # one is a brushed coat of neat laminating epoxy. Coat BOTH faces and do
    # the outside first: stopping water entering the wall beats catching it
    # after it is already travelling inside one.
    add("7  Module", "Epoxy wash coat, BOTH faces of the printed shell",
        0, "off", 0.00, OWNED,
        "off the laminating kit. Outside face first - that is the wet one. "
        "Keep it OFF the gasket flange and the insert faces; a soft film at "
        "a clamping surface undoes the seal geometry, which is V1's own "
        "warning about Flex Seal")
    # NO CONFORMAL COATING. Dropped on Derek's objection, and he is right -
    # on a VESC it is worse than awkward:
    #   - the 75200's aluminium PCB is thermally bonded to its baseplate, and
    #     that baseplate is the whole reason the module floor is aluminium.
    #     Coating it kills the heat path we just designed in.
    #   - connectors, the programming header and the thermal face all have to
    #     be masked, and you cannot reach under components anyway
    #   - PARTIAL coverage is worse than none: it traps moisture against the
    #     board instead of letting it dry
    # A coating is what you reach for when you accept the box will get wet.
    # The answer here is to make the box not get wet, and to PROVE it - which
    # is what the epoxy wash coat and the vacuum leak test are for.
    #
    # What does earn its place is DESICCANT, and for a reason that has
    # nothing to do with leaks. This box breathes: the Gore vent has to pass
    # gas both ways or the lid pumps its own seal. So every time the board
    # goes from cold water to hot sun it draws humid air in, and every time it
    # cools that moisture condenses INSIDE. Over a season that accumulates
    # with no leak at all - and "water got in and got trapped" is exactly what
    # that looks like. Silica gel with a colour indicator, so you can see when
    # it is spent and bake it dry.
    # SIZED, because Derek is right that a token pack does nothing. The
    # module holds 9.6 L of air, which carries 0.22 g of water at 100% RH, and
    # a 5 g pack absorbs ~1.5 g - about six full breathing cycles. A season is
    # nearer fifty, so it wants ~40 g and swapping, not two sachets.
    # Third-order either way. It is worth $12 because condensation is the one
    # path that leaves no trace to find, not because it is a main defence.
    add("9  Electrical", "Silica gel, indicating, 50 g per module", 1, "pk",
        12.00, EST, "~40 g is a season at 50 breathing cycles; a token sachet "
        "is worth about six. Bake it dry when the indicator turns")
    # THE MODULE HAS NO TEST PORT, and it does not need one - it has the VENT
    # BOSS. In service that boss carries the M12 membrane vent; for the test
    # it carries an M12 x 0.75 male-to-hose-barb adapter instead. Same
    # threaded hole, no extra penetration, and the fitting that occupies it in
    # service is the one thing that has to come out anyway.
    #
    # WHY THE VENT HAS TO BE OUT: a Gore-type ePTFE membrane passes AIR by
    # design - that is the entire point of it - so with the vent fitted the
    # module cannot hold vacuum or pressure and there is nothing to measure.
    # That is not the vent defeating the design, it is the vent defeating the
    # TEST, which is why the test happens first and the vent goes in after.
    # The two jobs are different: the seals must stop LIQUID WATER, and the
    # vent must pass AIR so the module breathes through a filtered path
    # instead of pumping through a marginal gasket every time it goes from
    # cold water to hot sun. Test the seals, then fit the breather.
    #
    # VACUUM, NOT PRESSURE, for two reasons. Submerged, the module sees
    # EXTERNAL pressure pushing the lid ONTO its gasket - vacuum inside
    # reproduces that direction, pressure inside tests the opposite and would
    # fail a joint the board never loads that way. And pressure here is
    # genuinely unsafe: 0.2 bar across a 451 x 292 lid is about 2.6 kN.
    # NO SPECIAL FITTING NEEDED - THE GLAND IS THE TEST PORT. The first plan
    # was an M12 x 0.75 male-to-barb into the vent boss, and that thread is a
    # fine pitch nobody stocks: searching it returns M12 x 1.25 and x 1.75 and
    # nothing else. Wrong problem anyway.
    # At leak-test time the module has NO cables fitted - all three PG11
    # glands are empty. A gland IS a compression seal on a round thing, so
    # feed a length of the test kit's own tubing through one and tighten it.
    # PG11 takes 5-10 mm, so use one of the smaller hoses in the kit, not the
    # 1/4 in. Blank the other two glands, blank the vent boss, pull vacuum.
    # No extra hole, no odd thread, no part to buy.
    add("5  Vacuum bagging", "Test cap + tubing, module leak test", 1, "set",
        12.00, EST,
        "PROVE THE MODULE BEFORE THE CELLS GO IN, and prove it the way the "
        "failure actually happens: run one of the kit's smaller hoses through "
        "an empty PG11 gland and tighten it - that is your test port - blank "
        "the other glands and the vent boss, "
        "seal it empty, pull 5 inHg, shut the ball valve and watch the gauge "
        "for 30 min - porosity reads as a slow bleed. Then do it again "
        "SUBMERGED: under vacuum any path pulls water IN and you see exactly "
        "where. V1 found its leaks by riding")
    add("5  Vacuum bagging", "Vacuum gauge, -30 inHg, 1/4 NPT, glycerin",
        1, "ea", 10.50, OK,
        "reads the BAG, not the pump - tee it in at the bag end. The "
        "regulator sets the level; this is how you know it worked. GLYCERIN "
        "FILLED on purpose: a dry needle flutters with every pump stroke and "
        "you cannot read 7 inHg off it, which is the one number that matters",
        vendor="Amazon", tool=True)
    # FILM IS THE CHEAP PART. 3.06 m2 an envelope-bagged hull, about $11 a
    # session, ~$75 for the project. It is also the one thing you should NOT
    # try to reuse on a shaped part: nylon film stretches permanently over a
    # compound curve, so a second use starts with a bag that no longer fits
    # and has work-hardened where it bridged. Reuse it for flat lids if you
    # like. 3 rolls covers 6 sessions with a re-do in hand.
    add("5  Vacuum bagging", "Vac bag film, 5 yd", 3, "roll", 24.95, OK,
        "3.06 m2 a hull session; 2 hulls + 4 lids + a practice piece + one "
        "re-do. Single-use on the hull, reusable on flat parts. Same Elite "
        "Lab product Fibre Glast sells, at the same price, with free "
        "delivery", vendor="Amazon")
    # These three are SACRIFICIAL, every one of them - they come out of the
    # bag full of cured resin. Nothing in this group is reusable, which is
    # the honest answer to "can we reuse it": the film sometimes, these never.
    # Sized off real area: 6.12 m2 of part across two boards (2 x 2.51 hull
    # + 2 x 0.55 of lids), against 1.39 m2 per yard of 60 in cloth. 4 yd was
    # 5.57 - short before any mistakes.
    add("5  Vacuum bagging", "Peel ply, 60in", 3 * N, "yd", 15.33, OK,
        "was only in the starter kit, and one kit's worth does not cover "
        "6.12 m2 of part", vendor="Amazon")
    add("5  Vacuum bagging", "Breather / bleeder cloth", 3 * N, "yd", 13.95,
        OK, "$13.95/yd cut; a 5 yd roll at $59.99 is $12.00/yd if you would "
        "rather buy the roll", vendor="Amazon")
    # NO RELEASE FILM. Perforated release film exists to CONTROL how much
    # resin bleeds through into the breather. On a wet layup, where the resin
    # content is already set by how much you put on, the peel ply bleeds into
    # the breather perfectly well on its own - and the bleed that does happen
    # takes the laminate DOWN in resin content, which is the direction you
    # want for strength. Saves $68 and one layer to fight with at de-bag.
    # The cost is that more resin ends up in the breather, so do not skimp
    # there - which is why breather is at 3 yd a board, not 2.
    # 5.2 m of bag perimeter a session, 6 sessions = 31 m, and a roll is 7.6.
    add("5  Vacuum bagging", "Sealant tape, 50 ft roll", 2, "roll", 19.99,
        OK, "31 m of bag perimeter across the project. 2 x 50 ft at $19.99 "
        "replaced 4 x 25 ft at $12 - same tape, fewer joins",
        vendor="Amazon")

    # ----------------------------------------------------- 6 hatch and seal
    # O3 CORD, BONDED IN - kept after the aluminium ring was reverted, because
    # the argument that decided it never depended on the ring material: 1857 mm
    # of hand-dispensed bead in a 4 x 2.4 groove will not be a uniform section,
    # and an extruded cord is dimensionally perfect out of the packet.
    # An extruded cord is dimensionally perfect out of the packet; bonding it
    # in solves the only thing pour-in-place was buying, which was stopping it
    # lifting out of the groove on a hatch opened every ride.
    # BUY BOTH SIZES AND CHOOSE AFTER MEASURING. This is what actually kills
    # the 10-30% squeeze spread, and it costs a few dollars.
    # The groove comes out somewhere in 2.1..2.7 deep depending on how much
    # glass ended up over the ring. Measure the routed groove with a depth
    # gauge at half a dozen points, then fit the cord that lands 20-25%:
    #     measured 2.1  ->  O3.0 = 30%
    #     measured 2.4  ->  O3.0 = 20%
    #     measured 2.7  ->  O3.5 = 23%   (O3.0 would be only 10%)
    # Guessing the cord before the groove exists is how you end up at 10%.
    # SIZING REALITY CHECK, priced on Amazon: silicone O-ring cord is sold in
    # 10 ft (3.05 m) pieces at ~$15.39, i.e. ~$5.05/m - NOT the $2/m this line
    # used to assume. And 3.5 mm is not a stocked section: Amazon carries the
    # inch series, so the sizes actually available around our target are
    #     3/32" = 2.62      1/8" = 3.175      3/16" = 4.76
    # plus a true metric 3.0. So the "one size up" spare is 1/8", not 3.5.
    add("6  Hatch and seal", "Solid silicone cord, 1/8 in (3.175 mm) - the "
        "spare size", 1, "pc", 15.39, OK,
        "10 ft piece, 70A. Fitted ONLY if the routed groove measures deep. "
        "Gives 24% squeeze at the nominal 2.4 depth and 15% at a bad 2.7 - "
        "the true 3.5 mm that would give 23% at 2.7 is an industrial-supply "
        "size, so if the groove really comes out at 2.7 the answer is to fix "
        "the groove, not to chase cord")
    # 1713 mm a board, so 3.43 m for the pair. Two 10 ft pieces is 6.1 m -
    # nearly 2x the need, which is the right call on a part where the failure
    # mode is a bad splice and the fix is to cut it out and start the run again.
    add("6  Hatch and seal", "Solid silicone cord, 3 mm round - BOTH seals",
        math.ceil(((M["hatch_cord_mm"] + M["mod_cord_mm"]) * N / 1000 + 2.5)
                  / 3.05),
        "pc", 15.39, OK,
        "10 ft (3.05 m) pieces, 70A. Buy long - splice on a straight run, "
        "never a corner")
    # The plug that keeps resin out of the groove while the deck is glassed
    # over it. It has to hold shape under the bag, release from ASA, and come
    # out in one piece afterwards.
    # BEST OPTION IS FREE: print a 4 x 1.8 filler strip WITH the ring, in the
    # same job. It is exactly the groove's section by definition, it is stiff
    # enough not to extrude at 7 inHg, and waxed it will not bond. Cut it into
    # the same 6 segments so it follows the corners.
    add("6  Hatch and seal", "Paste wax, releasing the groove filler", 1, "ea",
        12.00, EST, "the filler must NOT bond - it comes back out after the "
        "glass goes over it")
    # ONE, not two, and only as the fallback. Printing the filler strip 0.5 mm
    # PROUD turns this from routing-a-groove into sanding-the-ring-face-flat -
    # which that face needs regardless, because it is the seal land. The ridge
    # sands through first and the filler shows up as a line to pick out.
    add("6  Hatch and seal", "2.5 mm straight cutter - fallback", 1, "ea",
        14.00, EST, "only if you would rather cut the groove open than sand "
        "down to a proud filler strip. Undersize in a 4 mm groove on purpose")
    add("6  Hatch and seal", "Silicone adhesive, bonding the cord into groove",
        1, "tube", 12.00, EST,
        "a thin continuous bead under the cord. It cannot then migrate, lift "
        "out, or be pinched under the lid in a dark car park")
    # M5 x 25, not x 16. The bolt has to cross the 14 mm lid, then 6 mm of
    # ring above the nut, then 4 through the nut = 24. A 16 would have stood
    # 8 mm short of the thread it is supposed to reach - it would not have
    # picked up the nut at all.
    # PACK GOODS, NOT LOOSE UNITS. This whole block used to be priced as a
    # per-piece cost times a piece count - $0.55 an M5 screw, $0.22 a nut -
    # which is not a thing you can buy. Stainless metric fasteners come in
    # packs, and the A4/316 the salt water demands is several times the price
    # of the A2/304 those per-piece figures were really quoting. Every line
    # below is now (packs needed) x (real pack price).
    # SOCKET CAP, proud, no washer, no countersink. The head bears on a G10
    # plug buried in the core, not on the panel: at 1200 N - the PRELOAD at
    # the 1.2 Nm spec, not the 182 N the cord needs - a bare cap head puts
    # ~2.7 MPa into H100 even after the skin spreads it, against a core that
    # crushes at 2.0. On the plug the same head sits at 37 MPa against G10's
    # ~380, 10x, and the foam carries none of it.
    # A countersink would have hidden the head, but it needs 2.1 mm of solid
    # material under the top face and there is 1.0 mm of skin over the plug -
    # flush heads and a buried hardpoint do not combine. Caps it is.
    add("6  Hatch and seal", "M5 x 25 A4 socket cap, 20 pk",
        math.ceil(M["hatch_bolts"] * N / 20), "pk", 15.99, OK,
        str(M["hatch_bolts"] * N) + " needed. A4/316 - every cheaper listing "
        "is A2/304, which pits in salt water")
    # NO LINE FOR THE LID HARDPOINTS. They are twelve O16 holes in the bare
    # core filled with thickened epoxy off the TotalBoat 5:1 kit already on
    # this list - poured while the core is still a flat sheet on the bench.
    # A G10 rod was specced here for one turn and it was, in Derek's words,
    # "the epoxy plug with extra steps and material". He was right.
    # NOT the $0.14 self-tapping brass insert that was here: driving a coarse
    # thread into a brittle laminate wedges it between plies, which is exactly
    # why the mast plate uses bonded bushings. A wire-thread insert is tapped
    # in once and leaves a STAINLESS working thread - the hatch is opened
    # ~50+ times a season, so the thread has to survive cycling and not gall.
    # M5 wire-thread inserts and the M5 STI tap + tangless tool are GONE with
    # the captive nuts - $62 of them. Renaming a line to "REMOVED" and leaving
    # its quantity at 1 is not removing it; both were still being billed.
    # The washer is what sets how hard you can do these up. The nut alone
    # bears on its own 9.24 mm across-corners circle and tears out of 6 mm of
    # ASA at 5.2 Nm - 4.3x the 1.2 Nm spec, and a hand on a key hits 5 without
    # trying. On a O15 penny washer that becomes 8.5 Nm, 7.1x.
    # O18, not the O15 that was here. Same washer both ends of every bolt.
    # Under the NUT it is what a pull-out has to shear around, so capacity
    # scales with its diameter: 7.1x -> 8.5x at spec, and 1.1x -> 1.4x against
    # a 5 Nm hand-tight at a pessimistic printed-ASA shear. Under the HEAD it
    # keeps the epoxy plug at 14% of ultimate instead of 75%, which is the
    # difference between a seat that holds and one that cold-flows.
    # A4, and it took a third search to find - the first two rounds only
    # turned up 304 and zinc. The O15 line this replaces was 304, so the whole
    # list is finally consistent: every fastener in the wet is A4/316.
    # CHECK THE PACK COUNT AT CHECKOUT - the listing is by size, not by a
    # fixed quantity, and 58 are needed for two boards.
    add("6  Hatch and seal", "M6 penny washer O18 A4 DIN9021",
        1, "pk", 12.99, EST,
        str(M["hatch_bolts"] * N * 2 + 10) + " needed - TWO PER BOLT, one "
        "captive under the nut and one UNDER THE HEAD. M6 size on an M5 bolt: "
        "the 0.7 mm of slop is irrelevant on a washer and the 3 extra mm of "
        "OD is not")
    add("6  Hatch and seal",
        "M5 A4 hex nut DIN934, 50 pk - CAPTIVE in the ring",
        1, "pk", 9.19, OK,
        str(M["hatch_bolts"] * N + 10) + " needed. Dropped in at a print "
        "pause at Z=6.0; steel thread, so a hatch that comes off every ride "
        "never wears anything out")
    # 4 sheets, not a "full template set". With the makerspace pass booked, the
    # seven ROUTER templates are dead weight - the CNC cuts every feature they
    # would have guided: outline, cavity, rim rebate, both mast pockets, handle
    # and leash pads. templates.py now gates them behind HAND_SHAPE=False and
    # emits four GAUGES instead: three station sections and the rocker/deck
    # profile, to check the machined core before it gets glassed.
    # Flip HAND_SHAPE to True and it emits all 21 again - that is the fallback
    # if the machine falls through, and it is why they still exist.
    # The two MDF parts that are needed EITHER WAY are in the cut list, not
    # here: the cavity caul and the groove guide.
    add("6  Hatch and seal", "MDF 12 mm, 4 check gauges", 1, "sheet", 22.00,
        EST, "3 station sections + the rocker/deck profile. Was a 14-template "
        "set at $70 - the router templates go with the CNC pass. The caul is "
        "an EPS offcut and the groove guide is fallback-only, so this sheet "
        "is now the whole MDF requirement")

    # ---------------------------------------------------------- 7 module
    add("7  Module", "M4 x 12 A4 socket cap DIN912, 10 pk",
        math.ceil(M["mod_inserts"] * N / 10), "pk", 7.10, OK,
        str(M["mod_inserts"] * N) + " needed. A4/316 again - the $0.09/ea "
        "listings are all A2/304")
    # Not optional. The lid is cored; the washer is what spreads bolt load off
    # a O5 hole onto the potted plug. Without it the head sits on the plug edge.
    add("7  Module", "M4 A4 washer, 316, 100 pk", 1, "pk", 6.79, OK,
        str(M["mod_inserts"] * N) + " needed, under every lid bolt. NOTE the "
        "OD is 12 mm, not the 9 mm this line specced - the only 9 mm-OD "
        "listing is 304. Took the alloy over the diameter because this sits "
        "in the wet cavity; check 12 mm clears the lid pocket before ordering")
    # Heat-set inserts are RIGHT again: the flange prints as part of the wall,
    # so the insert melts into ASA the way it is meant to. This line went
    # heat-set (wrong - G10) -> tap set (right for G10) -> heat-set (right for
    # a printed flange). No tap, no STI kit, nothing to strip in a laminate.
    add("7  Module", "M4 x 8 brass heat-set insert, 100 pc", 1, "pack", 12.00,
        EST, str(M["mod_inserts"] * N) + " needed; 5.6 mm printed pilot")
    # The shell. V1 printed its battery enclosure in ASA for exactly this
    # reason - ASA creeps far less than PETG under sustained bolt load, which
    # is the whole job of a gasket flange. Derek has run it on the A1 already
    # (250-260C, bed 105, draft shield + brim for warp on an open frame).
    add("7  Module", "ASA filament, printed rim ring", 2, "kg", 24.49, OK,
        "6 dovetailed pieces/board at ~90% infill, 710 g of part each; "
        "PRINT SEAL FACE DOWN - the bed is flatter than any top surface")
    add("7  Module", "Acetone, solvent-welding the printed joints", 1, "qt",
        14.00, EST, "ASA dissolves in it like ABS - a brushed acetone/scrap "
        "slurry makes the joint one piece of plastic, not an adhesive line")
    add("7  Module", "ASA filament, printed module shell", 3, "kg", 24.49,
        OK, "4 L-pieces/board, ~1.13 kg of part + supports and brim; "
        "largest piece 226 x 146 fits the A1 bed")
    # The floor-to-wall bond. NOT epoxy and NOT a rigid acrylic: ASA and 5052
    # differ by 66 um/m/K, so a 451 mm floor moves 0.60 mm relative to the
    # walls from its centre over a 40 C swing. A 0.2 mm rigid bond line takes
    # that as 299% shear strain and tears itself apart; a 2 mm structural PU
    # line takes it as 30% and does not care. This is the upgrade over 4200 -
    # same family, roughly 3x the strength, and the bond line controlled.
    add("7  Module", "Sikaflex-292 marine structural PU", 1, "tube",
        28.99, OK, "~6-8 MPa vs 4200's ~2. Fillet BOTH sides of the joint - "
        "on a flexible bond the fillets are what stop it peeling",
        vendor="Amazon")
    add("7  Module", "Sika Aktivator-PRO 250 ml + daubers", 1, "ea", 28.95,
        OK, "abrade + solvent wipe + activate the 5052; scuff the ASA. "
        "Aktivator-205 is DISCONTINUED - Aktivator-PRO replaces it. "
        "UPGRADE PATH: full Primer-206 G+P is the belt-and-braces answer for "
        "immersed PU on metal but is $67/250 ml on Amazon. Skipping it is "
        "defensible HERE only because the bond line is mechanically backed by "
        "the flange bolts and the gasket - not the PU - is the water barrier")
    add("7  Module", "2 mm glass beads or shim wire, bond-line control", 1,
        "ea", 8.00, EST, "clamping a PU joint metal-to-plastic squeezes the "
        "line out and puts you back to a rigid joint that will fail")
    # TWO DIFFERENT RUBBERS, and the difference matters. The module lid gets
    # a FULL-FACE gasket over the whole 15 mm land, punched for the bolts -
    # V1's method. Squeeze is geometric, so the bolts have to supply whatever
    # stress the material needs at 33% over 23,000 mm2. In SOLID neoprene
    # that is about 11.6 kN, 609 N a bolt, and 1.3x on M4 heat-set pull-out
    # in printed ASA - too thin. In closed-cell sponge it is 2.8 kN, 146 N a
    # bolt, 5.5x. So the lid gets sponge.
    # THE MAST GASKET DOES NOT EXIST, so it is not bought. Splitting the old
    # "module + mast gaskets" line left a solid sheet whose only stated job
    # was a part with no geometry in the model, no step in the build guide
    # and no mention anywhere else - a $22.65 sheet for nothing. Searched
    # before deleting: the hatch seals on a cord, the conduit bungs come off
    # the 1/2 in sheet, and the module lid is sponge.
    # The mast interface needs no gasket. Its bolt holes are BLIND, so there
    # is no path into the board to seal, and the faying faces are aluminium
    # to aluminium - the galvanic couple is the A4 bolts, which is what the
    # Tef-Gel in step 23 is for. Bedding it on a compressible gasket would
    # actively hurt: it is the highest-loaded joint on the board, and rubber
    # under 4 x M8 creeps, loses preload and lets the plate rock.
    # Derek has punches. NOT LINKED, deliberately: a listing price overrides
    # the literal, so leaving a link on a $0 on-hand line would reprice it to
    # $17.99 and quietly bill for a tool that is already in the drawer.
    add("7  Module", "Hollow punch set 1/8-1/2in + cutting mat", 0, "off",
        0.00, OWNED,
        "7/32 in (5.556) is the size for M4 - the model sizes the gasket "
        "holes off it, not the other way round. Punch onto a mat: a hard "
        "bench rolls the edge on the first hit", tool=True)
    # EPDM, NOT NEOPRENE, and the reason is ageing rather than sealing. This
    # lid is rarely opened, so the gasket lives permanently at 33% squeeze and
    # takes a compression set - part of that deflection stops coming back. On
    # a hard-stop joint the gap cannot follow it down, so the loss lands
    # straight on contact stress. CR sets 25-40% of deflection, EPDM 10-20%,
    # for the same money and the same sheet size, and EPDM is better in
    # standing water and UV besides. NOT silicone: best set resistance of the
    # three but the worst water-vapour transmission, and this is the box that
    # has to stay dry inside.
    add("7  Module", "Closed-cell sponge EPDM 1/8in, module lid gasket",
        1, "roll", 13.99, OK,
        "blank is " + " x ".join(str(v) for v in M["seal_blank"])
        + " mm a board; the roll is 432 wide so it nests across, and 2032 "
        "long does both with room over")
    # module cord is now bought with the hatch cord - same 3 mm stock
    # PG11, not PG16 - and sized off the real chart: thread OD 18.03, thread
    # length 9.14, cable range 6.35-10.16 against our 6.5 mm 8 AWG silicone.
    # The model had an 16 mm hole, which is SMALLER THAN THE THREAD.
    add("7  Module", "Gebildet PG11 gland, M18x1.5, 30 pk", 1, "pk", 9.99, OK,
        "your listing: M18x1.5 thread (matches the 18.5 hole) and 5-10 mm "
        "cable, against our 6.5 mm 8 AWG. " + str(M["bay_glands"] * N)
        + " needed of 30 - one wire per gland; three in one gland deforms "
        "the insert into a clover and leaks between them")
    # Was a 25 mm cable gland - nothing to mount one to. See the GLAND_D note
    # in blender_board.py. Undersized rubber is the seal; 4200 is the fillet.
    #
    # NEOPRENE SPECIFICALLY, and it is the one rubber on this list that must
    # NOT follow the module gasket to EPDM. 3M 4200 is a POLYURETHANE, and
    # EPDM is about the hardest rubber there is to bond - non-polar, low
    # surface energy, wants a primer or a chlorination step. A fillet that
    # does not wet the bung leaves a capillary path along the exact interface
    # it was put there to close. Neoprene is polar and takes polyurethane.
    #
    # AND THE OLD LISTING WAS NEITHER. It said "EPDM/neoprene" and pointed at
    # a General Purpose sheet that is SBR - the cheap one, and the worst of
    # the three in water and UV, on a part that lives permanently wet at the
    # bottom of the board. Nobody would have caught that from the line name.
    #
    # THE SHEET'S THICKNESS IS THE BUNG'S LENGTH. 1/2 in of 50A is better
    # rubber for this than anything sold as 1-1/4 in rod - the only rod on
    # Amazon in that diameter is 75A, which is wear-pad hard: it will not
    # conform to a stranded jacket and it turns pushing 6.5 mm cable through
    # 5.5 mm holes into a fight. So the bung is a punched DISC, not a slug of
    # rod, and blender_board.py takes BUNG_L straight off the stock.
    add("7  Module", "Neoprene sheet 1/4in 50A, wire bung", 1, "sheet",
        16.00, EST, "1/4 in, not 1/2 - the bung lives entirely in the plate's "
        "counterbore now and butts the foam, so its length IS that depth. "
        "Punch O31.75 discs and drill 3 x O5.5 IN A ROW at 8.0 mm pitch, the "
        "order the leads leave the mast in - 15% interference, soap them "
        "through. One sheet is a lifetime of bungs for both boards")
    # Derek's existing punch set stops at 1/2 in and the bung is 1-1/4 in.
    # A 1-3/8 in hole saw also gets there - its plug comes out about 2.5 mm
    # under nominal, so ~32 mm, which is the size wanted - but a hole saw
    # grabs in rubber and an arch punch does not.
    add("7  Module", "Hollow punch set 3/16-1-3/8in, for the O31.75 bung", 1,
        "set", 32.99, EST, "the existing set stops at 1/2 in. Skip it if a "
        "1-3/8 in hole saw is already in the drawer - the plug it leaves is "
        "about 32 mm, which is the disc we want", tool=True, vendor="Amazon")
    add("7  Module", "3M 4200 FC 3 oz tube, fillet over the bung", 1, "tube",
        17.99, OK, "does both boards; 4200 NOT 5200 - 5200 never comes out",
        vendor="Amazon")
    # NO LINE FOR THE MODULE LIFT HANDLE HERE. It is one of the three
    # kayak grab handles bought in 9b - that was the whole point of picking
    # one handle part for both jobs. This line outlived that decision by
    # carrying on as a $0 "cut from the webbing pack in 10c", and the webbing
    # pack itself was deleted in the same breath, so it was a free part made
    # out of a part nobody buys. It bolts to the two printed pads on the AFT
    # wall (module_lift_handle in report.json), on the M5 hardware now listed
    # in 9b - the module is ~14 kg in a
    # cavity with 12 mm of side clearance, so there is no getting a hand
    # beside it.
    add("7  Module", "M12 IP68 membrane vent plug", N, "ea", 9.95, OK,
        "NOT optional on a sealed lithium box")
    # You have one on the shelf. CHECK IT IS A SPARE and not the one fitted
    # to V1 - V1 leaves with Kev, button included.
    # APIELE M12: O12 hole, M12 x 0.75, head O17.5. NOT 22 mm - that was a
    # placeholder. Its spec says PANEL 3.5 mm MAX and the wall is 4.0, so the
    # print carries a O17.5 pocket on the inside face taking it to 3.0 local.
    # ANSWERED: it goes to the DALY's SWITCH INPUT. That is the two-wire pair
    # that toggles the BMS output, and momentary is the right action for it.
    #
    # AND NO ANTI-SPARK MODULE. The reason there is nothing to protect:
    # inrush arcing is what happens when a CONNECTOR is mated under load, and
    # on this board no connector ever is. The pack and the ESC are hard-wired
    # together inside the module - there is no XT150 in that path any more, as
    # there was on V1. The 3 phase barrels are only ever parted with the pack
    # off. The charge port mates an unpowered charger.
    # The single remaining surge event is the BMS switching into the ESC's
    # input capacitors, and that is a solid-state switch doing the exact job
    # it is built for - every ebike on earth works this way.
    # CHECKED, AND IT DOES. This DALY's listing names a "Pre-charging
    # function" outright, so the FETs closing into the ESC's caps is
    # soft-started by the board. That question is closed.
    # THE SWITCH INPUT EXISTS - confirmed from DALY's own documentation,
    # which the Amazon listing never mentions: "the default function of the
    # key switch is to activate the BMS; other logic functions can be
    # customized". So the button has somewhere to land. Set it to "control
    # discharge MOS and sleep" in the app and it behaves like a power switch
    # rather than a wake button. Bluetooth can switch the MOSFETs too, so a
    # dead button strands nobody - but starting a board should not need a
    # phone and wet hands, which is why the button is here.
    add("7  Module", "M12 IP68 momentary panel button", max(0, N - 1), "ea",
        12.49, OK, "1 on hand; this line buys the second board's")
    # THE PART THAT MARRIES THEM. The BMS switch input is a JST GH 1.25 mm
    # connector, not a screw terminal, and the M12 button is bare wires.
    # Crimping GH 1.25 by hand is miserable, and this is a $6 problem now
    # against opening a sealed module later.
    add("7  Module", "JST GH 1.25 mm pigtail pair, BMS switch", 1, "pk",
        5.99, OK,
        "connects the panel button to the BMS key-switch input. CHECK THE "
        "BOX FIRST - DALY ship a ready-made key switch with some units",
        vendor="Amazon")
    # SP17 2-pin flange receptacle. Chosen over an XT60-in-a-box because this
    # port is unplugged and replugged EVERY RIDE: IP68 mated, screw cap when
    # not, gold-plated contacts, 500 mating cycles. 5 A of charge current is
    # nothing to it. Flange-bolted rather than nut-on-thread, because the wall
    # is 4 mm of printed ASA.
    add("7  Module", "SP17 2-pin IP68 flange receptacle", N, "ea",
        2.49, OK, "67.2 V 5 A charge; O17 panel hole, 2 x M3 flange screws. "
        "$2.49, not the $11 this carried. CHECK THE CAP IS INCLUDED before "
        "ordering - on a board that gets submerged the cap is the part that "
        "does the sealing when nothing is plugged in", vendor="Amazon")
    # ONE 361-pc M3 kit covers this AND the nose cone in 10b, so it is
    # bought once here and shows as 0 there.
    add("7  Module", "M3 heat-set insert kit, 361 pc", 1, "kit", 13.98, OK,
        "covers the port flange (" + str(2 * N) + " sets) and the nose cone. "
        "The kit's screws are PLAIN STEEL - buy M3 x 8 A4 separately for the "
        "flange, which lives in the wet cavity")
    add("7  Module", "M3 x 8 A4 stainless, 10 pk", 1, "pk", 6.76, OK,
        "the kit's screws are not stainless and this joint is submerged")

    # -------------------------------------------------- 8 mast hardpoint
    # The 316 bar, the lathe work and the DP460 are all GONE - $133 of parts
    # and a lathe dependency, deleted by tapping the plate instead of bonding
    # bushings into it. 6061 shears at ~207 MPa against G10's ~55, so less
    # material holds more: 136 mm2 of thread carries 17.7 kN and the M8 bolt's
    # own 16.5 kN proof load becomes the limit.
    # These are TWO purchases, not one. The cheap tap-and-drill sets all ship
    # a TAPER tap, which cannot finish a blind hole - it runs out of thread
    # about 4 mm before the bottom. Buying only the set would have left the
    # blind holes short of full engagement on the one joint that holds the
    # foil to the board.
    add("8  Mast hardpoint", "M8 x 1.25 tap + 6.8 mm drill set", 1, "set",
        8.63, OK, str(M["mast_bushings"] * N) + " blind holes",
        vendor="Amazon", tool=True)
    add("8  Mast hardpoint", "M8 x 1.25 BOTTOMING tap, 4-flute", 1, "ea",
        8.78, OK, "the one that actually matters - blind at 10 mm in a 12.7 "
        "plate, and the taper tap in the set above cannot reach the bottom",
        vendor="Amazon", tool=True)
    # Aluminium plate, A4 stainless bolts, wet cavity. Not optional.
    # NOT IN THE BUILD. I added this when the plan was still "hand-drill the
    # mast plate", where a wandering or stripped hole was a live risk. That
    # plan is gone - the plate is machined now, to a measured pattern - and
    # with it most of the reason for a repair kit.
    # What is left is SERVICE galling, not a machining error: A4 stainless
    # into aluminium, in salt water, on a bolt that comes out every time the
    # mast does. Tef-Gel is the actual mitigation for that and it is on the
    # list. A helicoil is only what you reach for years later if the Tef-Gel
    # was skipped once and a thread came out with the bolt.
    # So: a someday tool, not a build item. B09WN4QTNL, $14.59, if the day
    # comes. NO LINE - the reasoning survives here, which is where it always
    # was. A $0 row survived here too, and a row is a claim that the part is
    # part of the build: it printed into bom.md and shopping.md with a live
    # link and a price beside it, which is exactly how a part nobody decided
    # to buy ends up in a cart.
    add("8  Mast hardpoint", "Ultra Tef-Gel, galvanic barrier", 1, "ea",
        39.00, OK, "every mast bolt, every time it goes back in. DEARER than "
        "the $22 this was carried at - and do not reach for the small tube "
        "to save it: the 3cc syringe is $31.51, so it is 80% of the price "
        "for a fraction of the gel", vendor="Amazon")
    # No G10 tube. The conduit is a BORE, cut with the rest of the CNC work
    # and sealed with thickened epoxy off the laminating kit. A bought tube
    # would have been bonded into that same bore and added a part number, a
    # bias cut and $36 for nothing.

    # ------------------------------------------------------- 9 electrical
    add("9  Electrical", "Flipsky 65161 120KV motor", N, "ea", 298.00, OK)
    add("9  Electrical", "Flipsky 75200 Pro V2 ESC", N, "ea", 150.00, OK)
    # The whole reason the module floor is aluminium is to give this thing
    # somewhere to dump heat - and there was nothing specified between its
    # baseplate and that floor, which makes the path AIR. I argued the thermal
    # case for the alu floor and then left out the part that makes it work.
    # MUST BE NON-CONDUCTIVE. The ESC PCB face goes DOWN onto a 5052 floor.
    # Plenty of cheap "thermal pads" are carbon- or metal-loaded and are
    # electrically conductive; one of those between a populated PCB and an
    # aluminium plate is a dead short across the board. Pay the extra dollar
    # for a pad that says non-conductive on it.
    add("9  Electrical", "Thermal pad 1 mm non-conductive, 100 x 100",
        1, "ea", 9.99, OK, "15.8 W/mK. One 100 x 100 sheet cuts both boards' "
        "baseplates. The ESC PCB face goes DOWN onto the floor, same as V1 "
        "did onto its alu bottom plate", vendor="Amazon")
    add("9  Electrical", "Flipsky VX3 remote", N, "ea", 71.00, OK)
    # 150 A, not 200 A. The pack peaks at 92 A, and V1 has run a 150 A BMS all
    # season with the VESC limited to 100 A. CHECK THE DIMENSIONS before
    # ordering - the module is laid out around the 200 A unit at 164 x 66 x 21,
    # and a bigger board would need the service strip re-cut.
    # CONFIRMED FROM DALY'S OWN WIRING DIAGRAM, so this is no longer a
    # question to settle at build time: COMMON PORT, and the board carries
    # exactly two power terminals - B- and P-. There is NO B+ terminal; pack
    # positive never touches the BMS and is sensed through the sampling
    # cable, identical to V1's JK. The load and the charger both land on the
    # same P+ / P- pair, which is what makes those terminals the wire
    # splitter the charge port needs.
    # Common port is fine here: charge return goes P- -> MOSFETs -> B-, so
    # with the BMS off there is no path and the port cannot pass current.
    add("9  Electrical", "DALY Smart BMS Li-ion 16S 60V 150A", N, "ea",
        159.00, OK, "batteryint.com; confirm it is <= 164 x 66 x 21 mm")
    add("9  Electrical", "Charger 67.2 V 5 A, 16S  (NOT 58.8 V)",
        N, "ea", 45.99, OK, "Amazon B0DK6FTB1P, aluminium case + fan")
    buy = max(0, N - FREE_PACKS) * M["cells"]
    if buy:
        cases = math.ceil(buy / CELL_CASE_N)
        add("9  Electrical",
            "BAK N21700CG-50, 130-cell case (BatteryHookup)",
            cases, "case", CELL_CASE_USD, OK, "new overstock")
        add("9  Electrical", "BAK N21700CG-50 singles, spares",
            15, "ea", 2.50, OK, "7% margin on a spot-welded pack")
    add("9  Electrical", "21700 cells already on hand",
        M["cells"] * FREE_PACKS, "ea", 0.00, OWNED)
    # DERIVED, not the flat 8 m/board this used to assume. The pack is
    # 16S8P on a 24 mm pitch, so the geometry says exactly how much strip it
    # takes:
    #   15 series boundaries x 8 bridges each, one per parallel cell, each
    #   spanning the 24 mm pitch plus weld pads either side  ~34 mm
    #   + 2 terminal strips collecting 8 cells across             ~192 mm each
    #   + the 2 EDGE bridges at every boundary doubled - series current
    #     crowds at the outside of a serpentine, so those see roughly twice
    #     what the 6 middle ones do (~25 A vs ~12 A at 100 A), which is right
    #     at the limit for a single 0.2 x 10 strip
    _ser, _par = M["pack_series"], M["pack_parallel"]
    _bridge = (M["pack_pitch"] + 10.0) / 1000.0       # pitch + weld pads
    _nickel = ((_ser - 1) * _par * _bridge            # every bridge
               + 2 * _par * M["pack_pitch"] / 1000.0  # terminal collectors
               + (_ser - 1) * 2 * _bridge)            # edge doubling
    _nickel *= 1.25                                   # offcuts and redos
    add("9  Electrical", "Pure nickel 0.2 x 10 mm, 5 m roll",
        math.ceil(_nickel * N / 5), "roll", 14.83, OK,
        f"{_nickel:.1f} m a board derived from the pack, not guessed. "
        "YOU ALREADY OWN 3 ROLLS (SUIDI, ordered Apr 16 x2 and May 6) - "
        "check the drawer before buying more. There is also a 5 m roll of "
        "0.2 x 27 mm uxcell from Apr 12: too wide for bridges, but it is the "
        "right stock for the two terminal collectors and for doubling the "
        "edges without stacking two thin layers")
    # THESE WERE NEVER ACTUALLY IN THE BUILD. The line said "0, OWNED" and
    # the model's colour legend claimed "off-the-shelf 21700 spacer brackets
    # (already owned)" - but the model ALSO carries a build_cell_holder()
    # that designs a printed comb, and that function IS NEVER CALLED. It was
    # written for the 2-layer LYING pack and orphaned when the pack went to
    # 1-layer upright. So: a printed holder that never gets built, a bought
    # holder nobody costed, and 256 cells with nothing locating them.
    #
    # UPRIGHT CELLS NEED HOLDING AT BOTH ENDS. 128 cells a board x 2 boards
    # x 2 ends = 512 cell positions. 1x2 bricks because they tile ANY grid;
    # the 4x5 trays are cheaper per cell but 16 x 8 does not divide by 5.
    #
    # PITCH: these are ~22-23 mm centres, against the model's PITCH_Y = 24.0
    # which was chosen for the wall thickness of the PRINTED holder that no
    # longer exists. That is CONSERVATIVE, not a clash - the real pack comes
    # out ~16 mm narrower and ~8 mm shorter than the cavity is cut for. Do
    # not "fix" PITCH_Y without re-checking every clearance it feeds.
    # COUNT BRICKS, NOT POSITIONS. First pass here divided cell POSITIONS by
    # the pack size and asked for 11 packs - but each 1x2 brick covers TWO
    # positions, so it is half that. Driven off the model now so it cannot
    # drift again: 128 cells a board, both ends held, 2 positions per brick,
    # which works out to exactly one brick per cell.
    add("9  Electrical", "21700 cell holder, 1x2 brick, 50 pk",
        math.ceil(M["holder_bricks"] * N / 50), "pk", 9.99, OK,
        str(M["holder_positions"] * N) + " cell positions across both boards, "
        "2 per brick = " + str(M["holder_bricks"] * N) + " bricks. "
        "THROUGH-HOLE spacers, so they add no height - they locate the cells "
        "and set the pitch. ~22.5 mm against the model's 24, which leaves the "
        "real pack smaller than the cavity is cut for", vendor="Amazon")
    add("9  Electrical", "ANL 150 A fuse + holder", N, "ea", 9.99, OK,
        "in the NEGATIVE leg, between BMS P- and the ESC - that is where V1 "
        "ran it and it is the node the charge negative branches from too")
    # THE 150 A ANL DOES NOTHING FOR THE CHARGE LEADS. They are 16 AWG on a
    # 5 A charger, so in normal use the charger limits itself - but a shorted
    # charge lead inside a sealed module, protected only by a fuse sized for
    # 150 A, is an unprotected 16 AWG wire next to a lithium pack. One small
    # fuse at the positive split closes that.
    add("9  Electrical", "Inline 10 A fuse + holder, charge lead", 1, "pk",
        7.59, OK,
        "at SPLIT A on the charge positive. The ANL is sized for the motor "
        "and cannot protect 16 AWG", vendor="Amazon")
    add("9  Electrical", "8 AWG silicone, 10 ft red + 10 ft black",
        1, "pk", 21.99, OK, "one pack covers BOTH boards - the longest run in "
        "the module is the 278 mm ESC-to-fuse, so 10 ft a side is already 10x "
        "what the runs need. Motor supplies its own phase leads + bullets. "
        "Amazon 8 AWG 10+10 spans $18.88-$23.99; the 25 ft pack at $49.99 was "
        "buying 40 ft of wire to use about 3")
    add("9  Electrical", "PVC pack wrap, 200 mm lay-flat", 1, "roll", 13.99,
        OK, "wide enough to sleeve a 16S brick; one roll does both",
        vendor="Amazon")
    add("9  Electrical", "Kapton tape, pack insulation", 1, "roll", 8.00, EST,
        vendor="Amazon")

    # --------------------------------------------------- 9b odds and ends
    # Things that are easy to leave off a BOM and then stop a build dead.
    add("9b Small but essential", "Capacitor spot welder", 1, "ea", 0.00,
        OWNED, "used on V1")
    # THE TWO TOOLS THAT DECIDE WHETHER THE HOLES LINE UP.
    # Every hole pattern on this board mates to a part that was NOT machined
    # from the same drawing: the hatch lid meets a ring printed in six pieces
    # and glassed in, the mast plate meets a Gong extrusion. Drilling either
    # to nominal means hand-fitting it afterwards, which is the day V1 lost -
    # and the flush countersunk heads on the lid make it worse, because a
    # cone centres itself and clearance stops absorbing the error.
    # Transfer screws for THREADED holes (the ring's captive nuts), transfer
    # punches for CLEARANCE holes (the mast). They are different tools and
    # there is no one set that does both.
    add("9b Small but essential", "Transfer screw set M3-M6", 1, "set",
        24.99, EST, "RECOVERY, not method - the CNC cuts all 12 hatch holes "
        "in one setup and the pattern aligns as one rigid body. This is for "
        "the one hole that does not pick up: mark the real nut, drill it out "
        "of the resin boss, re-pot, re-drill. M5 hatch, M4 module lid, M6 "
        "handle strips", tool=True, vendor="Amazon")
    add("9b Small but essential", "Transfer punch set, metric 1-13 mm", 1,
        "set", 24.99, EST, "the 9 mm punch is a slip fit in Gong's own "
        "clearance holes and marks true centre within a few hundredths. A "
        "6.8 tap drill rattling in that same 9 mm hole does not - and the "
        "mast plate's whole positional budget is 0.25 mm", tool=True,
        vendor="Amazon")
    add("9b Small but essential", "M8 x 30 A4 mast bolts, 10 pk - spares",
        1, "pk", 10.82, OK, "Gong supplies its own; these are spares. Only "
        "listing confirming marine A4/316; head is ISO 7380 button, not "
        "socket cap - check that suits the counterbore")
    add("9b Small but essential", "Silicone grease for the seal cord",
        1, "tube", 9.00, EST, "stops the cord bonding to the lid in storage")
    # SPLICE PLACEMENT, and it is not fussiness - V1's own build notes say
    # "do NOT cut and butt-joint at corners (corner joints leak)". Put it at
    # the MIDPOINT OF A LONG STRAIGHT RUN, and also clear of the six printed
    # ring joints: a cord splice sitting on top of a ring joint stacks two
    # discontinuities in the same place.
    add("9b Small but essential", "Cyanoacrylate for the cord splice",
        1, "ea", 6.00, EST)
    add("9b Small but essential", "Water-ingress alarm, 2 pk", 1, "pk",
        12.99, OK, "Geevon 100 dB pucks - the 2-pack covers BOTH boards. Put "
        "the SENSOR on the module floor in the lowest corner, not up on the "
        "pack - it is only useful where water collects")
    # Remote float deleted - the VX3 ships with a floating band.
    # Used ONCE, to find which clutch number on the drill gives 3 Nm. After
    # that the drill does the 12 bolts at speed and the wrench goes in a
    # drawer. That is the right way round: nobody torque-wrenches 12 bolts in
    # a car park in the dark, and a clutch that has been calibrated is more
    # repeatable than a wrench that gets skipped.
    add("9b Small but essential", "1/4 in torque wrench, 10-50 in-lb", 1,
        "ea", 25.97, OK, "1.1-5.6 Nm. RANGE MATTERS: our hatch spec is 1.2 Nm "
        "= 10.6 in-lb, which is BELOW the 20 in-lb floor of the common "
        "20-200 in-lb wrenches - they cannot read our number at all. "
        "CALIBRATION TOOL - set the drill clutch with it, then "
        "use the clutch. The hatch is captive nuts in ASA against a hard "
        "stop; past the stop more torque only loads the nut pockets",
        tool=True, vendor="Amazon")
    add("9b Small but essential", "Coiled ankle leash", N, "ea", 14.99, OK,
        "you trust the remote failsafe; this is so the board stays with you")
    # SOURCED AND MODELLED NOW, not an estimate. 30 x 12.5 mm plastic cup with
    # a stainless pin, against a O30.16 x 12.7 bore - 0.16 mm of bond gap on
    # the diameter. That is a CLOSE fit, so it wants a structural adhesive
    # that tolerates a thin bond line rather than a gap-filling one.
    # Two per pack, which is exactly two boards - so this is one pack, not N.
    add("9b Small but essential", "Leash plug 30 x 12.5, stainless pin, 2 pk",
        1, "pk", 6.99, OK,
        "the pack does both boards")
    # A cloth handle, bolted on. That is all this ever needed to be - the
    # dense-foam surround that used to wrap the strip is gone.
    # ONE HANDLE PART FOR BOTH JOBS - Derek's call. Rubber/webbing kayak
    # handles, 2 per pack with screws included: 2 on the board's rails and 1
    # on the electronics module, per board. Six handles, three packs.
    # This also retires the separate "module lift loop" made from webbing:
    # one bought part with a moulded grip beats a loop of strap you have to
    # sew or fold, and it is the same part in both places.
    # THE STRAP SETS THE SPAN, not the other way round. That was backwards
    # here until Derek pointed at a real handle: a strap is a FIXED LENGTH,
    # so whatever is left over between its ends and the bolts becomes the
    # arch, and L = S + 8h^2/3S is not negotiable. The old 110 mm centres
    # with a 25 mm arch implied a 125 mm strap - shorter than anything sold.
    # A 7 in handle on those centres makes a 53 mm loop standing off the
    # rail, twice what was drawn.
    # Rails are 152.6 mm centres now, for a 38 mm arch.
    # THE MODULE'S SPAN CANNOT MOVE - outboard of those pads is 5 mm to the
    # gland nuts - so the same strap makes a 53 mm loop there. That is fine
    # for hauling a module out of a hole; it was the rail that needed the
    # shorter one. Same part, two spans, one number measured.
    # IF YOU CHANGE HANDLE, strap length is the ONE number to measure -
    # rail_handle_bolt_pattern_mm and the 6061 strip both derive from it.
    add("9b Small but essential", "Kayak/board grab handle, 2 pk + screws",
        math.ceil(3 * N / 2), "pk", 9.99, OK,
        "3 a board: 2 on the rails into the 6061 strip, 1 on the module. "
        "ONE HOLE PER STRAP END - so one bolt per pad, M6 on the rails and "
        "M5 on the module. Open the moulded hole out to suit; do not use the "
        "supplied self-tappers, everything here is threaded", vendor="Amazon")
    # TAPPED, NOT INSERTED. The strip is 12.7 mm of 6061 and M6 goes straight
    # into it - 90 mm2 of thread at 207 MPa. There was a "M6 heat-set insert,
    # strap mounts" line under this one for $9.99, left over from when the
    # strip was G10; a heat-set insert melts into plastic and there is no
    # plastic here. Deleted, and this note no longer sends you looking for it.
    # ONE BOLT SIZE FOR ALL THREE HANDLES. With the module pads on M6 too,
    # the same 16 mm button head does the lot: 1.5 of washer plus ~5 of strap
    # leaves 9.5 mm of engagement, into 12.7 of tapped 6061 on the rails and
    # into a 12.7 mm insert on the module. Long enough to hold, short enough
    # not to bottom in either.
    add("9b Small but essential", "M6 x 16 A4 button head, 10 pk",
        1, "pk", 8.06, OK,
        str((4 + M["mod_handle_bolts"]) * N) + " needed - 2 per rail handle "
        "into the 6061 strip, " + str(M["mod_handle_bolts"]) + " into the "
        "module pads. Fender washer under every one: the load lands on "
        "WEBBING, and a button head's edge is what tears it")
    # Derek asked for washers. They were already on the list - in the
    # drivetrain section - and they are the right part here: a wide face on a
    # strap rather than a small head cutting into it.
    add("9b Small but essential", "M6 washers for the rail handles", 0, "off",
        0.00, OWNED,
        str(4 * N) + " off the M6 x 20 fender washer pack in section 10b, "
        "not a second purchase")
    # THE MODULE PADS HAD NO FASTENERS ON THIS LIST AT ALL. The shell prints
    # two 8 mm-proud pads with 2 x M5 heat-set each (MOD_HANDLE_INS_D/_L),
    # which is 4 inserts and 4 screws a module - and the BOM bought neither,
    # because the module handle was a webbing loop when this section was
    # written and a loop needs no fasteners. The M4 kit in section 7 is the
    # lid flange's and is the wrong size.
    # M6, not M5, and HALVED - the strap has one hole an end, not two.
    # Counted from the model rather than typed here, so it cannot drift back.
    # Bolt size is free (the strap gets drilled either way), so it went where
    # margin cannot be bought with redundancy instead: two fasteners carry
    # the whole 13.2 kg module and a single-hole strap end leaves no way to
    # add a third. Bearing area 1.6x, margin 6.2 -> 10.1.
    add("9b Small but essential", "M6 x 12.7 brass heat-set insert, 50 pc",
        1, "pk", 12.00, EST,
        str(M["mod_handle_bolts"] * N) + " needed, module handle pads; "
        "8.2 mm printed pilot, same as the model's cut. LOCTITE the bolts - "
        "the pedestal pivots on them every time the module is lifted")


    # ---------------------------------------------- 9c every joint in the pack
    # Walked the whole current path: cells -> nickel -> bus -> BMS -> fuse ->
    # ESC -> motor, plus the balance taps and the two panel fittings. These
    # are what was missing.
    # NO copper bridging jumpers. The V1 design called for 8 AWG soldered
    # along the two edge strips at each row boundary; the pack that got BUILT
    # used stacked nickel instead - extra layers welded on at the edges - and
    # measured 2 mV spread at rest, 6 mV under load. That is a better answer
    # than the design: no solder goes anywhere near a cell, and the joint is
    # the same weld process as everything else on the pack.
    # Why the edges need anything at all: series current crowds at the outside
    # of a serpentine, so the 2 edge strips at each boundary see roughly twice
    # what the 6 middle ones do. At 100 A across 8 parallel strips that is
    # ~12 A nominal but ~25 A at the edges - right at the limit for a single
    # 0.2 x 10 strip. Doubling the nickel there halves it. The 6 middle strips
    # stay single-layer.
    add("9c Pack wiring", "Solder + flux, bus bars and jumpers", 0, "set",
        0.00, OWNED, "on hand from V1; only the ring lugs and balance leads "
        "need it now - the bridges are welded, not soldered")
    add("9c Pack wiring", "Balance harness, 17-wire", N, "ea", 0.00, OWNED,
        "DALY ships one - CONFIRM before you need it")
    add("9c Pack wiring", "16 AWG silicone, 6 colours x 5 ft", 1, "kit",
        14.49, OK, "charge port and power button runs are short; one kit "
        "does both boards and the colours keep them straight",
        vendor="Amazon")
    add("9c Pack wiring", "Dielectric grease, terminals", 1, "tube", 8.00, EST)
    add("9c Pack wiring", "Cable ties, lacing, adhesive mounts", N, "set",
        11.00, EST)
    add("9c Pack wiring", "Silicone sealant, BMS anti-vibration dabs",
        1, "tube", 7.00, EST, "V1 did this; stops the BMS walking")
    # The phase disconnect, in the cavity, exactly as V1. Without it the
    # potting/bung is decorative: the motor's pigtails run up the mast and
    # through the bore, so if they cannot be parted in the cavity the mast is
    # bolted on for life. M25 size takes 6-11 mm cable; 8 AWG silicone is 6.5.
    add("9c Pack wiring", "IP68 M25 inline housing, 5 pk", N, "pk", 15.98,
        OK, "3 per board, one per phase, 2 spare. M25 bodies take 4-14 mm "
        "cable against our 6.5 mm 8 AWG, so the size class is confirmed. "
        "Still CHECK THE BODY LENGTH against the 60 x 318 bay before "
        "ordering wire - diameter fits, length is the risk")
    add("9c Pack wiring", "5.5 mm gold bullets, 20 pair", 1, "pk", 12.99,
        OK, "3 pair a board, so one pack covers both with spares. Motor "
        "pigtails arrive with their own", vendor="Amazon")
    add("9c Pack wiring", "Fish tape / pull cord for the mast conduit",
        1, "ea", 12.00, EST)

    # ------------------------------------------------------------ 10 foil
    # Derek's own foil is X-Over V2 (480.51 EUR delivered on
    # sale). The V2 front wing and stab are now OUT OF STOCK IN EVERY SIZE -
    # Gong has moved to V3, then to V3 Atmo - so the two new boards cannot
    # repeat that order.
    #
    # I first specced a "bridge" fuselage to hang V3 wings off a V2 mast, so
    # that all boards shared the V2 top plate's bolt pattern. THAT WAS WRONG:
    # V1 is already built and is not being re-drilled, and Derek's V2 foil
    # leaves with it when Kev buys it. Only the TWO NEW boards need a mast-pad
    # pattern, and they can both be V3. So buy the complete Atmo setup - it is
    # $23/board more than piecing it together and includes the mast, the
    # connector, the top plate, every screw and a DEEP foil bag (a $59 part on
    # its own), plus the V3 mast, which is the better mast.
    add("10 Foil", "Gong Foil Setup X-Over V3 Atmo Perf Series - XL, Alu 85",
        N, "ea", 694.00, OK,
        "complete: FW + matched stab + V3 alu 85/17 mast + V3 MFC + fuselage "
        "+ V3 top plate + all screws + foil bag. Current range, not "
        "end-of-line like the non-Atmo V3")
    # MEASURED AT GONG'S OWN CHECKOUT, both foils in one cart:
    #     subtotal $1,404.00   shipping $268.63   total $1,672.63
    # The old line was internally inconsistent - it billed N x $124 = $248
    # while its own note said shipping is charged per ORDER, which would
    # have meant qty 1. It is per order, and the real figure is $268.63 for
    # the pair, so the line was $20.63 light rather than $124 heavy.
    add("10 Foil", "Gong shipping to Idaho, ONE order, both foils",
        1, "order", 268.63, OK,
        "quoted at checkout for 2 x XL Alu setups. PER ORDER, not per foil - "
        "ordering the two separately would roughly double it")
    # NOT IN THE TOTAL, AND IT SHOULD NOT BE FORGOTTEN. Gong ships from
    # France and its own site warns that US orders carry customs and import
    # duties separately. Those do not appear at checkout - they arrive later
    # as a courier duty-plus-brokerage invoice, which is exactly how people
    # get surprised. On $1,404 of goods a 15% rate would be about $210.
    # That rate is an ASSUMPTION, not a quote: it is the one number in this
    # BOM nobody has been able to verify, and it moves with trade policy.
    add("10 Foil", "US customs / import duty on the Gong order",
        0, "allow", 0.00, EST,
        "UNQUANTIFIED - carried at zero on purpose so it is never mistaken "
        "for a verified figure. Budget ~$210 if a 15% rate holds, and expect "
        "it as a courier invoice AFTER delivery, not at checkout")

    # ------------------------------------------- 10b drivetrain interface
    # Motor mount is jkoljo's printed PETG clamp (Thingiverse 5996522) - the
    # print is free, the hardware is not. Quantities off V1's as-built list.
    add("10b Drivetrain", "PETG filament 1 kg, mast clamp set", N, "kg",
        9.99, OK, "4 STEP files; 0.6 nozzle, 5 perims, 40% infill")
    add("10b Drivetrain", "M5 x 250 threaded rod, 4 pk (cut to ~171 mm)",
        N, "pk", 9.99, OK,
        "a 4-pack is exactly one board's worth. Dry-assemble and mark before "
        "cutting")
    add("10b Drivetrain", "M6 x 20 fender washer, 100 pk", 1, "pk", 9.49,
        OK, str(4 * N) + " needed")
    add("10b Drivetrain", "M5 nyloc nut 316, 150 pk", 1, "pk", 8.99, OK,
        "a separate pack from the washers above - they do not come together")
    add("10b Drivetrain", "M3 x 6 button head + heat-set, nose cone",
        0, "set", 0.00, OWNED,
        "off the 361-pc M3 kit bought in section 7 - one kit does both")
    add("10b Drivetrain", "Loctite 242", 1, "ea", 9.00, EST,
        "rod ends into the motor only - nyloc end does not need it")
    # Prop: PRINTED, as V1 ran. The MakerWorld prop is bored for our 12 mm
    # shaft with a slot for the drive pin, so it needs no reaming and no
    # adapter - which is the whole $140 the Flite route cost across two
    # boards. V1 ran it raw and uncoated as a test article and it held.
    # Flite stays the upgrade if the printed one disappoints under a heavier
    # rider; nothing here forecloses it.
    add("10b Drivetrain", "PETG for props, 4-5 spares per board", N, "kg",
        9.99, OK, "0.4 nozzle, 100% infill; balance-check on a bolt, then "
        "epoxy-coat - V1 skipped the coat and layer lines cost drag")
    add("10b Drivetrain", "Roll pin assortment M1.5-M6, 220 pc", 1, "kit",
        12.99, OK, str(2 * N) + " needed. An ASSORTMENT on purpose: the note "
        "says MEASURE the shaft cross-hole rather than trust the 4 mm "
        "figure, and a kit means the measurement does not cost another order")
    add("10b Drivetrain", "M8 nyloc nut 316, 30 pk - prop nut", 1, "pk",
        8.99, OK, str(N) + " needed. 316 not 304 - this one is permanently "
        "submerged. WASHER NOT INCLUDED, see below")
    add("10b Drivetrain", "M8 316 washer, prop nut", 1, "pk", 7.69, OK,
        "only 2 needed; sold in 10s")
    # Crimped, not soldered. XT150 is out.
    add("10b Drivetrain", "8 AWG marine ring lugs, 20 pk", 2, "pk", 16.99,
        OK, str(14 * N) + " needed; on M6 studs - nothing to solder")
    # DELETED - THERE IS NO BUSBAR. This line was $14 of unspecified "stud/
    # busbar hardware" with no note, nothing designed around it and no space
    # budgeted for it, and a wiring appendix then got written on top of it as
    # though it were a defined distribution block. It is not.
    # The positive node is the ANL FUSE HOLDER'S INPUT STUD, which already
    # exists in the module: pack B+, charge +, and the BMS sense lead all
    # ring-lug onto it. The negative node is the BMS's own P- terminal. Both
    # are hardware already on the list.
    # See Appendix D in fabrication.md for the distribution that replaced it.
    add("10b Drivetrain", "Hydraulic lug crimper, 10 ton, 12-2/0 AWG", 1, "ea", 39.99,
        OK, "one-time; this is what replaces soldering XT150s", tool=True)
    add("10b Drivetrain", "Adhesive-lined heat shrink 3:1, 400 pc kit", 1,
        "kit", 13.99, OK, "marine grade, glue-lined - plain heat shrink over "
        "a joint in a wet cavity is decoration", vendor="Amazon")

    # ------------------------------------------------ 10c restraint & fitout
    # Currently switched OFF in the model (SHOW_RESTRAINT), so it does not
    # appear in the part list - but the module and pack still have to be held
    # down and the ESC still has to bolt to something.
    # NO LINE, AND NOTHING TO CUT IT FROM. This was "G10 chocks, equipment
    # plate, pack tabs - cut from 1/8 and 1/2 in offcuts" at $0, written when
    # there were two G10 sheets in the build to have offcuts of. There is no
    # G10 anywhere on this board now, so the line was free in the way that a
    # part made of a material you do not own is free. When SHOW_RESTRAINT
    # comes back on, the chocks and the equipment plate have to be re-drawn
    # in ASA or 5052 and PRICED - they are not offcuts of anything any more.
    # BOTH OF THESE ARE OUT. Derek asked what they were for and the honest
    # answer is that neither had a defined job - they are leftovers from this
    # section back when SHOW_RESTRAINT was on, and they survived because
    # nobody re-read them.
    #   WEBBING + BUCKLES: its two stated purposes were "2 straps per board",
    #     which was never defined anywhere, and the module lift loops - and
    #     those are now a bought handle. Nothing left for it to do.
    #   EVA BEDDING PADS: no stated purpose at all beyond where the material
    #     came from. If the module ends up wanting a cushion under it, the
    #     deck-pad offcut is still sitting there and is still free.
    # Neither gets a line. If the module ends up wanting a cushion under it,
    # the deck-pad offcut is still sitting there and is still free.
    # STILL UNRESOLVED, and it is not these two parts: WHAT HOLDS THE MODULE
    # DOWN IN THE CAVITY. SHOW_RESTRAINT is False so nothing models it, the
    # chocks line below is 0/OWNED off-cuts, and the module's 18 bolts hold
    # its own LID on, not the module into the board. A 14 kg module loose in
    # a cavity is the heaviest thing on the board with nothing holding it.
    # Decide before the cavity is glassed - anything bonded in has to go in
    # before the laminate.

    # ------------------------------------------------- 10d shop consumables
    # The thermometer stays, and matters MORE without a hot box - it is the
    # instrument the whole "time it to the weather" plan runs on. Which
    # hardener goes in the pot is a reading, not a guess.
    add("10d Shop consumables", "Thermometer / hygrometer, 2 pk", 1, "pk",
        14.00, EST, "one in the shop, one by the part. Slow needs 60 F, fast "
        "needs 40-45, and below ~35 nothing cures at all")
    # NO HOT BOX. Derek's call: time the wet layups to the weather instead of
    # heating a tent. That works, and it is what the FAST hardener is for -
    # 40-45 F against slow's 60 opens up most of the shoulder season. What it
    # costs is SCHEDULE: deep winter is simply out, so the build pauses rather
    # than slows. Plan the six bagging sessions around that, and keep an eye
    # on blush - it is worse cold and damp, so wash every laminate before any
    # secondary bond.
    # DO NOT BUY SUPER 77 FOR THIS. It is $18.45 and it is the obvious
    # choice, and it is solvent-based - it attacks polystyrene. The thing
    # being held down here is an EPS blank. Spraying it would etch the blank
    # you are about to spend two days shaping. 3M Fastbond 1077 is
    # water-based and safe on foam, and that is the whole reason it is here
    # at $26.02 instead of $18.45.
    add("10d Shop consumables", "3M Fastbond 1077 water-based, CNC hold-down",
        1, "ea", 26.02, OK,
        "WATER-BASED because the blank is EPS - solvent sprays like Super 77 "
        "eat polystyrene. Foam is taped/tacked down, not clamped",
        vendor="Amazon")
    add("10d Shop consumables", "Sacrificial MDF, CNC spoilboard", 1, "sheet",
        16.00, EST, "buy it local, a 4x8 sheet does not travel well")
    add("10d Shop consumables", "Release wax / PVA for the cavity caul",
        1, "set", 20.00, EST)
    # Spare bagging film folded into the 3 rolls in section 5 - it was a
    # duplicate of the same consumable in a different section.
    add("10d Shop consumables", "Dowel pins + drill, two-sided registration",
        1, "set", 12.00, EST, tool=True)
    # ONLY IF THE MAKERSPACE MAKES US SUPPLY TOOLING - still unanswered, and
    # it is $108, so it is worth asking before it is worth buying. Priced
    # real rather than left at a $70 round number:
    add("10d Shop consumables", "1/2 in O-flute up-spiral, foam roughing",
        1, "ea", 66.05, OK, "Freud 73-214, 1/2 in shank. SINGLE flute for "
        "chip clearance - EPS chips are bulky and a 2- or 3-flute packs the "
        "gullets and starts melting the blank. ONLY if the makerspace does "
        "not supply tooling", tool=True, vendor="Amazon")
    add("10d Shop consumables", "1/2 in ball nose, finishing pass", 1, "ea",
        41.95, OK, "1/2 in shank. ONLY if the makerspace does not supply "
        "tooling", tool=True, vendor="Amazon")
    # THE DEEP-POCKET BIT, and a separate line rather than a replacement for
    # the O-flute above, because roughing and wall-finishing are not the same
    # job and only one of them needs the reach:
    #   ROUGHING DOES NOT. Z-level roughing clears the whole pocket at each
    #   level, so by the time the tool reaches 71.6 mm its shank is
    #   travelling through open air, not down a slot. The 31.8 mm Freud does
    #   every roughing pass perfectly well - which is why it stays.
    #   THE WALL FINISH DOES. On that last pass the tool runs down a finished
    #   wall, and above the cutting edge a 12.7 mm shank rubs 12.7 mm of EPS
    #   all the way up. Foam has no strength to resist it, but it does melt
    #   and glaze - and a glazed wall is a bond surface you cannot wet out.
    # 3 in of cutting length is 76.2 mm against the 71.6 mm needed.
    add("10d Shop consumables",
        "1/2 in spiral, 3 in cutting length - cavity wall", 1, "ea",
        82.99, OK,
        "76.2 mm of FLUTE - the only reach found that clears the 71.6 mm "
        "cavity wall in one pass. It is a COMPRESSION bit, which is not the "
        "ideal geometry for foam: if a plain upcut or a reduced-shank necked "
        "bit turns up at this reach, prefer it. Needed ONLY for the wall "
        "finish - rough with the Freud", tool=True, vendor="Amazon")
    # NO ROUTER. Derek already owns a rotary tool with a router/plunge base -
    # a Dremel-class spinner - and for what is actually left to rout that is
    # the RIGHT tool, not a compromise:
    #   - opening the seal groove is a 2.5 mm cutter taking 0.6 mm of glass
    #     off a filler strip. Light, shallow, and needing control rather than
    #     power. A 1.25 HP router is the wrong end of the tool for it.
    #   - everything else that used to want a router is gone. The rebate and
    #     the strip pockets are CNC'd into the foam; the module shell and rim
    #     ring print; the floor, mast plate and handle strips are aluminium
    #     and are bandsaw-and-drill work.
    #   - flush-trimming the laminate overhang is a sanding block job.
    # That is $229 of router and 1/4in carbide that this build does not need.
    # If the rotary tool's base cannot hold depth on a 590 mm run, THAT is
    # when to buy a trim router - not before.
    add("10d Shop consumables", "Rotary-tool router base + collets, if needed",
        1, "set", 35.00, EST,
        "you have the tool; this is only if the base you have will not hold "
        "depth over the groove run", tool=True)


    # ------------------------------------------- 10e layup, the actual doing
    # Everything you need in your hand on layup day. Missing any one of these
    # stops a wet layup, and a wet layup cannot wait.
    # No scale: the TotalBoat kit ships graduated mixing cups and 5:1 by
    # volume is what the resin is specified for. No cups line either, for the
    # same reason - buy more only if a layup runs long.
    # Spreaders, cups and stirrers all ship WITH the gallon kit - no line.
    add("10e Layup kit", "Chip brushes 2 in, 36 pk", 1, "pk", 17.99, OK,
        "disposable, 2-4 a session across 6 sessions. The 12 pk at $7.19 is "
        "dearer per brush and runs out mid-build", vendor="Amazon")
    add("10e Layup kit", "Laminating bubble roller kit, 4 pc", 1, "kit",
        17.99, OK, vendor="Amazon")
    # 6 mil, not the 3-4 mil exam glove - thin nitrile tears on a wet layup
    # and you find out mid-session with resin on your hands. ~6 pairs a
    # session x 6 sessions is 72 gloves before any contamination changes, so
    # two boxes is the honest number, not one.
    add("10e Layup kit", "Nitrile gloves 6 mil, 100 pk", 2, "box", 14.44, OK,
        vendor="Amazon")
    add("10e Layup kit", "Respirator", 1, "ea", 0.00, OWNED)
    add("10e Layup kit", "3M 60923 organic vapour / acid gas P100, pair",
        2, "pr", 18.39, OK,
        "$18.39/pr on Amazon against $31.49 at envirosafetyproducts. "
        "Cartridges EXPIRE - buy these near the layup, not with the rest of "
        "the order", vendor="Amazon")
    # NO GALLON. Asked directly whether it was needed, and on the named uses
    # it is not. What acetone actually does on this build:
    #   - solvent-welding the printed ASA rim segments (the quart line in 7)
    #   - degreasing the 5052 before the Sikaflex goes on
    # That is it. Chip brushes are disposable at $0.50 and get binned rather
    # than cleaned; cured epoxy comes off tools with a scraper; and amine
    # blush is washed off with WATER, not solvent - a mistake worth not
    # making, because acetone smears blush around instead of removing it.
    # Both named uses together are comfortably under a quart.
    # Worth knowing if that changes: at Home Depot a gallon is $20.98 and a
    # quart $11.48, so the gallon is CHEAPER than buying two quarts. The
    # moment you think you need more than one quart, buy the gallon.
    # So there is no gallon line here - just the quart in section 7.
    # --- somewhere to actually work, which V1 did not have ----------------
    # V1 was glassed on a blue tarp over a table, and tarps are the wrong
    # surface for two separate reasons: they do not absorb, so drips pool and
    # then get walked through everything, and they are slippery under a wet
    # board. Rosin/builder's paper soaks it up and rolls into the bin.
    add("10e Layup kit", "Rosin paper roll, floor and bench", 1, "roll",
        24.00, EST, "absorbs instead of pooling. This is the actual upgrade "
        "over a tarp, and it is $24", tool=True)
    # SAWHORSES. Derek's call and it is the right one. Proper shaping racks are
    # $180-400 and the DIY version is $50-90 of lumber you then have to build;
    # a pair of folding sawhorses is $35 off a shelf.
    # The one thing a rack buys that a sawhorse does not is HEIGHT - ~30 in
    # against 36-40 - and that gap matters for PLANING A BLANK. This core
    # arrives machined, so there is no planing. For wet-out and bagging,
    # leaning over a bit is not the constraint.
    add("10e Layup kit", "Folding sawhorses, pair, 700 lb", 1, "pair", 39.99,
        OK,
        "~30 in high. Racks buy height for planing, and this core comes "
        "machined - so they buy nothing here", tool=True, vendor="Amazon")
    add("10e Layup kit", "Pipe lagging or carpet, sawhorse padding", 1, "set",
        8.00, EST, "bare sawhorse tops mark foam and wet laminate")
    # NO "CONFORMING BAGGING BED". I put one here on a calculation that was
    # simply wrong: 24 kPa x 1400 x 600 = 20 kN "pressing the board into the
    # table". That is the sum on ONE face. This is an ENVELOPE bag - the part
    # is fully enclosed - so the same 24 kPa acts on the BOTTOM face pushing
    # UP. Uniform pressure on a closed body is ZERO net force. It consolidates
    # the laminate from every side and pushes the part nowhere.
    # The table only ever carries the board's WEIGHT: ~8 kg wet = 78 N, which
    # over even 50 cm2 of contact is 16 kPa against EPS's 150. Not a problem,
    # by three orders of magnitude.
    # The 20 kN figure would be real for SINGLE-SIDED bagging - bag taped down
    # to a table around the part, table acting as the pressure boundary - and
    # nobody bags a rockered board that way.
    # A blanket under it is still pleasant, and it stops a stray screw head
    # marking the skin. It is a nicety, not a requirement, and free.
    add("10e Layup kit", "Plastic sheeting + masking tape, bench protection",
        1, "set", 20.00, EST)
    # FLEX, not a rigid block. The deck is crowned and the bottom is
    # rockered; a rigid block bridges the curve and cuts flats into it, then
    # you fair the flats back out. The adjustable-radius longboard follows
    # the surface it is on.
    add("10e Layup kit", "Flex longboard sander, 16-1/2 x 2-3/4", 1, "ea",
        19.99, OK, "adjustable radius, hook-and-loop + PSA", tool=True,
        vendor="Amazon")
    add("10e Layup kit", "Adjustable hand sanding block", 1, "ea", 15.99, OK,
        "rails, nose, tail and anywhere the longboard will not reach",
        tool=True, vendor="Amazon")

    # ------------------------------------------------------- 11 finishing
    add("11 Finishing", "TotalBoat TotalFair epoxy fairing compound",
        N, "kit", 45.99, OK, "smallest kit, one per board")
    add("11 Finishing", "TotalBoat Premium Marine Topside Primer",
        1, "kit", 46.99, OK, "one covers both")
    add("11 Finishing", "TotalBoat Wet Edge topside paint, colour",
        N, "kit", 53.99, OK, "one-part polyurethane, quart")
    # FULL-DECK SHEET, not a 3-piece surf pad. Derek's call, and it suits a
    # foil board better: on a foil you move your feet fore and aft through
    # the whole ride to trim, so a pad sized for a surf stance leaves you
    # standing on bare paint half the time.
    # 0.23 in = 5.8 mm, which is about half a typical surf pad - thin was the
    # requirement. One 2400 x 600 sheet covers a 1400 x 560 deck with ~1000
    # mm left over, so it is one sheet per board and the offcut is what feeds
    # the bedding pads in 10c.
    # The 47.2 in wide sheet ($123.48) would yield BOTH decks side by side
    # out of one sheet, but two of these come to $108.28 and leave far more
    # usable offcut, so it is cheaper AND more useful.
    # ONE SHEET A BOARD, and it is the NEST that says so rather than an area
    # ratio. The two pieces - deck 890 x 446 and lid 537 x 334, both DEVELOPED
    # widths - lie side by side along the roll and use 60% of it. They will
    # not stack: 446 + 334 needs 786 mm of sheet width against 600. And two
    # boards will not share a sheet either, because 2 x 1433 mm overruns the
    # 2400 length. So: one sheet per board.
    # ONE SHEET FOR THE PAIR. Dropping the side slivers and splitting the
    # deck at the hatch took a board from 60% of the roll to 35%, so two
    # boards now lie down on one 2400 mm roll with 30% spare. Driven off the
    # measured nest length rather than rounding sheets per board and
    # doubling, which would have bought a second sheet to hold 700 mm of pad.
    add("11 Finishing", "FOCEAN EVA deck sheet 2400 x 600 x 5.8",
        math.ceil(M["pad_roll_mm"] * N / 2400.0), "sheet", 54.14, OK,
        str(M["pad_pieces"]) + " pieces a board - aft of the hatch, forward "
        "of it, and one on the lid - using "
        + str(int(round(M["pad_roll_mm"]))) + " mm of the 2400 roll each. "
        "Self-adhesive EVA, 55 shore. CUT LONG AND TRIM ON THE BOARD from "
        "the centreline outward: with no seams, the crown's arc excess has "
        "to go into stretch and into the trim at the rail", vendor="Amazon")
    # WAS "Abrasives, cups, gloves, tape" at 2 x $40. Two of those four were
    # already bought somewhere else - cups and stirrers ship with the gallon
    # kit, gloves are their own line in 10e - so the bundle was double-
    # counting about $30 of stuff and hiding the abrasive, which is the part
    # that actually gets consumed. Split out and priced:
    add("11 Finishing", "Longboard PSA sandpaper 80 grit, 20 yd roll",
        1, "roll", 15.99, OK, "2-3/4 in, self-adhesive, fits the longboard "
        "above. 80 is the fairing grit - it cuts fair, it does not finish",
        vendor="Amazon")
    add("11 Finishing", "Longboard PSA sandpaper 120-180 grit, 20 yd roll",
        1, "roll", 15.99, OK, "after 80 has the shape right",
        vendor="Amazon")
    add("11 Finishing", "Wet/dry sandpaper assortment, 45 pc", 1, "pk", 8.99,
        OK, "80-400 for detail and between primer coats", vendor="Amazon")

    # ------------------------------------------------------- 12 logistics
    # G10 sheets are heavy and epoxy ships hazmat. Leaving this off is how a
    # BOM comes in under on the day.
    # RE-SCOPED. This line was written when the build had G10 sheet and
    # drum-shipped epoxy in it. Both of those are gone:
    #   - G10 was eliminated entirely when the module became printed ASA +
    #     5052, so there is no heavy sheet order left at all
    #   - epoxy is TotalBoat off Amazon now, so there is no hazmat freight
    #   - 1708 biax and E-glass moved to Amazon too, which took the largest
    #     remaining Fibre Glast box out of the order
    # What actually still ships from a non-Amazon vendor, and therefore what
    # this number now has to cover:
    #     Fiberglass Supply   3 Divinycell quarter sheets, 24x48 - light but
    #                         oversize, so it prices on dimension not weight
    #     Speedy Metals       one 12 x 18 x 1/2 6061 plate, ~10.5 lb, WI->ID
    #     Fibre Glast         VR20 regulator and a few small items
    # Gong, Flipsky, BatteryHookup and Battery International each carry their
    # own shipping in their line prices and are NOT in here.
    add("12 Freight and tax", "Shipping - Divinycell, 6061 plate, VR20",
        1, "allow", 120.00, EST,
        "STILL THE BIGGEST UNVERIFIED LINE - it wants three real carts to "
        "settle. Was $220 when it covered G10 sheet and hazmat epoxy, both "
        "of which are now out of the build entirely")
    # Idaho is a flat 6% state rate with NO local add-on in Ada County -
    # Boise and Meridian are both exactly 6%. This is the real rate, not a
    # placeholder.
    add("12 Freight and tax", "Idaho sales tax, 6% (Ada County, no local)",
        1, "allow", round(0.06 * sum(r["ext"] for r in ROWS), 2), OK)

    # A LINK TO A PART THAT IS NOT IN THE BUILD IS A PART THAT IS STILL IN
    # THE BUILD as far as anyone reading links.py is concerned. Deleting a
    # line from this file never deleted its listing, so three dead parts were
    # still sitting there fully sourced: the kayak carry handle that lost to
    # the grab handle, the 3-piece traction pad that the full-deck EVA sheet
    # replaced, and a nose-cone fastener line under its OLD name - which was
    # the dangerous one. That entry carried the $13.98 kit price, so the day
    # anyone renamed the $0 "off the kit I already bought" line back to
    # matching, add() would have silently repriced it to $13.98 and charged
    # for the same kit twice. Orphans are not clutter, they are ambush.
    _orphan = sorted((set(LINKS) | set(LINK_VENDOR))
                     - {r["item"] for r in ROWS})
    if _orphan:
        raise SystemExit(
            "links.py lists " + str(len(_orphan)) + " item(s) that no BOM "
            "line buys any more. Delete them from LINKS and LINK_VENDOR - if "
            "a part was renamed, rename the key; if it left the build, the "
            "listing leaves with it:" + chr(10)
            + chr(10).join("  " + i for i in _orphan))
    return ROWS


def render(rows):
    out = []
    out.append("# eFoil V2 - full bill of materials")
    out.append("")
    out.append("For **" + str(N) + " boards**, " + str(FREE_PACKS)
               + " pack of cells already on hand. Regenerate with "
               "`python model/bom.py " + str(N) + "`.")
    out.append("")
    out.append("Sheet counts come from the live cut list and fastener counts "
               "from the model, so they cannot drift from the design. "
               "`verified` means read off the supplier's page or your own "
               "receipt; `estimate` means my number.")
    out.append("")
    secs, tot, ver = [], 0.0, 0.0
    for r in rows:
        if r["sec"] not in secs:
            secs.append(r["sec"])
    for sec in secs:
        out.append("## " + sec)
        out.append("")
        out.append("| Item | Qty | Unit | Unit $ | Ext $ | | Note |")
        out.append("|---|---:|---|---:|---:|---|---|")
        st = 0.0
        for r in rows:
            if r["sec"] != sec:
                continue
            st += r["ext"]
            tot += r["ext"]
            if r["conf"] == OK:
                ver += r["ext"]
            out.append("| " + linked(r) + " | " + str(r["qty"]) + " | "
                       + r["unit"] + " | $" + format(r["price"], ",.2f")
                       + " | $" + format(r["ext"], ",.2f") + " | "
                       + r["conf"] + " | " + r["note"] + " |")
        out.append("| **subtotal** | | | | **$" + format(st, ",.2f")
                   + "** | | |")
        out.append("")
    out.append("## Totals")
    out.append("")
    out.append("| | |")
    out.append("|---|---:|")
    out.append("| **Grand total, " + str(N) + " boards** | **$"
               + format(tot, ",.2f") + "** |")
    out.append("| Per board | $" + format(tot / N, ",.2f") + " |")
    out.append("| Of which verified | $" + format(ver, ",.2f") + "  ("
               + format(100 * ver / tot, ".0f") + "%) |")
    out.append("| Of which estimated | $" + format(tot - ver, ",.2f") + " |")
    # Tax and freight are computed allowances, not things you can open a
    # product page for. Counting them as "missing a link" would mean this
    # number could never reach zero, which makes it useless as a target.
    _nl = [r for r in rows if r["ext"] > 0 and not r.get("url")
           and not any(k in r["item"].lower() for k in NOT_A_PURCHASE)]
    _al = [r for r in rows if r["ext"] > 0
           and any(k in r["item"].lower() for k in NOT_A_PURCHASE)]
    out.append("| Linked to a real listing | "
               + str(len([r for r in rows if r.get("url")])) + " lines |")
    out.append("| Priced but NOT linked | " + str(len(_nl))
               + " lines, $" + format(sum(r["ext"] for r in _nl), ",.2f")
               + " |")
    # SPLIT BY CONFIDENCE. Calling all three of these "allowances" was
    # sloppy reporting: the Gong freight is a MEASURED figure off their own
    # checkout, and lumping it with an estimate and a computed tax made a
    # known number read as an unknown one.
    _al_ok = [r for r in _al if r["conf"] == OK]
    _al_est = [r for r in _al if r["conf"] != OK]
    out.append("| Not linkable, but MEASURED (freight quotes) | "
               + str(len(_al_ok)) + " lines, $"
               + format(sum(r["ext"] for r in _al_ok), ",.2f") + " |")
    out.append("| Not linkable and still estimated | " + str(len(_al_est))
               + " lines, $" + format(sum(r["ext"] for r in _al_est), ",.2f")
               + " |")
    out.append("")
    tl, marg = tooling(rows, tot)
    out.append("## What is a board, and what is a shop")
    out.append("")
    out.append("Some of the total above is not the cost of a board at all - "
               "it is tools, jigs and templates that exist afterwards and do "
               "not repeat. Splitting them out is the difference between "
               "\"a board costs $" + format(tot / N, ",.0f") + "\" and \"a "
               "board costs $" + format(marg, ",.0f") + " and I now own a "
               "vacuum rig, a crimper and a full template set\".")
    out.append("")
    out.append("| | |")
    out.append("|---|---:|")
    out.append("| One-time tooling (incl. its share of tax) | $"
               + format(tl, ",.2f") + " |")
    out.append("| **Marginal cost of a board** | **$"
               + format(marg, ",.2f") + "** |")
    out.append("| Cost of the NEXT board after these " + str(N) + " | $"
               + format(marg, ",.2f") + " |")
    out.append("")
    out.append("| One-time item | $ |")
    out.append("|---|---:|")
    for r in rows:
        if r["tool"]:
            out.append("| " + r["item"] + " | $" + format(r["ext"], ",.2f")
                       + " |")
    return "\n".join(out) + "\n"


# --- where each line is actually bought -------------------------------------
# The BOM says WHAT and HOW MUCH. This says WHERE, which is the part you need
# with a card in your hand. Keyed on words already in the item/note so it
# cannot drift out of step with the lines themselves.
VENDORS = [
    ("Fiberglass Supply", "https://fiberglasssupply.com", (
        "divinycell", "h-80", "h-100", "l18-", "l20-")),
    ("Easy Composites", "https://www.easycomposites.us", ("vr20",)),
    ("Fibre Glast", "https://www.fibreglast.com", (
        "breather", "peel ply", "vac bag film", "bagging", "1708", "e-glass",
        "release wax", "release film", "chip brush", "laminating roller",
        "vr20", "vacuum gauge", "sealant tape", "vacuum regulator")),
    ("Speedy Metals", "https://www.speedymetals.com/p-2411-12-6061-t651-"
                      "aluminum-plate.aspx", ("6061",)),
    ("Flipsky", "https://flipsky.net", ("flipsky",)),
    ("Gong", "https://www.gong-galaxy.com", ("gong",)),
    ("BatteryHookup", "https://batteryhookup.com", ("bak n21700", "batteryhookup")),
    ("Battery International", "https://batteryint.com", ("daly", "batteryint")),
    ("Maker Shop Boise", "", ("makerspace", "maker shop")),
    ("Home Depot / hardware", "https://www.homedepot.com", (
        "hd ", "eps rigid", "mdf", "sawhorse", "rosin", "pipe lagging",
        "acetone", "plastic sheeting", "gorilla", "pl300", "spray adhesive",
        "sacrificial", "dowel pin", "sanding block", "longboard", "abrasive",
        "paste wax", "masking", "respirator", "glove", "cutter", "tap set",
        "tap ", "drill", "torque wrench", "thermometer", "beads", "shim")),
    ("Amazon", "https://www.amazon.com", (
        "asin", "amazon", "b0", "gebildet", "apiele", "vecotools", "morningro",
        "cesfonjer", "sp17", "torrami", "suidi", "overture", "silica gel",
        "totalboat", "totalfair", "wet edge",
        "heat-set", "penny washer", "hex nut", "socket cap", "thermal pad",
        "webbing", "leash", "carry handle", "asa filament", "petg", "nickel",
        "heat shrink", "kapton", "awg", "fuse", "crimper", "traction",
        "cable tie", "vent plug", "silicone cord", "silicone adhesive",
        "silicone grease", "cyanoacrylate", "bullet", "eva ", "alarm",
        "solder", "dielectric", "fish tape", "loctite", "roll pin",
        "threaded rod", "lug", "charger", "button", "spacer bracket",
        "neoprene", "conduit", "gland", "rotary-tool", "collet")),
    ("Sika / marine supplier", "https://usa.sika.com", ("sikaflex", "sika primer")),
    ("3M / auto parts", "", ("3m ", "4200", "550fc", "tef-gel", "duralac", "dp460")),
]
# anything left that is plainly a fastener or a shop consumable
FASTENER_HINTS = ("a4", "nyloc", "washer", "insert", "stud", "busbar",
                  "sealant", "tubing", "test cap", "ball nose", "single-flute")
NOT_A_PURCHASE = ("sales tax", "shipping")


# Lines that are plainly Amazon buys but which the keyword table below sends
# somewhere else. Substring match on the item name.
AMAZON_LINES = (
    "m6 stainless stud", "test cap + tubing", "m6 x 16 a4",
    "m4 a4 washer", "silicone sealant", "m5 nyloc", "m8 nyloc",
    "release wax", "m8 x 30 a4", "rosin paper", "plastic sheeting",
    "pl300", "2.5 mm straight cutter", "thermometer", "paste wax",
    "dowel pins", "glass beads", "pipe lagging",
)


def vendor_of(r):
    # An explicit vendor= on the line always wins. The keyword table below is
    # a guess, and it guessed WRONG for every bagging consumable that got
    # re-sourced to Amazon: "peel ply" and "breather" still matched Fibre
    # Glast and sent the shopping list to the wrong vendor at the right
    # price. Where a line has been priced against a specific listing, say so.
    # A line that links to a real listing is sold BY WHOEVER THAT LISTING
    # BELONGS TO. That beats both the AMAZON_LINES list and the keyword
    # table below, which are guesses from the item's name.
    if not r.get("vendor") and r["item"] in LINK_VENDOR:
        v = LINK_VENDOR[r["item"]]
        for n, u, _ in VENDORS:
            if n == v:
                return n, u
        return v, ""
    if any(k in r["item"].lower() for k in AMAZON_LINES) and not r.get("vendor"):
        return "Amazon", "https://www.amazon.com"
    if r.get("vendor"):
        name = r["vendor"]
        for n, url, _ in VENDORS:
            if n == name:
                return n, url
        return name, ""
    # NOT_A_PURCHASE matches the ITEM NAME ONLY. It used to search the note
    # too, which filed a sheet of MDF under freight because its note happened
    # to contain the word "shipping".
    if any(k in r["item"].lower() for k in NOT_A_PURCHASE):
        return "Not a purchase - tax and freight", ""
    t = (r["item"] + " " + (r.get("note") or "")).lower()
    for name, url, keys in VENDORS:
        if any(k in t for k in keys):
            return name, url
    if any(k in t for k in FASTENER_HINTS):
        return "Fasteners / shop consumables", ""
    return "NOT SOURCED YET", ""


# Derek would rather buy everything on Amazon where he can. Which of these
# genuinely can be, and what it costs you if you do.
AMZ_NOTE = {
    "Fibre Glast": "**Amazon carries all of this** - bagging film, peel ply, "
                   "breather, sealant tape, gauges. Prices here are Fibre "
                   "Glast list; check Amazon before ordering, it is usually "
                   "close and ships faster.",
    "Battery International": "**Amazon carries DALY.** Check the price, but "
                             "confirm it is the 16S 150A and <= 164 x 66 x 21 "
                             "- the module is laid out around that size.",
    "Speedy Metals": "**Amazon carries 6061 plate** - you bought the 5052 "
                     "there. Speedy is $88.92 for 12x18 and cuts to size; "
                     "worth comparing.",
    "Sika / marine supplier": "**On Amazon.** Sikaflex-252 and Primer-206 "
                              "both list there.",
    "3M / auto parts": "**On Amazon**, and usually cheaper than the auto "
                       "parts counter.",
    "Fiberglass Supply": "**NOT on Amazon.** Divinycell in sheet form is a "
                         "composites-supplier item. These are verified part "
                         "numbers - just order them.",
    "BatteryHookup": "**Do NOT substitute.** The $260 case is 130 surplus "
                     "cells at $2 each; Amazon 21700s are ~$6. That single "
                     "line is worth ~$500 of the build.",
    "Gong": "Gong only. One order, and the Atmo-vs-standard decision is "
            "still open pending Dallin.",
    "Flipsky": "Some Flipsky appears on Amazon but the range is thin and "
               "usually dearer. Buy direct.",
    "Maker Shop Boise": "Unresolved - two emails unanswered. Phone "
                        "(208) 254-6151, or the EPS core goes to a shaping "
                        "service or gets hand-shaped.",
}


def shopping(rows):
    out = ["# Shopping list", "",
           "Generated by `model/bom.py` - do not edit by hand.", "",
           "Grouped by where you buy it rather than by what it does, because "
           "that is the order you actually place orders in. Quantities are for "
           "**" + str(N) + " boards**.", ""]
    buckets = {}
    for r in rows:
        if r["ext"] <= 0:
            continue
        v, u = vendor_of(r)
        buckets.setdefault((v, u), []).append(r)
    order = sorted(buckets, key=lambda k: -sum(r["ext"] for r in buckets[k]))
    out.append("| Supplier | Lines | $ |")
    out.append("|---|---:|---:|")
    for k in order:
        out.append("| " + k[0] + " | " + str(len(buckets[k])) + " | $"
                   + format(sum(r["ext"] for r in buckets[k]), ",.2f") + " |")
    out.append("| **TOTAL** | | **$"
               + format(sum(r["ext"] for r in rows), ",.2f") + "** |")
    out.append("")
    for name, url in order:
        out.append("## " + name)
        if url:
            out.append("")
            out.append(url)
        if name in AMZ_NOTE:
            out.append("")
            out.append(AMZ_NOTE[name])
        out.append("")
        out.append("| Item | Qty | Unit | Ext | Price | Note |")
        out.append("|---|---:|---|---:|---|---|")
        for r in sorted(buckets[(name, url)], key=lambda r: -r["ext"]):
            out.append("| " + linked(r) + " | " + str(r["qty"]) + " | "
                       + r["unit"] + " | $" + format(r["ext"], ",.2f") + " | "
                       + ("**verified**" if r["conf"] == OK else "estimate")
                       + " | " + (r.get("note") or "").replace("|", "/")[:110]
                       + " |")
        out.append("")
    return chr(10).join(out) + chr(10)


def tooling(rows, tot):
    """(tooling incl. its share of sales tax, marginal cost of one board)."""
    ex = sum(r["ext"] for r in rows if r["tool"])
    tl = ex * 1.06                       # its share of the 6% Idaho line
    return tl, (tot - tl) / N


if __name__ == "__main__":
    rows = build()
    md = render(rows)
    path = os.path.join(os.path.dirname(HERE), "docs", "bom.md")
    open(path, "w", encoding="utf-8").write(md)
    spath = os.path.join(os.path.dirname(HERE), "docs", "shopping.md")
    open(spath, "w", encoding="utf-8").write(shopping(rows))
    tot = sum(r["ext"] for r in rows)
    ver = sum(r["ext"] for r in rows if r["conf"] == OK)
    print("BOM  " + str(len(rows)) + " line items, " + str(N) + " boards")
    secs = []
    for r in rows:
        if r["sec"] not in secs:
            secs.append(r["sec"])
    for sec in secs:
        st = sum(r["ext"] for r in rows if r["sec"] == sec)
        print("  " + sec.ljust(26) + "$" + format(st, ">10,.2f"))
    print("  " + "TOTAL".ljust(26) + "$" + format(tot, ">10,.2f"))
    print("  " + "per board".ljust(26) + "$" + format(tot / N, ">10,.2f"))
    tl, marg = tooling(rows, tot)
    print("  " + "one-time tooling".ljust(26) + "$" + format(tl, ">10,.2f"))
    print("  " + "MARGINAL per board".ljust(26) + "$" + format(marg, ">10,.2f")
          + "   <- what board 3 costs")
    print("  verified " + format(100 * ver / tot, ".0f") + "% of spend")
    if DRIFT:
        _d = sorted(DRIFT, key=lambda x: -abs((x[2] - x[1]) * x[3]))
        print("")
        print("  " + str(len(DRIFT)) + " lines repriced from their listing "
              "(net $" + format(sum((b - a) * q for _i, a, b, q in DRIFT),
                                "+,.2f") + "):")
        for _i, _a, _b, _q in _d[:10]:
            print("    " + format(_a, "8.2f") + " -> " + format(_b, "8.2f")
                  + " x" + str(_q).ljust(4) + _i[:44])
        if len(_d) > 10:
            print("    ... and " + str(len(_d) - 10) + " smaller")
        print("")
    print("wrote " + path)
    print("wrote " + spath)
