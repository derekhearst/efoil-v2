# eFoil V2

A DIY electric hydrofoil board, generated from a parametric Blender model that
also emits its own CNC drawings, cutting patterns, glass ply templates and
bill of materials. Change a parameter, re-run, and every downstream document
follows.

**V1 is built and riding.** V2 is the board this repo is about: a full model
with `FAILS: ['none']` on every check, a BOM where 126 of 129 purchasable
lines link to a real listing, and a machining plan that fits a specific
router in a specific shop.

---

## The one rule

**Nothing in `cnc/`, `print/`, `docs/bom.md` or `docs/shopping.md` is written
by hand.** They are generated from `model/*.py`. Editing them guarantees
drift, and drift in a cut list is a part you machine twice.

`model/report.json` is the contract between the scripts: `blender_board.py`
writes it, everything else reads it. `bom.py` refuses to run if it is stale.

---

## Regenerate everything

```bash
blender -b --factory-startup --python-expr "exec(open(r'C:/Users/derek/Development/eFoil/model/blender_board.py').read())"
```

That rewrites `model/efoil_v2.blend`, `model/efoil_v2_hull.stl` and
`model/report.json`, and prints the full check report. **If you have the
.blend open in the GUI, reopen it afterwards** — otherwise you are looking at
geometry that has already been fixed.

Then, in any order:

```bash
python model/cnc_drawings.py      # DXF part drawings + cnc/cut-list.md
python model/bom.py               # docs/bom.md + docs/shopping.md
python model/glass_templates.py   # developed glass ply outlines, DXF + printable HTML
```

```bash
blender -b --factory-startup --python model/print_miniature.py
```

Miniatures are exported at an explicit scale — scene units are metres and the
board is 1.4 units long, so a plain STL export reads as **1.4 mm** in a
slicer. Each file arrives at the size in its own filename.

---

## Layout

```
model/       the parametric model and every generator that reads it
cnc/         generated DXF drawings + cut list        (regenerate, never edit)
docs/        V2 documentation - see below
docs/v1/     V1 as-built, kept for reference only     (see "V1 archive")
print/       print-ready miniature STLs               (regenerate, never edit)
snapshots/   dated .blend captures of past shape decisions
```

Not in the repo: `renders/` (173 MB of build output) and `reference/`
(manufacturer marketing imagery used to fit the hull — not ours to
redistribute).

---

## V2 documentation

These describe the board being built. Start here.

| Doc | What it covers |
|---|---|
| [fabrication.md](docs/fabrication.md) | How the core gets made: the CNC envelope, the two splits and why each exists, machining sequence, workholding, bagging, the winter schedule |
| [cut-list.md](cnc/cut-list.md) | *Generated.* Every flat part, the four core pieces, the milling table, and the deck-pad cutting pattern |
| [bom.md](docs/bom.md) | *Generated.* Every line, linked to the listing its price came from, with per-line confidence |
| [shopping.md](docs/shopping.md) | *Generated.* The same spend grouped by supplier — the order you actually place orders in |
| [materials-and-pricing.md](docs/materials-and-pricing.md) | What each material is and why it was chosen over the alternative |
| [colour-key.md](docs/colour-key.md) | What every colour in the model means |
| [shape-research.md](docs/shape-research.md) | Traced production boards and the shape law fitted from them |
| [v2-powertrain-options.md](docs/v2-powertrain-options.md) | Motor / ESC / BMS options, against V1's measured numbers |

---

## Key numbers

| | V1 (built) | V2 (current model) |
|---|---|---|
| Dimensions | 1600 × 600 × 153 mm | 1400 × 560 × 157 mm |
| Sealed displacement | 96.6 L | 86.2 L |
| Board mass | 25–30 kg | 24.0 kg |
| Board reserve, alone | — | +62.2 kg |
| With an 86 kg rider | — | **−23.8 kg — a sinker at rest** |
| Pack | 14S9P, 2,268 Wh | 16S8P, 2,304 Wh, 9.22 kg |
| Cavity | 660 × 280 × 115 mm | 535 × 323 × 100 mm |
| Electronics | 2 sealed boxes | 1 removable module: printed ASA walls on a 5052 floor |
| Mast plate | — | 6061-**T651**, 12.7 mm, M8 tapped, 2.6× margin |
| Hatch | — | 12 × M5 into captive nuts printed into an ASA rim ring |
| Core splits | — | vertical at 1030 mm (bed length), horizontal at 101.6 mm (gantry) |
| Machining | — | 4 pieces, 5 setups, 1 flip, no cradle |
| Deck pad | — | 3 pieces of 5.8 mm EVA, one sheet does both boards |
| Cost | ~$3,900 spent | **$3,849/board**, 93% verified |

