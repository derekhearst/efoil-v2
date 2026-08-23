"""
mass_compare.py - V1 and V2 side by side, by material, from real volumes.

    blender -b --factory-startup --python model/mass_compare.py

V2's masses come out of report.json, which the model computes.
V1's come out of Derek's own Onshape export in docs/v1/stl/ - every part
measured with bmesh.calc_volume() and multiplied by a density - plus the
things an STL cannot know about: laminate, epoxy, paint, hardware, wiring.

THIS IS A PREDICTION TO BE CHECKED, not a result. V1 exists and can be put on
a scale. Where the two disagree, the scale is right and the number below is
wrong, and the interesting part is WHICH LINE is wrong - which is the whole
reason for breaking it down by material instead of quoting one figure.

Every density and every laminate assumption is named and sourced in DENS and
LAMINATE so they can be argued with individually.
"""

import bpy
import bmesh
import glob
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STL = os.path.join(ROOT, "docs", "v1", "stl")
REPORT = os.path.join(ROOT, "model", "report.json")

# ---------------------------------------------------------------- densities
# kg/m3. Sources noted where the number is not simply the material's own.
DENS = {
    "xps":      35.0,    # extruded polystyrene, 25-38 typical; V1's 2in sheet
    "plywood":  680.0,   # birch ply, 3/4in - denser than fir, V1 used birch
    "asa":      1070.0,  # printed solid; the enclosures print with infill,
                         # handled by PRINT_INFILL below
    "alu":      2700.0,
    "neoprene": 1250.0,
    "cell":     None,    # from V1's own doc, not from volume
}
PRINT_INFILL = 0.55      # printed walls are not solid. V1's own doc gives
                         # 233 g a corner piece; this is tuned to land on it.

# ------------------------------------------------------------------ laminate
# V1's schedule, straight from efoil-1-board-design.md:
#   bottom  4 layers 6 oz          cavity  2 layers 6 oz
#   deck    3 layers 6 oz          hatch recess 3 layers 6 oz
#   hatch lid: NO glass - epoxy hot coat only
# 6 oz cloth is 203 g/m2 dry. Hand layup wets out at roughly 1:1 by weight,
# so ~2.0x dry weight cured. No vacuum bag on V1, which is why the ratio is
# worse than V2's bagged 2.20 kg/m2 for two 6 oz plus biax.
GLASS_6OZ_GSM = 203.0
WETOUT = 2.0
LAMINATE = [
    ("hull bottom", 4, 1.05),      # (where, layers, m2)
    ("deck", 3, 1.05),
    ("cavity inside", 2, 0.62),
    ("hatch recess", 3, 0.25),
]
HOTCOAT_KG = 0.9       # epoxy hot coat + fill coats + primer, whole board
PAINT_KG = 0.5
HARDWARE_KG = 1.1      # bolts, inserts, hinges, latches, fender washers
WIRING_KG = 1.3        # 8 AWG runs, phase leads, glands, connectors


