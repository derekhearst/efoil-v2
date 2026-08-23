"""
anim_materials.py - the look of the build animation.

exec()'d from animate_build.py, so it shares that module's namespace and can
use its helpers directly. Kept separate only because it is a self-contained
job: nothing in here knows anything about the timeline.

TWO RULES:

1. NOTHING IS TRANSPARENT. The model deliberately renders the deck pads and
   some shells see-through so the splits are visible while designing. That is
   the wrong choice for a build film - a part you can see through does not
   look like a part you are holding. Every material gets Alpha 1.

2. COLOURS ARE GIVEN IN sRGB. Setting a Principled Base Color from Python
   writes a LINEAR value, so typing 0.0, 0.78, 0.88 for #00C8E1 gets you a
   noticeably different, washed-out colour. srgb() does the conversion the UI
   would have done.

The board colour is measured, not guessed: TotalBoat publishes no hex for
Classic Whaler Blue, but every Wet Edge colour swatch on their CDN is the
paint colour behind a photo of the can. Sampling five others whose names
leave no doubt - Fire Red (208,19,26), Black (0,0,0), Flag Blue (1,30,64),
Fighting Lady Yellow, Bristol Beige - confirms the background IS the colour.
Classic Whaler Blue reads #00C8E1.
"""

import bpy


def srgb(h, a=1.0):
    """'#00C8E1' -> linear RGBA, the conversion the colour picker does."""
    h = h.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (out[0], out[1], out[2], a)


# --------------------------------------------------------------- the palette
WHALER_BLUE = "#00C8E1"        # TotalBoat Wet Edge, Classic Whaler Blue
PAL = dict(
    paint=WHALER_BLUE,
    eps="#F2F0EA",             # expanded polystyrene, faintly warm white
    eps_cut="#EAE7DE",         # a freshly machined face is duller than a skin
    divinycell="#C8A46A",      # H-80, the tan structural foam
    alu="#C9CDD2",
    asa="#2E3238",             # printed shells
    asa_lid="#3A4048",
    carbon="#1A1D22",
    cell="#1D9E6B",            # 21700 wrap
    wrap="#14202C",
    nickel="#B8BDC4",
    seal="#101215",            # EPDM
    steel="#A8ADB5",
    pcb="#0E5233",
    esc="#23262B",
    fuse="#B8410E",
    stock_al="#B4B8BE",        # 6061 mill finish, before it is cut
)


def _tree(m):
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (400, 0)
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(b.outputs["BSDF"], out.inputs["Surface"])
    return nt, b


def _set(b, **kw):
    names = dict(base="Base Color", rough="Roughness", metal="Metallic",
                 ior="IOR", coat="Coat Weight", coat_r="Coat Roughness",
                 sheen="Sheen Weight", spec="Specular IOR Level")
    for k, v in kw.items():
        n = names.get(k, k)
        if n in b.inputs:
            b.inputs[n].default_value = v


