"""
anim_machining.py - the CNC half of the build animation.

exec()'d from animate_build.py, so it shares that namespace (shot, caption,
cam_move, box, cyl, key_*, world_bvh, ...).

WHAT THE FIRST VERSION GOT WRONG, and why this file exists:

1. THE ROCKER WAS ALREADY CUT IN SETUP 1. Waste was split between the two
   setups by a flat horizontal plane at the cavity floor. That is not what a
   3-axis router can reach. The board's underside curves up towards the tail
   and nose, so the rocker rises well above that plane, and everything above
   it vanished in the first pass. The split has to be by the PART'S OWN
   SURFACE: what a cutter coming down in Z can reach from above is the waste
   above the part's top surface; what it reaches after the flip is the waste
   below the part's bottom surface. height_solid() builds exactly that
   boundary by raycasting the finished part.

2. ALL FOUR PIECES WERE ON THE TABLE IN EVERY SETUP. So they were machined
   three times over, and then step 4 glued together pieces that were already
   finished. Each blank now gets its own setups and nothing else is on the
   table while it is cut.

3. NOTHING SHOWED WHERE FOUR BLANKS CAME FROM. The glued slab is 1440 long
   and the bed is 1209.8, so the slab CANNOT be machined whole - it gets
   cross-cut at the 1030 seam first, and that is where four blanks come from.
   That cut was missing entirely, which is what made the bonding step look
   like it was gluing parts that had never been apart.

4. THE CONDUIT APPEARED DURING MACHINING. The router cuts what a router can
   reach in Z. The breakthrough that bridges into the cavity is cut by hand
   afterwards, so it is plugged until then.

5. THE ALUMINIUM AND THE H-80 WERE NEVER MACHINED. Both get cut, and the
   mast plate is the part with the tightest tolerance in the whole build.

Five setups across four blanks, one flip - the same count cut-list.md gives.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Quaternion, Matrix

X_SPLIT = 1.030            # the vertical seam; also the cross-cut line
KERF_GAP = 0.050           # how far the fwd blanks stand clear after the cut
PAD = 0.011                # trim allowance around the part, per side
GRID = 0.008               # height-field cell, metres


# ------------------------------------------------------------ height field
def shadow_solid(name, piece, x0, x1, y0, y1, z_stock, z_base):
    """Everything from the bottom of the stock up to the part's top surface.

    NOT the mirror image of this - and the difference matters. The first
    attempt built the volume ABOVE the part's top face, which over most of an
    aft-lower blank is the 0.4 mm sliver between the part and the top of its
    own stock. EXACT could not resolve a sheet that thin across a 130 x 73
    grid, and quietly returned an empty below-waste: setup 2 had nothing left
    to cut, which is exactly what it looked like.

    Built downwards it is thick everywhere the part exists - up to the full
    101.6 mm - and the two sides fall out of it cleanly:

        below = removed INTERSECT shadow     under the rocker, after the flip
        above = removed - shadow             the cavity, and the perimeter

    The cavity lands in `above` even though it is deep, because inside the
    cavity footprint the part's top surface IS the cavity floor, so the shadow
    stops there and the pocket above it does not belong to it.

    Sampled by raycasting the FINISHED part, so the boundary is the part's own
    surface rather than a plane someone picked. Where the part is absent the
    whole column is stock and belongs to this side.

    Sampling is deliberately CONSERVATIVE - the max (or min) over a small
    cross around each grid point - so the surface never dips inside the part
    between samples. It is only ever used to classify waste that has already
    been computed exactly, so a sliver landing in the wrong setup is cosmetic.
    """
    bvh = world_bvh(piece)
    nx = max(2, int((x1 - x0) / GRID))
    ny = max(2, int((y1 - y0) / GRID))
    dx, dy = (x1 - x0) / nx, (y1 - y0) / ny
    far = abs(z_stock - z_base) + 0.5
    off = GRID * 0.5

    def surf(x, y):
        """Nearest hit casting DOWN is the part's top face. Sampled over a
        small cross and taking the max, so the surface never dips inside the
        part between grid points."""
        best = None
        for ox, oy in ((0, 0), (off, 0), (-off, 0), (0, off), (0, -off)):
            hit = bvh.ray_cast(Vector((x + ox, y + oy, z_stock + far)),
                               Vector((0, 0, -1)))
            if hit and hit[0] is not None:
                best = hit[0].z if best is None else max(best, hit[0].z)
        return best

    # Where the part is absent the whole column is perimeter waste and belongs
    # to the first setup, so the shadow should be nothing there. A height
    # field cannot be nothing, so it gets a 2 mm floor - which hands a 2 mm
    # skirt of perimeter waste to the second setup instead. Invisible.
    FLOOR = 0.002
    eps = 0.0004
    bm = bmesh.new()
    top, bot = [], []
    for i in range(nx + 1):
        tc, bc = [], []
        x = x0 + i * dx
        for j in range(ny + 1):
            y = y0 + j * dy
            zs = surf(x, y)
            zt = (z_base + FLOOR if zs is None
                  else min(max(zs, z_base + FLOOR), z_stock - eps))
            tc.append(bm.verts.new((x, y, zt)))
            bc.append(bm.verts.new((x, y, z_base)))
        top.append(tc)
        bot.append(bc)
    bm.verts.index_update()
    for i in range(nx):
        for j in range(ny):
            bm.faces.new((top[i][j], top[i + 1][j], top[i + 1][j + 1],
                          top[i][j + 1]))
            bm.faces.new((bot[i][j + 1], bot[i + 1][j + 1], bot[i + 1][j],
                          bot[i][j]))
    for i in range(nx):
        bm.faces.new((top[i][0], bot[i][0], bot[i + 1][0], top[i + 1][0]))
        bm.faces.new((top[i + 1][ny], bot[i + 1][ny], bot[i][ny], top[i][ny]))
    for j in range(ny):
        bm.faces.new((top[0][j + 1], bot[0][j + 1], bot[0][j], top[0][j]))
        bm.faces.new((top[nx][j], bot[nx][j], bot[nx][j + 1], top[nx][j + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    scene.collection.objects.link(o)
    o.hide_render = True
    return o


def _bake(o):
    """Collapse an object's modifier stack to a real mesh, once.

    Every operand here is hidden, and a hidden object has no evaluated mesh -
    so un-hide, evaluate, put it back. Baking matters: leaving these live
    would re-run EXACT booleans over the whole blank on every frame.
    """
    was = []
    for m in o.modifiers:
        if m.type == 'BOOLEAN' and m.object is not None:
            was.append((m.object, m.object.hide_viewport))
            m.object.hide_viewport = False
    hv = o.hide_viewport
    o.hide_viewport = False
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    o.data = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    o.modifiers.clear()
    o.hide_viewport = hv
    for ob, h in was:
        ob.hide_viewport = h


def _bool(o, name, op, target, solver='EXACT'):
    m = o.modifiers.new(name, 'BOOLEAN')
    m.operation = op
    m.object = target
    m.solver = solver
    m.material_mode = 'INDEX'
    return m


# ------------------------------------------------------------------ blanks
def build_blanks():
    """One entry per blank: its stock, the finished piece inside it, and the
    waste split by which SETUP reaches it."""
    lo, hi = world_bounds(MACH)
    y0, y1 = lo.y - PAD, hi.y + PAD
    xg0, xg1 = lo.x - PAD, hi.x + PAD
    z_mid = world_bounds(LOWERS)[1].z            # top of the lower slab
    z_bot = lo.z
    z_top = z_bot + 2 * (z_mid - z_bot)          # stock is the full 101.6

    rig = dict(y0=y0, y1=y1, xg0=xg0, xg1=xg1, z_bot=z_bot, z_mid=z_mid,
               z_top=z_top, blanks={})
    rig["table"] = box("CNC_Table", (xg0 - .28, y0 - .20, z_bot - 0.019),
                       (xg1 + .28, y1 + .20, z_bot - 0.001), M_TABLE)

    spec = (
        # key          piece                       x range          z range
        ("AL", obj("MachStack_Aft_Lower"), (xg0, X_SPLIT), (z_bot, z_mid), 2),
        ("FL", obj("MachStack_Fwd_Lower"), (X_SPLIT, xg1), (z_bot, z_mid), 1),
        ("AU", obj("MachStack_Aft_Upper"), (xg0, X_SPLIT), (z_mid, z_top), 1),
        ("FU", obj("MachStack_Fwd_Upper"), (X_SPLIT, xg1), (z_mid, z_top), 1),
    )
    for key, piece, (bx0, bx1), (bz0, bz1), setups in spec:
        if piece is None:
            continue
        b = dict(key=key, piece=piece, x0=bx0, x1=bx1, z0=bz0, z1=bz1,
                 y0=y0, y1=y1, setups=setups)

        # the stock, 0.4 mm proud so its faces never land exactly on the
        # part's and z-fight
        e = 0.0004
        b["waste"] = box("Blank_" + key, (bx0, y0, bz0 - e), (bx1, y1, bz1 + e),
                         M_WASTE)

        # everything the router removes from this blank, exact
        rem_all = box("Rem_" + key, (bx0, y0, bz0 - e), (bx1, y1, bz1 + e))
        rem_all.hide_render = True
        _bool(rem_all, "part", 'DIFFERENCE', piece)
        _bake(rem_all)

        if setups == 2:
            # AFT LOWER is the only blank cut from both sides. Split its waste
            # by what a cutter reaches from above vs from below - the fix for
            # the rocker appearing during setup 1.
            hs = shadow_solid("HS_" + key, piece, bx0, bx1, y0, y1,
                              bz1 + e, bz0 - e)
            above = rem_all
            below = rem_all.copy()
            below.data = rem_all.data.copy()
            scene.collection.objects.link(below)
            below.hide_render = True
            below.name = "RemBelow_" + key
            above.name = "RemAbove_" + key
            _bool(above, "reach", 'DIFFERENCE', hs)
            _bool(below, "reach", 'INTERSECT', hs)
            _bake(above)
            _bake(below)
            parts = [("above", above), ("below", below)]
        else:
            rem_all.name = "Rem_" + key
            parts = [("only", rem_all)]

        b["cuts"] = []
        for tag, rem in parts:
            swept = box("Swept_%s_%s" % (key, tag),
                        (bx0 - 4.0, y0 - .05, bz0 - .06),
                        (bx0, y1 + .05, bz1 + .06))
            swept.hide_render = True
            _bool(rem, "swept", 'INTERSECT', swept)
            _bool(b["waste"], "cut_" + tag, 'DIFFERENCE', rem)
            b["cuts"].append(dict(tag=tag, removed=rem, swept=swept))

        # one pivot per blank: carries the flip, and the slide-clear after the
        # cross-cut, for the piece and all of its machining scaffolding
        piv = bpy.data.objects.new("Piv_" + key, None)
        scene.collection.objects.link(piv)
        piv.location = ((bx0 + bx1) / 2, (y0 + y1) / 2, (bz0 + bz1) / 2)
        piv.rotation_mode = 'QUATERNION'
        kids = [piece, b["waste"]] + [c["removed"] for c in b["cuts"]]
        for p in kids:
            p.parent = piv
            # NOT piv.matrix_world - the location was just set and the
            # depsgraph has not run, so it is still identity
            p.matrix_parent_inverse = Matrix.Translation(-piv.location)
        b["pivot"] = piv
        b["home"] = Vector(piv.location)
        rig["blanks"][key] = b

    # ---------------------------------------------------------- the tool
    tool = bpy.data.objects.new("Tool", None)
    scene.collection.objects.link(tool)
    parts = [cyl("Tool_Flute", 6.35 * MM, 0, 0.0762, M_FLUTE),
             cyl("Tool_Shank", 6.35 * MM, 0.0762, 0.115, M_TOOL),
             cyl("Tool_Collet", 0.022, 0.113, 0.155, M_TOOL, segments=24),
             cyl("Tool_Spindle", 0.058, 0.155, 0.560, M_TOOL, segments=32)]
    for p in parts:
        p.parent = tool
    rig["tool"] = tool
    rig["tool_parts"] = parts

    # ---------------------------------------------------------- the saw
    blade = cyl("Saw_Blade", 0.140, -0.0016, 0.0016, M_FLUTE, segments=64)
    blade.rotation_euler = (0, math.radians(90), 0)
    body = box("Saw_Body", (-0.040, -0.060, 0.055), (0.040, 0.060, 0.145),
               M_TOOL)
    saw = bpy.data.objects.new("Saw", None)
    scene.collection.objects.link(saw)
    for p in (blade, body):
        p.parent = saw
    rig["saw"] = saw
    rig["saw_parts"] = [blade, body]

    # -------------------------------------------- the bits that are not EPS
    # Machined on the same table, from their own stock. The mast plate is the
    # tightest-tolerance part in the build and was not shown being made at all.
    rig["bench"] = []
    for src, x, mname in ((obj("MastPlate_Alu"), 0.30, "V2_alu"),
                          (obj("DenseFoam_Block"), 0.86, "V2_dense")):
        if src is None:
            continue
        cp = src.copy()
        cp.data = src.data
        cp.name = src.name + "_OnBench"
        scene.collection.objects.link(cp)
        # Object.copy() carries the SOURCE'S ACTION across, and the two then
        # share it - so keyframing the bench copy visible also switched the
        # real part on, and the original H-80 block hung in the air through
        # the whole machining sequence.
        cp.animation_data_clear()
        blo, bhi = world_bounds([src])
        cp.location = (x, 0.0, src.location.z - blo.z + (z_bot + 0.0005))
        # Derive the moved bounds from the location delta rather than reading
        # matrix_world back. view_layer.update() did not refresh it here, and
        # the stock ended up built 530 mm away from the part it wraps - the
        # same stale-matrix trap as the parent inverse.
        d = Vector(cp.location) - Vector(src.location)
        clo, chi = blo + d, bhi + d
        p2 = 0.010
        st = box("Stock_" + src.name,
                 (clo.x - p2, clo.y - p2, clo.z - 0.0004),
                 (chi.x + p2, chi.y + p2, chi.z + 0.004),
                 bpy.data.materials.get("V2_alu") if "Plate" in src.name
                 else M_WASTE)
        rem = box("Rem_" + src.name,
                  (clo.x - p2, clo.y - p2, clo.z - 0.0004),
                  (chi.x + p2, chi.y + p2, chi.z + 0.004))
        rem.hide_render = True
        _bool(rem, "part", 'DIFFERENCE', cp)
        _bake(rem)
        swept = box("Swept_" + src.name,
                    (clo.x - p2 - 4.0, clo.y - p2 - .05, clo.z - .06),
                    (clo.x - p2, chi.y + p2 + .05, chi.z + .06))
        swept.hide_render = True
        _bool(rem, "swept", 'INTERSECT', swept)
        _bool(st, "cut", 'DIFFERENCE', rem)
        rig["bench"].append(dict(part=cp, stock=st, removed=rem, swept=swept,
                                 x0=clo.x - p2, x1=chi.x + p2,
                                 y0=clo.y - p2, y1=chi.y + p2,
                                 z_top=chi.z + 0.004))

    # ------------------------------------------------- the conduit, plugged
    # A router reaches what it can reach in Z. The bore that bridges into the
    # cavity is cut by hand afterwards, so it stays filled until then.
    plug = obj("ConduitBore")
    if plug is not None:
        cav = obj("Cavity_Void_cut")
        z_floor = world_bounds([cav])[0].z if cav else 0.0295
        plo, phi = world_bounds([plug])
        trim = box("PlugTrim", (plo.x - .01, plo.y - .01, plo.z - .01),
                   (phi.x + .01, phi.y + .01, z_floor))
        trim.hide_render = True
        _bool(plug, "trim", 'INTERSECT', trim)
        _bake(plug)                      # bake first - it replaces the mesh,
        plug.data.materials.clear()      # and materials live on the mesh
        m = bpy.data.materials.get("V2_mach_al") or M_WASTE
        plug.data.materials.append(m)
    if plug is not None and "AL" in rig["blanks"]:
        # it lives in the aft-lower blank, so it has to turn over with it
        pv = rig["blanks"]["AL"]["pivot"]
        plug.parent = pv
        plug.matrix_parent_inverse = Matrix.Translation(-pv.location)
    rig["plug"] = plug

    # four full-length layers, for the glue-up only. The four blanks together
    # occupy exactly the same volume, so the swap to them is invisible.
    rig["layers"] = []
    t = (z_top - z_bot) / 4.0
    for i in range(4):
        rig["layers"].append(
            box("Layer_%d" % i, (xg0, y0, z_bot + i * t),
                (xg1, y1, z_bot + (i + 1) * t), M_WASTE))
    return rig


# ------------------------------------------------------------------ passes
def pass_over(rig, b, cut, f0, f1, z_stock, passes=6, flipped=False,
              bvh_of=None):
    """Fly the cutter over one blank, dragging the sweep behind it.

    Cutter Z rides the finished surface, found by raycast, so it bottoms out
    where the pocket actually bottoms out. The sweep box stays in WORLD space
    even when the blank is flipped - booleans resolve through world
    transforms, so a world-space cutter against a flipped part is correct.
    """
    tool = rig["tool"]
    piv = b["pivot"]
    x0, x1 = b["x0"], b["x1"]
    y0, y1 = b["y0"], b["y1"]

    # the raycast reads matrix_world, and keyframes do not exist yet at
    # authoring time - so pose the pivot the way this pass is cut
    was_q = Quaternion(piv.rotation_quaternion)
    was_l = Vector(piv.location)
    piv.rotation_quaternion = (Quaternion((0, 1, 0), math.pi) if flipped
                               else Quaternion((1, 0, 0, 0)))
    if b["key"].startswith("F"):
        piv.location = b["home"] + Vector((KERF_GAP, 0, 0))
    bpy.context.view_layer.update()
    bvhs = [world_bvh(bvh_of or b["piece"])]

    steps = passes * 8
    key_vis(tool, f0, True)
    for p in rig["tool_parts"]:
        key_vis(p, f0, True)
        key_vis(p, f1, False)
    for i in range(steps + 1):
        u = i / steps
        f = round(f0 + (f1 - f0) * u)
        x = x0 + (x1 - x0) * u
        t = (u * passes) % 1.0
        yy = y0 + (y1 - y0) * (t if int(u * passes) % 2 == 0 else 1 - t)
        key_loc(tool, f, (x, yy, surface_z(bvhs, x, yy, z_stock + 0.4,
                                           z_stock)))
        key_loc(cut["swept"], f, (x - x0, 0, 0))
    key_vis(tool, f1, False)

    piv.rotation_quaternion = was_q
    piv.location = was_l
    bpy.context.view_layer.update()


def only_show(rig, keep, f):
    """One blank on the table at a time. Everything else off."""
    for k, b in rig["blanks"].items():
        on = k in keep
        key_vis(b["waste"], f, on)
        key_vis(b["piece"], f, on)
    # the conduit plug belongs to the aft lower blank - left to its own
    # devices it hangs in mid air through the setups that blank sits out
    key_vis(rig["plug"], f, "AL" in keep)


def bench_pass(rig, e, f0, f1, passes=5):
    """The same raster, for a part that is not one of the four EPS blanks."""
    tool = rig["tool"]
    bvhs = [world_bvh(e["part"])]
    steps = passes * 8
    key_vis(tool, f0, True)
    for p in rig["tool_parts"]:
        key_vis(p, f0, True)
        key_vis(p, f1, False)
    for i in range(steps + 1):
        u = i / steps
        f = round(f0 + (f1 - f0) * u)
        x = e["x0"] + (e["x1"] - e["x0"]) * u
        t = (u * passes) % 1.0
        yy = e["y0"] + (e["y1"] - e["y0"]) * (
            t if int(u * passes) % 2 == 0 else 1 - t)
        key_loc(tool, f, (x, yy, surface_z(bvhs, x, yy, e["z_top"] + 0.4,
                                           e["z_top"])))
        key_loc(e["swept"], f, (x - e["x0"], 0, 0))
    key_vis(tool, f1, False)


def machining_shots(rig):
    """Phase 1: four sheets of EPS to four bonded pieces."""
    B = rig["blanks"]
    AL, FL, AU, FU = B["AL"], B["FL"], B["AU"], B["FU"]
    ALL_W = [b["waste"] for b in B.values()]
    ALL_P = [b["piece"] for b in B.values()]
    for o in (ALL_W + ALL_P + rig["layers"]
              + [rig["table"], rig["tool"], rig["saw"], rig["plug"]]
              + rig["tool_parts"] + rig["saw_parts"]
              + [e["stock"] for e in rig["bench"]]
              + [e["part"] for e in rig["bench"]]):
        key_vis(o, 1, False)

    # -------------------------------------------------- glue up two slabs
    f0, f1 = shot("blank", 6)
    key_vis(rig["table"], f0, True)
    cam_hold(f0, f1, CTR_T, -62, 18, 2.6)
    caption(f0, f1, "Step 4  -  glue up two sub-stacks",
            "four 2in EPS layers become two 101.6 mm slabs, not one 203 mm stack")
    for i, w in enumerate(rig["layers"]):
        a = f0 + int((0.2 + 0.85 * i) * FPS)
        b = a + int(1.5 * FPS)
        key_vis(w, a, True)
        key_loc(w, a, (0, 0, 1.1 + 0.1 * i))
        key_loc(w, b, (0, 0, 0))
        ease(w)

    # ---------------------------------------------------- cross-cut to size
    # THIS WAS MISSING, and its absence is what made bonding look like it was
    # gluing parts that had never been apart.
    f0, f1 = shot("crosscut", 5)
    vis_all(rig["layers"], f0, False)
    vis_all(ALL_W, f0, True)
    key_vis(rig["saw"], f0, True)
    vis_all(rig["saw_parts"], f0, True)
    _tc = (X_SPLIT, 0, rig["z_mid"])
    cam_move(f0, f1, _tc, -146, 24, 1.55, _tc, -114, 34, 1.45)
    caption(f0, f1, "cross-cut both slabs at 1030 mm",
            "the glued slab is 1440 long and the bed is 1209.8 - it cannot be "
            "machined whole. Four blanks start here")
    # blade centre 30 mm up from the bottom of the slab being cut, so a
    # 280 mm blade passes clean through 101.6 mm and still shows 68 mm proud
    for zc, t0 in ((rig["z_mid"] + 0.030, 0.2), (rig["z_bot"] + 0.030, 1.9)):
        a, b = f0 + int(t0 * FPS), f0 + int((t0 + 1.5) * FPS)
        key_loc(rig["saw"], a, (X_SPLIT, rig["y0"] - 0.16, zc))
        key_loc(rig["saw"], b, (X_SPLIT, rig["y1"] + 0.16, zc))
    vis_all(rig["saw_parts"], f1 - int(0.6 * FPS), False)
    key_vis(rig["saw"], f1 - int(0.6 * FPS), False)
    for b in (FL, FU):                        # stand the fwd blanks clear
        key_loc(b["pivot"], f0 + int(3.5 * FPS), b["home"])
        key_loc(b["pivot"], f1, b["home"] + Vector((KERF_GAP, 0, 0)))
        ease(b["pivot"])

    # ============================================= five setups, four blanks
    def setup(tag, b, cut_i, secs, title, sub, passes, flipped=False,
              az=(-72, -104), el=(30, 24)):
        g0, g1 = shot(tag, secs)
        only_show(rig, {b["key"]}, g0)
        key_vis(rig["table"], g0, True)
        _t, _d = fit([b["waste"]], margin=1.25)
        cam_move(g0, g1, _t, az[0], el[0], _d, _t, az[1], el[1], _d * 0.94)
        caption(g0, g1, title, sub)
        pass_over(rig, b, b["cuts"][cut_i], g0 + int(0.4 * FPS),
                  g1 - int(0.4 * FPS), b["z1"], passes=passes, flipped=flipped)
        return g0, g1

    a0, a1 = setup("setup1_cavity", AL, 0, 9,
                   "Setup 1  -  aft lower, cavity from above",
                   "1/2in O-flute. The deepest pocket is 71.6 mm - the bit in "
                   "the BOM reaches 31.8", 7)
    key_vis(rig["plug"], a0, True)

    # --------------------------------------------------------- the one flip
    f0, f1 = shot("flip", 3)
    only_show(rig, {"AL"}, f0)
    key_vis(rig["table"], f0, True)
    key_vis(rig["plug"], f0, True)
    _t, _d = fit([AL["waste"]], spin=True, margin=1.30)
    cam_hold(f0, f1, _t, -104, 20, _d)
    caption(f0, f1, "the one flip",
            "5 setups across 4 blanks, and only this one turns over")
    key_rot(AL["pivot"], f0 + int(0.3 * FPS), Quaternion((1, 0, 0, 0)))
    key_rot(AL["pivot"], f1 - int(0.3 * FPS), Quaternion((0, 1, 0), math.pi))
    ease(AL["pivot"], "rotation_quaternion")

    f0, f1 = shot("setup2_rocker", 7)
    only_show(rig, {"AL"}, f0)
    key_vis(rig["table"], f0, True)
    key_vis(rig["plug"], f0, True)
    key_rot(AL["pivot"], f0, Quaternion((0, 1, 0), math.pi))
    key_rot(AL["pivot"], f1 - 2, Quaternion((0, 1, 0), math.pi))     # hold
    _t, _d = fit([AL["waste"]], margin=1.25)
    cam_move(f0, f1, _t, -110, 30, _d, _t, -142, 22, _d * 0.94)
    caption(f0, f1, "Setup 2  -  rocker and mast pocket",
            "beds on a flat face - tape or vacuum down, never clamp the "
            "24.8 mm rail")
    pass_over(rig, AL, AL["cuts"][1], f0 + int(0.4 * FPS), f1 - int(0.4 * FPS),
              AL["z1"], passes=5, flipped=True)
    key_vis(AL["waste"], f1 - 3, False)
    key_rot(AL["pivot"], f1, Quaternion((1, 0, 0, 0)))

    b0, b1 = setup("setup3_deck", AU, 0, 7,
                   "Setup 3  -  aft upper, from above",
                   "deck crown, cavity through, rim ledge, leash pocket", 6,
                   az=(-60, -28), el=(34, 40))
    key_vis(AU["waste"], b1 - 3, False)

    c0, c1 = setup("setup4_fwd_rocker", FL, 0, 5,
                   "Setup 4  -  fwd lower, mounted upside down",
                   "rocker only. One setup - the mid-plane face is flat and "
                   "beds straight onto the spoilboard", 5, flipped=True,
                   az=(-100, -132), el=(28, 22))
    key_rot(FL["pivot"], c0, Quaternion((0, 1, 0), math.pi))
    key_rot(FL["pivot"], c1 - 2, Quaternion((0, 1, 0), math.pi))
    key_vis(FL["waste"], c1 - 3, False)
    key_rot(FL["pivot"], c1, Quaternion((1, 0, 0, 0)))

    d0, d1 = setup("setup5_fwd_deck", FU, 0, 5,
                   "Setup 5  -  fwd upper, from above",
                   "deck crown. Five setups, four blanks, one flip", 5,
                   az=(-56, -24), el=(34, 42))
    key_vis(FU["waste"], d1 - 3, False)

    # -------------------------------------------- the parts that are not foam
    caps = (("the mast plate  -  6061-T651",
             "MACHINE it. Blind M8 at 0.25 mm true position, with 2.7 mm of "
             "solid left above the tap - not a hand-drill job"),
            ("the mast block  -  H-80 Divinycell",
             "the structural foam the mast plate bolts into, pocketed to fit"))
    for i, e in enumerate(rig["bench"]):
        f0, f1 = shot("machine_bench%d" % (i + 1), 5)
        only_show(rig, set(), f0)
        key_vis(rig["table"], f0, True)
        for j, e2 in enumerate(rig["bench"]):
            key_vis(e2["stock"], f0, j == i)
            key_vis(e2["part"], f0, j == i)
        _t, _d = fit([e["stock"]], margin=1.35)
        _d = max(_d, 1.05)          # the spindle is 560 mm tall; any closer
                                    # and it is the whole shot
        cam_move(f0, f1, _t, -68, 38, _d, _t, -22, 50, _d * 0.94)
        caption(f0, f1, caps[i][0] if i < len(caps) else "machined",
                caps[i][1] if i < len(caps) else "")
        bench_pass(rig, e, f0 + int(0.4 * FPS), f1 - int(0.7 * FPS), passes=5)
        key_vis(e["stock"], f1 - int(0.5 * FPS), False)
        key_vis(e["part"], f1, False)

    # -------------------------------------------------------- bond the core
    f0, f1 = shot("bond", 7)
    vis_all(ALL_P, f0, True)
    key_vis(rig["plug"], f0, True)
    key_vis(rig["table"], f0, False)
    vis_all(ALL_W, f0, False)
    cam_move(f0, f1, CTR_T, -35, 26, 2.4, CTR_T, 18, 20, 2.2)
    caption(f0, f1, "Step 6  -  bond the four blanks",
            "mid-plane first, then the vertical seam at 1030 mm")
    mid = f0 + int(4.2 * FPS)
    for b, off in ((AU, Vector((0, 0, 0.30))),
                   (FU, Vector((KERF_GAP, 0, 0.30))),
                   (FL, Vector((KERF_GAP, 0, 0)))):
        key_loc(b["pivot"], f0, b["home"] + off)
        key_loc(b["pivot"], mid, b["home"])
        ease(b["pivot"])
    key_loc(AL["pivot"], f0, AL["home"])

    # ----------------------------------------------------- by hand, not CNC
    f0, f1 = shot("handwork", 5)
    vis_all(ALL_P, f0, True)
    key_vis(rig["plug"], f0, True)
    # looking aft and down from inside the cavity at its aft wall, which is
    # where the bore breaks through. The old framing sat outside the hull
    # looking at a blank deck - there was nothing there to see.
    _t = (0.40, 0, 0.045)
    cam_move(f0, f1, _t, 6, 30, 0.62, _t, -26, 46, 0.55)
    caption(f0, f1, "then the part no router can reach",
            "a 3-axis cutter only reaches what it can see straight down - the "
            "conduit breakthrough into the cavity is cut by hand")
    key_vis(rig["plug"], f0 + int(2.6 * FPS), False)
