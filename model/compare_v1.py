"""
compare_v1.py - V1 and V2, side by side, to the same scale.

    blender -b model/efoil_v2.blend --python model/compare_v1.py -- [--res 1800]

V2 comes out of the model. V1 comes out of Derek's own Onshape export, kept
in docs/v1/stl/ - 32 parts, the whole as-built assembly: XPS board, both
printed enclosures, gaskets, lid, hardpoints, wood blocking, mast mount.

TWO THINGS HAVE TO BE RECONCILED before the two can share a frame:

  units        the STLs are millimetres and this scene is metres, so a 1.6 m
               board imports as a 1.6 KILOMETRE one
  orientation  V1's length runs along Y and V2's along X

ALIGNED AT THE MAST, not at the tail. The mast axis is the functional datum
on a foil board - it is what sets where the rider stands and how the board
trims - so lining the two up there makes the comparison mean something.
Aligning tails would just be a drawing convention.

Writes renders/compare/ : plan, side elevation, and a three-quarter view.
"""

import bpy
import glob
import io
import math
import os
import sys
from mathutils import Vector, Quaternion

BLEND = bpy.data.filepath
ROOT = os.path.dirname(os.path.dirname(BLEND)) if BLEND else os.getcwd()
MODEL = os.path.join(ROOT, "model")
STL = os.path.join(ROOT, "docs", "v1", "stl")
OUT = os.path.join(ROOT, "renders", "compare")

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def _arg(f, d):
    return argv[argv.index(f) + 1] if f in argv else d


RES = int(_arg("--res", "1800"))
SAMPLES = int(_arg("--samples", "24"))
GAP = 0.12                       # daylight between the two boards, metres
MM = 0.001

scene = bpy.context.scene
scene.render.resolution_x = RES
scene.render.resolution_y = int(RES * 9 / 16)
scene.render.resolution_percentage = 100


# ------------------------------------------------------------------ helpers
def show_all():
    for c in bpy.data.collections:
        c.hide_viewport = c.hide_render = False

    def walk(lc):
        lc.hide_viewport = lc.exclude = False
        for ch in lc.children:
            walk(ch)
    walk(bpy.context.view_layer.layer_collection)
    for o in bpy.data.objects:
        o.hide_viewport = o.hide_render = False
        try:
            o.hide_set(False)
        except RuntimeError:
            pass


def bake_all():
    """Same reason as the animation: these parts carry chains of booleans
    whose operands carry their own, and reading that live stack is not
    reliable. Flatten once."""
    show_all()
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    for o in list(bpy.data.objects):
        if o.type != 'MESH' or not o.modifiers:
            continue
        try:
            me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
        except Exception:
            continue
        o.modifiers.clear()
        o.data = me
    bpy.context.view_layer.update()


def bounds(objs):
    lo = Vector((1e18,) * 3)
    hi = Vector((-1e18,) * 3)
    for o in objs:
        if o.type not in ('MESH', 'FONT'):
            continue
        if o.type == 'MESH' and not len(o.data.vertices):
            continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            lo = Vector((min(lo.x, w.x), min(lo.y, w.y), min(lo.z, w.z)))
            hi = Vector((max(hi.x, w.x), max(hi.y, w.y), max(hi.z, w.z)))
    return lo, hi


def look_at(eye, target):
    return (Vector(eye) - Vector(target)).normalized().to_track_quat('Z', 'Y')


# ============================================================ V2 first
print("baking V2...")
bake_all()
exec(io.open(os.path.join(MODEL, "anim_materials.py"), encoding="utf-8").read())
build_materials()

V2 = [o for o in bpy.data.objects if o.type == 'MESH']
# The build-time scaffolding is not part of the board. Cutters, voids and the
# machining stand-ins would all render if left on.
DROP = ("_cut", "MachStack_", "BlankLayer_", "CoreHalf_", "Hull_", "Foil_")
V2 = [o for o in V2 if not any(t in o.name for t in DROP)]
for o in bpy.data.objects:
    if o.type == 'MESH' and o not in V2:
        o.hide_render = o.hide_viewport = True
