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
# SOLID. The STL walls ARE the printed shell - drawn at print thickness,
# not as a block waiting to be infilled - so there is no discount to take.
# 0.55 was a guess and it undercounted V1's printed parts by 0.66 kg. The
# geometry says this on its own, so the number is 1.0, not a fitted value.
PRINT_INFILL = 1.0

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
# FOUR on the deck, not three - C4 is in the schedule and Derek confirmed it.
# The rails therefore carry 8, which is what his doc says makes them the
# strongest part of the board.
LAMINATE = [
    ("hull bottom", 4, 1.05),      # (where, layers, m2)
    ("deck", 4, 1.05),
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

    R = json.load(open(REPORT))
    v1 = {}
    v1["EPS/XPS core"] = vols.get("xps", 0) * DENS["xps"] / 1000.0
    # SPLIT BY JOB, not by material, or the comparison hides the interesting
    # part. V1's structural floor and its hatch lid are both 3/4 in plywood;
    # V2 does the same two jobs in aluminium and in composite.
    ply = {n: v for n, v in parts.get("plywood", [])}

    def _ply(key):
        return sum(v for n, v in ply.items() if key in n.lower())             * DENS["plywood"] / 1000.0
    v1["structural floor"] = _ply("bottom plate")
    v1["hatch lid"] = _ply("top lid")
    v1["plywood blocking"] = (vols.get("plywood", 0) * DENS["plywood"] / 1000.0
                              - v1["structural floor"] - v1["hatch lid"])
    v1["printed shell"] = (vols.get("asa", 0) * DENS["asa"]
                           * PRINT_INFILL / 1000.0)
    v1["aluminium"] = vols.get("alu_plate", 0) * DENS["alu"] / 1000.0
    v1["seals"] = vols.get("neoprene", 0) * DENS["neoprene"] / 1000.0
    v1["dense foam"] = 0.0

    glass = sum(n * a * GLASS_6OZ_GSM * WETOUT / 1000.0
                for _w, n, a in LAMINATE)
    v1["hull laminate"] = glass + HOTCOAT_KG
    v1["paint"] = PAINT_KG
    v1["hardware"] = HARDWARE_KG
    v1["wiring"] = WIRING_KG
    # SAME CELL, SO SAME MASS. This line used to say 69.5 g a cell while the
    # model used 72.0 for V2 - two numbers for one part, which made V2's pack
    # look 0.46 kg heavier when the real difference is TWO CELLS. 16S8P is
    # 128, 14S9P is 126.
    cell_g = R["pack"]["mass_kg"] * 1000.0 / R["pack"]["cells"]
    v1["battery"] = 126 * cell_g / 1000.0
    v1["ESC + BMS + fuse"] = 0.6 + 0.32 + 0.45

    m2 = dict(R["mass_kg"])
    v2 = {
        "EPS/XPS core": m2.get("EPS core", 0),
        "structural floor": 0.0,      # V2 does this in aluminium
        "hatch lid": m2.get("lids", 0),
        "plywood blocking": 0.0,
        "dense foam": m2.get("dense foam", 0),
        "printed shell": m2.get("printed shell", 0) + m2.get("printed rim ring", 0),
        "aluminium": m2.get("aluminium", 0),
        "seals": m2.get("hardware + seal", 0) * 0.3,
        "hull laminate": m2.get("glass skin", 0),
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
    print("  V1 mast stub in the export: %.2f L of alu, excluded above"
          % vols.get("FOIL", 0.0))

    # ---- V1 DISPLACEMENT, FROM THE CAD, not from the doc. The doc's own
    # component figures do not survive the export: it claims 75.3 L of foam
    # where the model measures 73.26, and a 660 x 280 cavity where the
    # geometry gives 678 x 317. The lid gasket is a rectangular ring, so
    # its outer size and its VOLUME - both CAD facts - hand over the
    # opening it surrounds without anyone having to be taken at their word.
    gk = next((v for n, v in parts.get("neoprene", [])
               if "main lid" in n.lower()), None)
    v1_disp = None
    if gk:
        ox, oy, t = 701.9, 340.7, 7.6
        w = (2.0 * (ox + oy) - math.sqrt(4.0 * (ox + oy) ** 2
                                         - 16.0 * gk * 1e6 / t)) / 8.0
        opx, opy = ox - 2 * w, oy - 2 * w
        depth = 134.0 - 19.0      # bottom plate top -> gasket underside
        cav = opx * opy * depth / 1e6
        foam = vols.get("xps", 0)
        v1_disp = foam + cav
        print("")
        print("V1 DISPLACEMENT, FROM THE CAD")
        print("  gasket ring %.1f mm wide -> opening %.0f x %.0f"
              % (w, opx, opy))
        print("  cavity %.0f x %.0f x %.0f              %6.2f L"
              % (opx, opy, depth, cav))
        print("  foam, measured                       %6.2f L" % foam)
        print("  ENVELOPE                             %6.2f L" % v1_disp)
        print("  (doc claimed 75.3 + 21.3 = 96.6 - near on the total,")
        print("   wrong on both halves)")
        print("")
        print("  V1  %5.1f L, %5.2f kg -> 86 kg rider: %+6.1f kg"
              % (v1_disp, ta, v1_disp - ta - 86.0))
        print("  V2  %5.1f L, %5.2f kg -> 86 kg rider: %+6.1f kg"
              % (R["sealed_displacement_L"], R["board_mass_kg"],
                 R["sealed_displacement_L"] - R["board_mass_kg"] - 86.0))
    # ---- reconcile against the scale
    # ---- against the one hard number in the whole file
    MOTOR, MAST, MOUNT, MEASURED = 2.6, 3.2, 0.4, 50 * 0.4536
    dry = ta - v1["battery"]      # the pack was NOT in it when weighed
    print("")
    print("AGAINST THE SCALE  (50 lb; mast, mount, motor on, pack OUT)")
    print("  estimate, board                       %6.2f" % ta)
    print("  less the pack, confirmed not in it    %6.2f" % dry)
    print("  + motor %.1f, mast %.1f, mount %.1f       %6.2f"
          % (MOTOR, MAST, MOUNT, dry + MOTOR + MAST + MOUNT))
    print("  measured                              %6.2f" % MEASURED)
    print("  GAP                                   %6.2f kg"
          % (dry + MOTOR + MAST + MOUNT - MEASURED))
    print("")
    print("  WHAT COULD ACCOUNT FOR IT, biggest lever first. Every one is")
    print("  a density or an allowance - none of them is geometry:")
    ply_v = vols.get("plywood", 0)
    lam_m2 = sum(n * a for _w, n, a in LAMINATE)
    for nm, d in (("plywood at 500 not 680 kg/m3",
                   ply_v * (DENS["plywood"] - 500) / 1000.0),
                  ("hardware + wiring allowance halved",
                   (HARDWARE_KG + WIRING_KG) / 2),
                  ("wetout 1.5x not 2.0x",
                   lam_m2 * GLASS_6OZ_GSM * 0.5 / 1000.0),
                  ("mast + motor lighter than assumed", 1.0),
                  ("XPS at 25 not 35 kg/m3",
                   vols.get("xps", 0) * 10 / 1000.0)):
        print("    %5.2f kg   %s" % (d, nm))
    print("")
    print("  THE ONE MEASUREMENT THAT WOULD SETTLE MOST OF IT: put the")
    print("  hatch lid on the scale. One slab of 3/4 in ply, it unbolts,")
    print("  and this file predicts %.2f kg. Whatever it really weighs"
          % v1["hatch lid"])
    print("  calibrates plywood density - the largest assumption here.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
