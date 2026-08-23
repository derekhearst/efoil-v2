"""
animate_build.py - renders the V2 build sequence as an animation.

Every frame comes out of model/efoil_v2.blend, so this cannot drift from the
model the way a hand-drawn illustration would. Change a parameter, rebuild the
model, re-run this, and the animation shows the new board.

    blender -b model/efoil_v2.blend --python model/animate_build.py -- [opts]

    --preview     640x360, every 3rd frame - for checking choreography
    --res 1600    long edge in pixels (default 1600)
    --fps 30
    --shot NAME   render one shot only (see the shot list it prints)
    --stills      one PNG per shot instead of the animation - the fastest way
                  to check choreography, ~15 s for the lot
    --png         write a PNG sequence too, and encode from that. Slower: PNG
                  compression costs about as much as the render itself
    --samples N   EEVEE TAA samples (default 12; there is no motion blur or
                  depth of field here, so they only buy edge antialiasing)
    --dry         build the timeline and print the shot list, render nothing

Output lands in renders/build/ as a PNG sequence, plus build.mp4 if ffmpeg is
on PATH. renders/ is gitignored - it is build output, not source.

WHY THE MESHES GET BAKED FIRST: every part in this file carries a chain of
boolean modifiers whose operands carry their own. Reading that live stack is
exactly what produced two bogus check failures in the model, and re-evaluating
it on every one of ~3000 frames would be slow as well as unreliable.
bake_all() flattens the whole scene to static meshes once, up front.
Everything after that is honest geometry that renders the same every time.
"""

import bpy
import bmesh
import math
import io
import os
import subprocess
import sys
from mathutils import Vector, Quaternion, Matrix
from mathutils.bvhtree import BVHTree

MM = 0.001
BLEND = bpy.data.filepath
ROOT = os.path.dirname(os.path.dirname(BLEND)) if BLEND else os.getcwd()
OUT = os.path.join(ROOT, "renders", "build")

# ----------------------------------------------------------------- args
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
PREVIEW = "--preview" in argv
STILLS = "--stills" in argv


def _arg(flag, default):
    return argv[argv.index(flag) + 1] if flag in argv else default


RES = int(_arg("--res", "640" if PREVIEW else "1600"))
FPS = int(_arg("--fps", "24"))          # 24 is plenty for this, and 20%
                                       # fewer frames than 30
SAMPLES = int(_arg("--samples", "12"))
PNGS = "--png" in argv
ONLY = _arg("--shot", None)

scene = bpy.context.scene
# These four lines went missing in a rewrite, so --res and --fps were dead
# flags for the whole of the first render: it ran at the .blend's own
# 1920x1080 no matter what was asked for. It came out HIGHER than requested,
# which is exactly why nothing complained.
scene.render.resolution_x = RES
scene.render.resolution_y = int(RES * 9 / 16)
scene.render.resolution_percentage = 100
scene.render.fps = FPS


# ================================================================== helpers
def obj(name):
    return bpy.data.objects.get(name)


def by_prefix(*prefixes):
    return sorted((o for o in bpy.data.objects
                   if any(o.name.startswith(p) for p in prefixes)),
                  key=lambda o: o.name)


def coll_objs(name):
    c = bpy.data.collections.get(name)
    return list(c.objects) if c else []


def show_everything():
    """Un-hide the world so the depsgraph actually evaluates it for baking."""
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
    """Flatten every modifier stack to a real mesh. See the module docstring."""
    show_everything()
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    n = 0
    for o in list(bpy.data.objects):
        if o.type != 'MESH' or not o.modifiers:
            continue
        try:
            me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
        except Exception as e:
            print("  bake skipped", o.name, e)
            continue
        old = o.data
        o.modifiers.clear()
        o.data = me
        if old.users == 0:
            bpy.data.meshes.remove(old)
        n += 1
    bpy.context.view_layer.update()
    print("  baked %d objects to static meshes" % n)


def world_bounds(objs):
    lo = Vector((1e9, 1e9, 1e9))
    hi = Vector((-1e9, -1e9, -1e9))
    for o in objs:
        if o is None or o.type != 'MESH' or not len(o.data.vertices):
            continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            lo = Vector((min(lo.x, w.x), min(lo.y, w.y), min(lo.z, w.z)))
            hi = Vector((max(hi.x, w.x), max(hi.y, w.y), max(hi.z, w.z)))
    return lo, hi


def box(name, lo, hi, material=None):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        v.co.x = lo[0] + (v.co.x + .5) * (hi[0] - lo[0])
        v.co.y = lo[1] + (v.co.y + .5) * (hi[1] - lo[1])
        v.co.z = lo[2] + (v.co.z + .5) * (hi[2] - lo[2])
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    scene.collection.objects.link(o)
    if material:
        o.data.materials.append(material)
    return o


