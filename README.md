# eFoil V2

A DIY electric hydrofoil board, generated from a parametric Blender model that
also emits its own CNC drawings, cutting patterns, glass ply templates and
bill of materials. Change a parameter, re-run, and every downstream document
follows.

**V1 is built and riding.** V2 is the board this repo is about: a full model
with `FAILS: ['none']` on every check, a BOM where 131 of 135 purchasable
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

### The build animation

```bash
blender -b model/efoil_v2.blend --python model/animate_build.py -- --res 1600
```

Two minutes covering the whole build in the order
[fabrication.md](docs/fabrication.md) gives it: glue-up, the CNC setups with
the router actually removing material, the flip, bonding, hardpoints, layup,
pack, module, install, deck pad, foil. Lands in `renders/build.mp4`, which is
**gitignored like the rest of `renders/`** — regenerate it, do not commit it.

Add `--stills` for one PNG per shot (about 15 seconds, and the way to check
choreography), `--shot NAME` for one shot, or `--dry` to print the shot list
and render nothing.

The router is not faked. Waste is built as
`slab − ((slab − part) ∩ swept)`, so the stock starts **solid** and the
finished surface is uncovered exactly where the tool has already been; the
cutter's Z is raycast against the real machined geometry rather than dropped
at a guessed height. Get that construction backwards — waste as `slab − part`,
which is the obvious one — and the finished planform is on screen before the
tool has touched anything.

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

Four documents, three of them generated. Start with the build guide.

| Doc | What it covers |
|---|---|
| **[fabrication.md](docs/fabrication.md)** | **The build guide.** Every step in order, what blocks on what, what runs in parallel, and the exact BOM lines each step consumes |
| [cut-list.md](cnc/cut-list.md) | *Generated.* Every flat part, the four core pieces, the milling table, and the deck-pad cutting pattern |
| [bom.md](docs/bom.md) | *Generated.* Every line, linked to the listing its price came from, with per-line confidence |
| [shopping.md](docs/shopping.md) | *Generated.* The same spend grouped by supplier — the order you actually place orders in |
| [shape-research.md](docs/shape-research.md) | Traced production boards and the shape law fitted from them |

The build guide quotes BOM item names verbatim, and
`python model/check_build_guide.py` verifies every one still exists - and
now every bolded figure in this file and in the guide against `report.json`
and `bom_stats.json`. 133 of 135 purchasable lines are claimed by a step; the
rest are contingency tools.

---

## Key numbers

| | V1 (built) | V2 (current model) |
|---|---|---|
| Dimensions | 1600 × 600 × 153 mm | 1400 × 560 × 143.7 mm |
| Sealed displacement | 96.6 L | 79.0 L |
| Board mass | 25–30 kg | 23.6 kg |
| Board reserve, alone | — | +55.4 kg |
| With an 86 kg rider | — | **-30.6 kg — a sinker at rest** |
| Pack | 14S9P, 2,268 Wh | 16S8P, 2,304 Wh, 9.22 kg, 397 × 188 × 78 |
| Cavity | 660 × 280 × 115 mm | 512 × 323 × 86 mm |
| Electronics | 2 sealed boxes | 1 removable module: printed ASA walls on a 5052 floor, **outward** lid flange |
| Mast plate | — | 6061-**T651**, 12.7 mm, **M6** tapped, 1.44× margin |
| Hatch | — | 12 × M5 into captive nuts printed into an ASA rim ring |
| Core splits | — | vertical at 1030 mm (bed length), horizontal at 101.6 mm (gantry) |
| Machining | — | 4 pieces, 5 setups, 1 flip, no cradle |
| Deck pad | — | 3 pieces of 5.8 mm EVA, one sheet does both boards |
| Cost | ~$3,900 spent | **$4,048/board**, 91% verified |

The board is a **sinker** — 79.0 L will not float a rider standing still.
That is a consequence of narrowing to 560 mm, but note it has moved twice:
an earlier revision of this README claimed "+12.0 kg — it floats the rider"
from when displacement was 114 L, and the pack-height correction has since
given 5 kg of it back. If floating at rest matters to you, that is the number
to argue with.

---

## Open questions

Ordered by what can actually stop the build.

1. **Will the makerspace allow EPS on the CNC?** Unanswered. It is a
   woodworking shop with no published material policy, and this is the one
   that can stop the booking outright. Maker Shop Boise, (208) 254-6151.
2. ~~**Cutter reach.**~~ **Closed.** The deepest pocket is the cavity's lower
   half at **71.6 mm** and the Freud O-flute cuts **31.8 mm**, which is where
   this question came from — but roughing never needed the reach (Z-level
   passes put the shank in open air) and the BOM has carried a **76.2 mm**
   wall-finish spiral for the one pass that does. The check was asking the
   roughing bit.
