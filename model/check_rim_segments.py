"""Measure the rim segments against the ring - from the SAVED file.

    blender -b --python model/check_rim_segments.py

The same two checks exist inside blender_board.py but do not read reliably
there: each segment carries a chain of booleans whose operands carry their
own, and the live modifier stack gives volumes that the saved geometry
contradicts. Twice that reported a leak that was not there, and twice the
response was to back off a real design change to satisfy it.

Run this instead when the rim has changed. It opens the saved .blend, where
the modifiers have settled, and reports what is actually in the file.
"""
import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/derek/Development/eFoil/model/efoil_v2.blend')
import bmesh
dg=bpy.context.evaluated_depsgraph_get()
def vol(ob):
    me=ob.evaluated_get(dg).to_mesh()
    bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.triangulate(bm, faces=bm.faces[:])
    v=bm.calc_volume(signed=True); bm.free(); ob.evaluated_get(dg).to_mesh_clear()
    return abs(v)*1e9   # m3 -> mm3
tot=0
for ob in bpy.data.objects:
    if ob.name.startswith('RimSeg_'):
        v=vol(ob); tot+=v
        zs=[(ob.matrix_world@x.co).z*1000 for x in ob.evaluated_get(dg).to_mesh().vertices]
        print(f"  {ob.name:16} {v/1000:9.1f} cm3   ztop {max(zs):7.2f}")
cands=[o for o in bpy.data.objects
       if o.type=='MESH' and o.name.startswith('Rim')
       and not o.name.startswith(('RimSeg_','RimDT','RimChamfer'))
       and '_cut' not in o.name]
r=cands[0] if cands else None
seal=None
import re
print(" segments total:", round(tot/1000,1),"cm3")
tops=[max((ob.matrix_world@x.co).z*1000
          for x in ob.evaluated_get(dg).to_mesh().vertices)
      for ob in bpy.data.objects if ob.name.startswith('RimSeg_')]
print(f" highest segment point: {max(tops):.2f} mm")
print(" -> nothing may stand above the seal face; a lug there is a leak")
if r: print(" ring:", round(vol(r)/1000,1),"cm3  -> ",round(100*tot/vol(r),2),"%")
else: print(" ring object names:", [o.name for o in bpy.data.objects if 'Rim' in o.name][:8])
