"""Print-ready miniatures of the V2 board.

Run:  blender -b --factory-startup --python model/print_miniature.py

Scene units are METRES and the board is 1.4 units long, so a straight STL
export reads as 1.4 mm in a slicer. Everything here is exported with an
explicit global_scale so the file arrives in the slicer at the size named in
its filename, with no scaling to remember.
"""
import bpy, os, math

ROOT = r"C:/Users/derek/Development/eFoil"
exec(open(os.path.join(ROOT, "model/blender_board.py")).read())

OUT = os.path.join(ROOT, "print")
os.makedirs(OUT, exist_ok=True)
dg = bpy.context.evaluated_depsgraph_get()

# Board is 1400 mm. global_scale 1000 = full size in mm; divide by the ratio.
# Filament goes as the CUBE of scale, so these get cheap fast: 1:6 was ~200 g
# of PLA for the hull alone, 1:12 is ~25 g, 1:20 is ~5 g.
SCALES = {"1-20": 50.0, "1-16": 62.5, "1-12": 1000.0 / 12.0}
PLA_G_CM3 = 1.24
INFILL_F = 0.35        # rough solid-fraction for 2 perimeters + ~15% infill

# V2_ModPiece_ and V2_RimSeg_ are the PARTS - the four printed shell pieces
# and the six printed ring segments. "V2_Mod_" does not match "V2_ModPiece_",
# so the miniature was silently missing the shell entirely and printing the
# hidden one-piece V2_RimRing_ASA reference instead of the six real segments.
INTERNALS = ("Mod_", "ModPiece_", "RimSeg_", "Pack_", "BMS",
             "ESC", "Fuse", "MastPlate_Alu", "DenseFoam_Block",
             "Lid", "Conduit")


def bake(names, out_name):
    """Merge evaluated meshes into one object so it exports as a single body."""
    made = []
    for n in names:
        ob = bpy.data.objects.get(n)
        if not ob or ob.type != 'MESH':
            continue
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        cp = bpy.data.objects.new(n + "__p", me)
        cp.matrix_world = ob.matrix_world.copy()
        bpy.context.scene.collection.objects.link(cp)
        made.append(cp)
    if not made:
        return None
    bpy.ops.object.select_all(action='DESELECT')
    for o in made:
        o.select_set(True)
    bpy.context.view_layer.objects.active = made[0]
    if len(made) > 1:
        bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = out_name
    return ob


def export(ob, path, scale):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True,
                          global_scale=scale, apply_modifiers=True)


def half(ob, name):
    """Section on the centreline so the cavity and mast pocket are visible."""
    bpy.ops.mesh.primitive_cube_add(size=4, location=(0.7, 2.0, 0.07))
    k = bpy.context.object
    m = ob.modifiers.new("cut", 'BOOLEAN')
    m.object = k
    m.operation = 'DIFFERENCE'
    m.solver = 'EXACT'
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(
        bpy.context.evaluated_depsgraph_get()))
    cp = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(cp)
    ob.modifiers.remove(m)
    bpy.data.objects.remove(k, do_unlink=True)
    return cp


rows = []
hull = bake(["Hull"], "print_hull")
inner = bake([o.name for o in bpy.data.objects
              if o.type == 'MESH' and not o.hide_get()
              and any(o.name.startswith(p) for p in INTERNALS)], "print_internals")

cut = half(hull, "print_hull_cutaway")

for tag, sc in SCALES.items():
    for ob, kind in ((hull, "hull"), (inner, "internals"),
                     (cut, "hull_cutaway")):
        if not ob:
            continue
        fp = os.path.join(OUT, f"efoil_v2_{kind}_{tag}.stl")
        export(ob, fp, sc)
        d = [v * sc for v in ob.dimensions]
        # volume_litres works in the model's own units; scale is a cube law
        vol_cm3 = volume_litres(ob) * 1000.0 * (sc / 1000.0) ** 3
        grams = vol_cm3 * INFILL_F * PLA_G_CM3
        rows.append((os.path.basename(fp),
                     f"{d[0]:>5.0f} x {d[1]:>4.0f} x {d[2]:>4.0f} mm",
                     f"{vol_cm3:>7.1f}", f"{grams:>6.1f}"))

print("PRINTFILES")
print(f"  {'file':<34} {'size':<22} {'solid cm3':>9} {'~g PLA':>7}")
for n, d, v, g in rows:
    print(f"  {n:<34} {d:<22} {v:>9} {g:>7}")
NOZZLE = 0.4
print("")
print("  what survives a 0.4 mm nozzle at each scale:")
print("  ratio      board   cav floor   rebate dp   mod wall")
for tag, sc in SCALES.items():
    r = 1000.0 / sc
    wall = ENC_WALL / r
    flag = "" if wall >= NOZZLE else "   <- module walls vanish"
    print(f"  {tag:<8}{LENGTH/r:>7.0f}mm{22.3/r:>11.1f}{RIM_T/r:>12.1f}"
          f"{wall:>11.2f}{flag}")