def cyl(name, r, z0, z1, material=None, segments=40):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segments,
                          radius1=r, radius2=r, depth=z1 - z0)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, (z0 + z1) / 2))
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    scene.collection.objects.link(o)
    if material:
        o.data.materials.append(material)
    return o


def mat(name, rgba, rough=0.5, metal=0.0, emit=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgba
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = rgba
        b.inputs["Emission Strength"].default_value = emit
    if rgba[3] < 1.0:
        b.inputs["Alpha"].default_value = rgba[3]
        for attr, val in (("blend_method", 'BLEND'),
                          ("surface_render_method", 'BLENDED')):
            try:
                setattr(m, attr, val)
            except (AttributeError, TypeError):
                pass
    return m


# --------------------------------------------------------------- keyframes
def fcurves_of(o):
    """Blender 5 moved f-curves into slotted actions - action.fcurves is gone,
    and they now live under layers > strips > channelbag(slot)."""
    ad = o.animation_data if o else None
    if not ad or not ad.action:
        return []
    act = ad.action
    if hasattr(act, "fcurves"):
        return list(act.fcurves)
    slot = getattr(ad, "action_slot", None)
    out = []
    for layer in act.layers:
        for strip in layer.strips:
            try:
                cb = strip.channelbag(slot) if slot else None
            except Exception:
                cb = None
            if cb:
                out.extend(cb.fcurves)
    return out


def _const(o):
    for fc in fcurves_of(o):
        if fc.data_path in ("hide_viewport", "hide_render"):
            for kp in fc.keyframe_points:
                kp.interpolation = 'CONSTANT'


def key_vis(o, f, visible):
    """Keyframe on/off. CONSTANT interpolation - a part is there or it isn't."""
    if o is None:
        return
    o.hide_viewport = o.hide_render = not visible
    o.keyframe_insert("hide_viewport", frame=f)
    o.keyframe_insert("hide_render", frame=f)
    _const(o)


def vis_all(objs, f, visible):
    for o in objs:
        key_vis(o, f, visible)


def key_loc(o, f, v):
    if o is None:
        return
    o.location = Vector(v)
    o.keyframe_insert("location", frame=f)


def key_rot(o, f, q):
    if o is None:
        return
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = q
    o.keyframe_insert("rotation_quaternion", frame=f)


def key_roty(o, f, degrees):
    """Keyframe a rotation about Y as an EULER, not a quaternion.

    Quaternion components animate on four independent f-curves, so a bezier
    from identity (1,0,0,0) to a half turn (0,0,1,0) passes through
    (0.5,0,0.5,0) - magnitude 0.707. Blender builds the matrix from the raw
    quaternion, and a quaternion shorter than 1 IS a scale: the blank shrank
    to half size in the middle of its own flip, and everything downstream that
    read matrix_world got a garbage size out of it.
    """
    if o is None:
        return
    o.rotation_mode = 'XYZ'
    o.rotation_euler = (0.0, math.radians(degrees), 0.0)
    o.keyframe_insert("rotation_euler", frame=f)


def ease(o, path="location"):
    for fc in fcurves_of(o):
        if fc.data_path == path:
            for kp in fc.keyframe_points:
                if kp.co.x <= 1.5:
                    # The frame-1 pin is deliberately CONSTANT. Easing it made
                    # every part drift for minutes towards a fly-in that had
                    # not started yet - the reason the machined pieces sat
                    # 250 mm above their own stock.
                    continue
                kp.interpolation = 'BEZIER'
                kp.easing = 'EASE_IN_OUT'


HOME = {}


def home_of(o):
    if o.name not in HOME:
        HOME[o.name] = Vector(o.location)
    return HOME[o.name]


def fly_in(o, f0, f1, offset):
    """A part flies to its home position from home+offset. Home is wherever
    the model put it - nothing here invents a location."""
    if o is None:
        return
    h = home_of(o)
    key_vis(o, f0, True)
    key_loc(o, f0, h + Vector(offset))
    key_loc(o, f1, h)
    ease(o)


def park(o, f, offset):
    """Hold a part at an offset without revealing it yet."""
    if o is None:
        return
    key_loc(o, f, home_of(o) + Vector(offset))


# ------------------------------------------------------------------ camera
def look_at(eye, target):
    return (Vector(eye) - Vector(target)).normalized().to_track_quat('Z', 'Y')


def orbit_pos(target, az, el, dist):
    a, e = math.radians(az), math.radians(el)
    return Vector(target) + Vector((math.cos(e) * math.cos(a),
                                    math.cos(e) * math.sin(a),
                                    math.sin(e))) * dist


def cam_key(f, target, az, el, dist, lens=50.0):
    eye = orbit_pos(target, az, el, dist)
    key_loc(CAM, f, eye)
    key_rot(CAM, f, look_at(eye, target))
    CAM.data.lens = lens
    CAM.data.keyframe_insert("lens", frame=f)


def cam_move(f0, f1, t0, az0, el0, d0, t1, az1, el1, d1, lens=50.0, steps=10):
    """Interpolate the camera in ORBIT space, not world space - straight-line
    interpolation between two orbit positions cuts through the subject."""
    for i in range(steps + 1):
        u = i / steps
        t = Vector(t0).lerp(Vector(t1), u)
        cam_key(round(f0 + (f1 - f0) * u), t, az0 + (az1 - az0) * u,
                el0 + (el1 - el0) * u, d0 + (d1 - d0) * u, lens)
    ease(CAM)
    ease(CAM, "rotation_quaternion")


def fit(objs, lens=50.0, margin=1.18, spin=False):
    """Target and distance that actually FIT the subject, from its bounds.

    Hand-picked distances kept cropping the tops off things - the flip, and
    the board once the 890 mm of foil hung below it. spin=True frames the
    bounding SPHERE, for a subject that rotates through the shot.
    """
    lo, hi = world_bounds([o for o in objs if o])
    d = hi - lo
    ctr = (lo + hi) / 2
    hh = 10.125 / lens                       # half-height of a 16:9 frame
    hw = 18.0 / lens
    if spin:
        # the LONGEST edge, not the diagonal. A 1040 x 584 x 102 slab has a
        # 1.19 m diagonal but only ever presents 1.04 m as it turns, and
        # framing the diagonal pushed the camera far enough back to make the
        # blank a speck.
        return (ctr.x, ctr.y, ctr.z), max(d.x, d.y, d.z) / 2 / hh * margin
    return (ctr.x, ctr.y, ctr.z), max(max(d.x, d.y) / 2 / hw,
                                      d.z / 2 / hh) * margin


def cam_hold(f0, f1, target, az, el, dist, lens=50.0):
    cam_key(f0, target, az, el, dist, lens)
    cam_key(f1, target, az, el, dist, lens)


# ---------------------------------------------------------------- captions
CAP_D = 0.20        # metres in front of the camera. Far enough out to clear
                    # the near clip, close enough that no set piece - the CNC
                    # table especially - can ever get between text and lens.


def caption_backing():
    """A lower third. White text over the pale spoilboard was unreadable, and
    the frame is 16:9 with a 50 mm lens throughout, so the bar can be sized
    from the lens rather than eyeballed."""
    hw = (36 / 2) * CAP_D / 50.0
    hh = hw * 9 / 16
    b = box("CaptionBar", (-hw, -hh, -0.0002), (hw, -hh * 0.49, 0.0002),
            mat("A_bar", (0.03, 0.035, 0.045, 0.62), rough=1.0))
    b.parent = CAM
    b.location = (0, 0, -CAP_D - 0.0015)
    return b


CAPTIONS = []


def caption(f0, f1, title, sub=""):
    """Text parented to the camera, so it rides wherever the camera goes."""
    D = CAP_D
    for i, (body, size, dy, m) in enumerate(
            ((title, 0.0300 * D, -0.1450 * D, M_TEXT),
             (sub, 0.0155 * D, -0.1760 * D, M_TEXT_DIM))):
        if not body:
            continue
        c = bpy.data.curves.new("cap%d_%d" % (f0, i), type='FONT')
        c.body = body
        c.size = size
        c.align_x = 'LEFT'
        o = bpy.data.objects.new("Cap_%d_%d" % (f0, i), c)
        scene.collection.objects.link(o)
        o.data.materials.append(m)
        o.parent = CAM
        o.location = (-0.300 * D, dy, -D)
        key_vis(o, max(1, f0 - 1), False)     # <- or it is on screen from frame 1
        key_vis(o, f0, True)
        key_vis(o, f1, False)
        CAPTIONS.append(o)


# ============================================================ scene set-up
print("baking...")
bake_all()
exec(io.open(os.path.join(os.path.dirname(BLEND or "."), "anim_materials.py"),
             encoding="utf-8").read())
build_materials()
exec(io.open(os.path.join(os.path.dirname(BLEND or "."), "anim_machining.py"),
             encoding="utf-8").read())

# --- everything starts hidden; each shot turns on what it needs
ALL_PARTS = [o for o in bpy.data.objects if o.type == 'MESH']
for o in ALL_PARTS:
    key_vis(o, 1, False)

M_TEXT = mat("A_text", (0.96, 0.96, 0.94, 1), emit=1.6)
M_TEXT_DIM = mat("A_textdim", (0.62, 0.66, 0.70, 1), emit=1.0)
M_WASTE = mat("A_waste", (0.74, 0.70, 0.62, 1), rough=0.95)
M_TOOL = mat("A_tool", (0.20, 0.21, 0.24, 1), rough=0.30, metal=0.9)
M_FLUTE = mat("A_flute", (0.72, 0.74, 0.78, 1), rough=0.22, metal=1.0)
M_TABLE = mat("A_table", (0.17, 0.16, 0.15, 1), rough=0.9)
M_GLUE = mat("A_glue", (0.90, 0.72, 0.25, 1), rough=0.6)

# --- camera
cam_data = bpy.data.cameras.new("BuildCam")
cam_data.lens = 50
cam_data.clip_start = 0.05
cam_data.clip_end = 100
CAM = bpy.data.objects.new("BuildCam", cam_data)
scene.collection.objects.link(CAM)
scene.camera = CAM
CAM.rotation_mode = 'QUATERNION'

# --- lighting: key / fill / rim, plus a soft world
world = bpy.data.worlds.new("BuildWorld")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.045, 0.050, 0.060, 1)
# carries the ambient fill that use_fast_gi used to provide, for nothing
world.node_tree.nodes["Background"].inputs[1].default_value = 2.6