The board is a **sinker** — 86.2 L will not float a rider standing still.
That is a deliberate consequence of narrowing to 560 mm, but note it changed:
an earlier revision of this README claimed "+12.0 kg — it floats the rider",
from back when displacement was 114 L. If floating at rest matters to you,
that is the number to argue with.

---

## Open questions

Ordered by what can actually stop the build.

1. **Will the makerspace allow EPS on the CNC?** Unanswered. It is a
   woodworking shop with no published material policy, and this is the one
   that can stop the booking outright. Maker Shop Boise, (208) 254-6151.
2. **Cutter reach.** The deepest pocket is the cavity's lower half at
   **71.6 mm**. The O-flute in the BOM has a *cutting* length of 31.8 mm — it
   is 39.8 mm short and physically cannot reach the floor. Buy a long-reach
   ½ in spiral, or rough it with the ball nose.
3. **Wire bay stops at 68 mm.** At 75 the rim segmentation checks collapse —
   segment volumes sum to 50% of the ring and one reads 2 mm proud of the seal
   face — while a per-segment dump shows all six correct and flush. Geometry
   looks right, measurement does not, cause unresolved. 68 is the largest
   value that stays green.
4. **Gong import duty.** Shipping is measured ($268.63 for two foils, from
   their checkout), but US customs is not. It arrives later as a courier
   invoice. Budget ~$210 if a 15% rate holds; the BOM carries it at zero so it
   is never mistaken for a verified figure.
5. **Sinker at rest** — see above. A design characteristic, not a defect, but
   confirm it is the one you want.
6. **V1's reed-switch kill system is still not installed.** Parts on hand.
   Required before any beginner rides that board.

---

## V1 archive

`docs/v1/` is **reference only** — the board that was built, what it measured,
and where it leaked. It informs V2 but does not describe it. Where the two
disagree, the model and the V2 docs above are correct.

Two of these are superseded V2 *planning* documents, kept because the
reasoning is useful and the conclusions are not: they predate the model and
their numbers no longer hold.

| Doc | |
|---|---|
| [efoil-1-board-design.md](docs/v1/efoil-1-board-design.md) | V1 as-built: XPS construction, hatch, and the leak history that drove V2's sealing |
| [efoil-2-electrical.md](docs/v1/efoil-2-electrical.md) | V1 pack, BMS, enclosures, wiring as built |
| [efoil-3-propulsion.md](docs/v1/efoil-3-propulsion.md) | Motor, ESC, foil, prop, and measured performance |
| [efoil-4-build-order.md](docs/v1/efoil-4-build-order.md) | V1 build phases and pack welding procedure |
| [efoil-7-vesc-config.md](docs/v1/efoil-7-vesc-config.md) | VESC settings, current limits, power diagnosis |
| [efoil-8-v2-planning.md](docs/v1/efoil-8-v2-planning.md) | *Superseded.* Early V2 direction and budget |
| [efoil-9-v2-board-design.md](docs/v1/efoil-9-v2-board-design.md) | *Superseded.* Early V2 spec — 150 mm thick, G10 module, different cavity |
| [shopping-list-v10.md](docs/v1/shopping-list-v10.md) | V1 spend reconciliation |

Numbering skips 5 and 6 — those were never written.

---

## Other scripts

| Script | |
|---|---|
| `model/templates.py` | MDF check gauges for hand-verifying the machined core |
| `model/performance.py` | Speed / thrust / runtime against V1's measured numbers |
| `model/price_check.py` | Re-checks BOM prices against recorded sources |
| `model/trace_reference.py` | Extracts planform, thickness and rocker from manufacturer orthos |
| `model/links.py` | *Generated.* item → (ASIN or URL, price, title) for every sourced line |
