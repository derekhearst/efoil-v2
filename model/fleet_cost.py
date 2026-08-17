"""What N boards actually cost, from the current geometry.

Kev and Dallin want their own, so the interesting number stopped being "what
does a board cost" and became "what does the THIRD one cost" - which is a lot
less, because tools and templates are bought once and sheet goods are bought in
whole sheets whether you need a whole sheet or not.

Sheet areas come from the live cut list, so this cannot drift from the design.

Usage:  python model/fleet_cost.py [n_boards]
"""
import math
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cnc_drawings as C                                   # noqa: E402

IN2 = 645.16              # mm2 per in2
NEST = 0.75               # usable fraction of a sheet after nesting

# thickness mm -> (label, sheet in2, $/sheet, bulk qty, $/sheet bulk, verified)
SHEETS = {
    3.175:  ('1/8" 24x36',  864, 133.86, None, None, True),
    9.525:  ('3/8" 12x24',  288, 134.94, None, None, True),
    # 18x24, not 12x24. The four-piece ring's long bars are 23.3 in end to
    # end and 2.6 in deep; four of them plus four short bars need 15.8 in of
    # width. A 12 in sheet physically cannot nest two rings' worth.
    12.7:   ('1/2" 18x24',  432, 267.62, None, None, True),
    # 12x18, not 12x24. Two mast plates are 9.84 x 6.89 in each; laid with the
    # 9.84 across the 12 in width they stack to 14.0 of the 18 in length. Four
    # inches spare. The 12x24 was 63% used and $67 dearer for nothing.
    19.05:  ('3/4" 12x18',  216, 200.75, None, None, True),
}

# per board, $ low/high, verified?
PER_BOARD = [
    ("EPS blank (2 sheets construction foam)", 80, 120, False),
    ("Divinycell H80 lid cores",               115, 115, False),
    ("Divinycell H200 mast block",              70, 100, False),
    ("Glass cloth + biax",                      57,  57, True),
    # Was $330-390, carried over from the old budget's "2 gallon kits + a
    # quart". The laminate is 2.51 m2 (2.19 outer + 0.32 cavity); at 2 x 6 oz
    # throughout plus 1708 biax outside that is 2.82 kg of cloth, so 2.82 kg of
    # resin at a bagged 1:1, plus ~2 kg for fillets, bonding and fairing.
    # 4.8 kg mixed = ONE gallon kit, not two. Cross-checks against the model's
    # own GLASS_KGM2: 2.51 m2 x 2.20 = 5.5 kg of finished laminate vs 5.6 kg
    # of cloth+resin here.
    ("Epoxy + fillers (1-1.5 gal kits)",        160, 240, True),
    ("Bagging consumables (film/peel/breather)", 55,  70, False),
    ("Hardware, inserts, seal cord",            55,  75, False),
    ("Finishing",                              121, 151, False),
]

POWERTRAIN = [
    ("Flipsky 65161 motor",              298.00, 298.00, True),
    ("Flipsky 75200 Pro ESC",            150.00, 150.00, True),
    ("Flipsky VX3 remote",                71.00,  71.00, True),
    ("DALY Smart BMS 16S 200A",          183.36, 183.36, True),
    ("Charger 67.2 V 5 A  (16S - NOT 58.8)", 50.00, 70.00, False),
    ("Nickel strip, connectors, fuse",    52.00,  52.00, True),
]

ONE_TIME = [
    ("Vacuum pump",                      139.99, 139.99, True),
    ("Vacuum regulator",                  52.00,  52.00, True),
    ("Bagging hardware (reusable)",        40.00,  40.00, False),
    ("MDF templates + cauls",              30.00,  50.00, False),
]

