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
    d.poly(rrect(RIM_W - ci - cw / 2, ow - RIM_W + ci + cw / 2,
                 RIM_W - ci - cw / 2, oh - RIM_W + ci + cw / 2,
                 R + ci + cw / 2), layer="CHANNEL")
    d.poly(rrect(RIM_W - ci + cw / 2, ow - RIM_W + ci - cw / 2,
                 RIM_W - ci + cw / 2, oh - RIM_W + ci - cw / 2,
                 R + ci - cw / 2), layer="CHANNEL")
    bi = p["HATCH_BOLT_INSET"]
    hb = p["bolt_ring"](bi, ow - bi, bi, oh - bi, p["HATCH_BOLT_PITCH"],
                        r=R + RIM_W - bi)
    for (bx, by) in hb:
        d.circle(bx, by, p["HATCH_INSERT_D"] / 2)
    add("01_rim_ring", "G10", p["RIM_T"], 1, d, ow, oh,
        f"{len(hb)} x M5 inserts. Channel {cw:.0f} x {p['CHAN_D']:.0f} deep on "
        "CHANNEL layer. Nest as 4 bars + 4 corners to save material.")

    # 2 - hatch lid --------------------------------------------------------
    d = Dxf()
    lw, lh = ow - 3.0, oh - 3.0
    d.poly(rrect(0, lw, 0, lh, R + RIM_W - 1.5))
    for (bx, by) in hb:
        d.circle(bx - 1.5, by - 1.5, (p["HATCH_BOLT_D"] + 0.6) / 2)
    add("02_hatch_lid", f"glass/H80/glass {p['LID_T']:.0f}mm", p["LID_T"], 1,
        d, lw, lh, "Bag oversize flat, then machine to this profile. "
                   "Face the underside flat in the same setup.")

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
    add("04_module_floor", "G10", p["ENC_FLOOR"], 1, d, ext_l, ext_w,
        f"Inner rectangles are a {gr:.1f} mm deep locating groove for the "
        f"walls, NOT a through cut. Profile the outline only.")

    d = Dxf()
    d.poly(rect(0, ext_l, 0, wall_h))
    add("05_module_wall_long", "G10", ENC_WALL, 2, d, ext_l, wall_h,
        "Port and starboard")

    # The two end walls are NOT the same part any more - the aft one carries
    # the service-bay glands.
    d = Dxf()
    d.poly(rect(0, int_w, 0, wall_h))
    add("06_module_wall_fwd", "G10", ENC_WALL, 1, d, int_w, wall_h,
        "Fits between the long walls")

    d = Dxf()
    d.poly(rect(0, int_w, 0, wall_h))
    gz = 24.0 + p["ENC_FLOOR"]
    for g in range(p["BAY_GLAND_N"]):
        d.circle(int_w / 2 + (-55.0 + g * 55.0), gz, p["BAY_GLAND_D"] / 2)
    add("06b_module_wall_aft", "G10", ENC_WALL, 1, d, int_w, wall_h,
        f"{p['BAY_GLAND_N']} x PG11 glands O{p['BAY_GLAND_D']:.0f} facing the "
        f"aft service bay. Fits between the long walls.")

    # Corner posts replace the divider's stiffening job and give the corners
    # real glue area. Cut as one strip and parted off, or nested as 4 squares.
    cp = p["CORNER_POST"]
    d = Dxf()
    d.poly(rect(0, cp, 0, wall_h - p["ENC_FLOOR"]))
    add("07_module_corner_post", "G10", cp, 4, d, cp,
        wall_h - p["ENC_FLOOR"],
        f"{cp:.0f} mm square section, full internal height. Bonded into all "
        f"four internal corners with thickened epoxy.")

    # 4 - flange rails -----------------------------------------------------
    fw, fh = p["MOD_FLANGE_W"], p["MOD_FLANGE_H"]
    mb = p["bolt_ring"](fw / 2, int_l - fw / 2, fw / 2, int_w - fw / 2,
                        p["MOD_BOLT_PITCH"])
    d = Dxf()
    d.poly(rect(0, int_l, 0, fw))
    for (bx, by) in mb:
        if by < fw:
            d.circle(bx, fw / 2, p["MOD_INSERT_D"] / 2)
    add("08_flange_rail_long", "G10", fh, 2, d, int_l, fw,
        "Bonded inside the top edge of the long walls")

    d = Dxf()
    d.poly(rect(0, int_w - 2 * fw, 0, fw))
    for (bx, by) in mb:
        if bx < fw:
            d.circle(by - fw, fw / 2, p["MOD_INSERT_D"] / 2)
    add("09_flange_rail_end", "G10", fh, 2, d, int_w - 2 * fw, fw,
        "Bonded inside the top edge of the end walls")

    # 5 - module lid -------------------------------------------------------
    d = Dxf()
    d.poly(rect(0, ext_l, 0, ext_w))
    for (bx, by) in mb:
        d.circle(bx + ENC_WALL, by + ENC_WALL, (p["MOD_BOLT_D"] + 0.5) / 2)
    add("10_module_lid", f"glass/H80/glass {p['ENC_LID_T']:.0f}mm",
        p["ENC_LID_T"], 1, d, ext_l, ext_w, f"{len(mb)} x M4 clearance")

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
                     gw / 2 + sy * p["BOLT_SPACING_Y"] / 2, 6.5 / 2)
    add("12_mast_plate", "G10", p["G10_T"], 1, d, gl, gw,
        f"4 x O6.5 clearance on the {p['BOLT_SPACING_X']:.0f} x "
        f"{p['BOLT_SPACING_Y']:.0f} Gong pattern")

    # 7 - cavity caul ------------------------------------------------------
    d = Dxf()
    d.poly(rrect(0, cav_l - 1.0, 0, CAV_W - 1.0, R))
    add("13_cavity_caul", "MDF or foam", L["ext_h"], 1, d, cav_l - 1, CAV_W - 1,
        "Release-taped. Supports the deck skin during bagging, then presses "
        "the cavity laminate. 0.5 mm under size per side.")

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
              "| `CHANNEL` | pocket, not a through cut — see depth in notes |",
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