def add_light(name, kind, energy, loc, size=3.0, rot=(0, 0, 0)):
    d = bpy.data.lights.new(name, kind)
    d.energy = energy
    if kind == 'AREA':
        d.size = size
    if kind == 'SUN':
        d.angle = math.radians(6)
    o = bpy.data.objects.new(name, d)
    scene.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = rot
    return o


KEY = add_light("Key", 'AREA', 900, (1.6, -2.2, 3.0), size=4.0)
KEY.rotation_quaternion = look_at(KEY.location, (0.7, 0, 0.09))
KEY.rotation_mode = 'QUATERNION'
FILL = add_light("Fill", 'AREA', 260, (-1.8, -1.6, 1.2), size=5.0)
FILL.rotation_mode = 'QUATERNION'
FILL.rotation_quaternion = look_at(FILL.location, (0.7, 0, 0.09))
RIM = add_light("Rim", 'AREA', 420, (0.4, 3.0, 1.6), size=4.0)
RIM.rotation_mode = 'QUATERNION'
RIM.rotation_quaternion = look_at(RIM.location, (0.7, 0, 0.09))
# Everything in step 7 is fitted from BELOW, and the underside of the board
# faces away from all three lights above. Keyframed off elsewhere so it does
# not flatten the rest of the sequence.
UNDER = add_light("Under", 'AREA', 0.0, (0.45, -1.1, -1.7), size=3.0)
UNDER.rotation_mode = 'QUATERNION'
UNDER.rotation_quaternion = look_at(UNDER.location, (0.35, 0, 0.0))

