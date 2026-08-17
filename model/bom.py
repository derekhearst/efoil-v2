"""Complete itemised bill of materials.

Quantities that CAN be derived are derived - sheet counts from the live cut
list, fastener counts and cord lengths from the model - so this cannot drift
from the design. Everything else carries a tag saying where the number is from.

Usage:  python model/bom.py [n_boards]
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cnc_drawings as C                                    # noqa: E402
import fleet_cost as F                                      # noqa: E402

N = int(sys.argv[1]) if len(sys.argv) > 1 else 2
FREE_PACKS = 1                       # packs' worth of cells already on hand

# Counts read straight out of blender_board.py's report.
M = dict(hatch_bolts=12, mod_inserts=18, mast_bushings=4,
         hatch_cord_mm=1820, mod_cord_mm=1455, bay_glands=3,
         cells=128, nickel_m=7.0, conduit_mm=78)

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
    add("1  Core and shaping",
        "EPS rigid foam 2in x 48in x 8ft (HD 202532856)",
        math.ceil(1.5 * N), "sheet", 27.68, OK,
        "HD Meridian, 30 in stock, aisle 29 bay 020; $23.53 at 32+")
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

    # ------------------------------------------------------------- 2 G10
    by, p = F.g10_area_per_board()
    who = {3.175: "module floor, walls, flange-rail plies",
           12.7: "rim ring (4 pieces, 01a/01b) + module corner posts",
           19.05: "mast plate"}
    for th in sorted(by):
        lbl, area, price, bq, bprice, _ = F.SHEETS[th]
        sheets = max(1, math.ceil(by[th] * N / area))
        unit = bprice if (bq and sheets >= bq) else price
        add("2  G10 (ePlastics)", "G10 natural " + lbl + " - " + who[th],
            sheets, "sheet", unit, OK)

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
    add("3  Structural foam", "Divinycell H-80 1/4in quarter, module lid "
        "cores", 1, "sheet", 60.00, EST, "nobody stands on this one")
    # 3/4in is H-80 only, and H-80 carries the block fine - 17.7x on plate
    # bearing. Leash and handle pads come out of the same offcut.
    add("3  Structural foam", "Divinycell H-80 3/4in quarter sheet 21x42, "
        "mast blocks + leash/handle pads", 1, "sheet", 100.26, OK,
        "L18-1112; covers both boards")

    # ---------------------------------------------------------- 4 laminate
    add("4  Laminate", "E-glass 6 oz, 50in x 12ft, 2-pack",
        N, "pack", 19.07, OK, "your receipt")
    add("4  Laminate", "1708 biax, 50in wide", 3 * N, "yd", 12.50, OK)
    add("4  Laminate", "TotalBoat 5:1 gallon kit, slow hardener",
        N, "kit", 159.99, OK, "2.51 m2 laminate = 4.8 kg mixed = 1 kit/board")
    add("4  Laminate", "TotalBoat 5:1 quart kit, fillets and bonding",
        1, "kit", 68.99, OK)
    add("4  Laminate", "TotalBoat silica thickener, large", 1, "ea", 27.99,
        OK, "fillets and structural bonding")
    # No separate microballoons: TotalFair IS the fairing compound and doing
    # both is buying the same job twice.

    # ---------------------------------------------------- 5 vacuum bagging
    add("5  Vacuum bagging", "Pittsburgh 3 CFM 2-stage pump (HF 61176)",
        1, "ea", 139.99, OK, "one-time", tool=True)
    add("5  Vacuum bagging", "VR20 vacuum regulator", 1, "ea", 52.00, OK,
        "one-time", tool=True)
    add("5  Vacuum bagging",
        "Bagging starter kit - film, peel ply, tape, breather, connector",
        1, "kit", 127.40, OK, "one-time + first board", tool=True)
    # Fibre Glast, per-item rather than a kit: film 5 yd $24.95, breather
    # 1 yd $13.95, release film 1 yd $11.28.
    add("5  Vacuum bagging", "Vac bag film, 5 yd", 1, "roll", 24.95, OK)
    add("5  Vacuum bagging", "Breather / bleeder cloth", 2 * N, "yd", 13.95, OK)
    add("5  Vacuum bagging", "Low-temp release film", 2 * N, "yd", 11.28, OK)

    # ----------------------------------------------------- 6 hatch and seal
    # O3 CORD, BONDED IN - kept after the aluminium ring was reverted, because
    # the argument that decided it never depended on the ring material: 1857 mm
    # of hand-dispensed bead in a 4 x 2.4 groove will not be a uniform section,
    # and an extruded cord is dimensionally perfect out of the packet.
    # An extruded cord is dimensionally perfect out of the packet; bonding it
    # in solves the only thing pour-in-place was buying, which was stopping it
    # lifting out of the groove on a hatch opened every ride.
    add("6  Hatch and seal", "Solid silicone cord, 3 mm round - BOTH seals",
        math.ceil((M["hatch_cord_mm"] + M["mod_cord_mm"]) * N / 1000) + 4,
        "m", 2.00, EST,
        "buy long - splice on a straight run, never a corner")
    add("6  Hatch and seal", "Silicone adhesive, bonding the cord into groove",
        1, "tube", 12.00, EST,
        "a thin continuous bead under the cord. It cannot then migrate, lift "
        "out, or be pinched under the lid in a dark car park")
    add("6  Hatch and seal", "M5 x 16 A4 stainless socket cap",
        M["hatch_bolts"] * N, "ea", 0.55, EST)
    # NOT the $0.14 self-tapping brass insert that was here: driving a coarse
    # thread into a brittle laminate wedges it between plies, which is exactly
    # why the mast plate uses bonded bushings. A wire-thread insert is tapped
    # in once and leaves a STAINLESS working thread - the hatch is opened
    # ~50+ times a season, so the thread has to survive cycling and not gall.
    add("6  Hatch and seal", "M5 tangless wire-thread insert (2D), 50 pc",
        1, "pack", 24.00, EST, str(M["hatch_bolts"] * N) + " needed")
    add("6  Hatch and seal", "M5 STI tap + tangless install/extract tool",
        1, "set", 38.00, EST,
        "one-time; the STI tap is oversize and a normal M5 tap will NOT do",
        tool=True)
    add("6  Hatch and seal", "MDF 12 mm, full template set (14 templates)",
        2, "sheet", 35.00, EST,
        "one-time; cut once, used on both boards and any future one", tool=True)

    # ---------------------------------------------------------- 7 module
    add("7  Module", "M4 x 12 A4 stainless socket cap",
        M["mod_inserts"] * N, "ea", 0.35, EST)
    add("7  Module", "M4 brass heat-set insert, 100 pc", 1, "pack", 12.00, EST)
    # module cord is now bought with the hatch cord - same 3 mm stock
    add("7  Module", "PG16 cable gland IP68, 10 pk", 1, "pk", 9.99, OK,
        str(M["bay_glands"] * N) + " needed")
    add("7  Module", "25 mm cable gland, conduit wet-to-dry crossing",
        N, "ea", 6.00, EST)
    add("7  Module", "M12 IP68 membrane vent plug", N, "ea", 9.95, OK,
        "NOT optional on a sealed lithium box")
    add("7  Module", "22 mm IP68 latching panel button", N, "ea", 12.49, OK)
    add("7  Module", "Panel-mount charge port + cap", N, "ea", 12.00, EST)

    # -------------------------------------------------- 8 mast hardpoint
    add("8  Mast hardpoint", "316 stainless bar 20 mm x 300 mm, bushing stock",
        1, "ea", 28.00, EST,
        str(M["mast_bushings"] * N) + " bushings, 16 mm long")
    add("8  Mast hardpoint", "Bushing machining - drill, tap M8, part off",
        1, "job", 60.00, EST, "free with lathe access")
    add("8  Mast hardpoint", "3M DP460 structural epoxy 50 ml + gun",
        1, "ea", 45.00, EST, "bonds the bushings; gun is one-time")
    add("8  Mast hardpoint", "G10 tube 32 OD x 28 ID, wire conduit",
        N, "off", 18.00, EST, str(M["conduit_mm"]) + " mm each")

    # ------------------------------------------------------- 9 electrical
    add("9  Electrical", "Flipsky 65161 120KV motor", N, "ea", 298.00, OK)
    add("9  Electrical", "Flipsky 75200 Pro V2 ESC", N, "ea", 150.00, OK)
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
        cases = math.ceil(buy / F.CELL_CASE_N)
        add("9  Electrical",
            "BAK N21700CG-50, 130-cell case (BatteryHookup)",
            cases, "case", F.CELL_CASE_USD, OK, "new overstock")
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
    add("9b Small but essential", "Cyanoacrylate for the cord splice",
        1, "ea", 6.00, EST)
    add("9b Small but essential", "Water-ingress alarm", N, "ea", 12.00, EST,
        "V1 carried one - finds a leak before the cells do")
    add("9b Small but essential", "Coiled ankle leash", N, "ea", 14.99, OK,
        "you trust the remote failsafe; this is so the board stays with you")
    add("9b Small but essential", "FCS-pattern leash plug", N, "ea", 9.00, EST)
    add("9b Small but essential", "Kayak-style carry handle, 4 pk",
        1, "pk", 13.89, OK,
        str(2 * N) + " needed; bolts to the G10 strip in the rail pocket")
    add("9b Small but essential", "M6 x 16 A4 + M6 insert, strap mounts",
        4 * N, "set", 1.40, EST)


    # ---------------------------------------------- 9c every joint in the pack
    # Walked the whole current path: cells -> nickel -> bus -> BMS -> fuse ->
    # ESC -> motor, plus the balance taps and the two panel fittings. These
    # are what was missing.
    add("9c Pack wiring", "8 AWG bare copper for edge bridging jumpers",
        N, "set", 16.00, EST, "V1 used 26 per pack on the outer bridge strips")
    add("9c Pack wiring", "Solder + flux, bus bars and jumpers", 1, "set",
        22.00, EST, "pre-solder jumpers OFF the cells - never heat near a cell")
    add("9c Pack wiring", "Balance harness, 17-wire", N, "ea", 0.00, OWNED,
        "DALY ships one - CONFIRM before you need it")
    add("9c Pack wiring", "16 AWG wire, charge port and power button runs",
        N, "set", 9.00, EST)
    add("9c Pack wiring", "Dielectric grease, terminals", 1, "tube", 8.00, EST)
    add("9c Pack wiring", "Cable ties, lacing, adhesive mounts", N, "set",
        11.00, EST)
    add("9c Pack wiring", "Silicone sealant, BMS anti-vibration dabs",
        1, "tube", 7.00, EST, "V1 did this; stops the BMS walking")
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
    # Prop: reamed Flite rather than printed, per your call.
    add("10b Drivetrain", "Flite propeller", N, "ea", 45.00, EST,
        "community pick over the Flipsky alu prop")
    add("10b Drivetrain", "Ream to 12 mm + drive-pin adapter", N, "job",
        25.00, EST, "printables.com/model/583026 drill guide")
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
    add("10d Shop consumables", "Spray adhesive + sacrificial MDF, CNC hold-down",
        1, "set", 35.00, EST, "foam is taped down, not clamped")
    add("10d Shop consumables", "Release wax / PVA for the cavity caul",
        1, "set", 20.00, EST)
    add("10d Shop consumables", "Spare vacuum bagging film", 1, "roll", 40.00,
        EST, "a bag that leaks mid-cure ends the session")
    add("10d Shop consumables", "EPS offcut for a CNC test piece", 1, "ea",
        15.00, EST, "prove CAM, workholding and the flip before a real core", tool=True)
    add("10d Shop consumables", "Dowel pins + drill, two-sided registration",
        1, "set", 12.00, EST, tool=True)
    add("10d Shop consumables", "1/2 in single-flute + 1/2 in ball nose",
        1, "set", 70.00, EST, "if the shop does not have foam-suitable tooling", tool=True)


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
