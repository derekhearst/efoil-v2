"""Every template needed to build the board without measuring anything.

The point is that no line on this board should ever be hand-traced or laid out
with a tape. Each template below is cut once from 12 mm MDF and used on both
boards - and on any future one, since they all come off the parametric model
and cannot drift from it.

Two kinds of template, and it matters which is which:

  BEARING  cut at the FINISHED size. Use a flush-trim bit whose bearing rides
           the template edge, so the cut matches the template exactly.
  BUSHING  cut OVERSIZE by GUIDE_OFF. Use a guide bushing; the cutter runs
           inboard of the template edge by that offset.

Registration: every template carries the board centreline and two station
marks on the REG layer. Line those up with the marks on the blank and the
template can only sit one way.

Run:  python model/templates.py
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cnc_drawings as C                                    # noqa: E402

OUT = os.path.join(os.path.dirname(HERE), "cnc", "templates")

# (guide bushing OD - cutter OD) / 2. CHECK THIS AGAINST YOUR OWN ROUTER
# before cutting any BUSHING template - it is the one number here that
# depends on tooling rather than on the design.
GUIDE_OFF = 5.0
# Every 100 mm, not every 15% of length. Six gauges is enough to CHECK a
# machined core; it is nowhere near enough to SHAPE one by hand, and hand
# shaping is now the realistic fallback - the makerspace is not answering, and
# the EPS core is the only part left on this board that wants a CNC at all.
# 13 stations at 100 mm centres is what a longboard sander can fair between.
# --- WHO ACTUALLY NEEDS THESE ---------------------------------------------
# T01-T07 are ROUTER templates, and every feature they guide is cut by the CNC
# if there is a CNC: the outline, the cavity, the rim rebate, the mast pockets,
# the handle and leash pads. With a month pass booked they are dead weight.
# They exist as the HAND-SHAPING FALLBACK, and that is the only reason.
#
# What is needed EITHER WAY lives in cnc_drawings, not here:
#   13_cavity_caul  - presses the cavity laminate during bagging
#   14_groove_guide - opens the seal groove AFTER glassing, on a finished
#                     board. That is a hand operation on both routes.
#
# T08/T09 are GAUGES, not templates - MDF sections you offer up to the
# machined core to check it before it gets glassed. Derek does not want
# them, and it is his call at the machine: they only ever caught SETUP
# error, which is the flip and the two-piece seam, and he is the one
# standing there able to see a seam.
# CHECK_GAUGES = True brings them back. They are not deleted, because the
# day the CNC falls through and HAND_SHAPE goes True they are the cheap end
# of the same family.
HAND_SHAPE = False                 # True -> full fallback set, 21 templates
CHECK_GAUGES = False               # True -> 3 stations + rocker/deck gauge
CHECK_STATIONS = (0.25, 0.50, 0.75) if CHECK_GAUGES else ()
STATIONS = tuple(round(x / 1400.0, 4) for x in range(100, 1400, 100))

PARTS = []


def add(name, dxf, w, h, kind, note):
    # Every BEARING template is a router guide for a feature the CNC cuts
    # anyway. With machine access booked they are dead weight, so they are
    # only emitted for the hand-shaping fallback. GAUGES always emit - a few
    # sections are worth having to check a machined core before it is glassed.
    if kind == "BEARING" and not HAND_SHAPE:
        return
    dxf.save(os.path.join(OUT, name + ".dxf"))
    PARTS.append(dict(name=name, w=w, h=h, kind=kind, note=note))


def reg_marks(d, x0, x1, xs, y):
    """Centreline + station ticks so the template can only land one way."""
    d.line(x0, 0.0, x1, 0.0, layer="REG")
    for x in xs:
        d.line(x, -y, x, y, layer="REG")


def offs(pts, off):
    """Crude outward offset of a closed polyline about its own centroid.

    Good enough for a bushing offset on shapes this size, and it keeps the
    template generation dependency-free.
    """
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    out = []
    for x, y in pts:
        dx, dy = x - cx, y - cy
        n = math.hypot(dx, dy) or 1.0
        out.append((x + dx / n * off, y + dy / n * off))
    return out


def build(p):
    os.makedirs(OUT, exist_ok=True)
    L = p["LENGTH"]
    cav_l = p["CAV_X1"] - p["CAV_X0"]
    CAV_W, RIM_W, R = p["CAV_WIDTH"], p["RIM_W"], p["CAV_CORNER_R"]

    # ---- T01 planform, half ------------------------------------------------
    d = C.Dxf()
    pts = [(x * L / 200.0, p["half_width"](x / 200.0)) for x in range(201)]
    d.poly(pts + [(L, 0.0), (0.0, 0.0)], close=True)
    reg_marks(d, 0, L, (p["SEAM_X"], p["MAST_X"], p["CAV_X0"], p["CAV_X1"]),
              max(q[1] for q in pts))
    add("T01_planform_half", d, L, max(q[1] for q in pts), "BEARING",
        "half outline - flip on the centreline for the other side. Marks are "
        "the seam, the mast axis and both ends of the cavity.")

    # ---- T02 cavity opening ------------------------------------------------
    d = C.Dxf()
    cav = C.rrect(0, cav_l, 0, CAV_W, R)
    d.poly(cav)
    reg_marks(d, -40, cav_l + 40, (cav_l / 2,), CAV_W / 2 + 30)
    add("T02_cavity_opening", d, cav_l, CAV_W, "BEARING",
        "through-cut in layers 2 and 3, and the floor pocket wall in layer 1. "
        "Same outline all three times.")

    # ---- T03 rim rebate ----------------------------------------------------
    d = C.Dxf()
    d.poly(C.rrect(-RIM_W, cav_l + RIM_W, -RIM_W, CAV_W + RIM_W, R + RIM_W))
    d.poly(cav, layer="CHANNEL")
    reg_marks(d, -RIM_W - 40, cav_l + RIM_W + 40, (cav_l / 2,),
              CAV_W / 2 + RIM_W + 30)
    add("T03_rim_rebate", d, cav_l + 2 * RIM_W, CAV_W + 2 * RIM_W, "BEARING",
        "the ledge the G10 rim ring beds into, cut to the RIM_T depth. "
        "CHANNEL line is the cavity opening for reference - do not cut it.")

    # ---- T04 mast pocket (dense block) ------------------------------------
    d = C.Dxf()
    gl, gw = p["G10_L"], p["G10_W"]
    mx0 = p["MAST_X"] - gl / 2 - p["DENSE_MARGIN_X"]
    mx1 = p["MAST_X"] + gl / 2 + p["DENSE_MARGIN_X"]
    my = gw / 2 + p["DENSE_MARGIN_Y"]
    d.poly(C.rrect(0, mx1 - mx0, -my, my, 30.0))
    d.poly(C.rect(mx1 - mx0) if False else
           C.rect((mx1 - mx0) / 2 - gl / 2, (mx1 - mx0) / 2 + gl / 2,
                  -gw / 2, gw / 2), layer="CHANNEL")
    reg_marks(d, -40, mx1 - mx0 + 40, ((mx1 - mx0) / 2,), my + 30)
    add("T04_mast_block_pocket", d, mx1 - mx0, 2 * my, "BEARING",
        "dense-foam block pocket in the hull underside. CHANNEL rectangle is "
        "the G10 plate footprint - that is T05, cut deeper inside this one.")

    # ---- T05 mast plate pocket --------------------------------------------
    d = C.Dxf()
    d.poly(C.rect(0, gl, 0, gw))
    for sx in (-1, 1):
        for sy in (-1, 1):
            d.circle(gl / 2 + sx * p["BOLT_SPACING_X"] / 2,
                     gw / 2 + sy * p["BOLT_SPACING_Y"] / 2,
                     p["INSERT_OD"] / 2, layer="HOLES")
    reg_marks(d, -30, gl + 30, (gl / 2,), gw / 2 + 20)
    add("T05_mast_plate_pocket", d, gl, gw, "BEARING",
        "plate pocket, and it doubles as the drill guide for the four "
        "bushing bores.")

    # ---- T06 handle strip + drill positions --------------------------------
    d = C.Dxf()
    hl, hw_ = p["HANDLE_PLATE_L"], p["HANDLE_PLATE_W"]
    d.poly(C.rect(0, hl, 0, hw_))
    for sx in (-1, 1):
        d.circle(hl / 2 + sx * p["HANDLE_BOLT_DX"] / 2, hw_ / 2,
                 p["HANDLE_INS_D"] / 2, layer="HOLES")
    reg_marks(d, -30, hl + 30, (hl / 2,), hw_ + 20)
    add("T06_handle_strip", d, hl, hw_, "BEARING",
        "one template, used both sides. NOT a pocket - the handles are a "
        "webbing strap bolted to the rail surface. This locates the shallow "
        "milled facet the G10 strip beds into, and drills the two inserts. "
        "Strip centreline sits " + format(p["HANDLE_Y"], ".0f") + " mm off the "
        "board centreline, where the rail is at "
        + format(p["HANDLE_PLATE_T"], ".1f") + " mm thick stock; facet is only "
        "~1.6 mm deep because the strip is narrow.")

    # ---- T07 leash pad -----------------------------------------------------
    d = C.Dxf()
    lp = p["LEASH_PAD"]
    d.poly(C.rect(0, lp, 0, lp))
    d.circle(lp / 2, lp / 2, p["LEASH_BORE_D"] / 2, layer="HOLES")
    reg_marks(d, -25, lp + 25, (lp / 2,), lp / 2 + 20)
    add("T07_leash_pad", d, lp, lp, "BEARING",
        "pad pocket; HOLES circle is the FCS plug bore, cut after the pad is "
        "bonded in.")

    # ---- T08 station sections ---------------------------------------------
    # Not router templates - shape gauges. Cut them, notch the centreline,
    # and check the machined core against them before glassing.
    for st in (STATIONS if HAND_SHAPE else CHECK_STATIONS):
        d = C.Dxf()
        hw, t = p["half_width"](st), p["thickness"](st)
        sec = p["section"](hw, t, st)
        r = p["rocker"](st)
        prof = [(q[0], q[1] + r) for q in sec]
        d.poly(prof + [(-q[0], q[1] + r) for q in reversed(sec)], close=True)
        d.line(0, -20, 0, max(q[1] for q in prof) + 20, layer="REG")
        add("T08_station_" + format(st * 100, "02.0f"), d, 2 * hw,
            max(q[1] for q in prof), "GAUGE",
            "section at x = " + format(st * p["LENGTH"], ".0f") + " mm "
            "(" + format(st * 100, ".0f") + "% of length). Shape gauge, not a "
            "router template.")

    # ---- T09 rocker / deck profile ----------------------------------------
    d = C.Dxf()
    bot = [(x * L / 200.0, p["rocker"](x / 200.0)) for x in range(201)]
    dk = [(x * L / 200.0, p["deck_z_at"](x * L / 200.0, 0.0))
          for x in range(201)]
    d.poly(bot, close=False)
    d.poly(dk, layer="CHANNEL", close=False)
    reg_marks(d, 0, L, (p["SEAM_X"], p["MAST_X"]), 0)
    if HAND_SHAPE or CHECK_GAUGES:
        add("T09_rocker_and_deck", d, L, max(q[1] for q in dk), "GAUGE",
            "centreline profile. Solid is the hull bottom (rocker), CHANNEL "
            "is the deck. Cut as two separate gauges or one long one.")
    return PARTS


if __name__ == "__main__":
    p = C.load_params()
    p["derive_layout"]()
    parts = build(p)
    lines = ["# Templates", "",
             "Cut from **12 mm MDF**. Every one comes off the parametric model, "
             "so nothing here needs measuring or tracing.", "",
             "| Kind | Meaning |", "|---|---|",
             "| `BEARING` | cut at FINISHED size - flush-trim bit, bearing "
             "rides the template edge |",
             "| `BUSHING` | cut OVERSIZE by the guide-bushing offset |",
             "| `GAUGE` | not a router template - a shape gauge to check "
             "against |", "",
             "Every template carries the centreline and station ticks on the "
             "`REG` layer. **`CHANNEL` lines are reference, not cuts.**", "",
             "| Template | Size mm | Kind | What it does |", "|---|---|---|---|"]
    for q in parts:
        lines.append("| `" + q["name"] + "` | " + format(q["w"], ".0f") + " x "
                     + format(q["h"], ".0f") + " | " + q["kind"] + " | "
                     + q["note"] + " |")
    lines += ["", "## The one number that is not from the model", "",
              "`GUIDE_OFF = " + format(GUIDE_OFF, ".0f") + " mm` is the guide-"
              "bushing offset, and it depends on **your** bushing and cutter, "
              "not on the design. Every `BEARING` template above avoids it "
              "entirely by using a flush-trim bit instead - which is why they "
              "are all cut at finished size. Only the two seal-groove "
              "templates (parts 14 and 15, in `cnc/`) need it.", ""]
    open(os.path.join(OUT, "templates.md"), "w",
         encoding="utf-8").write("\n".join(lines) + "\n")
    print("TEMPLATES  " + str(len(parts)) + " cut from 12 mm MDF")
    for q in parts:
        print("  " + q["name"].ljust(26) + format(q["w"], ">7.0f") + " x "
              + format(q["h"], "<7.0f") + q["kind"])
    # --- DO THESE ACTUALLY FIT THE SHEET THE BOM BUYS? ---------------------
    # Nothing was asking. The BOM bought a 2 x 4 ft panel - 1220 x 610 - and
    # T09 is 1400 mm long. The single most useful gauge, the one that checks
    # the rocker across the whole board and across the machining seam, could
    # not be cut from the sheet bought for it.
    # The groove guide was missing from that line too: it is MDF, it is
    # 580 x 391, and the note beside the panel still called it "fallback
    # only" after it was promoted to the primary way the seal groove is cut.
    # 2 x 4 ft is enough again now the gauges are off. It was 4 x 8 ONLY
    # because T09_rocker_and_deck is 1400 mm long and would not fit; with no
    # gauges the sheet carries one part, 14_groove_guide at 580 x 391.
    MDF_SHEET = (1220.0, 610.0) if not (HAND_SHAPE or CHECK_GAUGES)         else (2440.0, 1220.0)
    # both cut by cnc_drawings.py, both from this sheet
    GUIDES = [("14_groove_guide", 580.0, 391.0),
              ("16_module_lid_guide", 443.0, 314.0)]
    bad = []
    for nm, w, h in [(q["name"], q["w"], q["h"]) for q in parts] + GUIDES:
        L, W = MDF_SHEET
        if not ((w <= L and h <= W) or (w <= W and h <= L)):
            bad.append("%s (%.0f x %.0f)" % (nm, w, h))
    area = (sum(q["w"] * q["h"] for q in parts)
            + sum(g[1] * g[2] for g in GUIDES))
    print("  MDF sheet %.0f x %.0f, parts use %.2f m2 of %.2f"
          % (MDF_SHEET[0], MDF_SHEET[1], area / 1e6,
             MDF_SHEET[0] * MDF_SHEET[1] / 1e6))
    for g in GUIDES:
        print("  + " + g[0].ljust(24) + format(g[1], ">7.0f") + " x "
              + format(g[2], "<7.0f") + "(same sheet)")
    if bad:
        print("  FAILS TO FIT THE SHEET: " + ", ".join(bad))
    print("wrote " + OUT)