# BAK N21700CG-50 - the exact cell the pack is designed around, and NOT the
# Samsung/EVE 50E at $4.99: those are 9.8 A cells against an 11.5 A/cell peak,
# i.e. 117% of rating.
#
# Battery Hookup has it as new overstock at $2.00/cell in 130-cell cases
# ($260), against $5.99 retail. The listing has been up a long time at the same
# price, so it reads as standing overstock rather than a clearance that will
# evaporate. Retail is still kept as the high figure, because surplus is
# surplus and the day it does go, it goes.
CELL_CASE_N, CELL_CASE_USD = 130, 260.00
CELL_EA_LO, CELL_EA_HI = CELL_CASE_USD / CELL_CASE_N, 5.99
FOIL_EA = 629.00
CNC_DAY = 200.00


# Bounding box is the right material area for a solid plate and badly wrong for
# a ring. The rim ring's bbox is 3.7x its actual annulus.
#
# But 0.55 for the bar nesting was also wrong, and pessimistically so. A 34 mm
# band is a 1.34 in strip: eight of them fit across a 12 in sheet, giving 192 in
# of strip per sheet, and the longest straight run is 18.9 in so nothing is
# wasted on length. Two boards need 119 in of strip plus 39 in2 of corner
# blocks = 198 in2 of a 288 in2 sheet. Strips nest at ~0.97, not 0.55, and the
# difference is a whole $178 sheet.
# Now measured against the ACTUAL four-piece split (parts 01a/01b), not a
# hand-wave. Per ring the two long bars are 591 x 66 bbox and the two short
# bars 34 x 254, so 147.7 in2 of blank buys 95.8 in2 of ring: 0.65. Knocked to
# 0.65 because the long bars are a deep-C profile whose bbox is mostly air on
# the inboard side, and real nesting will not recover all of it.
#
# This used to be 0.90, which claimed two rings fitted a 12x24 sheet. Checked
# against real pieces with saw kerf they do not - it needs a 12x36. That was
# an $89 hole in the budget.
RING_NEST = 0.65

# Rails laminated from three plies of 1/8" rather than bought as 3/8" stock:
# 3 x 3.175 = 9.525 mm exactly, the leftover 1/8" is already paid for, the seal
# groove is 2.4 mm deep so it stays inside the top ply, and a bonded-in rail is
# not primary structure. Saves the entire 3/8" sheet.
FLANGE_FROM_EIGHTH = True


def g10_area_per_board():
    p = C.load_params()
    parts, _, _ = C.build(p)
    cav_l = p["CAV_X1"] - p["CAV_X0"]
    rw, cw = p["RIM_W"], p["CAV_WIDTH"]
    ring_in2 = ((cav_l + 2 * rw) * (cw + 2 * rw) - cav_l * cw) / IN2
    by = defaultdict(float)
    for q in parts:
        if "G10" not in q["material"]:
            continue
        th = round(q["thick"], 3)
        if "ring_bar" in q["name"]:
            continue            # 01a/01b ARE the ring - counted once, below
        if "rim_ring" in q["name"]:
            a = ring_in2 / RING_NEST      # four-piece split; RING_NEST is it
        else:
            a = q["w"] * q["h"] / IN2 / NEST      # bbox + nesting waste
        # Laminate from 1/8" plies rather than buy the thickness as stock. The
        # imperial sizes are exact multiples of 1/8" (3.175 mm):
        #   flange rail  9.525 = 3 x 3.175
        # The rail is not primary structure, is fully bonded and encapsulated,
        # and the leftover 1/8" is already bought - so this saves the whole
        # 3/8" sheet. The module corner posts could go the same way (4 plies),
        # but they share the 1/2" sheet the rim ring already needs, so there is
        # nothing to gain and one less process step to keep them as stock.
        if FLANGE_FROM_EIGHTH and "flange_rail" in q["name"]:
            th = 3.175
            a *= 3
        by[th] += q["qty"] * a
    return by, p


