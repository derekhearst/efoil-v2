# eFoil board shape — what production boards actually do

Research behind the V2 hull in `blender_board.py`. Everything here is either a
published manufacturer figure or measured off manufacturer orthographic renders
with `trace_reference.py`.

## Published dimensions

Lift quotes 4" (100 mm) thickness across its **entire** range — every board,
42 L to 83 L.

| Model | L (mm) | W (mm) | T (mm) | Vol (L) | bbox fill |
|---|---|---|---|---|---|
| LIFTX 4'3 | 1300 | 480 | 100 | 42 | 67.3% |
| LIFTX 4'7 (Florence) | 1400 | 520 | 100 | 49 | 67.3% |
| LIFTX 4'8 | 1420 | 530 | 100 | 52 | 69.1% |
| LIFTX 5'2 | 1570 | 580 | 100 | 64 | 70.3% |
| LIFTX 5'4 | 1630 | 620 | 100 | 70 | 69.3% |
| LIFT5 4'4 Pro | 1320 | 570 | 100 | 55 | 73.1% |
| LIFT5 4'9 Sport | 1450 | 640 | 100 | 67 | 72.2% |
| LIFT5 Laird 5'2 | 1570 | 600 | 100 | 64 | 67.9% |
| LIFT5 5'4 Cruiser | 1630 | 700 | 100 | 83 | 72.7% |
| Fliteboard Air Pro S3 | 1580 | 647 | 110 | 80 | 71.2% |
| Fliteboard Air Icon | 1740 | 698 | 115 | 110 | 78.7% |

**Production eFoils are ~100 mm thick and fill 67–73% of their bounding box.**

The V2 spec assumed 45–47% fill. That number is real, but it belongs to
surfboards and prone foil boards — thin tapered rails, pointed nose, domed
deck. An eFoil is a battery box you stand on: boxy rails, blunt ends, flat
deck, thickness held nearly constant over most of the length.

## Traced silhouettes

Two boards traced from Lift's ortho product renders. Scale checks out — the
traced width of the 4'3 came to 481.8 mm against a published 480 mm.

| | LIFTX 4'3 | LIFTX 5'4 |
|---|---|---|
| Planform area fraction | 0.818 | 0.827 |
| Wide point (station from tail) | 0.50 | 0.525 |
| Half width at 0.10 from tail | 0.62 | 0.70 |
| Half width at 0.10 from nose | 0.63 | 0.66 |
| Thickness plateau | 0.10 → 0.55 | 0.10 → 0.55 |

The two boards agree closely, so the shape law is scale-invariant.

### Planform — a superellipse, near symmetric fore/aft

`(1 - u^n)^(1/n)` about a wide point at 0.50, with `n = 2.1` on the tail half
and `n = 2.5` on the nose half. That reproduces the traced area fraction of
0.82 and both tip roundings, and it needs no separate nose/tail rounding fudge
— the vertical tangent at `u → 1` rounds the tips on its own.

Both ends are far blunter than a surfboard. Half width is still ~0.63 of max
at 10% from the nose.

### Thickness — a plateau, not a spindle

Full thickness from 0.35 to 0.55, only ~5% down at 0.10, then a taper to a
thin nose. **The deck is dead flat lengthwise through the middle third.**

This is the single most useful finding, because it is what lets a big hatch
sit on one flat sealing plane. A surfboard-style centred thickness peak makes
the deck fall away in both directions and the flat land pinches.

### Rocker

Dead flat aft of 0.55, then (scaled to length) 12 mm at 0.70, 29 mm at 0.80,
55 mm at 0.90. A square law through 95 mm hits all three. The V2 spec's 78 mm
starting at 0.55 was close — rocker was the one parameter already right.

### Section — boxy

Planform × thickness integrates to 0.72 of the bounding box. Lift lands at
67–73% overall, so the section itself must be ~0.87 of its own box. That is a
near-rectangular section: flat deck most of the way out, rail apex just past
mid-height, hard chine below it.

## The hatch

From the deck render of the 4'3:

- The hatch is **flush**. The traction pad runs straight across it; the joint
  is a hairline.
- It is large — roughly a third of the board's length, and most of the
  standing width.
- Two flush pull-latches on the rail-side edges. Not a bolt pattern.
- Charge port and status LEDs are on the lid itself.

## What changed in the model

| | V2 spec | Now | Why |
|---|---|---|---|
| Thickness | 150 mm | 125 mm | 150 mm is a SUP number. 125 is a compromise — still 25 mm over Lift, which a DIY pack and a bonded floor need. |
| Volume | 53.9 L target | 64.1 L result | Falls out of the shape; volume is an output, not an input. |
| bbox fill | 45–47% assumed | 64.3% | Matches the production band. |
| Deck crown | 3 mm | 2 mm | Trades directly against hatch width — see below. |
| Lid recess | 14 mm | 2.6 mm | Flush, pad bridges the joint. |
| Thickness dist. | peak at 0.46 | plateau 0.35–0.55 | Flat land for the hatch. |
| Planform | pull factors | superellipse 2.1 / 2.5 | Fitted to the traced boards. |

### Deck crown drives hatch width

The gasket land is a flat plane, so every mm of deck dome pulls the usable
opening inboard. Going from 5 mm of crown to 2 mm took the hatch from 198 mm
to 280 mm wide — a 41% gain for a change nobody can feel underfoot. This is
why production decks are all but flat over the pad.

Cavity position was swept across 5 lengths × 16 positions; 320–940 mm is
already the optimum, giving a 620 × 280 mm pack rectangle (V1's proven cavity
was 620 × 300).

## Open items

- 64.1 L gives −38.8 kg net float at 86 kg rider + 17 kg board. Still a sinker
  at rest, which is normal — Lift ships 42–70 L for the same job.
- 125 mm leaves 11 mm of compression column between the G10 plate and the
  cavity floor. It works, but it is the tightest part of the stack-up.
- Only Lift boards were traced. Fliteboard's hard boards would be a useful
  second opinion, but their spec page blocks scraping.

## Sources

- [LIFTX range](https://liftfoils.com/pages/liftx-efoil)
- [LIFT5 range](https://liftfoils.com/pages/lift5-efoil)
- [4'3 LIFTX product page](https://liftfoils.com/products/43-liftx) (ortho renders traced)
- [Fliteboard model overview](https://e-surfer.com/en/blog/fliteboards-the-fliteboard-model-overview-2025/)
- [foil.zone — What is the optimal board shape?](https://foil.zone/t/what-is-the-optimal-board-shape/713)