# --- render settings
scene.render.engine = 'BLENDER_EEVEE'
scene.render.film_transparent = False
# Keeps the engine's synced scene alive between frames instead of tearing it
# down and rebuilding it 2905 times. An EMPTY scene still cost 0.284 s a frame
# without this - almost the entire per-frame budget was setup, not drawing.
scene.render.use_persistent_data = True
# STRAIGHT TO VIDEO. The first pass wrote 2905 PNGs at 1920x1080 and then ran
# ffmpeg over them, and the profiling was unambiguous: a warm frame RENDERS in
# 0.45 s and took 0.95 s to render-and-write. Half the wall clock was PNG
# compression, for an intermediate that gets deleted. Encoding H.264 inline
# costs almost nothing by comparison. --png restores the frame sequence when
# you actually want to inspect or re-cut frames.
if PNGS:
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.compression = 15    # was effectively maximum
    scene.render.filepath = os.path.join(OUT, "f_")
else:
    # Blender 5 gates the video formats behind media_type - file_format on
    # its own only offers stills, and setting FFMPEG without this raises.
    scene.render.image_settings.media_type = 'VIDEO'
    scene.render.image_settings.file_format = 'FFMPEG'
    ff = scene.render.ffmpeg
    ff.format = 'MPEG4'
    ff.codec = 'H264'
    ff.constant_rate_factor = 'HIGH'
    ff.ffmpeg_preset = 'GOOD'
    ff.gopsize = 12
    scene.render.use_file_extension = False
    scene.render.filepath = os.path.join(ROOT, "renders", "build.mp4")
# RENDER COST. The first pass took 57 minutes for 121 seconds on a 4070 Ti,
# which is far too slow for what is on screen. GPU was never the problem -
# gpu.platform.renderer_get() reports the 4070 Ti - it was EEVEE Next
# settings: the .blend ships 64 TAA samples and screen-space fast GI on, and
# every sample is a full raster pass that re-resolves shadows.
#
# There is no motion blur and no depth of field here, so TAA samples buy
# nothing but edge antialiasing and soft-shadow convergence. A dozen is
# plenty. Fast GI is replaced by an ambient world level, which for flat
# technical shading is indistinguishable and free.
for _a, _v in (("taa_render_samples", 4 if PREVIEW else SAMPLES),
               ("use_fast_gi", False),
               ("use_raytracing", False),
               ("use_shadows", True),
               ("shadow_ray_count", 1),
               ("shadow_step_count", 4),
               ("use_gtao", True),
               ("use_bloom", False)):
    try:
        setattr(scene.eevee, _a, _v)
    except (AttributeError, TypeError):
        pass