# A longer board for a heavier rider is very nearly free, which is not
# obvious. The cavity is derived from the MODULE, which is derived from the
# PACK - none of it depends on LENGTH - so every G10 part, both lid cores, the
# cavity caul and both MDF routing templates are byte-identical between a
# 1400 mm board and a 1532 mm one. Only the EPS core program and the paper
# glass templates change, and both regenerate for nothing. All a variant costs
# is the extra foam, cloth, resin and filler for the extra hull area.
HULL_SCALED = ("EPS blank (2 sheets construction foam)", "Glass cloth + biax",
               "Epoxy + fillers (1-1.5 gal kits)", "Finishing",
               "Bagging consumables (film/peel/breather)")


def run(n, free_packs=1, cnc_days=None, share_foil=0, sizes=None):
    by, p = g10_area_per_board()
    cells = p["PACK_S"] * p["PACK_P"]
    cnc_days = cnc_days if cnc_days is not None else 2 + n

    print(f"FLEET  {n} board(s)   pack {p['PACK_S']}S{p['PACK_P']}P = "
          f"{cells} cells each")
    print()
    print("  G10 - whole sheets (areas already include nesting waste):")
    g10_lo = g10_hi = 0.0
    for th in sorted(by):
        lbl, area, price, bq, bprice, _ = SHEETS[th]
        need = by[th] * n
        sheets = max(1, math.ceil(need / area))
        unit = bprice if (bq and sheets >= bq) else price
        cost = sheets * unit
        g10_lo += cost
        g10_hi += cost
        print(f"    {lbl:<12} need {need:>6.0f} in2  -> {sheets} sheet(s) "
              f"@ ${unit:>7.2f} = ${cost:>8.2f}   ({need/(area*sheets):.0%} "
              f"of what you buy)")
    print(f"    {'':<12} {'':>25}    G10 total  ${g10_lo:>8.2f}")

    def block(title, rows, mult):
        lo = sum(r[1] for r in rows) * mult
        hi = sum(r[2] for r in rows) * mult
        print(f"\n  {title}  (x{mult})")
        for nm, a, b, v in rows:
            tag = "OK" if v else "est"
            rng = f"${a:,.2f}" if a == b else f"${a:,.0f}-{b:,.0f}"
            print(f"    {nm:<42} {rng:>16}  {tag}")
        return lo, hi

    # sizes = list of length factors, one per board (1.0 = the 1400 mm hull)
    sizes = sizes or [1.0] * n
    area = sum(sizes)
    print("")
    print(f"  Per board, materials   (hull-area lines x{area:.2f} for {len(sizes)} boards)")
    b_lo = b_hi = 0.0
    for nm, a, b, v in PER_BOARD:
        mult = area if nm in HULL_SCALED else n
        b_lo += a * mult
        b_hi += b * mult
        rng = f"${a*mult:,.0f}" if a == b else f"${a*mult:,.0f}-{b*mult:,.0f}"
        print(f"    {nm:<42} {rng:>16}  {'OK' if v else 'est'}")
    p_lo, p_hi = block("Per board, powertrain", POWERTRAIN, n)
    o_lo, o_hi = block("One-time (already yours after board 1)", ONE_TIME, 1)

    buy_packs = max(0, n - free_packs)
    need_cells = buy_packs * cells
    cases = math.ceil(need_cells / CELL_CASE_N)
    c_lo = cases * CELL_CASE_USD
    c_hi = need_cells * CELL_EA_HI
    print("")
    print(f"  Cells: {free_packs} pack(s) free, {buy_packs} to buy = {need_cells} cells")
    print(f"         surplus  {cases} case(s) x {CELL_CASE_N} @ ${CELL_CASE_USD:,.0f}"
          f"  = ${c_lo:>7,.0f}   ({cases*CELL_CASE_N - need_cells} spare)")
    print(f"         retail   {need_cells} @ ${CELL_EA_HI}"
          f"          = ${c_hi:>7,.0f}")

    foils = n - share_foil
    f_tot = foils * FOIL_EA
    print(f"  Foils: {foils} @ ${FOIL_EA:,.0f} = ${f_tot:,.0f}"
          f"   ({share_foil} shared)")
    cnc = cnc_days * CNC_DAY
    print(f"  CNC:   {cnc_days} day passes @ ${CNC_DAY:,.0f} = ${cnc:,.0f}")

    lo = g10_lo + b_lo + p_lo + o_lo + c_lo + f_tot + cnc
    hi = g10_hi + b_hi + p_hi + o_hi + c_hi + f_tot + cnc
    print(f"\n  {'TOTAL':<20} ${lo:>10,.0f} - ${hi:,.0f}")
    print(f"  {'per board':<20} ${lo/n:>10,.0f} - ${hi/n:,.0f}")
    return lo, hi


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    run(n)


