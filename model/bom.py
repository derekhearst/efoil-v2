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
M = dict(hatch_bolts=R["bom_hatch_bolts"],
         mod_inserts=R["bom_mod_inserts"],
         mast_bushings=R["bom_mast_bolts"],
         hatch_cord_mm=R["bom_hatch_cord_mm"],
         mod_cord_mm=R["bom_mod_cord_mm"],
         bay_glands=R["bom_bay_glands"],
         cells=R["pack"]["cells"],
         conduit_mm=R["bom_conduit_mm"],
         # nickel_m is not geometry - it is a build estimate, so it stays
         # here. 8.0 not 7.0: the edge strips get a second welded layer.
         nickel_m=8.0)
         # strips get a second welded layer, which V1 did and the 7.0 figure
         # (copied from V1's COPPER-jumper design) never paid for.

OK, EST, OWNED = "verified", "estimate", "on hand"
ROWS = []


def add(sec, item, qty, unit, price, conf, note="", tool=False):
    """tool=True marks a ONE-TIME cost - a tool, jig or template that is
    bought once and still exists after the build. It is real money out the
    door, but it is not the cost of a board, and it does not repeat on the
    next one. Keeping the two apart is the difference between "a board costs
    $4,100" and "a board costs $3,700 and I now own a vacuum rig".
    """
    ROWS.append(dict(sec=sec, item=item, qty=qty, unit=unit, price=price,
                     conf=conf, note=note, ext=qty * price, tool=tool))


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
    add("1  Core and shaping", "Makerspace month pass", 1, "mo", 150.00, OK,
        "their quoted rate. Only ONE part still truly wants a CNC - the EPS "
        "core - but the pass covers the lids and templates too",
        tool=True)
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
        "note at RHO_EPS in blender_board.py")
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
        1, "month", 150.00, OK, "month-to-month; confirm it cancels cleanly", tool=True)

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
    add("3  Structural foam", "Divinycell H-80 3/4in quarter sheet 24x48, "
        "mast block + leash pad", 1, "sheet", 100.26, OK,
        "L18-1112, 24x48. Was 2 sheets when it carried 2 shear ribs")

    # ---------------------------------------------------------- 4 laminate
    add("4  Laminate", "E-glass 6 oz, 50in x 12ft, 2-pack",
        N, "pack", 19.07, OK, "your receipt")
    add("4  Laminate", "1708 biax, 50in wide", 3 * N, "yd", 12.50, OK)
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
    add("4  Laminate", "TotalBoat 5:1 quart FAST hardener, cold days",
        1, "ea", 39.99, EST,
        "min 40-45 F against slow's 60. In a cold shop this is the one that "
        "cures, and the cold gives the pot life back")
    add("4  Laminate", "TotalBoat 5:1 gallon kit, slow hardener",
        N, "kit", 159.99, OK, "2.51 m2 laminate = 4.8 kg mixed = 1 kit/board")
    add("4  Laminate", "TotalBoat 5:1 quart kit, fillets and bonding",
        1, "kit", 68.99, OK)
    add("4  Laminate", "TotalBoat silica thickener, large", 1, "ea", 27.99,
        OK, "fillets and structural bonding")
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
    add("5  Vacuum bagging", "VR20 vacuum regulator", 1, "ea", 52.00, OK,
        "one-time", tool=True)
    add("5  Vacuum bagging",
        "Bagging starter kit - film, peel ply, tape, breather, connector",
        1, "kit", 127.40, OK, "one-time + first board", tool=True)
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
    add("5  Vacuum bagging", "Test cap + tubing, module leak test", 1, "set",
        12.00, EST,
        "PROVE THE MODULE BEFORE THE CELLS GO IN, and prove it the way the "
        "failure actually happens: seal it empty, pull 5 inHg, shut the pump "
        "off and watch the gauge for 30 min - porosity reads as a slow "
        "bleed. Then do it again SUBMERGED: under vacuum any path pulls water "
        "IN and you see exactly where. V1 found its leaks by riding")
    add("5  Vacuum bagging", "Vacuum gauge, 0-30 inHg, 1/4 NPT", 1, "ea",
        18.00, EST, "reads the BAG, not the pump - tee it in at the bag end. "
        "The regulator sets the level; this is how you know it worked",
        tool=True)
    # FILM IS THE CHEAP PART. 3.06 m2 an envelope-bagged hull, about $11 a
    # session, ~$75 for the project. It is also the one thing you should NOT
    # try to reuse on a shaped part: nylon film stretches permanently over a
    # compound curve, so a second use starts with a bag that no longer fits
    # and has work-hardened where it bridged. Reuse it for flat lids if you
    # like. 3 rolls covers 6 sessions with a re-do in hand.
    add("5  Vacuum bagging", "Vac bag film, 5 yd", 3, "roll", 24.95, OK,
        "3.06 m2 a hull session; 2 hulls + 4 lids + a practice piece + one "
        "re-do. Single-use on the hull, reusable on flat parts")
    # These three are SACRIFICIAL, every one of them - they come out of the
    # bag full of cured resin. Nothing in this group is reusable, which is
    # the honest answer to "can we reuse it": the film sometimes, these never.
    # Sized off real area: 6.12 m2 of part across two boards (2 x 2.51 hull
    # + 2 x 0.55 of lids), against 1.39 m2 per yard of 60 in cloth. 4 yd was
    # 5.57 - short before any mistakes.
    add("5  Vacuum bagging", "Peel ply", 3 * N, "yd", 12.50, OK,
        "was only in the starter kit, and one kit's worth does not cover "
        "6.12 m2 of part")
    add("5  Vacuum bagging", "Breather / bleeder cloth", 3 * N, "yd", 13.95, OK)
    # NO RELEASE FILM. Perforated release film exists to CONTROL how much
    # resin bleeds through into the breather. On a wet layup, where the resin
    # content is already set by how much you put on, the peel ply bleeds into
    # the breather perfectly well on its own - and the bleed that does happen
    # takes the laminate DOWN in resin content, which is the direction you
    # want for strength. Saves $68 and one layer to fight with at de-bag.
    # The cost is that more resin ends up in the breather, so do not skimp
    # there - which is why breather is at 3 yd a board, not 2.
    # 5.2 m of bag perimeter a session, 6 sessions = 31 m, and a roll is 7.6.
    add("5  Vacuum bagging", "Sealant tape, 25 ft roll", 4, "roll", 12.00,
        EST, "31 m of bag perimeter across the project; the kit has one roll")

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
    add("6  Hatch and seal", "Solid silicone cord, 3.5 mm round - the spare "
        "size", 4, "m", 4.00, EST,
        "fitted ONLY if the routed groove measures deep. Choosing after you "
        "measure is the whole point")
    add("6  Hatch and seal", "Solid silicone cord, 3 mm round - BOTH seals",
        math.ceil((M["hatch_cord_mm"] + M["mod_cord_mm"]) * N / 1000) + 4,
        "m", 2.00, EST,
        "buy long - splice on a straight run, never a corner")
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
    add("6  Hatch and seal", "M5 x 25 A4 stainless socket cap",
        M["hatch_bolts"] * N, "ea", 0.55, EST)
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
    # ASA at 5.2 Nm - only 2.6x the 2 Nm spec, and a hand on a hex key hits 5
    # without trying. On a O15 penny washer that becomes 8.5 Nm, 4.2x.
    add("6  Hatch and seal", "M5 penny washer O15, under the captive nut",
        M["hatch_bolts"] * N + 10, "ea", 0.18, EST,
        "goes in at the SAME print pause as the nut, underneath it")
    add("6  Hatch and seal", "M5 A4 hex nut, CAPTIVE - printed into the ring",
        M["hatch_bolts"] * N + 10, "ea", 0.22, EST,
        "dropped in at a print pause at Z=6.0; steel thread, so a hatch that "
        "comes off every ride never wears anything out")
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
    add("7  Module", "M4 x 12 A4 stainless socket cap",
        M["mod_inserts"] * N, "ea", 0.35, EST)
    # Not optional. The lid is cored; the washer is what spreads bolt load off
    # a O5 hole onto the potted plug. Without it the head sits on the plug edge.
    add("7  Module", "M4 A4 washer O9, 100 pk", 1, "pk", 8.00, EST,
        str(M["mod_inserts"] * N) + " needed, under every lid bolt")
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
    add("7  Module", "ASA filament, printed rim ring", 2, "kg", 24.00, EST,
        "6 dovetailed pieces/board at ~90% infill, 710 g of part each; "
        "PRINT SEAL FACE DOWN - the bed is flatter than any top surface")
    add("7  Module", "Acetone, solvent-welding the printed joints", 1, "qt",
        14.00, EST, "ASA dissolves in it like ABS - a brushed acetone/scrap "
        "slurry makes the joint one piece of plastic, not an adhesive line")
    add("7  Module", "ASA filament, printed module shell", 3, "kg", 24.00,
        EST, "4 L-pieces/board, ~1.13 kg of part + supports and brim; "
        "largest piece 226 x 146 fits the A1 bed")
    # The floor-to-wall bond. NOT epoxy and NOT a rigid acrylic: ASA and 5052
    # differ by 66 um/m/K, so a 451 mm floor moves 0.60 mm relative to the
    # walls from its centre over a 40 C swing. A 0.2 mm rigid bond line takes
    # that as 299% shear strain and tears itself apart; a 2 mm structural PU
    # line takes it as 30% and does not care. This is the upgrade over 4200 -
    # same family, roughly 3x the strength, and the bond line controlled.
    add("7  Module", "Sikaflex-252 or 3M 550FC structural PU", 1, "tube",
        24.00, EST, "~6-8 MPa vs 4200's ~2. Fillet BOTH sides of the joint - "
        "on a flexible bond the fillets are what stop it peeling")
    add("7  Module", "Sika Primer-206 G+P, aluminium side", 1, "ea", 28.00,
        EST, "abrade + solvent wipe + prime the 5052; scuff the ASA. The "
        "primer is not optional on aluminium and it is why this beats 4200")
    add("7  Module", "2 mm glass beads or shim wire, bond-line control", 1,
        "ea", 8.00, EST, "clamping a PU joint metal-to-plastic squeezes the "
        "line out and puts you back to a rigid joint that will fail")
    add("7  Module", "Neoprene sheet 1/8in, module + mast gaskets", 1,
        "sheet", 16.00, EST,
        "TORRAMI 18x24 or similar - you kept a part sheet from V1")
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
    add("7  Module", "EPDM/neoprene sheet 1/2in, conduit bungs", 1, "sheet",
        14.00, EST, "cut O33 plugs for a O32 bore, punch 3 x O5 for 6.5 mm "
        "lead - interference fit, soap them through")
    add("7  Module", "3M 4200 FC, fillet over the bung", 1, "tube", 18.00,
        EST, "does both boards; 4200 NOT 5200 - 5200 never comes out")
    add("7  Module", "25 mm webbing loop, module lift handle", N, "ea", 6.00,
        EST, "through the two printed bosses on the forward wall - the module "
        "is ~14 kg in a cavity with 12 mm of side clearance, so there is no "
        "way to get a hand beside it")
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
    # WORTH CHECKING once: some smart DALYs carry precharge on the switch
    # input. If yours does, even that surge is soft-started for free.
    add("7  Module", "M12 IP68 momentary panel button", max(0, N - 1), "ea",
        12.49, OK, "1 on hand; this line buys the second board's")
    # SP17 2-pin flange receptacle. Chosen over an XT60-in-a-box because this
    # port is unplugged and replugged EVERY RIDE: IP68 mated, screw cap when
    # not, gold-plated contacts, 500 mating cycles. 5 A of charge current is
    # nothing to it. Flange-bolted rather than nut-on-thread, because the wall
    # is 4 mm of printed ASA.
    add("7  Module", "SP17 2-pin IP68 flange receptacle + cap", N, "ea",
        11.00, EST, "67.2 V 5 A charge; O17 panel hole, 2 x M3 flange screws")
    add("7  Module", "M3 heat-set insert + M3 x 8 A4, port flange", 2 * N,
        "set", 0.60, EST)

    # -------------------------------------------------- 8 mast hardpoint
    # The 316 bar, the lathe work and the DP460 are all GONE - $133 of parts
    # and a lathe dependency, deleted by tapping the plate instead of bonding
    # bushings into it. 6061 shears at ~207 MPa against G10's ~55, so less
    # material holds more: 136 mm2 of thread carries 17.7 kN and the M8 bolt's
    # own 16.5 kN proof load becomes the limit.
    add("8  Mast hardpoint", "M8 x 1.25 tap set + 6.8 mm drill", 1, "set",
        18.00, EST, str(M["mast_bushings"] * N) + " blind holes; a BOTTOMING "
        "tap is the one that matters - blind at 10 mm in a 12.7 plate",
        tool=True)
    # Aluminium plate, A4 stainless bolts, wet cavity. Not optional.
    add("8  Mast hardpoint", "Tef-Gel or Duralac, galvanic barrier", 1, "ea",
        22.00, EST, "every mast bolt, every time it goes back in")
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
    add("9  Electrical", "Thermal pad 1 mm, ESC baseplate to alu floor",
        N, "ea", 9.00, EST, "or paste; the ESC PCB face goes DOWN onto the "
        "floor, same as V1 did onto its alu bottom plate")
    add("9  Electrical", "Flipsky VX3 remote", N, "ea", 71.00, OK)
    # 150 A, not 200 A. The pack peaks at 92 A, and V1 has run a 150 A BMS all
    # season with the VESC limited to 100 A. CHECK THE DIMENSIONS before
    # ordering - the module is laid out around the 200 A unit at 164 x 66 x 21,
    # and a bigger board would need the service strip re-cut.
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
    add("9  Electrical", "Pure nickel 0.2 x 10 mm, 5 m roll",
        math.ceil(M["nickel_m"] * N / 5), "roll", 14.83, OK)
    add("9  Electrical", "21700 spacer brackets", 0, "set", 0.00, OWNED)
    add("9  Electrical", "ANL 150 A fuse + holder", N, "ea", 10.59, OK)
    add("9  Electrical", "8 AWG silicone wire, 5 m red + 5 m black",
        N, "set", 22.00, EST, "motor supplies its own phase leads + bullets")
    add("9  Electrical", "Heat shrink, Kapton, pack wrap", N, "set", 18.00, EST)

    # --------------------------------------------------- 9b odds and ends
    # Things that are easy to leave off a BOM and then stop a build dead.
    add("9b Small but essential", "Capacitor spot welder", 1, "ea", 0.00,
        OWNED, "used on V1")
    add("9b Small but essential", "M8 x 30 A4 mast bolts, spares",
        8, "ea", 0.90, EST, "Gong supplies its own; these are spares")
    add("9b Small but essential", "Silicone grease for the seal cord",
        1, "tube", 9.00, EST, "stops the cord bonding to the lid in storage")
    # SPLICE PLACEMENT, and it is not fussiness - V1's own build notes say
    # "do NOT cut and butt-joint at corners (corner joints leak)". Put it at
    # the MIDPOINT OF A LONG STRAIGHT RUN, and also clear of the six printed
    # ring joints: a cord splice sitting on top of a ring joint stacks two
    # discontinuities in the same place.
    add("9b Small but essential", "Cyanoacrylate for the cord splice",
        1, "ea", 6.00, EST)
    add("9b Small but essential", "Water-ingress alarm", N, "ea", 12.00, EST,
        "V1 carried one. Put the SENSOR on the module floor in the lowest "
        "corner, not up on the pack - it is only useful where water collects")
    # Remote float deleted - the VX3 ships with a floating band.
    # Used ONCE, to find which clutch number on the drill gives 3 Nm. After
    # that the drill does the 12 bolts at speed and the wrench goes in a
    # drawer. That is the right way round: nobody torque-wrenches 12 bolts in
    # a car park in the dark, and a clutch that has been calibrated is more
    # repeatable than a wrench that gets skipped.
    add("9b Small but essential", "1/4 in torque wrench, 1-10 Nm", 1, "ea",
        38.00, EST, "CALIBRATION TOOL - set the drill clutch with it, then "
        "use the clutch. The hatch is captive nuts in ASA against a hard "
        "stop; past the stop more torque only loads the nut pockets",
        tool=True)
    add("9b Small but essential", "Coiled ankle leash", N, "ea", 14.99, OK,
        "you trust the remote failsafe; this is so the board stays with you")
    add("9b Small but essential", "FCS-pattern leash plug", N, "ea", 9.00, EST)
    # A cloth handle, bolted on. That is all this ever needed to be - the
    # dense-foam surround that used to wrap the strip is gone.
    add("9b Small but essential", "Kayak-style webbing carry handle, 4 pk",
        1, "pk", 13.89, OK,
        str(2 * N) + " needed; 2 x M6 into the 6061 strip in the rail pocket")
    add("9b Small but essential", "M6 x 16 A4 + M6 insert, strap mounts",
        4 * N, "set", 1.40, EST)


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
    add("9c Pack wiring", "16 AWG wire, charge port and power button runs",
        N, "set", 9.00, EST)
    add("9c Pack wiring", "Dielectric grease, terminals", 1, "tube", 8.00, EST)
    add("9c Pack wiring", "Cable ties, lacing, adhesive mounts", N, "set",
        11.00, EST)
    add("9c Pack wiring", "Silicone sealant, BMS anti-vibration dabs",
        1, "tube", 7.00, EST, "V1 did this; stops the BMS walking")
    # The phase disconnect, in the cavity, exactly as V1. Without it the
    # potting/bung is decorative: the motor's pigtails run up the mast and
    # through the bore, so if they cannot be parted in the cavity the mast is
    # bolted on for life. M25 size takes 6-11 mm cable; 8 AWG silicone is 6.5.
    add("9c Pack wiring", "CESFONJER IP68 M25 inline housing, 3 pk",
        N, "pk", 15.00, EST,
        "3 per board, one per phase; SIZE UNVERIFIED - Amazon blocks "
        "scraping. Check they fit the 60 x 318 bay before ordering wire")
    add("9c Pack wiring", "5.5 mm bullets + adhesive shrink, ESC side",
        N, "set", 12.00, EST, "motor pigtails arrive with their own")
    add("9c Pack wiring", "Fish tape / pull cord for the mast conduit",
        1, "ea", 12.00, EST)

    # ------------------------------------------------------------ 10 foil
    # Derek's own foil is X-Over V2 (order 252112, 480.51 EUR delivered on
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
    add("10 Foil", "Gong shipping to Idaho, per foil", N, "ea", 124.00, OK,
        "115.50 EUR on order 252112; charged per ORDER, so putting both "
        "boards' foils in ONE order saves about $124")

    # ------------------------------------------- 10b drivetrain interface
    # Motor mount is jkoljo's printed PETG clamp (Thingiverse 5996522) - the
    # print is free, the hardware is not. Quantities off V1's as-built list.
    add("10b Drivetrain", "PETG filament 1 kg, mast clamp set", N, "kg",
        9.99, OK, "4 STEP files; 0.6 nozzle, 5 perims, 40% infill")
    add("10b Drivetrain", "M5 x 250 threaded rod (cut to ~171 mm)", 4 * N,
        "ea", 2.20, EST, "dry-assemble and mark before cutting all four")
    add("10b Drivetrain", "M5 nyloc nut + M6 x 20 fender washer", 4 * N,
        "set", 0.60, EST)
    add("10b Drivetrain", "M3 x 6 button head + M3 brass heat-set, nose cone",
        4 * N, "set", 0.50, EST)
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
    add("10b Drivetrain", "Stainless roll pin, drive pin", 2 * N, "ea", 1.50,
        EST, "MEASURE the shaft cross-hole - do not trust the 4 mm figure")
    add("10b Drivetrain", "M8 nyloc + washer, prop nut", N, "set", 1.50, EST)
    # Crimped, not soldered. XT150 is out.
    add("10b Drivetrain", "8 AWG marine ring lugs, 20 pk", 2, "pk", 16.99,
        OK, str(14 * N) + " needed; on M6 studs - nothing to solder")
    add("10b Drivetrain", "M6 stainless stud/busbar hardware", N, "set",
        14.00, EST)
    add("10b Drivetrain", "Hydraulic lug crimper, 6-70 mm2", 1, "ea", 38.00,
        EST, "one-time; this is what replaces soldering XT150s", tool=True)
    add("10b Drivetrain", "Adhesive-lined heat shrink, assorted", 1, "kit",
        16.00, EST)

    # ------------------------------------------------ 10c restraint & fitout
    # Currently switched OFF in the model (SHOW_RESTRAINT), so it does not
    # appear in the part list - but the module and pack still have to be held
    # down and the ESC still has to bolt to something.
    add("10c Restraint & fitout", "G10 chocks, equipment plate, pack tabs",
        0, "off", 0.00, OWNED, "cut from 1/8 and 1/2 in offcuts")
    add("10c Restraint & fitout", "25 mm webbing + ladder-lock buckles",
        N, "set", 20.00, EST, "2 straps per board")
    add("10c Restraint & fitout", "EVA bedding pads", N, "set", 12.00, EST)

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
    add("10d Shop consumables", "Spray adhesive + sacrificial MDF, CNC hold-down",
        1, "set", 35.00, EST, "foam is taped down, not clamped")
    add("10d Shop consumables", "Release wax / PVA for the cavity caul",
        1, "set", 20.00, EST)
    # Spare bagging film folded into the 3 rolls in section 5 - it was a
    # duplicate of the same consumable in a different section.
    add("10d Shop consumables", "Dowel pins + drill, two-sided registration",
        1, "set", 12.00, EST, tool=True)
    add("10d Shop consumables", "1/2 in single-flute + 1/2 in ball nose",
        1, "set", 70.00, EST, "if the shop does not have foam-suitable tooling", tool=True)
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
    add("10e Layup kit", "TotalBoat flexible spreader set", 2, "set", 5.99,
        OK)
    add("10e Layup kit", "Chip brushes and laminating roller", 1, "set",
        22.00, EST)
    add("10e Layup kit", "Nitrile gloves, 100 pk", 2, "box", 12.00, EST)
    add("10e Layup kit", "Respirator", 1, "ea", 0.00, OWNED)
    add("10e Layup kit", "3M 60923 organic vapour / acid gas P100, pair",
        2, "pr", 31.49, OK,
        "envirosafetyproducts.com; cartridges expire - buy near the layup")
    add("10e Layup kit", "Acetone, 1 gal, cleanup", 1, "gal", 39.95, OK)
    add("10e Layup kit", "Plastic sheeting + masking tape, bench protection",
        1, "set", 20.00, EST)
    add("10e Layup kit", "Sanding blocks + longboard for fairing", 1, "set",
        30.00, EST, tool=True)

    # ------------------------------------------------------- 11 finishing
    add("11 Finishing", "TotalBoat TotalFair epoxy fairing compound",
        N, "kit", 45.99, OK, "smallest kit, one per board")
    add("11 Finishing", "TotalBoat Premium Marine Topside Primer",
        1, "kit", 46.99, OK, "one covers both")
    add("11 Finishing", "TotalBoat Wet Edge topside paint, colour",
        N, "kit", 53.99, OK, "one-part polyurethane, quart")
    add("11 Finishing", "Traction pad, 3-piece", N, "set", 24.95, OK)
    add("11 Finishing", "Abrasives, cups, gloves, tape", N, "set", 40.00, EST)

    # ------------------------------------------------------- 12 logistics
    # G10 sheets are heavy and epoxy ships hazmat. Leaving this off is how a
    # BOM comes in under on the day.
    add("12 Freight and tax", "Shipping - G10, Divinycell, epoxy hazmat",
        1, "allow", 220.00, EST, "heavy and hazmat lines")
    # Idaho is a flat 6% state rate with NO local add-on in Ada County -
    # Boise and Meridian are both exactly 6%. This is the real rate, not a
    # placeholder.
    add("12 Freight and tax", "Idaho sales tax, 6% (Ada County, no local)",
        1, "allow", round(0.06 * sum(r["ext"] for r in ROWS), 2), OK)
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
            out.append("| " + r["item"] + " | " + str(r["qty"]) + " | "
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
    print("wrote " + path)