scene.view_settings.look = 'None'
for _vt in ('Khronos PBR Neutral', 'Standard'):
    try:
        scene.view_settings.view_transform = _vt
        break
    except TypeError:
        continue


# ====================================================== named part groups
MACH = [obj("MachStack_Aft_Lower"), obj("MachStack_Aft_Upper"),
        obj("MachStack_Fwd_Lower"), obj("MachStack_Fwd_Upper")]
MACH = [m for m in MACH if m]
LOWERS = [obj("MachStack_Aft_Lower"), obj("MachStack_Fwd_Lower")]
UPPERS = [obj("MachStack_Aft_Upper"), obj("MachStack_Fwd_Upper")]
LOWERS = [m for m in LOWERS if m]
UPPERS = [m for m in UPPERS if m]

HULL = obj("Hull")
DENSE = obj("DenseFoam_Block")
HARD = coll_objs("Hardpoints")
RIMSEG = by_prefix("RimSeg_")
RIMRING = obj("RimRing_ASA")
LID = obj("Lid")
SEAL = obj("Seal")
HBOLT = by_prefix("HatchBolt_")
HNUT = by_prefix("HatchNut_")
PADS = coll_objs("Deck pad")
FOIL = coll_objs("Foil")

CELLS = obj("Pack_Cells")
HOLD_B = obj("CellHolder_Btm")
HOLD_T = obj("CellHolder_Top")
WRAP = obj("Pack_Wrap")
BMS, ESC, FUSE = obj("BMS"), obj("ESC"), obj("Fuse")
ELEC_MISC = (by_prefix("BayGland_") + [obj("PowerButton"), obj("ChargePort"),
                                       obj("ChargePortCap"), obj("Conduit")])
ELEC_MISC = [o for o in ELEC_MISC if o]

MODPIECE = by_prefix("ModPiece_")
MODFLOOR = obj("Mod_Floor")
MODLID = obj("Mod_Lid")
MODSEAL = obj("Mod_Seal")
MODVENT = obj("Mod_Vent")
MODINS = by_prefix("ModInsert_")

BOARD_DONE = ([HULL] + HARD + [DENSE] + RIMSEG + [LID, SEAL] + HBOLT + HNUT
              + PADS)
BOARD_DONE = [o for o in BOARD_DONE if o]

# Buried parts. Once the hull is on they are inside it, and leaving them
# switched on put a tan H-80 patch through the deck at the tail - the leash
# hardpoint, poking out of a board it is supposed to be laminated inside.
BURIED = [o for o in ([DENSE, obj("LeashHardpoint")]
                      + by_prefix("MastInsert_", "HandleIns")) if o]
BOARD_FINISHED = [o for o in BOARD_DONE if o not in BURIED]

# board framing target
_lo, _hi = world_bounds([HULL] if HULL else MACH)
CTR = ((_lo + _hi) / 2)
CTR_T = (CTR.x, CTR.y, CTR.z)
print("  board centre", tuple(round(v, 3) for v in CTR_T))


# =================================================== machining rig (built)
def world_bvh(p):
    """A BVH of the part's REAL mesh, in world space.

    Object.ray_cast() reads the evaluated mesh, and an object hidden by a
    visibility keyframe has none - it is dropped from the depsgraph entirely.
    Everything here is baked already, so the raw mesh is the final mesh and
    this sidesteps the whole question.
    """
    mw = p.matrix_world
    return BVHTree.FromPolygons([mw @ v.co for v in p.data.vertices],
                                [list(f.vertices) for f in p.data.polygons])


def surface_z(bvhs, x, y, z_from, default):
    """Where the finished surface actually is - so the tool rides real
    geometry instead of a guessed height."""
    best = None
    for t in bvhs:
        hit = t.ray_cast(Vector((x, y, z_from)), Vector((0, 0, -1)))
        if hit and hit[0] is not None:
            best = hit[0].z if best is None else max(best, hit[0].z)
    return default if best is None else best


# ================================================================== shots
F = 1
SHOT_MARKS = []


def shot(name, seconds):
    global F
    f0 = F
    f1 = F + int(seconds * FPS)
    F = f1
    SHOT_MARKS.append((name, f0, f1))
    return f0, f1


