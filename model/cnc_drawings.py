"""Generate CNC part drawings (DXF) and a cut list from blender_board.py.

Reads the parameter block out of the Blender script without importing bpy, so
the drawings can never drift from the model. Rerun after any parameter change.

    python model/cnc_drawings.py

Writes DXF per part into cnc/ plus cnc/cut-list.md.
"""
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "cnc")
MARKER = "# ------------------------------------------------------------------- scene"


def load_params():
    """Exec only the bpy-free head of blender_board.py.

    The head still carries `import bpy, bmesh` at the top, so stub them - the
    parameter block and the profile functions never touch either.
    """
    import sys
    import types
    for mod in ("bpy", "bmesh"):
        if mod not in sys.modules:
            sys.modules[mod] = types.ModuleType(mod)
    src = open(os.path.join(HERE, "blender_board.py"), encoding="utf-8").read()
    head = src.split(MARKER)[0]
    ns = {"__name__": "params"}
    exec(compile(head, "blender_board_params", "exec"), ns)
    # bolt_ring() calls rounded_rect(), which lives below the marker
    ns["rounded_rect"] = rrect
    ns["derive_layout"]()
    return ns


# ------------------------------------------------------------------- DXF
class Dxf:
    """Minimal R12 ASCII DXF - LINE and CIRCLE only, universally importable."""

    def __init__(self):
        self.e = []

    def line(self, x1, y1, x2, y2, layer="CUT"):
        self.e.append(("LINE", layer, x1, y1, x2, y2))

    def circle(self, cx, cy, r, layer="HOLES"):
        self.e.append(("CIRCLE", layer, cx, cy, r))

    def poly(self, pts, layer="CUT", close=True):
        n = len(pts)
        for i in range(n if close else n - 1):
            a, b = pts[i], pts[(i + 1) % n]
            self.line(a[0], a[1], b[0], b[1], layer)

    def save(self, path):
        out = ["0", "SECTION", "2", "ENTITIES"]
        for ent in self.e:
            if ent[0] == "LINE":
                _, lay, x1, y1, x2, y2 = ent
                out += ["0", "LINE", "8", lay,
                        "10", f"{x1:.4f}", "20", f"{y1:.4f}", "30", "0.0",
                        "11", f"{x2:.4f}", "21", f"{y2:.4f}", "31", "0.0"]
            else:
                _, lay, cx, cy, r = ent
                out += ["0", "CIRCLE", "8", lay,
                        "10", f"{cx:.4f}", "20", f"{cy:.4f}", "30", "0.0",
                        "40", f"{r:.4f}"]
        out += ["0", "ENDSEC", "0", "EOF"]
        with open(path, "w", encoding="ascii") as fh:
            fh.write("\n".join(out) + "\n")


