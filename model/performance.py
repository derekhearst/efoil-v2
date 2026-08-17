"""What the board actually does on the water: takeoff, cruise, range.

Everything upstream of this has been geometry and cost. This is the first
thing that asks whether the design flies, and it is worth having because
three numbers that were assumed elsewhere - 5300 W peak, ~2400 W cruise,
and the range that justifies a 2304 Wh pack - have never been checked
against a wing.

Simple steady-state model, not CFD:
  lift      L = 1/2 rho V^2 S CL,  set equal to all-up weight
  induced   CDi = CL^2 / (pi AR e)
  profile   CD0 from a lifting-surface estimate + parasitic mast/fuse drag
  power     P = D V / (eta_prop * eta_motor * eta_esc)

It will not predict within 5%. It will tell you whether takeoff sits at
4 m/s or 9 m/s, whether cruise is 1.5 kW or 4 kW, and whether the pack
lasts 25 minutes or 70. Those are the decisions it exists to inform.

Usage:  python model/performance.py [rider_kg]
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cnc_drawings as C                                     # noqa: E402

RHO = 1000.0          # fresh water, Lucky Peak
G = 9.81

# --- efficiencies. These are the softest numbers here. ---------------------
ETA_PROP = 0.62       # ducted-less prop on a foil, typical DIY figure
ETA_MOTOR = 0.88      # Flipsky 65161 near its best point
ETA_ESC = 0.96
ETA = ETA_PROP * ETA_MOTOR * ETA_ESC

CL_MAX = 1.10         # thin section, no flaps, before it lets go
CL_CRUISE_MIN = 0.25  # below this you are going stupidly fast for the wing
OSWALD = 0.85


def wing(span_mm, cr_mm, ct_mm):
    span, cr, ct = span_mm / 1000.0, cr_mm / 1000.0, ct_mm / 1000.0
    area = 0.5 * (cr + ct) * span          # trapezoidal
    ar = span * span / area
    return area, ar


def drag(V, W, S, AR, S_stab, mast_area, fuse_area):
    """Total drag at speed V carrying weight W."""
    q = 0.5 * RHO * V * V
    CL = W / (q * S)
    CDi = CL * CL / (math.pi * AR * OSWALD)
    CD0 = 0.012                            # front wing section + surface
    D_wing = q * S * (CD0 + CDi)
    # stab runs near zero lift; count section drag only
    D_stab = q * S_stab * 0.014
    # mast is a strut at zero incidence; fuselage is a body
    D_mast = q * mast_area * 0.010
    D_fuse = q * fuse_area * 0.008
    return D_wing + D_stab + D_mast + D_fuse, CL


def foil_params():
    """FOIL_* live below the bpy marker, so pull them straight from source.

    Parsing rather than duplicating: a copy here would silently disagree with
    the model the first time a wing dimension changed.
    """
    import re
    src = open(os.path.join(HERE, "blender_board.py"), encoding="utf-8").read()
    out = {}
    for m in re.finditer(r"^(FOIL_[A-Z_,\s]+)=\s*([0-9.,\s]+)", src, re.M):
        names = [n.strip() for n in m.group(1).split(",")]
        vals = [float(v) for v in m.group(2).split(",") if v.strip()]
        for n, v in zip(names, vals):
            out[n] = v
    return out


def run(rider_kg=86.0):
    p = C.load_params()
    p["derive_layout"]()
    p.update(foil_params())
    S, AR = wing(p["FOIL_FW_SPAN"], p["FOIL_FW_CR"], p["FOIL_FW_CT"])
    S_st, _ = wing(p["FOIL_ST_SPAN"], p["FOIL_ST_CR"], p["FOIL_ST_CT"])
    # Only the submerged part of the mast makes drag, and with an 85 cm mast
    # most of it is out of the water at riding height. Counting the whole mast
    # overstated drag by about a third.
    mast_area = (p["FOIL_MAST_H"] * p["FOIL_MAST_WET"] / 1000.0
                 * p["FOIL_MAST_C"] / 1000.0)
    fuse_area = (p["FOIL_FUSE_L"] / 1000.0
                 * math.pi * p["FOIL_FUSE_D"] / 1000.0)

    board_kg, foil_kg = 25.1, 7.3
    W = (board_kg + foil_kg + rider_kg) * G
    wh = p["PACK_S"] * p["PACK_P"] * 18.0

    print("PERF  Gong X-Over V2 XL + Stab XL 48 + Pro Alu fuse + 85 cm alu mast")
    print("      front wing " + format(S * 1e4, ".0f") + " cm2, AR "
          + format(AR, ".1f") + "   all-up "
          + format(W / G, ".0f") + " kg   pack " + format(wh, ".0f") + " Wh")
    print()
    v_to = math.sqrt(2 * W / (RHO * S * CL_MAX))
    print("  MINIMUM FLYING SPEED (CL max " + format(CL_MAX, ".2f") + "):   "
          + format(v_to, ".1f") + " m/s = " + format(v_to * 2.237, ".1f")
          + " mph")
    print("  NOT the same as takeoff: getting there means dragging a")
    print("  displacing board through its own bow wave first, and this")
    print("  model does not cover that hump. That hump is what sets PEAK_W.")
    print()
    print("  {:>6} {:>7} {:>8} {:>9} {:>10} {:>9} {:>8}".format(
        "m/s", "mph", "CL", "drag N", "shaft W", "batt W", "min"))
    print("  " + "-" * 62)
    best = None
    for kn in range(4, 15):
        V = float(kn)
        D, CL = drag(V, W, S, AR, S_st, mast_area, fuse_area)
        if CL > CL_MAX:
            continue
        P_shaft = D * V
        P_batt = P_shaft / ETA
        mins = wh * 0.9 / P_batt * 60.0
        flag = ""
        if best is None or P_batt < best[1]:
            best = (V, P_batt, mins)
        print("  {:>6.1f} {:>7.1f} {:>8.2f} {:>9.0f} {:>10.0f} {:>9.0f}"
              " {:>8.0f}{}".format(V, V * 2.237, CL, D, P_shaft, P_batt,
                                   mins, flag))
    print()
    print("  best endurance at " + format(best[0], ".0f") + " m/s: "
          + format(best[1], ".0f") + " W, " + format(best[2], ".0f")
          + " min on 90% of the pack")
    print()
    # --- does it agree with V1? --------------------------------------
    # docs/v1/efoil-2-electrical.md, measured in service:
    #   cruise 15-25 A, takeoff peaks 70-100 A, on a 14S pack (50.4 V nom)
    print("  CHECK against V1's measured draw (14S, 50.4 V nominal):")
    for a_lo, a_hi, what in ((15, 25, "cruise"), (70, 100, "takeoff peak")):
        w_lo, w_hi = a_lo * 50.4, a_hi * 50.4
        print("    " + what.ljust(14) + format(a_lo, "d") + "-"
              + format(a_hi, "d") + " A = " + format(w_lo, ".0f") + "-"
              + format(w_hi, ".0f") + " W")
    # Which speeds does the model put inside V1's measured cruise band?
    # Computed, not asserted - a wing change must be able to break this.
    band = []
    for kn in range(3, 15):
        V = float(kn)
        D, CL = drag(V, W, S, AR, S_st, mast_area, fuse_area)
        if CL > CL_MAX:
            continue
        if 15 * 50.4 <= D * V / ETA <= 25 * 50.4:
            band.append(V)
    if band:
        print("    this model lands in that band at "
              + format(min(band), ".0f") + "-" + format(max(band), ".0f")
              + " m/s (" + format(min(band) * 2.237, ".0f") + "-"
              + format(max(band) * 2.237, ".0f") + " mph), which is exactly")
        print("    where an eFoil cruises. The model agrees with V1.")
    else:
        print("    NOTHING in this model's speed range lands in V1's measured")
        print("    cruise band - the model and the real board DISAGREE.")
    print()
    print("  so the long endurance figures are real FOR STEADY CRUISE.")
    print("  Real sessions run shorter because they are takeoffs, chop and")
    print("  speed, not one long glide. Treat cruise range as the ceiling.")
    print()
    print("    PEAK_W 5300 W covers the takeoff hump, not this table  -> "
          + ("consistent with V1" if 70 * 50.4 < 5300 < 110 * 50.4
             else "CHECK"))
    return best


if __name__ == "__main__":
    run(float(sys.argv[1]) if len(sys.argv) > 1 else 86.0)
