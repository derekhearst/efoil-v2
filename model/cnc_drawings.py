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
    add("01_rim_ring", "printed ASA (reference only)", p["RIM_T"], 1, d, ow, oh,
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
    # ---------------------------------------------------------------------
    # Parts 01a / 01b (the G10 ring bars) ARE GONE. The rim ring is PRINTED
    # ASA, in 6 dovetailed pieces, and it is not a machined part at all.
    #
    # Geometry lives in blender_board.py as V2_RimSeg_* - export those to STL
    # rather than working from a DXF, because the dovetails and the nut
    # pockets are 3D and a flat profile will not carry them.
    #
    # 6 PIECES, per board:
    #   4 corner L-pieces, 170 mm along each long side and half-way along each
    #     short side, so the two corners of a short side MEET at its centre.
    #     Largest bbox 182 x 206 with its tabs - inside the A1's 256.
    #   2 straight fillers, 253 mm, closing each long side.
    #   6 joints, and NOT ONE ON A CORNER. Corners are where a ring wants to
    #     be continuous; straight runs are where a joint is cheapest.
    #
    # EVERY JOINT IS DOVETAILED, 8 mm neck -> 14 mm head x 12 mm deep, 0.15 mm
    #   clearance a face. Neck narrower than head, so a joint locates itself,
    #   pulls together as it seats and cannot pull apart in the ring's plane.
    #   Verified in the model: adjacent pieces intersect at 0.0 mm3, the six
    #   pieces sum to 99.98% of the ring (the 0.02 is the clearance), and
    #   nothing stands proud of the seal face.
    #
    # JOIN WITH ACETONE, NOT EPOXY. ASA dissolves in acetone the way ABS does,
    #   so a brushed acetone/ASA-scrap slurry on both faces makes the joint one
    #   piece of plastic. Epoxy on ASA is a 2-5 MPa mechanical grip; a solvent
    #   weld is the parent material.
    #
    # PRINT SEAL FACE DOWN. The bed gives a flatter, smoother seal land than
    #   any top surface will, and the 4 x 2.4 groove then only has to bridge
    #   4 mm, which ASA does without support.
    #
    # PAUSE AT Z = 6.0 mm and drop in 12 M5 nuts. That is the whole fastening:
    #   a captive steel thread, ~5.2 kN pull-out against the 910 N a bolt the
    #   seal actually needs, and nothing to wear out on a hatch that comes off
    #   every single ride. No STI tap, no tangless tool, no heat-set insert.
    #   DO NOT OVER-TORQUE - the lid lands on a hard stop, so past that point
    #   more torque adds nothing to the seal and goes into the nut pockets.
    #   3 Nm is plenty.
    # ---------------------------------------------------------------------

    # 1c - handle strips (were missing from the cut list entirely) ---------
    d = Dxf()
    hl, hw_ = p["HANDLE_PLATE_L"], p["HANDLE_PLATE_W"]
    d.poly(rect(0, hl, 0, hw_))
    for sx in (-1, 1):
        d.circle(hl / 2 + sx * p["HANDLE_BOLT_DX"] / 2, hw_ / 2,
                 p["HANDLE_INS_D"] / 2)
    add("01c_handle_strip", "6061-T651 aluminium", p["HANDLE_PLATE_T"], 2, d, hl, hw_,
        "TWO PER BOARD, port and starboard. Takes the two M6 strap inserts. "
        "Beds into a shallow (~1.6 mm) milled facet on the rail so the "
        "laminate lies over it - there is NO handle pocket. Nests in the "
        "offcut of the 1/2in sheet the rim ring comes from.")

    # 2 - hatch lid --------------------------------------------------------
    d = Dxf()
    lw, lh = ow - 3.0, oh - 3.0
    d.poly(rrect(0, lw, 0, lh, R + RIM_W - 1.5))
    # BOTH circles, both cut, ONE SETUP. The boss and the bolt hole it
    # surrounds are concentric by machine, and all twelve are mutually
    # accurate for free - which is the whole reason to cut them here.
    for (bx, by) in hb:
        d.circle(bx - 1.5, by - 1.5, p["HATCH_POT_D"] / 2)
        d.circle(bx - 1.5, by - 1.5, (p["HATCH_BOLT_D"] + 0.6) / 2)
    add("02_hatch_lid", f"glass/H80/glass {p['LID_T']:.0f}mm", p["LID_T"], 1,
        d, lw, lh,
        "Bag oversize flat, then machine to this profile. Face the underside "
        "flat in the same setup - it is the sealing face and it lands hard on "
        "the rim ring, so it must be flat. "
        f"TWO CONCENTRIC CIRCLES AT EACH OF THE 12, BOTH CUT IN THIS ONE "
        f"SETUP: the O{p['HATCH_POT_D']:.0f} potting boss, pocketed "
        f"{p['LID_SKIN'] + p['LID_CORE']:.0f} mm deep - top skin and core "
        f"only, LEAVE THE BOTTOM SKIN - and the "
        f"O{p['HATCH_BOLT_D'] + 0.6:.1f} bolt hole straight through the "
        f"middle of it. Set the pocket Z off the MEASURED thickness of the "
        f"bagged panel, not the nominal {p['LID_T']:.0f}. "
        f"CUTTING BOTH HERE IS THE POINT: twelve holes bored in one setup "
        f"are mutually accurate to the machine, so lining the lid up on the "
        f"ring is a single rigid-body fit - get two right and the rest are "
        f"right. Nothing about the potting changes that; the boss is a "
        f"bearing surface, not a substitute for machining. "
        f"POTTING SEQUENCE, and it matters: DRILL THE "
        f"O{p['HATCH_BOLT_D'] + 0.6:.1f} RIGHT THROUGH, BOTTOM SKIN "
        f"INCLUDED, in this setup. Then tape over it on the underside, fill "
        f"the pocket from the top, cure, and peel the tape - the machined "
        f"hole is still there in the bottom skin. Flip the panel sealing "
        f"face up and re-drill down through the cured resin using that hole "
        f"as the guide. The machine keeps the position and NOTHING STEEL "
        f"EVER SITS IN CURING EPOXY - a greased bolt used as a plug works "
        f"right up until one of the twelve does not release, and then the "
        f"lid is scrap. Skip the through hole and fill the pocket blind and "
        f"you have thrown away the setup you just paid for. "
        f"IF ONE OR TWO STILL WILL NOT PICK UP: the ring is six printed "
        f"pieces dovetailed, welded and glassed into a rebate, so a little "
        f"drift is possible. That is what the boss is really insurance for - "
        f"it is "
        f"{(p['HATCH_POT_D'] - p['HATCH_BOLT_HEAD_D']) / 2:.1f} mm of solid "
        f"resin all round every hole, so a stray one gets drilled out, "
        f"re-potted and re-drilled on a transfer-screw mark WITHOUT touching "
        f"the other eleven. A five-minute fix instead of a scrapped lid. "
        f"POT EVERY BOLT HOLE, THEN COUNTERSINK IT. NOT a V1 problem - V1's "
        f"lid was solid plywood and never crushed - but this one is a cored "
        f"sandwich. At 910 N a bolt, an M5 cap head puts 28 MPa on H100 and "
        f"even a O15 penny washer puts 6.0, against a core that crushes at "
        f"2.0. It takes a O25 fender washer to get under the limit, twelve "
        f"times round the hatch, which is why the answer is resin and not "
        f"hardware. Drill O{p['HATCH_POT_D']:.0f} through the TOP skin and "
        f"core only, leave the bottom skin, fill with thickened epoxy, cure, "
        f"re-drill from the underside, then countersink 90 deg to "
        f"O{p['HATCH_BOLT_HEAD_D']:.1f} - about "
        f"{(p['HATCH_BOLT_HEAD_D'] - p['HATCH_BOLT_D'] - 0.6) / 2:.1f} mm "
        f"deep - so the flat head finishes FLUSH WITH THE DECK. Cut the cone "
        f"to the head you actually bought: the sourced screw measures O9.0, "
        f"which sits ~0.4 mm sub-flush in a full-spec O9.8 cone. NO WASHER "
        f"GOES ON TOP OF THIS LID. "
        f"AND SEAL EVERY CUT EDGE WITH NEAT EPOXY - machined perimeter and "
        f"the inside of all 12 bores. THAT part is V1's Test 2 verbatim: "
        f"water wicking in through unsealed fibre ends at the cavity ledge.")

    d = Dxf()
    d.poly(rrect(2.0, lw - 2.0, 2.0, lh - 2.0, R + RIM_W - 3.5))
    add("03_hatch_lid_core", "Divinycell " + p["LID_CORE_GRADE"],
        p["LID_CORE"], 1, d,
        lw - 4, lh - 4, "Inset 2 mm so the skins wrap the edge - no exposed core.")

    # 3 - module floor -----------------------------------------------------
    # A PLAIN RECTANGLE now. It used to carry a JOINT_GROOVE_D locating groove
    # for the walls, which made it a 2-depth milling job - fine when it was
    # G10, wrong now it is 3.175 mm of 5052 (a 1.5 mm groove leaves 1.7) and
    # unnecessary once the joint became a filleted bond rather than a socket.
    # OVERSIZED by MOD_FLOOR_LEDGE all round: the walls land inboard of the
    # edge, leaving a ledge to run an external fillet onto. On a flexible
    # bond the fillets are most of the strength.
    lg = p["MOD_FLOOR_LEDGE"]
    fl_l, fl_w = ext_l + 2 * lg, ext_w + 2 * lg
    d = Dxf()
    d.poly(rect(0, fl_l, 0, fl_w))
    # scribe line only - where the wall foot lands. NOT a cut.
    d.poly(rect(lg, fl_l - lg, lg, fl_w - lg), layer="CHANNEL")
    add("04_module_floor", "5052 aluminium", p["ENC_FLOOR"], 1, d, fl_l, fl_w,
        f"1/8in 5052, NOT G10. One 12x24 sheet is one floor, so a 2-pack does "
        f"both boards. Chosen for the ESC as much as the price: the ESC sits "
        f"sealed in with 128 cells and no airflow, and G10 conducts 500x "
        f"worse than aluminium - this floor is its heat spreader and thermal "
        f"mass, the same job V1's alu bottom plate did. "
        f"Costs +355 g a board, taken deliberately. "
        f"NO GROOVE and no through-holes: bandsaw or jigsaw the rectangle and "
        f"deburr, that is the whole part. The CHANNEL rectangle is a SCRIBE "
        f"LINE showing where the wall foot lands - do not cut it. "
        f"BONDING: abrade, solvent wipe and PRIME the aluminium, scuff the "
        f"ASA, and hold a {p['MOD_FLOOR_BOND']:.0f} mm bond line on beads or "
        f"shim wire. Structural polyurethane, never epoxy - ASA and 5052 "
        f"differ by 66 um/m/K, so a rigid line sees ~300% shear strain across "
        f"a hot afternoon. Fillet inside AND outside onto the {lg:.0f} mm "
        f"ledge.")

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
    # Radial slop in Gong's own clearance hole - the entire positional budget
    # these four tapped holes get. Derived from the model so it tracks
    # MAST_CLEAR_D rather than being retyped here.
    # The conduit and its BUNG COUNTERBORE. Neither was on this drawing, so
    # the one part that has to be machined anyway was going to a shop with
    # its most awkward feature missing. The counterbore floor is the ledge
    # that squeezes the bung when the plate is pulled up to the hull.
    _cx = gl / 2 + p["CONDUIT_X_OFF"]
    d.circle(_cx, gw / 2, (p["CONDUIT_D"] + 0.8) / 2)
    if p.get("BUNG"):
        d.circle(_cx, gw / 2, p["BUNG_D"] / 2)
    _slop = (p["MAST_CLEAR_D"] - 8.0) / 2.0
    add("12_mast_plate", "6061-T651 aluminium", p["G10_T"], 1, d, gl, gw,
        f"1/2in 6061-T651, NOT 3/4in G10, and NOT bushed. "
        f"4 x M8 TAPPED {p['INSERT_L']:.0f} mm BLIND from the PAD FACE "
        f"(the wetted underside), leaving {p['INSERT_BLIND']:.1f} mm of solid "
        f"aluminium above so the plate stays watertight. Tap drill 6.8 mm. "
        f"CONDUIT: O{p['CONDUIT_D'] + 0.8:.1f} through on centre, "
        f"counterbored O{p['BUNG_D']:.2f} x {p['BUNG_IN_PLATE']:.1f} deep "
        f"FROM THE TOP FACE (the dry side). That counterbore is not "
        f"clearance - its floor is the ledge that pushes the wire bung up "
        f"against the step in the foam as the plate is drawn face to face "
        f"with the hull, so the depth is a real dimension, not a >= . "
        f"POSITION COMES OFF THE REAL MAST, NOT OFF THIS DRAWING. The "
        f"{p['BOLT_SPACING_X']:.0f} x {p['BOLT_SPACING_Y']:.0f} here is "
        f"UNVERIFIED layout. Clamp the mast to the blank and spot all four "
        f"with a {p['MAST_CLEAR_D']:.0f} mm TRANSFER PUNCH - a slip fit in "
        f"Gong's own clearance holes, so it marks the true centre within a "
        f"few hundredths, where a tap drill rattling in the same hole does "
        f"not. Then indicate off the four punch marks and machine to them. "
        f"That splits the job the way it wants splitting: the mast owns "
        f"POSITION, the machine owns ANGLE and DEPTH, and neither is being "
        f"asked to do the other's part. "
        f"*** MACHINE THIS ONE. DO NOT HAND-DRILL IT. *** An earlier version "
        f"of this note called it bandsaw and drill-press work. That was "
        f"wrong, and it was wrong because it reasoned from V1 - where the "
        f"holes were THROUGH holes, a nut landed on the far side, and "
        f"clearance quietly absorbed every error of position, angle and "
        f"depth. None of that is true here. These are BLIND TAPPED holes: "
        f"the thread IS the fastener, nothing absorbs anything, and all four "
        f"bolts have to start at once. The budget, in numbers: Gong's "
        f"clearance hole gives {_slop:.2f} mm of radial slop, so true "
        f"position has to hold about {_slop / 2:.2f} mm across the pattern "
        f"(errors at opposite corners do not cancel, they add). A hole "
        f"drilled just 2 degrees off wanders {p['INSERT_L'] * 0.0349:.2f} mm "
        f"over its {p['INSERT_L']:.0f} mm depth - MORE THAN THE WHOLE BUDGET, "
        f"on its own, and a hand-held drill is routinely 3-5 degrees off. "
        f"Depth is no kinder: {p['INSERT_BLIND']:.1f} mm of solid aluminium "
        f"is all that stands between the tap and a hole through the plate "
        f"that keeps the cavity dry. "
        f"ORDER OF OPERATIONS THAT MATTERS: measure the REAL Gong plate "
        f"first and machine to what you measured, not to the "
        f"{p['BOLT_SPACING_X']:.0f} x {p['BOLT_SPACING_Y']:.0f} nominal in "
        f"this drawing - that figure is UNVERIFIED layout only, and a "
        f"perfectly machined plate on the wrong pattern is still scrap. "
        f"Route, in order of preference: (1) job-shop it - a 250 x 175 "
        f"rectangle with four tapped holes is a trivial job and cheap "
        f"against the cost of getting it wrong; (2) the makerspace CNC, IF "
        f"they permit aluminium - it is a woodworking shop, so ask; (3) drill "
        f"press with a bought drill bushing and a tapping guide, depth stop "
        f"set - acceptable, but it is the fallback, not the plan. "
        f"KEEP A THREAD REPAIR KIT ON THE BENCH either way: an M8 Time-Sert "
        f"or helicoil turns a stripped or wandering hole into a ten-minute "
        f"fix instead of a scrapped plate and a lost weekend. "
        f"6061 shears at ~207 MPa against G10's ~55, so the tapped thread "
        f"(136 mm2, 17.7 kN) beats the O20 bonded bushing it replaced and the "
        f"M8 bolt itself becomes the weak link - which is where you want it. "
        f"TEF-GEL EVERY BOLT: aluminium plate, A4 stainless bolts, wet "
        f"cavity. That is the whole galvanic mitigation and it is not "
        f"optional. Nest both plates on one 12x18 sheet: 2 x 6.89in of the "
        f"18in length, 4.2in spare.")

    # 7 - cavity caul ------------------------------------------------------
    # RESTORED. This was deleted by accident when the G10 ring bars came out -
    # it lived in the same block and went with them, silently, because nothing
    # references it. It is the part that makes the cavity bag-able at all.
    #
    # THE PROBLEM IT SOLVES: the cavity is a CONCAVE box. Atmospheric pressure
    # presses a bag onto convex shapes and BRIDGES it across concave ones, so
    # a bag laid over the cavity opening spans it like a drum skin and touches
    # nothing inside. Every corner and fillet would cure as a void.
    # The caul is a male plug of the cavity. It drops in on top of the wet
    # laminate, and the bag presses on the CAUL - which presses the laminate
    # into the floor, the walls and the R10 fillets. Pressure gets where a bag
    # cannot reach.
    # 0.5 mm under size per side is the laminate-plus-peel-ply allowance.
    # RELEASE IT PROPERLY - wax and PVA, or packing tape over the whole plug.
    # A caul bonded into a cured cavity is not recoverable.
    d = Dxf()
    d.poly(rrect(0, cav_l - 1.0, 0, CAV_W - 1.0, R))
    # HEIGHT IS THE CAVITY'S DEPTH TO THE LEDGE, not the module's height.
    # This used to be L["ext_h"] - the height of the thing that goes IN the
    # cavity afterwards, which is a different measurement and 6.5 mm shorter.
    # The consequence was not cosmetic: the caul stopped 6.5 mm below the
    # ledge, so the wall-to-ledge corner - concave, exactly where a bag
    # bridges and cures a void - got pressure from neither the caul nor the
    # bag. And that corner is where the rim ring sits.
    _caul_h = p["THICK"] - p["LID_T"] - p["RIM_T"] - p["FLOOR_Z"]
    add("13_cavity_caul", "EPS offcut", _caul_h, 1, d, cav_l - 1, CAV_W - 1,
        "CUT IT TO FIT WITH THE RIM RING ALREADY IN PLACE. The ring is not "
        "bonded on after glassing - it is GLASSED IN during this same layup, "
        "sitting on its ledge with the printed filler strip waxed into its "
        "groove, and the laminate runs up the cavity wall, across the ledge "
        "and over the ring in one piece. So the caul has to drop inside the "
        "ring's inner edge and bear on the cavity, and it has to be the full "
        "depth to the ledge or the corner it exists to consolidate is the one "
        "corner it misses. Trial-fit it dry, with the ring in, before there "
        "is resin anywhere. "
        "EPS, not MDF - it only has to transmit bag pressure, and at 7 inHg "
        "that is 24 kPa against EPS's 150 kPa crush, 6x, deflecting 0.2 mm "
        "over its 90 mm depth. MDF was over-specifying a pusher. "
        "BEST CASE IT IS FREE: if the CNC PROFILES the cavity rather than "
        "pocketing it to chips, the plug that drops out IS this part, already "
        "the right shape - just skim it undersize. "
        "Release-taped or waxed. Supports the deck skin during bagging, then "
        "presses the cavity laminate into the corners. 0.5 mm under size per "
        "side. Break its own edges to the cavity's R10 or it will not seat.")

    # 8 - router guide for opening the seal groove -------------------------
    # BACK, because the groove is glassed over and has to be opened again -
    # but this is NOT the part that used to live here. The old one guided a
    # full-depth cut into virgin G10 on a finished board, which is why it was
    # deleted. This one guides a shallow window through ~0.6 mm of glass into
    # a SACRIFICIAL FILLER sitting in an already-printed groove, with an
    # UNDERSIZED cutter. Miss by half a millimetre and you are still inside
    # the groove; the printed walls below define the finished geometry, not
    # the cutter.
    GUIDE_OFF = 5.0     # (guide bushing OD - cutter OD) / 2 - CHECK your router
    d = Dxf()
    gi = p["CHAN_INSET"]
    d.poly(rrect(RIM_W - gi - GUIDE_OFF, ow - RIM_W + gi + GUIDE_OFF,
                 RIM_W - gi - GUIDE_OFF, oh - RIM_W + gi + GUIDE_OFF,
                 R + gi + GUIDE_OFF))
    d.poly(rrect(0, ow, 0, oh, R + RIM_W), layer="CHANNEL")
    add("14_groove_guide", "MDF 12 mm - FALLBACK ONLY", 12.0, 1, d, ow, oh,
        f"PROBABLY NOT NEEDED. Print the filler strip "
        f"{p['CHAN_FILLER_PROUD']:.1f} mm PROUD of the ring face and the glass "
        f"drapes over a {p['CHAN_W']:.0f} mm ridge you can see and feel. Then "
        f"the job is just SANDING THE RING FACE FLAT - which that face needs "
        f"anyway, since it is the seal land and the lid has to bottom evenly "
        f"on it. The ridge sands through first, the filler shows as a line "
        f"along the whole groove, and you pick it out. No cutter, no guide, "
        f"no template on a finished board. "
        f"Cut this only if you would rather route it. "
        f"Opens the seal groove AFTER glassing. Use a "
        f"{p['CHAN_CUTTER']:.1f} mm cutter in the {p['CHAN_W']:.0f} mm groove "
        f"- {(p['CHAN_W']-p['CHAN_CUTTER'])/2:.2f} mm of lateral slop each "
        f"side before it can touch the sealing land. Set depth to just break "
        f"into the filler; you will feel it go soft. Then pick the filler out "
        f"and the PRINTED walls are the finished groove. "
        f"THEN WET THE GROOVE OUT WITH NEAT EPOXY and let it cure before the "
        f"cord goes in. Routing through the laminate leaves cut glass fibre "
        f"ends in the groove's top edge, in the seal itself - the same path "
        f"that flooded V1's cavity. Silicone adhesive does not stop a wick; "
        f"epoxy does. Opening offset "
        f"{GUIDE_OFF:.0f} mm for a guide bushing - RE-CHECK against your own. "
        f"The CHANNEL outline is the rim ring's outer edge, for registering.")

    # 15 - deck pad nest ---------------------------------------------------
    # NOT a machined part - a CUTTING PATTERN for a knife, laid out on the
    # 2400 x 600 EVA sheet so you can see all twelve panels land on one sheet.
    #
    # THE WIDTHS ARE DEVELOPED, NOT PROJECTED. The deck crown is ~50 mm over a
    # 280 mm half width, so its surface arc is about 8.6% longer than the flat
    # shadow it casts. Cutting panels to the projected width leaves them short
    # of the rail by ~20 mm and you find out with the backing paper already
    # off. Each panel's flat width here is the ARC across the deck between its
    # two boundaries, station by station, so it wraps onto the crown and lands
    # where it was drawn.
    #
    # The same crown is why it is panelled at all: the arc excess is not
    # constant - about 10 mm at the nose, 22 mm amidships - and a single sheet
    # cannot absorb that 12 mm differential without wrinkling at the ends.
    # Three strips a side split it, and the seams take up the remainder.
    dz, hwf = p["deck_z_at"], p["half_width"]
    PX0, PX1 = p["DECK_PAD_X0"], p["DECK_PAD_X1"]
    PIN, PGAP = p["DECK_PAD_INSET"], p["DECK_PAD_GAP"]
    SHT_L, SHT_W = p["DECK_PAD_SHEET"]
    LEN = p["LENGTH"]

    def _arc(x, ya, yb, n=64):
        tot, py, pz = 0.0, ya, dz(x, ya)
        for i in range(1, n + 1):
            y = ya + (yb - ya) * i / n
            z = dz(x, y)
            tot += math.hypot(y - py, z - pz)
            py, pz = y, z
        return tot

    STN = 110
    LIDIN = p["LID_PAD_INSET"]
    _lc = p["CAV_LAM"] + 1.5
    GAP = p["DECK_PAD_GAP"]
    CR = p["DECK_PAD_CORNER_R"]
    SLOPE = p["DECK_PAD_MAX_SLOPE"]
    aft_x1 = p["CAV_X0"] - RIM_W - GAP
    fwd_x0 = p["CAV_X1"] + RIM_W + GAP
    lx0 = p["CAV_X0"] - RIM_W + _lc + LIDIN
    lx1 = p["CAV_X1"] + RIM_W - _lc - LIDIN
    lhy = p["CAV_WIDTH"] / 2 + RIM_W - 1.5 - LIDIN
    lr = max(0.0, p["CAV_CORNER_R"] + RIM_W - 1.5 - LIDIN)

    def _edge(x, tol=0.25):
        """Bisect to the slope limit - stepping quantises the cut line."""
        hwv = hwf(x / LEN) - 1.0

        def sl(y):
            y0, y1 = max(0.0, y - 1.0), min(hwv, y + 1.0)
            return math.degrees(math.atan2(abs(dz(x, y1) - dz(x, y0)),
                                           max(1e-6, y1 - y0)))
        if sl(hwv) <= SLOPE:
            return hwv
        lo, hi = 0.0, hwv
        while hi - lo > tol:
            mid = (lo + hi) / 2.0
            if sl(mid) <= SLOPE:
                lo = mid
            else:
                hi = mid
        return lo

    def _tap(x):
        f = 1.0
        n0 = PX1 - p["DECK_PAD_NOSE_TAPER"]
        if x > n0:
            t = (x - n0) / p["DECK_PAD_NOSE_TAPER"]
            f = min(f, 1.0 - (1.0 - p["DECK_PAD_TIP_F"]) * t * t)
        t1 = PX0 + p["DECK_PAD_TAIL_TAPER"]
        if x < t1:
            t = (t1 - x) / p["DECK_PAD_TAIL_TAPER"]
            f = min(f, 1.0 - (1.0 - p["DECK_PAD_TAIL_F"]) * t * t)
        return f

    def _rounded(fn, x0, x1, r0, r1):
        def f(x):
            h = fn(x)
            for d, r in ((x - x0, r0), (x1 - x, r1)):
                if r > 0.0 and d < r:
                    d = max(0.0, d)
                    h = min(h, h - r + math.sqrt(max(0.0, r * r - (r - d) ** 2)))
            return h
        return f

    def _flat(x_lo, x_hi, half_f):
        """Symmetric flat pattern - developed half width either side of centre."""
        up, dn = [], []
        for i in range(STN + 1):
            x = x_lo + (x_hi - x_lo) * i / STN
            hy = half_f(x)
            if hy <= 0.5:
                continue
            w = _arc(x, 0.0, hy)
            up.append((x - x_lo, w))
            dn.append((x - x_lo, -w))
        return (up + list(reversed(dn))) if up else None

    def _base(x):
        return _edge(x) * _tap(x)

    pieces = [
        ("lid", _flat(lx0, lx1, _rounded(lambda _x: lhy, lx0, lx1, lr, lr))),
        ("fwd", _flat(fwd_x0, PX1, _rounded(_base, fwd_x0, PX1, CR, CR))),
        ("aft", _flat(PX0, aft_x1, _rounded(_base, PX0, aft_x1, CR, CR))),
    ]

    d = Dxf()
    d.poly([(0, 0), (SHT_L, 0), (SHT_L, SHT_W), (0, SHT_W), (0, 0)],
           layer="CHANNEL")
    KERF = 8.0
    x_cur, placed, spill = 0.0, 0, 0
    for _nm, pat in pieces:
        if not pat:
            continue
        w = max(q[0] for q in pat) - min(q[0] for q in pat)
        h = max(q[1] for q in pat) - min(q[1] for q in pat)
        lo = min(q[1] for q in pat)
        if x_cur + w > SHT_L or h > SHT_W:
            spill += 1
            continue
        d.poly([(q[0] + x_cur, q[1] - lo) for q in pat] +
               [(pat[0][0] + x_cur, pat[0][1] - lo)])
        x_cur += w + KERF
        placed += 1
    use = 100.0 * x_cur / SHT_L
    add("15_deck_pad_nest", "EVA sheet 2400 x 600", p["DECK_PAD_T"], 1, d,
        SHT_L, SHT_W,
        f"CUTTING PATTERN, not a machined part - knife and a straightedge. "
        f"{placed} pieces for ONE BOARD"
        + (f", {spill} SPILLED to a second sheet" if spill else "")
        + f", using {use:.0f}% of the roll: one aft of the hatch, one forward "
        f"of it, one on the lid. "
        f"NOT PANELLED - seams land where you stand and every seam is an edge "
        f"that lifts and packs with grit. Three pieces only because the hatch "
        f"occupies the middle 600 mm and there is no continuous path past it. "
        f"NOTHING RUNS UP THE SIDES of the hatch: those 27 mm slivers were "
        f"outboard of the lid pad and bought four more lifting edges for "
        f"nothing. "
        f"ALL CORNERS RADIUSED {CR:.0f} mm (lid {lr:.0f} mm, matching the lid "
        f"itself). A square corner on 5.8 mm self-adhesive sheet is the first "
        f"place it peels and a snag underfoot besides. "
        f"WIDTHS ARE DEVELOPED - the arc across the crown, not the flat "
        f"shadow, which runs ~8.6% short. The outline is bisected to the "
        f"{SLOPE:.0f} deg slope limit rather than stepped to it; stepping "
        f"quantises the cut line to a visible staircase. "
        f"That slope limit is what keeps the pad ON TOP - about 55 mm of bare "
        f"rail, which is where the top of this board ends, not a shy margin. "
        f"Lid piece inset {LIDIN:.0f} mm so the 12 M5 bolt heads stay exposed. "
        f"CUT LONG AND TRIM ON THE BOARD, working from the centreline out. "
        f"The CHANNEL outline is the sheet edge.")

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
              "", "## EPS core — FOUR pieces, two splits", "",
              "The core is cut in **four** pieces, not two, because it is "
              "bounded on two different axes:", "",
              "| Split | Why | Number |",
              "|---|---|---|",
              f"| Vertical at x = {p['SEAM_X']:.0f} | bed is "
              f"{p['CNC_BED_X']:.0f} mm long, board is {p['LENGTH']:.0f} | "
              f"{p['SEAM_X']:.0f} + {p['LENGTH']-p['SEAM_X']:.0f} |",
              f"| Horizontal at z = "
              f"{p['CNC_SUBSTACK_LAYERS']*p['EPS_SHEET_T']:.1f} | gantry is "
              f"{p['CNC_BED_Z']:.1f} mm, GLUED STACK is "
              f"{p['EPS_LAYERS']*p['EPS_SHEET_T']:.1f} | 2 layers + 2 layers |",
              "",
              "**The horizontal split is the one that is easy to miss.** The "
              "height that has to pass under the gantry is not the finished "
              "envelope of the board - it is the GLUED STACK it is carved "
              f"from, {p['EPS_LAYERS']*p['EPS_SHEET_T']:.1f} mm, before a "
              f"chip is cut. Against {p['CNC_BED_Z']:.1f} mm of Z that is a "
              f"{p['EPS_LAYERS']*p['EPS_SHEET_T']-p['CNC_BED_Z']:.0f} mm "
              "overshoot, not a near miss.",
              "",
              "So **machine the halves and bond last**, rather than gluing the "
              "stack and then carving it:", "",
              "| Piece | Layers | What gets cut |",
              "|---|---|---|",
              "| `*_Lower` | 1 + 2 | rocker and mast pocket on the underside; "
              "**lower** half of the cavity pocketed into the top face |",
              "| `*_Upper` | 3 + 4 | deck crown on the top face; **upper** "
              "half of the cavity cut straight through |",
              "",
              f"Nothing goes under the gantry taller than "
              f"{p['CNC_SUBSTACK_LAYERS']*p['EPS_SHEET_T']:.1f} mm. Two things "
              "fall out for free: the deepest single pocket drops from ~124 mm "
              "(which would want a ~130 mm cutter that does not exist in "
              "1/2 in for foam at sane money) to about 77 mm, and the 203 mm "
              "stack stops being an awkward thing to square up on a bed with "
              "24.8 mm of side clearance.",
              "",
              "Cost is one full-area glue line at mid-thickness, in EPS, where "
              "the skins carry the load - and the board already has three such "
              "lines between its four layers. This promotes one to the "
              "assembly joint. Alignment is the dowel-pin fixture already on "
              "the list for two-sided registration.",
              "",
              "Bond order: **mid-plane first** (Lower to Upper, each side of "
              "the seam), which gives two full-thickness halves you can handle "
              "on a bench; then butt those at the vertical seam.",
              "",
              "### How the four pieces are actually milled", "",
              "**Five setups, one flip, no cradle.** Not eight - \"4 pieces "
              "x 2 faces\" is arithmetic, not a plan, because most of these "
              "faces have nothing on them. The cavity is entirely aft of the "
              "vertical seam, so both forward pieces are one-and-done.", "",
              "| Piece | Setup | Face up | What gets cut |",
              "|---|---|---|---|",
              "| `Aft_Lower` | 1 | top | lower half of the cavity, "
              f"{p['CNC_SUBSTACK_LAYERS']*p['EPS_SHEET_T'] - p['FLOOR_Z']:.1f}"
              " mm deep |",
              "| `Aft_Lower` | 2 | bottom | rocker (3D) + mast block pocket "
              "— **the one flip** |",
              "| `Aft_Upper` | 3 | top | deck crown (3D), cavity cut through, "
              "rim ledge, leash pocket |",
              "| `Fwd_Lower` | 4 | bottom | rocker (3D). Top is the mid-plane "
              "— nothing on it |",
              "| `Fwd_Upper` | 5 | top | deck crown (3D). Bottom is the "
              "mid-plane — nothing on it |",
              "",
              "**Workholding: tape or vacuum to the spoilboard, every time.** "
              "Every setup presents a flat face — the as-glued slab face, or "
              "the mid-plane, or (for the flip) a top that has a pocket in it "
              "but is still flat all the way round it. **No cradle is needed "
              "anywhere**, and that is the real prize from splitting "
              "horizontally: machining a full-thickness board means holding a "
              "crowned deck while you cut the rocker into the other side, and "
              "that needs a cradle milled to match the deck. This plan never "
              "has to.", "",
              "Only setup 2 is a flip, so the dowel-pin registration matters "
              "exactly once. Drill the dowel holes in the spoilboard and in "
              "the waste perimeter of the slab before any 3D work starts.", "",
              "> **CUTTER REACH — CHECK THIS BEFORE THE DAY.** The deepest "
              f"single pocket is the cavity's lower half at "
              f"{p['CNC_SUBSTACK_LAYERS']*p['EPS_SHEET_T'] - p['FLOOR_Z']:.1f}"
              " mm. The O-flute the BOM buys (Freud 73-214) has a **cutting "
              f"length of {p['CUTTER_FLUTE_L']:.1f} mm** — that is its flute, "
              "not its overall length, and it is "
              f"{p['CNC_SUBSTACK_LAYERS']*p['EPS_SHEET_T'] - p['FLOOR_Z'] - p['CUTTER_FLUTE_L']:.1f}"
              " mm short. Either buy a long-reach 1/2 in spiral with 75 mm+ "
              "of flute for that one pocket, or rough it with the ball nose "
              "and accept the stepover. Do not find this out with the foam "
              "already taped down.", "",
              "### Station table", "",
              "Width and thickness are the finished "
              "hull; rocker is the bottom's rise above the datum plane.", "",
              "| Station (mm) | Width | Thickness | Rocker |",
              "|---|---|---|---|"]
    for (x, w, t, r) in rows:
        lines.append(f"| {x:.0f} | {w:.1f} | {t:.1f} | {r:.1f} |")

    lines += ["", "## Two-day plan", "",
              "**Day 1 — before layup**", "",
              "1. EPS core — **4 pieces, 5 setups, 1 flip**. None taller "
              f"than {p['CNC_SUBSTACK_LAYERS']*p['EPS_SHEET_T']:.1f} mm; see "
              "the milling table above",
              "2. Bond mid-plane (Lower+Upper), then butt at the vertical seam",
              "3. Cavity caul (13)",
              "4. Aluminium flat parts (4 module floor, 12 mast plate)",
              "5. H80 lid cores (3, 11)", "",
              "**Day 2 — after layup**", "",
              "5. Trim the cured sandwich lids to net profile (2, 10)",
              "6. Face the hatch lid underside flat in the same setup",
              "7. Drill lid bolt clearance off the installed inserts", "",
              "## Before booking", "",
              "- Will they allow **EPS** dust? Still unanswered, and it is "
              "a woodworking shop with no published material policy. This is "
              "the one that can stop the booking.",
              "- **Gantry clearance?** Now a nice-to-know rather than a "
              f"blocker: the split sequence needs only ~"
              f"{p['CNC_SUBSTACK_LAYERS']*p['EPS_SHEET_T']+10:.0f} mm. If they "
              "say 180+, the mid-plane bond can be skipped and the core goes "
              "back to two pieces.",
              "- G10 is **no longer a question** — there is none in the build.",
              "- Bed clears the longer half already: "
              f"{max(p['SEAM_X'], p['LENGTH']-p['SEAM_X']):.0f} mm of "
              f"{p['CNC_BED_X']:.0f}, and "
              f"{p['WIDTH']:.0f} mm of {p['CNC_BED_Y']:.0f} across — but that "
              "leaves only "
              f"{(p['CNC_BED_Y']-p['WIDTH'])/2:.1f} mm a side, so it has to be "
              "taped or vac-held, not clamped from the edges."]
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