def _noise_bump(nt, b, scale, strength, detail=2.0, rough=0.5, coord="Object"):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-800, -300)
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.location = (-600, -300)
    n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = detail
    n.inputs["Roughness"].default_value = rough
    bump = nt.nodes.new("ShaderNodeBump")
    bump.location = (-300, -300)
    bump.inputs["Strength"].default_value = strength
    nt.links.new(tc.outputs[coord], n.inputs["Vector"])
    nt.links.new(n.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return n, bump


# ------------------------------------------------------------------- looks
def look_paint(m):
    """High-gloss one-part polyurethane. Rolled and tipped by hand, so it gets
    a little orange peel - a mirror-perfect finish would look like plastic."""
    nt, b = _tree(m)
    _set(b, base=srgb(PAL["paint"]), rough=0.13, metal=0.0,
         coat=0.55, coat_r=0.09)
    _noise_bump(nt, b, 55.0, 0.05, detail=2.0)


def look_eps(m, shade="eps"):
    """Bead foam. The bump is what sells it - EPS is visibly made of beads,
    and a machined face is a field of cut half-beads."""
    nt, b = _tree(m)
    _set(b, base=srgb(PAL[shade]), rough=0.92, metal=0.0, spec=0.25)
    _noise_bump(nt, b, 260.0, 0.22, detail=3.0, rough=0.6)


def look_divinycell(m):
    nt, b = _tree(m)
    _set(b, base=srgb(PAL["divinycell"]), rough=0.85, spec=0.3)
    _noise_bump(nt, b, 320.0, 0.16, detail=3.0)


def look_alu(m, shade="alu", rough=0.28):
    """Brushed, not mirror. Anisotropy is faked with a stretched noise, which
    at this scale reads better than the real thing."""
    nt, b = _tree(m)
    _set(b, base=srgb(PAL[shade]), rough=rough, metal=1.0)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.0, 260.0, 1.0)
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = 30.0
    n.inputs["Detail"].default_value = 2.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.09
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], n.inputs["Vector"])
    nt.links.new(n.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])


def look_asa(m, shade="asa"):
    """FDM. Layer lines run in Z, so a wave texture banded on Z is literally
    the right primitive."""
    nt, b = _tree(m)
    _set(b, base=srgb(PAL[shade]), rough=0.62, spec=0.4)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    w = nt.nodes.new("ShaderNodeTexWave")
    w.wave_type = 'BANDS'
    w.bands_direction = 'Z'
    w.wave_profile = 'SIN'
    w.inputs["Scale"].default_value = 2.6
    w.inputs["Distortion"].default_value = 0.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.30
    nt.links.new(tc.outputs["Object"], w.inputs["Vector"])
    nt.links.new(w.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])


def look_carbon(m):
    """2x2 twill, near enough: two wave textures crossed at 90 degrees."""
    nt, b = _tree(m)
    _set(b, base=srgb(PAL["carbon"]), rough=0.24, metal=0.15,
         coat=0.8, coat_r=0.06)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value = (0, 0, 0.7854)
    mx = nt.nodes.new("ShaderNodeMath")
    mx.operation = 'MULTIPLY'
    ws = []
    for d in ('X', 'Y'):
        w = nt.nodes.new("ShaderNodeTexWave")
        w.wave_type = 'BANDS'
        w.bands_direction = d
        w.wave_profile = 'TRI'
        w.inputs["Scale"].default_value = 130.0
        nt.links.new(mp.outputs["Vector"], w.inputs["Vector"])
        ws.append(w)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(ws[0].outputs["Fac"], mx.inputs[0])
    nt.links.new(ws[1].outputs["Fac"], mx.inputs[1])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.35
    nt.links.new(mx.outputs[0], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])


