# eFoil

DIY electric hydrofoil. V1 is built and in shakedown at Lucky Peak; V2 is a
design spec that starts after a season of V1 riding data.

## Layout

```
docs/        project documentation (originals + research)
model/       parametric hull generator, Blender scene, STL export, CNC drawings
cnc/         generated DXF part drawings + cut list  (regenerate, never edit)
renders/     model renders
print/       print-ready miniature STLs  (regenerate, never edit)
print/glass/ full-size glass ply templates  (regenerate, never edit)
reference/   traced manufacturer orthos used to fit the hull shape
```

Running `blender_board.py` now rewrites `model/efoil_v2.blend` **and**
`model/efoil_v2_hull.stl` on every run. It used not to, and both files silently
drifted a full day behind the script — opening the .blend showed geometry that
had already been fixed in the model, which is a very convincing way to waste an
afternoon. If you have the .blend open in the GUI, reopen it after a run.

Regenerate the CNC drawings after any parameter change — they are derived from
`blender_board.py`, so editing them by hand guarantees drift:

```bash
python model/cnc_drawings.py
```

Miniatures for printing. Scene units are metres and the board is 1.4 units
long, so a plain STL export reads as **1.4 mm** in a slicer — these are exported
with an explicit scale so each file arrives at the size in its own filename,
with nothing to remember:

```bash
blender -b --factory-startup --python model/print_miniature.py
```

Glass ply templates — developed (not plan) outlines plus relief-cut positions,
as DXF and as tiled HTML you print at 100% from a browser:

```bash
python model/glass_templates.py
```

## Docs

| File | What it covers |
|---|---|
| [efoil-1-board-design.md](docs/efoil-1-board-design.md) | V1 board as-built: dimensions, 3-layer XPS construction, hatch, leak history |
| [efoil-2-electrical.md](docs/efoil-2-electrical.md) | Pack architecture, BMS, enclosures, mast mount hardware, wiring |
| [efoil-3-propulsion.md](docs/efoil-3-propulsion.md) | Motor, ESC, foil, prop, motor mount, measured performance |
| [fabrication.md](docs/fabrication.md) | How the V2 core actually gets machined — CNC plan, sequence, workholding, two-sided registration, what to job-shop |
| [efoil-4-build-order.md](docs/efoil-4-build-order.md) | Build phases, pack welding procedure, 3D printing |
| [efoil-7-vesc-config.md](docs/efoil-7-vesc-config.md) | VESC settings, current limits, power diagnosis, gotchas |
| [efoil-8-v2-planning.md](docs/efoil-8-v2-planning.md) | V2 direction: pillars, construction method, CNC, budget |
| [efoil-9-v2-board-design.md](docs/efoil-9-v2-board-design.md) | V2 board spec: dimensions, hardpoint, cavity, hatch, sealing, layup |
| [shopping-list-v10.md](docs/shopping-list-v10.md) | Full spend reconciliation, ~$3,900 to date |
| [shape-research.md](docs/shape-research.md) | Production eFoil dimensions + traced shape law behind the V2 hull |
| [v2-powertrain-options.md](docs/v2-powertrain-options.md) | Motor / ESC / BMS options for V2, against V1's measured numbers |
| [materials-and-pricing.md](docs/materials-and-pricing.md) | What each material is, quantities from the model, quoted + estimated prices |
| [build-budget.md](docs/build-budget.md) | Complete BOM and cost for the whole V2 build, per-line confidence |
| [colour-key.md](docs/colour-key.md) | What every colour in the model means, and the foil dimensions |

Numbering skips 5 and 6 — those docs are either missing from the archive or
were never written.

## Model

`model/blender_board.py` builds the whole V2 board in Blender from parameters:
hull, cavity, G10 rim with machined O-ring groove, sandwich lid, mast
hardpoint, dense-foam load path, CNC seam, charge port, vent boss, and the
actual Gong X-Over V2 XL foil. It reports volume, fit, and clash checks on
every run.

Run it with Blender open:

```bash
blender --python-expr "exec(open(r'C:/Users/derek/Development/eFoil/model/blender_board.py').read())"
```

`model/trace_reference.py` extracts planform, thickness and rocker curves from
manufacturer orthographic renders. Usage:

```bash
python model/trace_reference.py reference/lift43_ortho.png 1300 480 100 42
```

## Key numbers

| | V1 (built) | V2 (current model) |
|---|---|---|
| Dimensions | 1600 x 600 x 153 mm | 1400 x 600 x 167 mm |
| Volume | 96.6 L sealed | 114.0 L sealed (81.3% bbox fill) |
| Net float | - | **+12.0 kg** - it floats the rider |
| Weight | 25-30 kg | 16-18 kg target |
| Pack | 14S9P upright, 82 mm tall | 14S9P upright, BMS on top, 93 mm |
| Energy | 2,268 Wh | 2,268 Wh |
| Cavity | 660 x 280 x 115 mm | 479 x 329 x 111 mm (incl. aft service bay) |
| Electronics | 2 sealed boxes | 1 removable G10 module, 383 x 313 x 109, no divider |
| Mast | 400 mm from tail, 90 x 165 mm | same, M8 blind inserts in a 16 mm G10 plate |
| CG | - | 641.2 mm, 45.8% from tail, 241.2 mm ahead of the mast |
| Seam | - | 1030 mm (halves 1030 + 370) |

Hull shape is fitted to traced production boards - see
[shape-research.md](docs/shape-research.md). Both ends terminate in a flat
(108 mm tail, 54 mm nose), and the nose rocker is *derived* from a specified
deck line rather than dialled in, so the deck rises monotonically to +10 mm at
the tip instead of dropping. Colour coding of every part is documented in
[colour-key.md](docs/colour-key.md).

The model runs a fit check on every build (pack, BMS, ESC, fuse, lift-out
clearance, rim vs rail, floor thickness over the rocker, lid flush). Current
status: **no failures**. Tightest clearance is the BMS in its pocket, 17 mm.

## Open questions

Carried from the V2 docs, plus what the shape research and pack analysis added:

- **Pack architecture** — 14S vs 16S, and whether cells lie down (21.4 mm per
  layer) instead of standing up (70.75 mm). This drives cavity depth, which
  drives board thickness.
- **`board_gen.py` is missing.** The V2 doc cites it as the source of the
  53.9 L headline figure; it is not in the archive. That number also rests on a
  45–47% bounding-box fill assumption that does not hold for eFoils.
- **Thickness disagreement** — efoil-9 specs 150 mm, efoil-8 specs a
  1600 × 600 × 120 mm blank. Also 1600 vs 1400 length.
- **Mast position** — V2 proposes 350 mm; V1 as-built is 400 mm with a
  90 × 165 mm pattern. Verify against the wing's centre of lift.
- Makerspace CNC bed size, and whether they allow foam.
- Lid flush vs proud (currently flush, 2.6 mm below deck).
- **Reed switch kill system is still not installed on V1.** Parts on hand.
  Required before any beginner rides the board.