def pin_home(objs):
    """Hold every part at its home position from frame 1, with CONSTANT
    interpolation so it does not drift towards a fly-in that starts minutes
    later. Without this the FIRST location keyframe a part receives - normally
    the start of its fly-in, off in space - extends backwards over everything
    before it, and the finished board in the opening shot is exploded."""
    for o in objs:
        if o is None or o.type not in ('MESH', 'FONT', 'EMPTY'):
            continue
        key_loc(o, 1, home_of(o))
        if o.type == 'EMPTY':
            # the blank pivots carry the flips; without a pinned zero at frame
            # 1 the first flip keyframe reaches back over every shot before it
            # and the blanks start the film half turned over
            key_roty(o, 1, 0.0)
        for fc in fcurves_of(o):
            if fc.data_path in ("location", "rotation_euler",
                                "rotation_quaternion"):
                for kp in fc.keyframe_points:
                    if kp.co.x <= 1.5:
                        kp.interpolation = 'CONSTANT'


def build_timeline():
    caption_backing()
    RIG = build_blanks()
    pin_home(bpy.data.objects)

    # ---------------------------------------------------------- intro
    f0, f1 = shot("intro", 6)
    vis_all(BOARD_FINISHED, f0, True)
    cam_move(f0, f1, CTR_T, -55, 22, 2.5, CTR_T, -18, 30, 2.2)
    caption(f0, f1, "eFoil V2", "1400 x 560 x 167 mm  -  16S8P, 2304 Wh  -  two boards")
    vis_all(BOARD_FINISHED, f1, False)

    machining_shots(RIG)

    # ------------------------------------------------- the hardpoints
    f0, f1 = shot("hardpoints", 7)
    vis_all(MACH, f0, True)
    cam_move(f0, f1, (0.34, 0, 0.01), -120, -34, 1.05, (0.34, 0, 0.03), -55, 6, 1.30)
    for _f, _e in ((f0 - 1, 0.0), (f0 + 8, 700.0), (f1 - 8, 700.0), (f1, 0.0)):
        UNDER.data.energy = _e
        UNDER.data.keyframe_insert("energy", frame=_f)
    caption(f0, f1, "Step 7  -  hardpoints",
            "H-80 mast block, then a MACHINED 6061-T651 plate - blind M8, 0.25 mm true position")
    fly_in(DENSE, f0 + int(0.2 * FPS), f0 + int(2.0 * FPS), (0, 0, -0.25))
    for o in HARD:
        if o.name.startswith("MastPlate"):
            fly_in(o, f0 + int(1.6 * FPS), f0 + int(3.4 * FPS), (0, 0, -0.30))
        elif o.name.startswith("MastInsert"):
            fly_in(o, f0 + int(3.0 * FPS), f0 + int(4.2 * FPS), (0, 0, -0.14))
        elif o.name.startswith("MastBolt"):
            fly_in(o, f0 + int(4.0 * FPS), f0 + int(5.4 * FPS), (0, 0, -0.18))
        else:
            fly_in(o, f0 + int(4.6 * FPS), f0 + int(6.2 * FPS), (0, 0, 0.16))

    # --------------------------------------------------- the laminate
    f0, f1 = shot("laminate", 6)
    LAMINATE_F0 = f0
    vis_all(MACH + HARD + [DENSE], f0, True)
    cam_move(f0, f1, CTR_T, -45, 24, 2.4, CTR_T, -85, 30, 2.2)
    caption(f0, f1, "Phase 2  -  laminate",
            "biaxial carbon over the deck, glass below, bagged at 5-10 inHg")
    mid = f0 + int(3.0 * FPS)
    vis_all(MACH, mid, False)
    vis_all(BURIED, mid, False)
    key_vis(HULL, mid, True)

    # ------------------------------------------------ the rim ring
    f0, f1 = shot("rim", 7)
    key_vis(HULL, f0, True)
    vis_all(HARD, f0, True)
    vis_all(BURIED, f0, False)
    cam_move(f0, f1, (0.64, 0, 0.15), -70, 40, 1.35, (0.64, 0, 0.15), -20, 55, 1.15)
    caption(f0, f1, "the rim ring goes in DURING the cavity layup",
            "6 printed segments, dovetailed - captive M5 nuts already inside")
    ang = [(-0.22, -0.16), (-0.22, 0.16), (0.22, -0.16), (0.22, 0.16),
           (0, -0.26), (0, 0.26)]
    for i, s in enumerate(RIMSEG):
        dx, dy = ang[i % len(ang)]
        fly_in(s, f0 + int((0.3 + 0.25 * i) * FPS),
               f0 + int((2.6 + 0.25 * i) * FPS), (dx, dy, 0.22))

    # ----------------------------------------------------- the pack
    f0, f1 = shot("pack", 10)
    key_vis(HULL, f0, False)
    vis_all(HARD + [DENSE] + RIMSEG, f0, False)
    pk_t = world_bounds([o for o in (CELLS, HOLD_B, HOLD_T) if o])
    pk = ((pk_t[0] + pk_t[1]) / 2)
    pkc = (pk.x, pk.y, pk.z)
    cam_move(f0, f1, pkc, -60, 26, 0.85, pkc, 30, 34, 0.75)
    caption(f0, f1, "Phase 3  -  the pack",
            "16S8P. 128 cells in printed holders, 78 mm tall assembled - V1 measured 82")
    fly_in(HOLD_B, f0 + int(0.3 * FPS), f0 + int(1.8 * FPS), (0, 0, -0.20))
    fly_in(CELLS, f0 + int(1.8 * FPS), f0 + int(4.4 * FPS), (0, 0, 0.30))
    fly_in(HOLD_T, f0 + int(4.4 * FPS), f0 + int(6.0 * FPS), (0, 0, 0.26))
    fly_in(WRAP, f0 + int(6.4 * FPS), f0 + int(8.0 * FPS), (0, 0, 0.22))

    # --------------------------------------------------- the module
    f0, f1 = shot("module", 11)
    for o in (HOLD_B, CELLS, HOLD_T, WRAP):
        key_vis(o, f0, True)
    md = world_bounds([o for o in MODPIECE + [MODFLOOR, MODLID] if o])
    mc = (md[0] + md[1]) / 2
    mct = (mc.x, mc.y, mc.z)
    cam_move(f0, f1, mct, -55, 22, 1.15, mct, 25, 38, 1.0)
    caption(f0, f1, "Phase 4  -  the electronics module",
            "printed ASA walls on a 5052 floor - lifts out as one piece")
    fly_in(MODFLOOR, f0 + int(0.2 * FPS), f0 + int(1.6 * FPS), (0, 0, -0.22))
    for i, p in enumerate(MODPIECE):
        fly_in(p, f0 + int((1.4 + 0.2 * i) * FPS),
               f0 + int((3.2 + 0.2 * i) * FPS),
               (0.20 if "Fwd" in p.name else -0.20,
                0.16 if p.name.endswith("P") else -0.16, 0.05))
    for o, t in ((BMS, 3.6), (ESC, 4.0), (FUSE, 4.4)):
        fly_in(o, f0 + int(t * FPS), f0 + int((t + 1.6) * FPS), (0, 0, 0.28))
    for o in ELEC_MISC:
        fly_in(o, f0 + int(5.4 * FPS), f0 + int(6.8 * FPS), (-0.16, 0, 0))
    for o in MODINS:
        fly_in(o, f0 + int(6.6 * FPS), f0 + int(7.6 * FPS), (0, 0, 0.14))
    fly_in(MODSEAL, f0 + int(7.4 * FPS), f0 + int(8.4 * FPS), (0, 0, 0.18))
    fly_in(MODVENT, f0 + int(7.8 * FPS), f0 + int(8.8 * FPS), (-0.12, 0, 0))
    fly_in(MODLID, f0 + int(8.6 * FPS), f0 + int(10.2 * FPS), (0, 0, 0.24))

    # ---------------------------------------------- module into board
    f0, f1 = shot("install", 8)
    MODULE_ALL = ([o for o in [MODFLOOR, MODLID, MODSEAL, MODVENT] if o]
                  + MODPIECE + MODINS + [o for o in (BMS, ESC, FUSE, CELLS,
                                                     HOLD_B, HOLD_T, WRAP) if o]
                  + ELEC_MISC)
    vis_all(MODULE_ALL, f0, True)
    key_vis(HULL, f0, True)
    vis_all(HARD + RIMSEG, f0, True)
    vis_all(BURIED, f0, False)
    cam_move(f0, f1, (0.64, 0, 0.12), -75, 34, 1.7, (0.64, 0, 0.12), -25, 46, 1.5)
    caption(f0, f1, "Phase 5  -  install and close",
            "module drops in, 12 x M5 into the captive nuts, gasket compressed")
    for o in MODULE_ALL:
        h = home_of(o)
        key_loc(o, f0, h + Vector((0, 0, 0.34)))
        key_loc(o, f0 + int(3.0 * FPS), h)
        ease(o)
    fly_in(SEAL, f0 + int(3.0 * FPS), f0 + int(4.0 * FPS), (0, 0, 0.20))
    for o in HNUT:
        key_vis(o, f0 + int(3.4 * FPS), True)
    fly_in(LID, f0 + int(4.0 * FPS), f0 + int(5.6 * FPS), (0, 0, 0.26))
    for i, b in enumerate(HBOLT):
        fly_in(b, f0 + int((5.4 + 0.06 * i) * FPS),
               f0 + int((6.4 + 0.06 * i) * FPS), (0, 0, 0.12))

    # -------------------------------------------------------- fair and paint
    # The hull used to arrive already Whaler Blue at the laminate step, which
    # is several weekends early. It comes out of the bag as bare laminate now
    # and gets painted here, where the build guide puts it.
    f0, f1 = shot("paint", 6)
    vis_all(RIMSEG + [LID, SEAL] + HBOLT + HNUT + HARD, f0, True)
    vis_all(BURIED, f0, False)
    key_vis(HULL, f0, True)
    cam_move(f0, f1, CTR_T, -70, 30, 2.3, CTR_T, -28, 38, 2.1)
    caption(f0, f1, "fair, then paint",
            "TotalBoat Wet Edge, Classic Whaler Blue - rolled and tipped, "
            "above the waterline only")
    paint_keys(LAMINATE_F0, f0 + int(1.4 * FPS), f0 + int(3.4 * FPS))

    # -------------------------------------------------- the deck pad
    f0, f1 = shot("deckpad", 5)
    key_vis(HULL, f0, True)
    vis_all(RIMSEG + [LID, SEAL] + HBOLT + HNUT + HARD, f0, True)
    vis_all(BURIED, f0, False)
    cam_move(f0, f1, CTR_T, -40, 44, 2.2, CTR_T, -10, 60, 2.0)
    caption(f0, f1, "deck pad", "5.8 mm EVA, 3 pieces - one sheet does both boards")
    for i, p in enumerate(PADS):
        fly_in(p, f0 + int((0.4 + 0.5 * i) * FPS),
               f0 + int((2.2 + 0.5 * i) * FPS), (0, 0, 0.18))

    # ------------------------------------------------------- the foil
    f0, f1 = shot("foil", 7)
    vis_all(BOARD_FINISHED, f0, True)
    _t, _d = fit(BOARD_FINISHED + FOIL)
    cam_move(f0, f1, _t, -60, 4, _d, _t, -15, 16, _d * 0.94)
    caption(f0, f1, "the foil", "Gong X-Over V3, 85 alu mast  -  Flipsky 65161 on a 120KV")
    for i, p in enumerate(FOIL):
        fly_in(p, f0 + int((0.3 + 0.35 * i) * FPS),
               f0 + int((2.4 + 0.35 * i) * FPS), (0, 0, -0.45))

    # ------------------------------------------------------ finished
    f0, f1 = shot("final", 9)
    vis_all(BOARD_FINISHED + FOIL, f0, True)
    _t, _d = fit(BOARD_FINISHED + FOIL, margin=1.38)
    cam_move(f0, f1, _t, -20, 16, _d, _t, 320, 26, _d, steps=16)
    caption(f0, f1, "eFoil V2", "24.3 kg  -  91.8 L  -  $3,917 a board")