3. ~~**Wire bay stops at 68 mm.**~~ **Closed — it is 75.** The check that
   refused 75 was the in-build rim-segment volume test, the one later shown to
   report 53% of a ring that measures 99.96% in the saved file. It was
   measuring the booleans wrong, not the geometry. That test is demoted, and
   the bay is the 75 mm Derek asked for in the first place.
4. **Gong import duty.** Shipping is measured ($268.63 for two foils, from
   their checkout), but US customs is not. It arrives later as a courier
   invoice. Budget ~$210 if a 15% rate holds; the BOM carries it at zero so it
   is never mistaken for a verified figure.
5. **Sinker at rest** — see above. A design characteristic, not a defect, but
   confirm it is the one you want.
6. **V1's reed-switch kill system is still not installed.** Parts on hand.
   Required before any beginner rides that board.
7. **Measure the Gong top plate's four clearance holes.** `MAST_CLEAR_D` is a
   guess at 7.0 mm and it sets the *entire* positional budget for the four
   tapped holes in our plate — at 7.0 that budget is 0.25 mm, which is what
   makes it a machine-shop part rather than a drill-press one. A wider hole
   relaxes it; a tighter one may make it unbuildable by hand at all. **Derek
   has this plate** — he cut its wire slot.
8. **Where the mast's wire slot sits relative to the chord.** `CONDUIT_X_OFF`
   is 0, i.e. the conduit is assumed to be on the mast's centreline, and that
   is unverified. If it is not, the conduit and the plate's Ø30.8 bore are in
   the wrong place — and that bore is drilled and reamed into the one part
   that has to go to a machine shop.
9. **The charge port's flange pitch, and whether a screw cap ships with it.**
   `CHG_BOLT_PITCH` is 22 mm on a two-hole SP17 flange, and no drawing has
   ever been found for it — the four-on-a-20-mm-square pattern belongs to the
   EW-LP16, a different connector. These holes go into a **printed** wall, so
   order the connector early and measure it before the module shell prints at
   step 3. The cap matters just as much: it is the entire reason this
   connector was chosen over the LP16's nicer one-touch latch, and Renhotec
   list SP17 sealing caps as *available*, which is not *included*.
10. ~~**The module vent is the next barrier down.**~~ **Closed for water.**
    It was a $9.95 no-name "IP68 nylon breather", and IP68 with no stated
    depth or duration is a marketing string, not a rating. Now a **GORE
    PolyVent Stainless, M12 × 1.5, 316L** — tested to IEC 60529 at 2 m for
    1 hour, IP69K to ISO 20653, salt fog, UL 94 VTM-0 membrane, laser-marked
    for traceability. Against the **62.2 mm** of head this cavity can ever
    put on it that is **32×**, so it goes from the module's weakest opening
    to its strongest. Sized on Gore's own table: 1.6 L/min covers a 20 L
    enclosure and the module has ~3.3 L of free air, 6× over.
11. ~~**Nothing relieves a cell venting.**~~ **Answered, and better than
    feared.** The vent is still not relief — it passes **1.6 L/min** against
    the ~12 a runaway cell wants — but the box was never a pressure vessel
    either. Both lids are hard-stop bolted joints, and a bolted joint
    separates, dumps and re-seats: the **module lets go at 0.81 bar**, the
    **hatch at 0.87**. Both are ~7× the 0.11 bar a hot box makes going into
    cold water, so neither opens in service, and both are far under anything
    that stores dangerous energy. It will not be pretty, but it blows through
    rather than building up. Which lid goes *first* is not knowable — 7%
    apart on two numbers that each carry ±25% preload scatter — so the check
    asserts a **ceiling** on both rather than an order it cannot measure.
12. **Mast plate weight: both routes are blocked, and by different checks.**
    Derek is happy to trade the thread margin for the ~375 g. Tried, and the
    model refused it twice:
    - **Thinner (3/8 in)** → `FAILS: mast insert bore breaks into the cavity
      floor: only −0.5 mm above it`. The tap depth is not ours to choose — it
      is Gong's **M6 × 30 screw minus their mast head**, and the model
      *assumes* a 20 mm head it has never measured, giving 10 mm of
      engagement that a 9.5 mm plate cannot hold blind. 3/8 needs a head of
      **≥ 23.2 mm**, or shorter screws — and shorter screws land near
      0.9× thread-vs-bolt, which is our buried side failing *first*, not
      together.
    - **Smaller footprint (225 × 150)**, which saves the same weight without
      touching the thread → `FAILS: mast hardpoint shear path is under 1 g
      at 45° of bank: 0.91 g`. The footprint is not just prying; it is the
      area that feeds the mast's couple into the skins.

    So the plate is at its minimum on **both** axes and the 375 g is not
    free. **What unblocks it: measure Gong's mast head thickness** — the same
    trip to the caliper as questions 7 and 8.

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
| `model/check_build_guide.py` | Verifies the build guide's BOM references still resolve |
| `model/check_rim_segments.py` | Measures the rim segments from the SAVED .blend — the in-build check is not reliable |
| `model/animate_build.py` | The build animation, above |