def rrect(x0, x1, y0, y1, r, seg=18):
    r = max(0.01, min(r, (x1 - x0) / 2 - 0.01, (y1 - y0) / 2 - 0.01))
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -math.pi / 2), (x1 - r, y1 - r, 0.0),
                       (x0 + r, y1 - r, math.pi / 2), (x0 + r, y0 + r, math.pi)):
        for i in range(seg + 1):
            a = a0 + (math.pi / 2) * i / seg
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def rect(x0, x1, y0, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


# ------------------------------------------------------------------ parts
def build(p):
    os.makedirs(OUT, exist_ok=True)
    L = p["derive_layout"]()
    parts = []

    CAV_X0, CAV_X1 = p["CAV_X0"], p["CAV_X1"]
    CAV_W, RIM_W, R = p["CAV_WIDTH"], p["RIM_W"], p["CAV_CORNER_R"]
    ENC_WALL, ENC_GAP = p["ENC_WALL"], p["ENC_GAP"]
    ext_l, ext_w, ext_h = L["ext_l"], L["ext_w"], L["ext_h"]
    int_l, int_w = L["int_l"], L["int_w"]
    wall_h = ext_h - p["ENC_LID_T"]
    cav_l = CAV_X1 - CAV_X0

    def add(name, material, thick, qty, dxf, w, h, note=""):
        dxf.save(os.path.join(OUT, f"{name}.dxf"))
        parts.append(dict(name=name, material=material, thick=thick, qty=qty,
                          size=f"{w:.0f} x {h:.0f}", note=note,
                          dxf=dxf, w=w, h=h))

    # 1 - hatch rim ring ---------------------------------------------------
    d = Dxf()
    ow, oh = cav_l + 2 * RIM_W, CAV_W + 2 * RIM_W
    d.poly(rrect(0, ow, 0, oh, R + RIM_W))
    d.poly(rrect(RIM_W, ow - RIM_W, RIM_W, oh - RIM_W, R), layer="CUT")
    ci, cw = p["CHAN_INSET"], p["CHAN_W"]
    for sgn in (+1, -1):
        d.poly(rrect(RIM_W - ci + sgn * cw / 2, ow - RIM_W + ci - sgn * cw / 2,
                     RIM_W - ci + sgn * cw / 2, oh - RIM_W + ci - sgn * cw / 2,
                     R + ci - sgn * cw / 2), layer="CHANNEL")
    bi = p["HATCH_BOLT_INSET"]
    hb = p["bolt_ring"](bi, ow - bi, bi, oh - bi, p["HATCH_BOLT_PITCH"],
                        r=R + RIM_W - bi)
    for (bx, by) in hb:
        d.circle(bx, by, p["HATCH_INSERT_D"] / 2)
    add("01_rim_ring", "G10", p["RIM_T"], 1, d, ow, oh,
        f"{len(hb)} x M5 STI tapped for stainless wire-thread inserts. "
        "ASSEMBLED REFERENCE ONLY - DO NOT CUT THIS OUTLINE. A one-piece G10 "
        "ring needs a blank 3.7x its own material. Cut parts 01a and 01b and "
        "bond them into this. Shown here to check the assembled ring against "
        "the rebate and to carry the bolt pattern and CHANNEL reference. "
        "Do NOT machine the CHANNEL groove at this stage: the ring is glassed "
        "into the foam, so the groove is routed LAST, through the cured "
        f"laminate into the ring, off template part 14 - {p['CHAN_W']:.0f} "
        f"wide x {p['CHAN_D']:.1f} deep for an O{p['CORD_D']:.0f} cord "
        "BONDED in. "
        f"Break the INNER top edge to R{p['RIM_CHAMFER']:.0f} - the laminate "
        "turns over it into the cavity. Leave the outer edge and the bottom "
        "face SQUARE.")

    # 1a / 1b - the ring as four pieces ------------------------------------
    # Four pieces, not eight: the two LONG pieces carry their own corner arcs,
    # so no joint lands on a corner - where the groove curves, the cutter works
    # hardest, and the ring resists spread under bolt tension. Joints run
    # PERPENDICULAR to the seal groove, are scarfed, and sit under continuous
    # laminate, so the leak path is the full 34 mm width of the ring.
    #
    # JOINT_OFF 10, not 25: at 25 the long bar is 81 mm deep and four of them
    # need 12.8 in across a sheet, which a 12 in sheet cannot take.
    JOINT_OFF = 10.0
    Ro, Ri = R + RIM_W, R
    ycut = Ro + JOINT_OFF

    def arc(cx, cy, rad, a0, a1, seg=24):
        return [(cx + rad * math.cos(math.radians(a)),
                 cy + rad * math.sin(math.radians(a)))
                for a in [a0 + (a1 - a0) * i / seg for i in range(seg + 1)]]

    prof = ([(0.0, ycut), (0.0, Ro)]
            + arc(Ro, Ro, Ro, 180, 270)
            + [(ow - Ro, 0.0)]
            + arc(ow - Ro, Ro, Ro, 270, 360)
            + [(ow, ycut), (ow - RIM_W, ycut), (ow - RIM_W, RIM_W + Ri)]
            + arc(ow - RIM_W - Ri, RIM_W + Ri, Ri, 0, -90)
            + [(RIM_W + Ri, RIM_W)]
            + arc(RIM_W + Ri, RIM_W + Ri, Ri, 270, 180)
            + [(RIM_W, ycut)])
    d2 = Dxf()
    d2.poly(prof)
    for (bx, by) in hb:
        if by <= ycut:
            d2.circle(bx, by, p["HATCH_INSERT_D"] / 2)
    add("01a_ring_bar_long", "G10", p["RIM_T"], 2, d2, ow, ycut,
        "TWO PER BOARD (the second is this one flipped - the profile is "
        "symmetric). Carries both corner arcs. SCARF or half-lap the joint "
        "faces rather than butting them square, and bond with the same "
        "structural epoxy as the mast bushings - the seal groove is routed "
        "across these joints later, so a joint that opens is a leak. "
        "BOND THE FOUR PIECES IN PLACE, IN THE REBATE - do not pre-assemble a "
        "ring and then try to drop it in. The rebate is the jig: its outer "
        "wall is CNC-cut off template T03 and sets the ring's outer profile, "
        "and its floor is machined flat, so with all four pieces off ONE sheet "
        "their top faces come out coplanar on their own. "
        "CUT THE BARS A HAIR SHORT, NEVER LONG. Four joints with 0.2 mm of "
        "epoxy in each grows the assembly 0.8 mm, and the rebate will not "
        "accept a ring that has grown - short bars just leave more glue line, "
        "which is fine. Push every piece OUTWARD against the rebate wall as "
        "you bond: the outer edge is the datum, the inner edge is free, and "
        "there is 8 mm of ring inboard of the groove to absorb any step.")

    d3 = Dxf()
    d3.poly([(0.0, 0.0), (RIM_W, 0.0), (RIM_W, oh - 2 * ycut),
             (0.0, oh - 2 * ycut)])
    for (bx, by) in hb:
        if ycut < by < oh - ycut and bx < ow / 2:
            d3.circle(bx, by - ycut, p["HATCH_INSERT_D"] / 2)
    add("01b_ring_bar_short", "G10", p["RIM_T"], 2, d3, RIM_W, oh - 2 * ycut,
        "TWO PER BOARD. Plain straight bar - the short sides between the two "
        "long pieces. Nest alongside the 01a bars.")

    # 1c - handle strips (were missing from the cut list entirely) ---------
    d = Dxf()
    hl, hw_ = p["HANDLE_PLATE_L"], p["HANDLE_PLATE_W"]
    d.poly(rect(0, hl, 0, hw_))
    for sx in (-1, 1):
        d.circle(hl / 2 + sx * p["HANDLE_BOLT_DX"] / 2, hw_ / 2,
                 p["HANDLE_INS_D"] / 2)
    add("01c_handle_strip", "G10", p["HANDLE_PLATE_T"], 2, d, hl, hw_,
        "TWO PER BOARD, port and starboard. Takes the two M6 strap inserts. "
        "Beds into a shallow (~1.6 mm) milled facet on the rail so the "
        "laminate lies over it - there is NO handle pocket. Nests in the "
        "offcut of the 1/2in sheet the rim ring comes from.")

    # 2 - hatch lid --------------------------------------------------------
    d = Dxf()
    lw, lh = ow - 3.0, oh - 3.0
    d.poly(rrect(0, lw, 0, lh, R + RIM_W - 1.5))
    for (bx, by) in hb:
        d.circle(bx - 1.5, by - 1.5, (p["HATCH_BOLT_D"] + 0.6) / 2)
    add("02_hatch_lid", f"glass/H80/glass {p['LID_T']:.0f}mm", p["LID_T"], 1,
        d, lw, lh, "Bag oversize flat, then machine to this profile. Face the "
                   "underside flat in the same setup - it is the sealing face "
                   "and it lands hard on the rim ring, so it must be flat.")

    d = Dxf()
    d.poly(rrect(2.0, lw - 2.0, 2.0, lh - 2.0, R + RIM_W - 3.5))
    add("03_hatch_lid_core", "Divinycell H80", p["LID_CORE"], 1, d,
        lw - 4, lh - 4, "Inset 2 mm so the skins wrap the edge - no exposed core.")

    # 3 - module floor + walls + corner posts ------------------------------
    # The floor carries a locating groove for the walls - it is a 2-depth part,
    # profile all the way through and the groove only JOINT_GROOVE_D deep.
    d = Dxf()
    d.poly(rect(0, ext_l, 0, ext_w))
    gr, wt = p["JOINT_GROOVE_D"], ENC_WALL
    d.poly(rect(0.15, ext_l - 0.15, 0.15, wt - 0.15))
    d.poly(rect(0.15, ext_l - 0.15, ext_w - wt + 0.15, ext_w - 0.15))
    d.poly(rect(0.15, wt - 0.15, 0.15, ext_w - 0.15))
    d.poly(rect(ext_l - wt + 0.15, ext_l - 0.15, 0.15, ext_w - 0.15))
    add("04_module_floor", "5052 aluminium", p["ENC_FLOOR"], 1, d, ext_l, ext_w,
        f"1/8in 5052, NOT G10. One 12x24 sheet is one floor, so a 2-pack does "
        f"both boards. Chosen for the ESC as much as the price: the ESC sits "
        f"sealed in with 128 cells and no airflow, and G10 conducts 500x "
        f"worse than aluminium - this floor is its heat spreader and thermal "
        f"mass, the same job V1's alu bottom plate did. "
        f"Inner rectangles are a {gr:.1f} mm deep locating groove for the "
        f"printed walls, NOT a through cut. Profile the outline only. "
        f"Costs +355 g a board, taken deliberately.")

    # ---------------------------------------------------------------------
    # Parts 05-09 (long walls, both end walls, corner posts, both flange
    # rails) ARE GONE. The module shell is 3D PRINTED, not cut from G10.
    #
    # Why: G10 walls were specced to save weight and did the opposite. The
    # 3.175 mm G10 shell - walls, bonded flange ring, four corner posts - came
    # to 1323 g against ~1130 g printed, and cost six CNC parts, a bond jig, a
    # four-joint tolerance chain and a seal groove that had to be routed after
    # assembly. The module's real weight win over V1 is one box instead of two
    # and a sandwich lid instead of 4 mm aluminium; neither needs G10 walls.
    #
    # PRINTED SHELL, per board (Bambu A1, 256 mm bed):
    #   4 L-shaped pieces, split at WALL MIDPOINTS not corners, so every
    #     corner prints solid and each seam lands on the flattest part of a
    #     wall. Largest piece is ~226 x 146 mm - fits the bed with room.
    #   4 mm walls, 10 x 10 mm external rib each side of every seam: the
    #     paired ribs self-align the pieces and double the bond area.
    #   Flange prints integral with the wall, 20 mm wide x 9.525 deep, taking
    #     18 x M4 heat-set inserts at a 5.6 mm printed pilot. No tapping, no
    #     wire-thread inserts - heat-set is finally on its proper material.
    #   Aft-wall piece carries the 3 x PG11 gland bores, the power button and
    #     the charge port cutout - all printed in, none of them drilled.
    #   Seam bond: thickened epoxy on the paired ribs + a 6 mm glass-tape
    #     fillet inside every corner.
    #   PETG or ASA. ASA if you can print it - better creep resistance under
    #     sustained bolt load, which is exactly what a gasket flange sees.
    # SEAL: a FLAT NEOPRENE GASKET on the flange face, 7 mm band, 3 mm stock
    #   squeezed to 2.0 (33%). NOT an O-ring in a groove - a printed groove
    #   holds about +/-0.2 mm, a third of an O3 cord's squeeze, so the seal
    #   would vary bolt to bolt. A flat gasket absorbs the irregularity, which
    #   is what V1 did on both printed enclosures and they still seal.
    # ---------------------------------------------------------------------

    # Bolt ring: still needed here even though the flange rails are printed,
    # because the LID is the one module part still cut on the machine and its
    # holes must match the printed flange's insert pattern.
    fw = p["MOD_FLANGE_W"]
    bi = p["MOD_BOLT_INSET"]
    mb = p["bolt_ring"](bi, int_l - bi, bi, int_w - bi, p["MOD_BOLT_PITCH"])

    # 5 - module lid -------------------------------------------------------
    d = Dxf()
    d.poly(rect(0, ext_l, 0, ext_w))
    for (bx, by) in mb:
        d.circle(bx + ENC_WALL, by + ENC_WALL, (p["MOD_BOLT_D"] + 1.0) / 2)
    add("10_module_lid", f"glass/H80/glass {p['ENC_LID_T']:.0f}mm",
        p["ENC_LID_T"], 1, d, ext_l, ext_w,
        f"{len(mb)} x O5.0 M4 clearance. O5.0 not O4.5: the rails are drilled "
        f"FLAT and then bonded up as a four-piece ring, so the ring's hole "
        f"positions carry whatever the bond-up drifted. O4.5 leaves 0.25 mm "
        f"radial and will bind. O5.0 leaves 0.5 mm, which the floor-as-master "
        f"bond sequence holds. "
        f"EVERY HOLE MUST BE POTTED. This is a cored panel: at 646 N a bolt "
        f"an M4 washer puts ~15 MPa on the seat and H-80 crushes at 1.4, so "
        f"bare holes lose seal squeeze the first time it is torqued. Drill "
        f"O12 through the top skin and core ONLY, leave the bottom skin, "
        f"fill with thickened epoxy, cure, then drill O5.0 through the lot. "
        f"The washer then bears on solid epoxy - ~4.4x margin.")

    d = Dxf()
    d.poly(rect(2.0, ext_l - 2.0, 2.0, ext_w - 2.0))
    add("11_module_lid_core", "Divinycell H80", p["ENC_LID_CORE"], 1, d,
        ext_l - 4, ext_w - 4, "Inset 2 mm for skin wrap")

    # 6 - mast plate -------------------------------------------------------
    d = Dxf()
    gl, gw = p["G10_L"], p["G10_W"]
    d.poly(rect(0, gl, 0, gw))
    for sx in (-1, 1):
        for sy in (-1, 1):
            d.circle(gl / 2 + sx * p["BOLT_SPACING_X"] / 2,
                     gw / 2 + sy * p["BOLT_SPACING_Y"] / 2,
                     p["INSERT_OD"] / 2)
    add("12_mast_plate", "6061-T651 aluminium", p["G10_T"], 1, d, gl, gw,
        f"1/2in 6061-T651, NOT 3/4in G10, and NOT bushed. "
        f"4 x M8 TAPPED {p['INSERT_L']:.0f} mm BLIND from the PAD FACE "
        f"(the wetted underside), leaving {p['INSERT_BLIND']:.1f} mm of solid "
        f"aluminium above so the plate stays watertight. Tap drill 6.8 mm. "
        f"Bolt pattern {p['BOLT_SPACING_X']:.0f} x {p['BOLT_SPACING_Y']:.0f} "
        f"- UNVERIFIED, check against a real Gong plate before drilling. "
        f"This is no longer a CNC part: a 250 x 175 rectangle and four "
        f"tapped holes is bandsaw and drill-press work. "
        f"6061 shears at ~207 MPa against G10's ~55, so the tapped thread "
        f"(136 mm2, 17.7 kN) beats the O20 bonded bushing it replaced and the "
        f"M8 bolt itself becomes the weak link - which is where you want it. "
        f"TEF-GEL EVERY BOLT: aluminium plate, A4 stainless bolts, wet "
        f"cavity. That is the whole galvanic mitigation and it is not "
        f"optional. Nest both plates on one 12x18 sheet: 2 x 6.89in of the "
        f"18in length, 4.2in spare.")

    # 7 - cavity caul ------------------------------------------------------
    d = Dxf()
    d.poly(rrect(0, cav_l - 1.0, 0, CAV_W - 1.0, R))
    add("13_cavity_caul", "MDF or foam", L["ext_h"], 1, d, cav_l - 1, CAV_W - 1,
        "Release-taped. Supports the deck skin during bagging, then presses "
        "the cavity laminate. 0.5 mm under size per side.")

    # 8 - router template for the hatch seal groove ------------------------
    # The ring is glassed in, so its groove is cut LAST, through the laminate.
    # This is the guide: a guide-bushing template, oversized by the bushing
    # offset so the cutter tracks the groove centreline.
    GUIDE_OFF = 5.0     # (guide bushing OD - cutter OD) / 2 - CHECK your router
    d = Dxf()
    gi = p["CHAN_INSET"]
    d.poly(rrect(RIM_W - gi - GUIDE_OFF, ow - RIM_W + gi + GUIDE_OFF,
                 RIM_W - gi - GUIDE_OFF, oh - RIM_W + gi + GUIDE_OFF,
                 R + gi + GUIDE_OFF))
    d.poly(rrect(0, ow, 0, oh, R + RIM_W), layer="CHANNEL")
    add("14_seal_groove_template", "MDF 12 mm", 12.0, 1, d,
        ow, oh,
        f"Router template for the hatch seal groove, cut AFTER the board is "
        f"glassed. Inner opening is offset {GUIDE_OFF:.0f} mm outboard of the "
        f"groove centreline for a guide bushing - RE-CHECK that offset against "
        f"your own bushing and cutter before cutting the template. Cut the "
        f"groove {p['CHAN_W']:.0f} wide x {p['CHAN_D']:.0f} deep, measured from "
        f"the GLASSED face. The CHANNEL outline is the rim ring's own outer "
        f"edge, for registering the template on the board.")

    # Template 15 (module seal groove) IS GONE. There is no module groove any
    # more: the printed flange takes a FLAT NEOPRENE GASKET, so there is
    # nothing to rout and nothing that has to stay continuous across joints.
    # Cut the gasket from 1/8" neoprene sheet with the lid as the pattern.

    # 8 - EPS core station table ------------------------------------------
    rows = []
    for i in range(0, 41):
        x = i / 40.0
        rows.append((x * p["LENGTH"], p["half_width"](x) * 2.0,
                     p["thickness"](x), p["rocker"](x)))
    return parts, rows, L


COLOR = {"CUT": "#1a1a1a", "HOLES": "#c0392b", "CHANNEL": "#2e7d32"}


def write_sheet(parts, p, path, cols=4, cell=330, pad=26):
    """One SVG contact sheet of every flat part, each scaled to its cell."""
    rows_n = (len(parts) + cols - 1) // cols
    W, H = cols * cell, rows_n * cell + 60
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
         'style="background:#fff;font-family:ui-sans-serif,system-ui,sans-serif">',
         f'<text x="16" y="30" font-size="19" font-weight="700">eFoil V2 — CNC '
         f'flat parts</text>',
         f'<text x="16" y="50" font-size="12" fill="#666">Board '
         f'{p["LENGTH"]:.0f} x {p["WIDTH"]:.0f} x {p["THICK"]:.1f} · black = '
         f'cut · red = holes · green = pocket (channel)</text>']
    for i, q in enumerate(parts):
        cx0 = (i % cols) * cell
        cy0 = 60 + (i // cols) * cell
        avail = cell - 2 * pad - 44
        sc = min(avail / max(q["w"], 1.0), avail / max(q["h"], 1.0))
        ox = cx0 + pad + (avail - q["w"] * sc) / 2
        oy = cy0 + pad + 30 + (avail - q["h"] * sc) / 2

        def X(v):
            return ox + v * sc

        def Y(v):
            return oy + (q["h"] - v) * sc

        s.append(f'<text x="{cx0+pad}" y="{cy0+pad+8}" font-size="12.5" '
                 f'font-weight="600">{i+1}. {q["name"][3:].replace("_"," ")}</text>')
        s.append(f'<text x="{cx0+pad}" y="{cy0+pad+24}" font-size="10.5" '
                 f'fill="#666">{q["material"]} · {q["thick"]:.0f} mm · '
                 f'x{q["qty"]} · {q["size"]}</text>')
        for ent in q["dxf"].e:
            col = COLOR.get(ent[1], "#1a1a1a")
            if ent[0] == "LINE":
                _, _, x1, y1, x2, y2 = ent
                s.append(f'<line x1="{X(x1):.2f}" y1="{Y(y1):.2f}" '
                         f'x2="{X(x2):.2f}" y2="{Y(y2):.2f}" stroke="{col}" '
                         f'stroke-width="{1.1 if col!="#2e7d32" else 0.9}"/>')
            else:
                _, _, ccx, ccy, r = ent
                s.append(f'<circle cx="{X(ccx):.2f}" cy="{Y(ccy):.2f}" '
                         f'r="{max(r*sc,1.4):.2f}" fill="none" stroke="{col}" '
                         f'stroke-width="1.1"/>')
    s.append("</svg>")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(s))