build_timeline()

scene.frame_start = 1
scene.frame_end = F
print("\nSHOTS")
for n, a, b in SHOT_MARKS:
    print("  %-16s %5d - %-5d  %5.1fs" % (n, a, b, (b - a) / FPS))
print("  TOTAL %d frames, %.1f s at %d fps" % (F, F / FPS, FPS))


# ================================================================== render
def render():
    if ONLY:
        m = [s for s in SHOT_MARKS if s[0] == ONLY]
        if not m:
            print("no such shot:", ONLY)
            return
        scene.frame_start, scene.frame_end = m[0][1], m[0][2]
    if STILLS:
        d = os.path.join(ROOT, "renders", "stills")
        os.makedirs(d, exist_ok=True)
        # video is the default output now, and a still is not a video
        scene.render.image_settings.media_type = 'IMAGE'
        scene.render.image_settings.file_format = 'PNG'
        scene.render.image_settings.compression = 15
        scene.render.use_file_extension = True
        for n, a, b in ([x for x in SHOT_MARKS if x[0] == ONLY] if ONLY
                        else SHOT_MARKS):
            scene.frame_set(a + (b - a) // 2)
            scene.render.filepath = os.path.join(d, "shot_%s_" % n)
            bpy.ops.render.render(write_still=True)
            print("  still:", n)
        return
    scene.frame_step = 3 if PREVIEW else 1
    if PNGS:
        os.makedirs(OUT, exist_ok=True)
    bpy.ops.render.render(animation=True)
    if PNGS:
        encode()
    else:
        print("  wrote", scene.render.filepath)


def encode():
    pat = os.path.join(OUT, "f_%04d.png")
    mp4 = os.path.join(ROOT, "renders", "build.mp4")
    try:
        subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS if not PREVIEW else FPS // 3),
                        "-start_number", str(scene.frame_start), "-i", pat,
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                        "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", mp4],
                       check=True, capture_output=True)
        print("  wrote", mp4)
    except Exception as e:
        print("  ffmpeg failed, PNGs are in", OUT, e)


if "--dry" not in argv:
    render()