# the hull IS the board; the machining pieces it was cut from are not
for nm in ("Hull",):
    h = bpy.data.objects.get(nm)
    if h:
        h.hide_render = h.hide_viewport = False
        if h not in V2:
            V2.append(h)

v2_lo, v2_hi = bounds(V2)
print("  V2 bounds", tuple(round(v, 3) for v in v2_lo),
      tuple(round(v, 3) for v in v2_hi))

# V2's mast axis, from the plate the mast bolts to
mp = bpy.data.objects.get("MastPlate_Alu")
V2_MAST_X = ((bounds([mp])[0].x + bounds([mp])[1].x) / 2) if mp else 0.34


# ============================================================ then V1
print("importing V1...")
imp = getattr(bpy.ops.wm, "stl_import", None) or bpy.ops.import_mesh.stl
before = set(bpy.data.objects)
for f in sorted(glob.glob(os.path.join(STL, "*.stl"))):
    imp(filepath=f)
V1 = [o for o in bpy.data.objects if o not in before]
MAST_PARTS = [o for o in V1 if "Mast Mount" in o.name]
print("  %d parts" % len(V1))

# --- a parent to carry units, rotation and placement in one transform
piv = bpy.data.objects.new("V1_Root", None)
scene.collection.objects.link(piv)
for o in V1:
    o.parent = piv

# millimetres -> metres, and V1's length (Y) onto V2's length (X).
# -90 about Z maps (x, y) -> (y, -x).
piv.scale = (MM, MM, MM)
piv.rotation_mode = 'QUATERNION'
piv.rotation_quaternion = Quaternion((0, 0, 1), math.radians(-90))
bpy.context.view_layer.update()

v1_lo, v1_hi = bounds(V1)
mast = MAST_PARTS
board = [o for o in V1 if "Foam Board" in o.name]
if mast:
    m_lo, m_hi = bounds(mast)
    V1_MAST_X = (m_lo.x + m_hi.x) / 2
else:
    V1_MAST_X = (v1_lo.x + v1_hi.x) / 2

# The mast has to end up at the SAME x as V2's, and the board sitting on
# z = 0 like V2's does. If the nose came out at the low-x end, spin it.
b_lo, b_hi = bounds(board or V1)
if mast and V1_MAST_X > (b_lo.x + b_hi.x) / 2:
    piv.rotation_quaternion = Quaternion((0, 0, 1), math.radians(90))
    bpy.context.view_layer.update()
    v1_lo, v1_hi = bounds(V1)
    m_lo, m_hi = bounds(mast)
    V1_MAST_X = (m_lo.x + m_hi.x) / 2
    b_lo, b_hi = bounds(board or V1)

# V2 gets a root as well. One transform per board is what makes it possible
# to re-lay them out per shot - side by side for a plan view, stacked for an
# elevation - instead of nudging 200 objects each time.
V2_ROOT = bpy.data.objects.new("V2_Root", None)
scene.collection.objects.link(V2_ROOT)
for o in V2:
    if o.parent is None:
        o.parent = V2_ROOT
bpy.context.view_layer.update()

# align the mast, and stand V1 on z = 0 the way V2 already is
piv.location = (V2_MAST_X - V1_MAST_X, -((b_lo.y + b_hi.y) / 2), -b_lo.z)
bpy.context.view_layer.update()
V1_HALF = (bounds(V1)[1].y - bounds(V1)[0].y) / 2
V2_HALF = (bounds(V2)[1].y - bounds(V2)[0].y) / 2
V1_HOME = Vector(piv.location)