def scenarios():
    """The three boards Derek actually wants, which are not three of the same.

    A - V2 hull, V1's electronics moved across (and V1's foil with them)
    B - V2 hull, new powertrain, the spare cells on hand
    C - V2 hull, everything new
    """
    by, p = g10_area_per_board()
    n = 3
    cells = p["PACK_S"] * p["PACK_P"]

    g10 = 0.0
    for th in sorted(by):
        lbl, area, price, bq, bprice, _ = SHEETS[th]
        sheets = max(1, math.ceil(by[th] * n / (area * NEST)))
        unit = bprice if (bq and sheets >= bq) else price
        g10 += sheets * unit
    g10_ea = g10 / n
    cnc_ea = (2 + n) * CNC_DAY / n
    mat_lo = sum(r[1] for r in PER_BOARD)
    mat_hi = sum(r[2] for r in PER_BOARD)
    pwr_lo = sum(r[1] for r in POWERTRAIN)
    pwr_hi = sum(r[2] for r in POWERTRAIN)
    one_lo = sum(r[1] for r in ONE_TIME)
    one_hi = sum(r[2] for r in ONE_TIME)
    cell_lo = CELL_CASE_USD                     # one 130-case covers one pack
    cell_hi = cells * CELL_EA_HI

    rows = [
        ("A  V1 electronics moved over", mat_lo, mat_hi, 0, 0, 0, 0, 0, 0),
        ("B  new powertrain, spare cells", mat_lo, mat_hi,
         pwr_lo, pwr_hi, 0, 0, FOIL_EA, FOIL_EA),
        ("C  everything new", mat_lo, mat_hi,
         pwr_lo, pwr_hi, cell_lo, cell_hi, FOIL_EA, FOIL_EA),
    ]
    print(f"THREE BOARDS   G10 ${g10_ea:,.0f}/board (3-board buy), "
          f"CNC ${cnc_ea:,.0f}/board, pack = {cells} cells")
    print()
    hdr = (f"  {'board':<32}{'hull':>13}{'powertrain':>13}"
           f"{'cells':>13}{'foil':>8}{'TOTAL':>17}")
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    t_lo = t_hi = 0.0
    for nm, ml, mh, pl, ph, cl, ch, fl, fh in rows:
        hl, hh = ml + g10_ea + cnc_ea, mh + g10_ea + cnc_ea
        lo, hi = hl + pl + cl + fl, hh + ph + ch + fh
        t_lo += lo
        t_hi += hi
        def f(a, b):
            return "-" if a == b == 0 else (f"${a:,.0f}" if a == b
                                            else f"${a:,.0f}-{b:,.0f}")
        print(f"  {nm:<32}{f(hl,hh):>13}{f(pl,ph):>13}{f(cl,ch):>13}"
              f"{f(fl,fh):>8}{f(lo,hi):>17}")
    print(f"\n  {'one-time tools (already yours)':<32}"
          f"{'':>47}{f'${one_lo:,.0f}-{one_hi:,.0f}':>17}")
    print(f"  {'ALL THREE':<32}{'':>47}"
          f"{f'${t_lo+one_lo:,.0f}-{t_hi+one_hi:,.0f}':>17}")
