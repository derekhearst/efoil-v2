# V2 Materials & Pricing

**Created:** August 12, 2026
**Status:** Quantities are from the current model; prices are a mix of quoted
and estimated and are flagged as such.

Quantities come straight out of `blender_board.py` — rerun it after any
parameter change and these move.

---

## What each material actually is

Easy to conflate, so stating it plainly:

| | What it is | Density | Role |
|---|---|---|---|
| ~~G10 / FR4~~ | **No longer used** — see the box below | 1.85 g/cm³ | — |
| **ASA** | UV-stable styrenic, printed | 1.07 g/cm³ | Module shell, rim ring |
| **5052 / 6061 aluminium** | Sheet and plate | 2.70 g/cm³ | Module floor, mast plate, handle strips |
| **Divinycell H80** | Closed-cell PVC structural foam | 80 kg/m³ | Sandwich core, lids |
| ~~Divinycell H200/H250~~ | **Not used.** H-80 carries the mast block at 17.7× on plate bearing, and H-200 is not stocked anywhere normal | — | — |
| **EPS** | Expanded polystyrene bead foam | ~32 kg/m³ | Board core |
| **E-glass 6 oz** | Plain-weave cloth, fibres 0°/90° | — | Skins |
| **1708 biax** | ±45° stitched cloth + chopped mat | — | Local reinforcement |

**G10 is not foam.** It is solid, dense and rigid. H80 is the foam, and on its
own it is structurally almost nothing — it exists only to hold two glass skins
apart. That separation is where sandwich stiffness comes from, which is why
the lids are mostly foam rather than solid G10.

> ## SUPERSEDED — there is no G10 on this board any more
>
> This section was written when the hull carried three sheets of it. It went
> in four steps, and each one made the board lighter or simpler as well as
> cheaper:
>
> | Was | Is | Why |
> |---|---|---|
> | Module walls + flange rail, G10 | **printed ASA** | the G10 shell was *heavier* — 1,323 g against ~1,130 printed — and cost six CNC parts, a bond jig and a groove routed after assembly |
> | Module floor, G10 | **⅛" 5052 aluminium** | the ESC is sealed in with 128 cells and no airflow; G10 conducts 500× worse |
> | Mast plate, ¾" G10 + bonded bushings | **½" 6061, tapped** | 6061 shears at ~207 MPa against G10's ~55, so less material holds more — and it deletes the 316 bar, the lathe work and the DP460 |
> | Rim ring, ½" G10 | **printed ASA** | a groove printed flat is repeatable to ~0.05 mm, better than hand-routing G10 on a finished board |
>
> **$736 of G10 → $0.** The claim below — that foam cannot hold a threaded
> insert — is still true, and it is still what drives the design. What changed
> is the answer: heat-set inserts and captive nuts in printed ASA, and threads
> tapped straight into aluminium.

**Where a solid hardpoint is non-negotiable:** rim ring, mast plate, module
flange, lid bolt pucks. Foam cannot hold a threaded insert, and an insert
pulling out of a soft substrate is exactly how V1's hatch failed.

---

## Quantities for this build

| Material | Spec | Qty | Where it goes |
|---|---|---|---|
| EPS blank | ~2 lb/ft³ | 1500 × 650 × 185 mm (~0.18 m³) | Board core, milled in 2 halves |
| G10 | 3 mm | ~0.32 m² | Module floor, 4 walls, divider |
| G10 | 8 mm | ~0.05 m² | Mast plate (250 × 175) |
| G10 | 12 mm | ~0.10 m² if segmented | Hatch rim ring |
| G10 | 10 mm | small offcuts | Module flange rails, lid pucks |
| Divinycell H80 | 12 mm | ~0.19 m² | Hatch lid core |
| Divinycell H80 | 6 mm | ~0.12 m² | Module lid core |
| Divinycell H200/H250 | 28 mm | ~0.16 m² | Mast hardpoint ring |
| E-glass 6 oz | — | ~8 m² | 2 layers each face |
| 1708 biax | — | ~2.5 m² | Cavity walls, mast region, seam band |
| Epoxy | TotalBoat 5:1, slow | ~3 gal + Cab-O-Sil | Everything |
| Pour silicone | Shore 20–30A | ~30 cm³ needed; smallest kit is plenty | Hatch seal |

---

## Pricing

### Quoted (found on supplier sites, Aug 2026)

| Item | Price | Source |
|---|---|---|
| Divinycell H80, 3/8", 24 × 48 sheet | **$58.99** (qty 1–3), $48.99 (4+) | Fiberglass Supply Depot |
| G10 natural, 0.060", 12 × 24 | **$25.55** | ePlastics |
| G10 natural, 0.032", 24 × 48 | **$63.13** | ePlastics |
| Fiberglass sheet, 36 × 48 (thin gauges) | $46.70 – $140.00 | ACP Composites |

### Estimated from those rates

Scaling the ePlastics figures gives roughly **$90 per m² per mm of
thickness** for G10. That is a linear extrapolation and thick sheet is
usually cheaper per unit volume, so treat it as an upper bound.

| Item | Estimate | Confidence |
|---|---|---|
| G10 3 mm, 0.32 m² | ~$90 | medium |
| G10 8 mm, 0.05 m² | ~$35 | medium |
| **G10 12 mm rim ring** | **~$110 segmented / ~$300 as one blank** | low — get a quote |
| H80 12 mm + 6 mm | ~$120 (two part-sheets) | medium |
| H200/H250 ring | ~$80 | low |
| EPS blank | $150 – $350 | from efoil-8 |
| CNC time | $100/day pass × 2 | confirmed by you |
| E-glass + biax | $180 – $270 | from efoil-8 |
| Epoxy + fillers | $390 – $490 | from efoil-8 |
| Pour silicone kit | ~$35 | from efoil-1 |

---

## The one cost surprise

**The 12 mm G10 rim ring is the expensive part**, and it is expensive for a
stupid reason: cut as a single blank it needs a 483 × 392 mm piece of 12 mm
sheet and the entire middle becomes scrap. That is roughly $300 of material to
get $60 of ring.

**Cut it as four straight bars plus four corner pieces instead.** They nest
efficiently on a much smaller sheet, drop the material to ~0.10 m², and the
joints land in the middle of straight runs where they are structurally
irrelevant — the ring is bonded to the ledge along its whole footprint, so it
is not carrying bending as a ring.

Second lever: **RIM_T is 12 mm to swallow a 10 mm M5 insert.** Dropping to
10 mm with a shorter insert saves ~17% of the most expensive material in the
build.

---

## Open

- Real quote for 12 mm and 8 mm G10 — the extrapolated figure is the least
  trustworthy number here
- Whether the makerspace will allow G10 dust at all; if not, the rim ring is
  the one part that must be job-shopped
- H200/H250 availability — it is a different density from the H80 and often a
  separate order with its own minimum