def layout(mode):
    """SIDE BY SIDE for plan and three-quarter; STACKED for the elevation.

    An elevation of two boards sitting side by side is degenerate - the near
    one simply hides the far one. Stacking them in Z is the only way that
    view says anything, and thickness is the whole reason to draw it.
    """
    if mode == "stack":
        piv.location = V1_HOME + Vector((0, 0, 0.34))
        V2_ROOT.location = (0, 0, 0)
    else:
        piv.location = V1_HOME + Vector((0, -(V1_HALF + GAP / 2), 0))
        V2_ROOT.location = (0, V2_HALF + GAP / 2, 0)
    bpy.context.view_layer.update()
    for lb, anchor in LABEL_ANCHORS:
        bx = bounds(anchor)
        lb.location = (bx[0].x - 0.11,
                       (bx[0].y + bx[1].y) / 2,
                       (bx[0].z + bx[1].z) / 2 if mode == "stack" else 0.0)
        lb.rotation_euler = ((math.pi / 2, 0, 0) if mode == "stack"
                             else (0, 0, 0))
    bpy.context.view_layer.update()


# The mount has served its purpose as the alignment datum. It is a 760 mm
# stub with no wings, and V2's foil is not being shown either, so out it goes.
for _o in MAST_PARTS:
    _o.hide_render = _o.hide_viewport = True
    if _o in V1:
        V1.remove(_o)


