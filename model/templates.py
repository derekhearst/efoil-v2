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
STATIONS = tuple(round(x / 1400.0, 4) for x in range(100, 1400, 100))

PARTS = []


def add(name, dxf, w, h, kind, note):
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
    for st in STATIONS:
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
    add("T09_rocker_and_deck", d, L, max(q[1] for q in dk), "GAUGE",
        "centreline profile. Solid is the hull bottom (rocker), CHANNEL is "
        "the deck. Cut as two separate gauges or one long one.")
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
    print("wrote " + OUT)