def look_eva(m):
    """Diamond-groove EVA deck pad, blue camo.

    Built rather than photographed. A product listing image is not ours to
    redistribute - the same reason reference/ is gitignored - and a procedural
    one tiles across a 1.4 m pad without a visible repeat, which a 500 px crop
    would not. Two wave textures crossed at right angles cut the diamond
    grooves; a couple of octaves of noise do the camo mottle.
    """
    nt, b = _tree(m)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-1400, 0)

    # ---- grooves. 45 degrees so the diamonds sit point-forward, ~14 mm pitch
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.location = (-1200, 200)
    mp.inputs["Rotation"].default_value = (0, 0, 0.7854)
    mp.inputs["Scale"].default_value = (1.0, 1.0, 1.0)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    waves = []
    for i, d in enumerate(('X', 'Y')):
        w = nt.nodes.new("ShaderNodeTexWave")
        w.location = (-1000, 300 - 200 * i)
        w.wave_type = 'BANDS'
        w.bands_direction = d
        w.wave_profile = 'TRI'
        w.inputs["Scale"].default_value = 21.0      # 0.314/21 = ~15 mm pitch
        w.inputs["Distortion"].default_value = 0.0
        nt.links.new(mp.outputs["Vector"], w.inputs["Vector"])
        waves.append(w)
    gmin = nt.nodes.new("ShaderNodeMath")
    gmin.location = (-800, 200)
    gmin.operation = 'MINIMUM'
    nt.links.new(waves[0].outputs["Fac"], gmin.inputs[0])
    nt.links.new(waves[1].outputs["Fac"], gmin.inputs[1])
    gramp = nt.nodes.new("ShaderNodeValToRGB")     # sharpen into a groove
    gramp.location = (-620, 200)
    gramp.color_ramp.elements[0].position = 0.03
    gramp.color_ramp.elements[1].position = 0.16
    nt.links.new(gmin.outputs[0], gramp.inputs["Fac"])

    # ---- camo mottle
    cn = nt.nodes.new("ShaderNodeTexNoise")
    cn.location = (-1000, -220)
    cn.inputs["Scale"].default_value = 26.0
    cn.inputs["Detail"].default_value = 4.0
    cn.inputs["Roughness"].default_value = 0.75
    nt.links.new(tc.outputs["Object"], cn.inputs["Vector"])
    cramp = nt.nodes.new("ShaderNodeValToRGB")
    cramp.location = (-800, -220)
    cr = cramp.color_ramp
    cr.interpolation = 'CONSTANT'                  # camo has hard edges
    cr.elements[0].position = 0.0
    cr.elements[0].color = srgb("#0B4C86")
    cr.elements[1].position = 0.455
    cr.elements[1].color = srgb("#1E7FC0")
    for pos, col in ((0.505, "#3EA5DC"), (0.555, "#7FC8EA")):
        e = cr.elements.new(pos)
        e.color = srgb(col)

    # ---- grooves darken the camo
    mixc = nt.nodes.new("ShaderNodeMixRGB")
    mixc.location = (-420, 0)
    mixc.blend_type = 'MULTIPLY'
    mixc.inputs["Fac"].default_value = 0.75
    nt.links.new(cramp.outputs["Color"], mixc.inputs[1])
    nt.links.new(gramp.outputs["Color"], mixc.inputs[2])
    nt.links.new(mixc.outputs["Color"], b.inputs["Base Color"])

    bump = nt.nodes.new("ShaderNodeBump")
    bump.location = (-220, -300)
    bump.inputs["Strength"].default_value = 0.55
    nt.links.new(gramp.outputs["Color"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    _set(b, rough=0.78, spec=0.35, sheen=0.15)


def look_plain(m, shade, rough=0.5, metal=0.0):
    nt, b = _tree(m)
    _set(b, base=srgb(PAL[shade]), rough=rough, metal=metal)


# ------------------------------------------------------------------ apply
ASSIGN = {
    "V2_hull_glass": lambda m: look_paint(m),
    "V2_carbon": look_carbon,
    "V2_eva": look_eva,
    "V2_dense": look_divinycell,
    "V2_alu": lambda m: look_alu(m),
    "V2_alu_anod": lambda m: look_alu(m, rough=0.42),
    "V2_asa": lambda m: look_asa(m),
    "V2_lid": lambda m: look_paint(m),
    "V2_lid_mod": lambda m: look_asa(m, "asa_lid"),
    "V2_enclosure": lambda m: look_asa(m, "asa_lid"),
    "V2_cell": lambda m: look_plain(m, "cell", rough=0.45),
    "V2_wrap": lambda m: look_plain(m, "wrap", rough=0.35),
    "V2_seal": lambda m: look_plain(m, "seal", rough=0.75),
    "V2_steel": lambda m: look_plain(m, "steel", rough=0.22, metal=1.0),
    "V2_pcb": lambda m: look_plain(m, "pcb", rough=0.6),
    "V2_esc": lambda m: look_plain(m, "esc", rough=0.5),
    "V2_fuse": lambda m: look_plain(m, "fuse", rough=0.5),
    "V2_eps": lambda m: look_eps(m),
    "V2_eps_fwd": lambda m: look_eps(m),
    "V2_mach_al": lambda m: look_eps(m, "eps_cut"),
    "V2_mach_au": lambda m: look_eps(m, "eps_cut"),
    "V2_mach_fl": lambda m: look_eps(m, "eps_cut"),
    "V2_mach_fu": lambda m: look_eps(m, "eps_cut"),
}


RAW_LAMINATE = "#3B4148"      # cured epoxy over biaxial carbon, unfaired


def paint_keys(f_raw, f_hold, f_paint):
    # see the note on the frame-1 key below
    """Animate the hull and hatch lid from bare laminate to Whaler Blue.

    The hull was PAINTED from the moment it appeared, which put a finished
    board on screen at the laminate step, several weekends early. Node inputs
    are animatable, so this is four keyframes on two materials rather than a
    second copy of the hull mesh.
    """
    for name in ("V2_hull_glass", "V2_lid"):
        m = bpy.data.materials.get(name)
        if not m or not m.use_nodes:
            continue
        b = next((n for n in m.node_tree.nodes
                  if n.type == 'BSDF_PRINCIPLED'), None)
        if b is None:
            continue
        # THE FRAME-1 KEY IS NOT DECORATION. A keyframe's first value
        # extends BACKWARDS, so keying bare laminate at the laminate shot
        # reached back over the opening title and the hero board came up
        # GREY. The film opens on a finished board, so frame 1 is painted;
        # CONSTANT below stops it drifting towards raw across the two minutes
        # in between.
        for f, col, rough, coat in ((1, PAL["paint"], 0.13, 0.55),
                                    (f_raw, RAW_LAMINATE, 0.46, 0.10),
                                    (f_hold, RAW_LAMINATE, 0.46, 0.10),
                                    (f_paint, PAL["paint"], 0.13, 0.55)):
            b.inputs["Base Color"].default_value = srgb(col)
            b.inputs["Roughness"].default_value = rough
            b.inputs["Base Color"].keyframe_insert("default_value", frame=f)
            b.inputs["Roughness"].keyframe_insert("default_value", frame=f)
            if "Coat Weight" in b.inputs:
                b.inputs["Coat Weight"].default_value = coat
                b.inputs["Coat Weight"].keyframe_insert("default_value",
                                                        frame=f)
        ad = m.node_tree.animation_data
        act = ad.action if ad else None
        curves = []
        if act is not None:
            if hasattr(act, "fcurves"):
                curves = list(act.fcurves)
            else:
                slot = getattr(ad, "action_slot", None)
                for layer in act.layers:
                    for strip in layer.strips:
                        cb = strip.channelbag(slot) if slot else None
                        if cb:
                            curves.extend(cb.fcurves)
        for fc in curves:
            for kp in fc.keyframe_points:
                if kp.co.x <= max(1.5, f_raw + 0.5):
                    kp.interpolation = 'CONSTANT' 


def build_materials():
    n = 0
    for name, fn in ASSIGN.items():
        m = bpy.data.materials.get(name)
        if m:
            fn(m)
            n += 1

    # RULE 1. Whatever a material was doing before, it is opaque now - the
    # model draws the pads and some shells see-through so the splits show
    # while designing, and a part you can see through does not look like a
    # part you are holding.
    for m in bpy.data.materials:
        if m.name.startswith("A_"):
            continue          # the animation's own materials - the caption
                              # backing is deliberately semi-transparent
        for attr, val in (("blend_method", 'OPAQUE'),
                          ("surface_render_method", 'DITHERED')):
            try:
                setattr(m, attr, val)
            except (AttributeError, TypeError):
                pass
        if m.use_nodes:
            for nd in m.node_tree.nodes:
                if nd.type == 'BSDF_PRINCIPLED' and "Alpha" in nd.inputs:
                    nd.inputs["Alpha"].default_value = 1.0
    print("  materials: %d re-authored, all opaque" % n)