# ------------------------------------------------------------ V1 materials
def mat(name, rgba, rough=0.6, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgba
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


# Deliberately muted. V2 is the one being proposed, so it keeps its colour;
# V1 reads as the reference it is.
M1 = dict(
    board=mat("V1_board", srgb("#C9CBC8"), rough=0.75),
    printed=mat("V1_printed", srgb("#4A5058"), rough=0.62),
    gasket=mat("V1_gasket", srgb("#101215"), rough=0.8),
    cells=mat("V1_cells", srgb("#1D9E6B"), rough=0.45),
    metal=mat("V1_metal", srgb("#B9BEC4"), rough=0.3, metal=1.0),
    wood=mat("V1_wood", srgb("#B08A54"), rough=0.8),
    esc=mat("V1_esc", srgb("#23262B"), rough=0.5),
    fuse=mat("V1_fuse", srgb("#B8410E"), rough=0.5),
)
for o in V1:
    n = o.name
    k = ("board" if "Foam Board" in n else
         "gasket" if "Gasket" in n else
         "cells" if ("Battery" in n and "Wall" not in n and "Plate" not in n) else
         "esc" if n.endswith("ESC") or "BMS" in n else
         "fuse" if "Fuse" in n else
         "metal" if ("Mast Mount" in n or "Plate" in n) else
         "wood" if "Wood Blocking" in n else
         "printed")
    o.data.materials.clear()
    o.data.materials.append(M1[k])


# ------------------------------------------------------------------- stage
world = bpy.data.worlds.new("CmpWorld")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (.045, .05, .06, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 2.6

CTR = (bounds(V1 + V2)[0] + bounds(V1 + V2)[1]) / 2
TGT = (CTR.x, CTR.y, CTR.z)


def add_light(nm, e, loc, size=5.0):
    d = bpy.data.lights.new(nm, 'AREA')
    d.energy = e
    d.size = size
    o = bpy.data.objects.new(nm, d)
    scene.collection.objects.link(o)
    o.location = loc
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = look_at(loc, TGT)
    return o


add_light("K", 1400, (CTR.x + 1.6, CTR.y - 2.4, 3.4), 5.0)
add_light("F", 420, (CTR.x - 2.0, CTR.y - 1.6, 1.4), 6.0)
add_light("R", 700, (CTR.x + 0.2, CTR.y + 3.0, 2.0), 5.0)

cam_d = bpy.data.cameras.new("Cmp")
cam_d.clip_start, cam_d.clip_end = 0.05, 200
CAM = bpy.data.objects.new("Cmp", cam_d)
scene.collection.objects.link(CAM)
scene.camera = CAM
CAM.rotation_mode = 'QUATERNION'

scene.render.engine = 'BLENDER_EEVEE'
scene.render.use_persistent_data = True
for a, v in (("taa_render_samples", SAMPLES), ("use_fast_gi", False),
             ("use_raytracing", False), ("shadow_ray_count", 1)):
    try:
        setattr(scene.eevee, a, v)
    except (AttributeError, TypeError):
        pass
scene.view_settings.look = 'None'
for vt in ('Khronos PBR Neutral', 'Standard'):
    try:
        scene.view_settings.view_transform = vt
        break
    except TypeError:
        continue
scene.render.image_settings.media_type = 'IMAGE'
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.compression = 15


def shoot(name, az, el, margin=1.08, ortho=False, lens=55.0):
    """Frame from the bounding box PROJECTED ONTO THE CAMERA'S OWN AXES.

    Fitting to world x/y/z instead is what put both boards half out of frame:
    a plan view does not care how deep the board is, and ortho_scale is the
    frame's WIDTH, so a subject that is tall in screen terms has to be sized
    through the aspect ratio to fit at all.
    """
    lo, hi = bounds(V1 + V2 + LABELS)
    ctr = (lo + hi) / 2
    a_, e_ = math.radians(az), math.radians(el)
    dirv = Vector((math.cos(e_) * math.cos(a_), math.cos(e_) * math.sin(a_),
                   math.sin(e_)))
    q = look_at(ctr + dirv, ctr)
    right, up = q @ Vector((1, 0, 0)), q @ Vector((0, 1, 0))
    corners = [Vector((x, y, z)) for x in (lo.x, hi.x)
               for y in (lo.y, hi.y) for z in (lo.z, hi.z)]
    w = 2 * max(abs((c - ctr).dot(right)) for c in corners)
    h = 2 * max(abs((c - ctr).dot(up)) for c in corners)
    aspect = scene.render.resolution_x / scene.render.resolution_y
    if ortho:
        cam_d.type = 'ORTHO'
        cam_d.ortho_scale = max(w, h * aspect) * margin
        dist = max(w, h) + 10.0
    else:
        cam_d.type = 'PERSP'
        cam_d.lens = lens
        hw, hh = 18.0 / lens, 10.125 / lens
        dist = max(w / 2 / hw, h / 2 / hh) * margin
    eye = ctr + dirv * dist
    CAM.location = eye
    CAM.rotation_quaternion = look_at(eye, ctr)
    os.makedirs(OUT, exist_ok=True)
    scene.render.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True)
    print("  wrote %s  (%.2f x %.2f m in frame)" % (name, w, h))


def label(text, x, y, size=0.085):
    c = bpy.data.curves.new("lbl", type='FONT')
    c.body = text
    c.size = size
    c.align_x = 'CENTER'
    o = bpy.data.objects.new("Lbl_" + text, c)
    scene.collection.objects.link(o)
    o.location = (x, y, 0.0)
    m = bpy.data.materials.new("lbl_" + text)
    m.use_nodes = True
    bs = m.node_tree.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value = (0.9, 0.92, 0.95, 1)
    bs.inputs["Emission Color"].default_value = (0.9, 0.92, 0.95, 1)
    bs.inputs["Emission Strength"].default_value = 1.4
    o.data.materials.append(m)
    LABELS.append(o)
    return o


# Two characters, not a spec sheet. The long version was a metre of text at
# the tail of a 1.4 m board and framed itself straight off the edge; the
# numbers belong in the caption, not in the render.
LABELS = []
LABEL_ANCHORS = [(label("V1", 0, 0, size=0.095), V1),
                 (label("V2", 0, 0, size=0.095), V2)]

print("rendering...")
layout("side_by_side")
shoot("plan", -90.0, 89.0, margin=1.08, ortho=True)
shoot("iso", -62.0, 26.0, margin=1.16)
layout("stack")
shoot("side", -90.0, 0.0, margin=1.10, ortho=True)
print("done ->", OUT)