def write_cut_list(parts, rows, L, p):
    lines = [
        "# CNC Cut List — eFoil V2", "",
        "Generated by `model/cnc_drawings.py` from `blender_board.py`. "
        "Rerun after any parameter change.", "",
        f"Board {p['LENGTH']:.0f} x {p['WIDTH']:.0f} x {p['THICK']:.1f} mm · "
        f"cavity {p['CAV_X1']-p['CAV_X0']:.0f} x {p['CAV_WIDTH']:.0f} x "
        f"{L['ext_h']+p['ENC_TOP_GAP']:.0f} mm", "",
        "## Flat parts", "",
        "| # | Part | Material | Thick | Qty | Size (mm) | Notes |",
        "|---|---|---|---|---|---|---|",
    ]
    for i, q in enumerate(parts, 1):
        lines.append(f"| {i} | `{q['name']}.dxf` | {q['material']} | "
                     f"{q['thick']:.1f} | {q['qty']} | {q['size']} | {q['note']} |")

    # Stock check. G10 is sold in fixed sheet sizes and a part that is 6 mm
    # over a 24 in sheet is a re-buy or a re-design, not a rounding error -
    # the rim ring crossed 610 mm the moment the cavity grew a wire bay.
    STOCK = [("12 x 24 in", 305.0, 610.0), ("24 x 36 in", 610.0, 914.0),
             ("24 x 48 in", 610.0, 1219.0), ("36 x 48 in", 914.0, 1219.0)]
    over = []
    for q in parts:
        if "G10" not in q["material"] and "H80" not in q["material"]:
            continue
        try:
            a, b = (float(v) for v in q["size"].split(" x "))
        except ValueError:
            continue
        w, l = min(a, b), max(a, b)
        fit = next((n for n, sw, sl in STOCK if w <= sw and l <= sl), None)
        if fit is None:
            over.append((q["name"], q["size"]))
        q["stock"] = fit
    lines += ["", "## Stock", "",
              "| Part | Size (mm) | Smallest sheet that holds it |",
              "|---|---|---|"]
    for q in parts:
        if "stock" in q:
            lines.append(f"| `{q['name']}` | {q['size']} | "
                         f"{q['stock'] or '**does not fit stock**'} |")
    if over:
        lines += ["", "> **Over stock size.** " + ", ".join(
            f"`{n}` ({s})" for n, s in over) +
            " — make it in scarfed segments or buy the next sheet up."]

    lines += ["", "## DXF layers", "",
              "| Layer | Meaning |", "|---|---|",
              "| `CUT` | through profile |",
              "| `HOLES` | drill / bore, diameter as drawn |",
              "| `CHANNEL` | placement line for the gasket lane — not a cut |",
              "", "## EPS core — station table", "",
              "Cut in two halves, seam at "
              f"{p['SEAM_X']:.0f} mm. Width and thickness are the finished "
              "hull; rocker is the bottom's rise above the datum plane.", "",
              "| Station (mm) | Width | Thickness | Rocker |",
              "|---|---|---|---|"]
    for (x, w, t, r) in rows:
        lines.append(f"| {x:.0f} | {w:.1f} | {t:.1f} | {r:.1f} |")

    lines += ["", "## Two-day plan", "",
              "**Day 1 — before layup**", "",
              "1. EPS core, two halves (3D, both faces)",
              "2. Cavity caul (13)",
              "3. G10 flat parts (1, 4–9, 12) — nest 1 + 12 + 8 + 9 on one "
              "3/8\" sheet",
              "4. H80 lid cores (3, 11)", "",
              "**Day 2 — after layup**", "",
              "5. Trim the cured sandwich lids to net profile (2, 10)",
              "6. Face the hatch lid underside flat in the same setup",
              "7. Drill lid bolt clearance off the installed inserts", "",
              "## Before booking", "",
              "- Will they allow **EPS** dust?",
              "- Will they allow **G10** dust? It is abrasive and a "
              "respiratory hazard; many shops ban it. If banned, part 1 "
              "(rim ring) is the one that must be job-shopped — everything "
              "else can be hand-cut from sheet.",
              "- Bed must clear "
              f"{max(p['SEAM_X'], p['LENGTH']-p['SEAM_X']):.0f} mm for the "
              "longer core half."]
    with open(os.path.join(OUT, "cut-list.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    P = load_params()
    parts, rows, L = build(P)
    write_cut_list(parts, rows, L, P)
    write_sheet(parts, P, os.path.join(OUT, "part-sheet.svg"))
    print(f"wrote {len(parts)} DXF parts + cut-list.md + part-sheet.svg to {OUT}")
    for q in parts:
        print(f"  {q['name']:26s} {q['material']:26s} "
              f"{q['thick']:5.1f} x{q['qty']}  {q['size']}")
