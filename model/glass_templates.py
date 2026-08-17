"""Full-size paper templates for cutting the glass plies.

Flat cloth cannot cover a doubly-curved hull without either shearing or
gathering. Two things follow, and this generates both:

  * the DEVELOPED outline - the ply's shape flattened, so its width at every
    station is the real girth over the board rather than the plan half-width.
    Cutting to the plan outline leaves you short over the rails.
  * the RELIEF CUTS - where the overhang has to be slit so it can turn the
    plan curve at the nose and tail instead of bunching.

Run:  python model/glass_templates.py

Outputs to print/glass/: a DXF per ply (full size, half pattern - fold the
cloth on the centreline) and a tiled HTML you print from a browser.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cnc_drawings as C                                   # noqa: E402

OUT = os.path.join(os.path.dirname(HERE), "print", "glass")

# --- how the plies are laid ------------------------------------------------
LAP = 60.0            # how far each ply laps past the other's edge
SLIT_BACK = 10.0      # a relief slit stops this far short of the fold line
TURN_PER_CUT = 8.0    # degrees of plan turn one relief cut can absorb
N_ST = 281            # stations along the length

# --- paper -----------------------------------------------------------------
PAGE_W, PAGE_H = 215.9, 279.4      # US Letter
MARGIN = 9.0
OVERLAP = 10.0


def arclen(pts, a, b):
    """Length along a section polyline between two indices."""
    lo, hi = (a, b) if a < b else (b, a)
    return sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
               for i in range(lo, hi))


def build(p):
    """Develop both plies. Returns {name: dict} with per-station geometry."""
    L = p["LENGTH"]
    i_chine = p["SEC_BOT"] - 1
    i_deck_edge = p["SEC_BOT"] + p["SEC_RAIL_LO"] + p["SEC_RAIL_HI"] - 1
    i_deck_ctr = p["SEC_TOTAL"] - 1

    st = []
    for i in range(N_ST):
        u = i / (N_ST - 1)
        pts = p["section"](p["half_width"](u), p["thickness"](u), u)
        r = p["rocker"](u)
        st.append(dict(
            u=u, x=u * L,
            z_deck=pts[i_deck_ctr][1] + r,
            z_bot=pts[0][1] + r,
            y_chine=pts[i_chine][0],
            y_deck_edge=pts[i_deck_edge][0],
            # girths measured from each ply's own centreline
            g_deck_edge=arclen(pts, i_deck_edge, i_deck_ctr),
            g_deck_chine=arclen(pts, i_chine, i_deck_ctr),
            g_bot_chine=arclen(pts, 0, i_chine),
            g_bot_deck_edge=arclen(pts, 0, i_deck_edge),
        ))

    plies = {}
    for name, zkey, foldk, edgek, foldy in (
            ("deck", "z_deck", "g_deck_edge", "g_deck_chine", "y_deck_edge"),
            ("bottom", "z_bot", "g_bot_chine", "g_bot_deck_edge", "y_chine")):
        # longitudinal coordinate is arc length along THAT ply's centreline,
        # not plan x - the deck rises and the tail rockers
        s, acc = [], 0.0
        for i, a in enumerate(st):
            if i:
                b = st[i - 1]
                acc += math.hypot(a["x"] - b["x"], a[zkey] - b[zkey])
            s.append(acc)
        rows = [dict(s=s[i], fold=st[i][foldk], edge=st[i][edgek] + LAP,
                     x=st[i]["x"], y_fold=st[i][foldy]) for i in range(N_ST)]
        plies[name] = dict(rows=rows, length=acc,
                           cuts=relief_cuts(rows), lap=LAP)
    return plies


def relief_cuts(rows):
    """Place a slit every TURN_PER_CUT degrees of turn on the fold line.

    The fold line is where the cloth stops lying flat and starts turning down
    the rail. Everything outboard of it has to follow a tighter plan curve, and
    the excess is what the slits let out - so the cuts belong wherever that
    line turns, which is the nose and the tail and almost nowhere else.
    """
    poly = [(r["x"], r["y_fold"]) for r in rows]
    # close the loop round the tips so their turn is counted too
    poly = poly + [(rows[-1]["x"], -rows[-1]["y_fold"])] \
                + [(r["x"], -r["y_fold"]) for r in reversed(rows)] \
                + [(rows[0]["x"], rows[0]["y_fold"])]
    cuts, acc, run = [], 0.0, 0.0
    for i in range(1, len(poly) - 1):
        a, b, c = poly[i - 1], poly[i], poly[i + 1]
        t0 = math.atan2(b[1] - a[1], b[0] - a[0])
        t1 = math.atan2(c[1] - b[1], c[0] - b[0])
        d = (t1 - t0 + math.pi) % (2 * math.pi) - math.pi
        run += math.hypot(b[0] - a[0], b[1] - a[1])
        acc += abs(math.degrees(d))
        while acc >= TURN_PER_CUT:
            acc -= TURN_PER_CUT
            if i < len(rows):                     # keep to the half pattern
                cuts.append(dict(idx=i, x=b[0], run=run))
    return cuts


def outline(rows, cuts):
    """Half pattern: centreline is the fold, so cut two of these on a fold."""
    edge = [(r["s"], r["edge"]) for r in rows]
    fold = [(r["s"], r["fold"]) for r in rows]
    segs = []
    segs.append(("CUT", [(rows[0]["s"], 0.0)] + edge
                 + [(rows[-1]["s"], 0.0), (rows[0]["s"], 0.0)]))
    segs.append(("FOLD", fold))
    for c in cuts:
        r = rows[c["idx"]]
        segs.append(("SLIT", [(r["s"], r["edge"]), (r["s"], r["fold"] + SLIT_BACK)]))
    return segs


def write_dxf(name, segs):
    d = C.Dxf()
    for layer, pts in segs:
        for i in range(len(pts) - 1):
            d.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                   layer={"CUT": "CUT", "FOLD": "CHANNEL"}.get(layer, "HOLES"))
    fp = os.path.join(OUT, f"{name}_ply.dxf")
    d.save(fp)
    return fp


def write_tiled(name, segs, bbox):
    x0, y0, x1, y1 = bbox
    pw, ph = PAGE_W - 2 * MARGIN, PAGE_H - 2 * MARGIN
    sx, sy = pw - OVERLAP, ph - OVERLAP
    # Which way round the pattern goes on the page is not obvious - the long
    # axis on the long page edge is not always fewer sheets, because what
    # matters is how each axis divides. Try both and take the cheaper one.
    def grid(dx, dy):
        return max(1, math.ceil(dx / sx)) * max(1, math.ceil(dy / sy))
    span_x, span_y = x1 - x0, y1 - y0
    swap = grid(span_y, span_x) < grid(span_x, span_y)
    if swap:
        segs = [(lay, [(q[1], q[0]) for q in pts]) for lay, pts in segs]
        x0, y0, x1, y1 = y0, x0, y1, x1
    ncol = max(1, math.ceil((y1 - y0) / sy))
    nrow = max(1, math.ceil((x1 - x0) / sx))
    pages = []
    for r in range(nrow):
        for c in range(ncol):
            ox, oy = x0 + r * sx, y0 + c * sy
            body = [f'<svg xmlns="http://www.w3.org/2000/svg" '
                    f'width="{PAGE_W}mm" height="{PAGE_H}mm" '
                    f'viewBox="{ox - MARGIN} {oy - MARGIN} {PAGE_W} {PAGE_H}">']
            body.append(f'<rect x="{ox}" y="{oy}" width="{pw}" height="{ph}" '
                        'fill="none" stroke="#bbb" stroke-width="0.2" '
                        'stroke-dasharray="2 2"/>')
            for layer, pts in segs:
                st = {"CUT": "#000;0.5", "FOLD": "#0a7;0.35;3 2",
                      "SLIT": "#c00;0.45"}[layer].split(";")
                dash = f' stroke-dasharray="{st[2]}"' if len(st) > 2 else ""
                pd = "M " + " L ".join(f"{a:.2f} {b:.2f}" for a, b in pts)
                body.append(f'<path d="{pd}" fill="none" stroke="{st[0]}" '
                            f'stroke-width="{st[1]}"{dash}/>')
            # 50 mm calibration square, top-left of every page
            body.append(f'<rect x="{ox + 4}" y="{oy + 4}" width="50" height="50" '
                        'fill="none" stroke="#08f" stroke-width="0.3"/>')
            body.append(f'<text x="{ox + 6}" y="{oy + 60}" font-size="4" '
                        'fill="#08f">50 mm - measure me before cutting</text>')
            body.append(f'<text x="{ox + 6}" y="{oy + ph - 4}" font-size="5">'
                        f'{name} ply  row {r + 1}/{nrow}  col {c + 1}/{ncol}</text>')
            body.append("</svg>")
            pages.append('<div class="pg">' + "".join(body) + "</div>")
    html = ("<!doctype html><meta charset=utf-8><style>"
            f"@page{{size:{PAGE_W}mm {PAGE_H}mm;margin:0}}"
            "body{margin:0}"
            f".pg{{width:{PAGE_W}mm;height:{PAGE_H}mm;page-break-after:always;"
            "position:relative;overflow:hidden}</style>" + "".join(pages))
    fp = os.path.join(OUT, f"{name}_ply_tiled.html")
    open(fp, "w", encoding="utf-8").write(html)
    return fp, nrow * ncol


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    p = C.load_params()
    plies = build(p)
    lines = ["# Glass ply templates", "",
             "Half patterns - **cut on a fold down the centreline**. Green is the",
             "fold line where the cloth leaves the flat and starts down the rail;",
             "red are the relief slits. Print the HTML at **100% / actual size**",
             "and check the 50 mm square on every page before you cut anything.",
             ""]
    print("GLASSTEMPLATES")
    for name, d in plies.items():
        segs = outline(d["rows"], d["cuts"])
        xs = [q[0] for _, pts in segs for q in pts]
        ys = [q[1] for _, pts in segs for q in pts]
        bbox = (min(xs), min(ys), max(xs), max(ys))
        dxf = write_dxf(name, segs)
        html, npg = write_tiled(name, segs, bbox)
        w = 2 * max(r["edge"] for r in d["rows"])
        print(f"  {name:<7} {d['length']:.0f} x {w / 2:.0f} mm half pattern   "
              f"cloth {w:.0f} mm wide x {d['length']:.0f} long   "
              f"{len(d['cuts'])} slits/side   {npg} pages")
        lines += [f"## {name} ply", "",
                  f"| | |", "|---|---|",
                  f"| Developed length | {d['length']:.0f} mm |",
                  f"| Cloth width needed | **{w:.0f} mm** (half pattern "
                  f"{w / 2:.0f} mm) |",
                  f"| Lap past the other ply | {d['lap']:.0f} mm |",
                  f"| Relief slits per side | {len(d['cuts'])} |",
                  f"| Slit depth | to {SLIT_BACK:.0f} mm short of the fold line |",
                  f"| Tiled pages | {npg} (Letter) |", "",
                  "Half-widths every 100 mm, if you would rather use a batten "
                  "and a tape than tape 20 sheets together:", "",
                  "| from tail (mm) | fold line | outer edge |", "|---|---|---|"]
        for r in d["rows"][::(N_ST - 1) // 14]:
            lines.append(f"| {r['s']:.0f} | {r['fold']:.1f} | {r['edge']:.1f} |")
        lines.append("")
    open(os.path.join(OUT, "glass-templates.md"), "w",
         encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"\n  wrote to {OUT}")