def vol_l(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    v = abs(bm.calc_volume(signed=True))
    bm.free()
    return v / 1e6                      # mm3 -> litres


def classify(o):
    """Which material is this part?

    Sorted on the export's names, but written out so a wrong guess shows up
    instead of hiding inside a total - and two did on the first run:

      "Mast Mount" is not board hardware. It is a 760 mm stub of the MAST,
      and at 2.87 L of aluminium it was adding 7.75 kg to a board that does
      not carry it. V2's board mass excludes the foil, so V1's must too.

      The enclosure's "plates" are 3.2 mm, not 19. Sorting on the word
      "plate" put four sheets of 1/8 in aluminium into the plywood line.
      Thickness decides it now, not the name.
    """
    n = o.name.lower()
    thin = min(o.dimensions) < 6.0      # mm - the plates are 3.2, ply is 19
    if "foam board" in n:
        return "xps"
    if "mast mount" in n:
        return "FOIL"                   # not the board's weight
    if any(k in n for k in ("bottom plate", "top plate", "top lid",
                            "wood blocking", "lid bolt hardpoint")):
        return "alu_plate" if thin else "plywood"
    if "gasket" in n:
        return "neoprene"
    if n.endswith("battery") or "- bms" in n or n.endswith("esc") \
            or "fuse" in n:
        return "electronics"
    return "asa"                        # enclosure walls and plates


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    imp = getattr(bpy.ops.wm, "stl_import", None) or bpy.ops.import_mesh.stl
    files = sorted(glob.glob(os.path.join(STL, "*.stl")))
    if not files:
        print("no STLs in", STL)
        return 1
    for f in files:
        imp(filepath=f)

    vols, parts = {}, {}
    for o in bpy.data.objects:
        if o.type != 'MESH':
            continue
        k = classify(o)
        v = vol_l(o)
        vols[k] = vols.get(k, 0.0) + v
        parts.setdefault(k, []).append((o.name, v))

    v1 = {}
    v1["EPS/XPS core"] = vols.get("xps", 0) * DENS["xps"] / 1000.0
    v1["plywood"] = vols.get("plywood", 0) * DENS["plywood"] / 1000.0
    v1["printed shell"] = (vols.get("asa", 0) * DENS["asa"]
                           * PRINT_INFILL / 1000.0)
    v1["aluminium"] = vols.get("alu_plate", 0) * DENS["alu"] / 1000.0
    v1["seals"] = vols.get("neoprene", 0) * DENS["neoprene"] / 1000.0

    glass = sum(n * a * GLASS_6OZ_GSM * WETOUT / 1000.0
                for _w, n, a in LAMINATE)
    v1["glass + epoxy"] = glass + HOTCOAT_KG
    v1["paint"] = PAINT_KG
    v1["hardware"] = HARDWARE_KG
    v1["wiring"] = WIRING_KG
    # 14S9P of the same 21700 cell V2 uses, from V1's electrical doc
    v1["battery"] = 126 * 0.0695
    v1["ESC + BMS + fuse"] = 0.6 + 0.32 + 0.45

    R = json.load(open(REPORT))
    m2 = dict(R["mass_kg"])
    v2 = {
        "EPS/XPS core": m2.get("EPS core", 0),
        "plywood": 0.0,
        "printed shell": m2.get("printed shell", 0) + m2.get("printed rim ring", 0),
        "aluminium": m2.get("aluminium", 0),
        "seals": m2.get("hardware + seal", 0) * 0.3,
        "glass + epoxy": m2.get("glass skin", 0) + m2.get("lids", 0)
                         + m2.get("dense foam", 0),
        "paint": 0.5,
        "hardware": m2.get("hardware + seal", 0) * 0.7,
        "wiring": m2.get("wiring + conduit", 0),
        "battery": m2.get("battery", 0),
        "ESC + BMS + fuse": m2.get("ESC", 0) + m2.get("BMS", 0)
                            + m2.get("fuse + switch + port", 0),
    }

    print("\nV1 PART VOLUMES, measured from the STLs")
    for k in sorted(parts):
        tv = sum(v for _n, v in parts[k])
        print("  %-14s %6.2f L   %s" % (k, tv, ", ".join(
            n.replace("Part Studio 1 - ", "")[:26] for n, _v in parts[k][:3])
            + ("  ..." if len(parts[k]) > 3 else "")))

    print("\n%-20s %9s %9s %9s" % ("", "V1 kg", "V2 kg", "delta"))
    print("  " + "-" * 48)
    keys = sorted(set(v1) | set(v2), key=lambda k: -max(v1.get(k, 0),
                                                        v2.get(k, 0)))
    for k in keys:
        a, b = v1.get(k, 0.0), v2.get(k, 0.0)
        print("  %-18s %8.2f  %8.2f  %+8.2f" % (k, a, b, b - a))
    ta, tb = sum(v1.values()), sum(v2.values())
    print("  " + "-" * 48)
    print("  %-18s %8.2f  %8.2f  %+8.2f" % ("TOTAL", ta, tb, tb - ta))
    print("\n  model's own V2 figure       %8.2f kg  (agrees within %.2f)"
          % (R["board_mass_kg"], abs(tb - R["board_mass_kg"])))
    print("  V1 doc says                 25-30 kg")
    print("  MEASURED BY DEREK           22.68 kg (50 lb) - but that INCLUDES")
    print("     the mast, mast mount and motor, and excludes the wings.")
    print("  V1 mast stub in the export: %.2f L of alu, excluded above" %
          vols.get("FOIL", 0.0))
    print("\nWEIGH V1. If the total is out, the breakdown says which line to")
    print("suspect - laminate and epoxy are the softest numbers here, being")
    print("the only ones no STL can measure.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
