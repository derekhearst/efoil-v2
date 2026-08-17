# V2 Powertrain — Options Research

**Created:** August 11, 2026
**Status:** Research. No decision made.

V2 gets a fresh powertrain, so motor / ESC / BMS are all open. This collects
the options against what V1 actually measured, rather than against spec sheets.

Prices are indicative — several community figures are years old and are marked
where that's the case.

---

## What V1 measured (the actual requirement)

Everything below has to beat or match these, not a datasheet number.

| | Measured | Configured limit |
|---|---|---|
| Peak power | 4,169 W | ~5.3 kW expected at limits |
| Peak battery current | 78.8 A | 100 A |
| Peak motor current | 153.3 A | 180 A |
| Peak FET temp | 47.4 °C | 80 °C cutoff |
| Peak ERPM | 13,977 (≈4,660 rpm mech) | — |
| Cruise | 1,000–1,600 W / 20–30 A | — |

**The 75200 Pro V2 is not the limiting factor.** It ran 4.1 kW with peak FETs
at 47.4 °C against an 80 °C cutoff, on passive cooling. Any replacement is
being bought for reliability, form factor or voltage headroom — not because
the current one is short of capability.

---

## The architecture question — already solved

The requirement: **never disconnect the ESC from the battery**, charge through
a separate waterproof port, one button, three phase wires out.

A **common-port BMS does this natively.** Charger and load share Pack+ / P−,
so both stay permanently wired in parallel:

```
Pack +  ──┬─────────────────────────────► ESC  (hard wired, never unplugged)
          └─────────────────────────────► charge port
Pack −  → BMS B− → MOSFETs → P− → fuse ──┴─
```

Every JK BMS in the 16S / 150 A class is common-port, so this needs no special
part. Two things fall out of it:

**It fixes the anti-spark discipline.** V1's rule was "BMS must be OFF during
connector mating" because the ESC shared the charge connector. Hard-wire the
ESC and the connection is *always* mated, so the BMS soft-start always works.
The workflow rule disappears rather than being followed carefully.

**Watch the live charge pins.** Common port means the charge port sits at pack
voltage whenever the BMS is on. Use a shrouded board-side connector, and note
that the normal workflow (BMS off between rides) leaves it dead. Verify the JK
wakes on charger detection, or just press the button — it's there anyway.

A separate-port BMS would buy electrical independence of the charge path, but
nothing that matters here.

---

## Voltage: 14S vs 16S

16S8P = **128 cells. 130 were bought.** No extra cells needed.

| | 14S9P (V1) | 16S8P |
|---|---|---|
| Cells | 126 | 128 |
| Nominal / full | 50.4 / 58.8 V | 57.6 / 67.2 V |
| Energy | 2,268 Wh | 2,304 Wh |
| Current @ 5.3 kW | 105 A | 92 A |
| Per cell | 11.7 A | 11.5 A |

Same margin against the 15 A cell rating, slightly more energy, ~12% less
current everywhere — pack, nickel, wiring, FETs. 67.2 V is comfortable against
the 75200's 84 V ceiling.

**Costs:** a new charger (67.2 V, not the current 58.8 V), a 17-tap balance
harness instead of 15, and — if the BMS pocket is wanted — a 660 mm cavity so
the columns split 9 + 7 rather than 8 + 8.

**Possibly free:** the current BD6A20S15P reads like a 20S-capable board. If it
is, 16S is a reconfiguration, not a new BMS. Confirm in the JK app.

---

## Motor

### The 65161 family

Flipsky, Maytech and Reacher 65161/65162 are the **same underlying motor** —
community consensus is they differ in shaft, seals and bearings, not
performance. Flipsky is generally recommended, not because the motor is
better, but because the **12 mm threaded shaft takes aftermarket props**
(including the Flying Rodeo prop, widely described as faster and more
efficient than stock). Maytech uses a proprietary prop connector.

65161 spec: 6–20S (25.2–84 V), 100 or 120 KV, 3,000 W rated / 6,000 W peak,
200 A peak, D65 × L161 mm, IP68, ~$330–450.

### 65161 vs 65162

The 65162 is the same diameter but longer — roughly 40–60% more power for
about 70% more weight. Given V2's second pillar is **light weight** and V1
never exceeded 4.2 kW against a 6 kW rating, the extra mass buys headroom
that has not been needed.

### Flying Rodeo

Widely called the best direct-drive eFoil motor available, and what Lift uses.
€1,000+. The quality step, at roughly 2–3× the price.

### KV choice — this interacts with 16S

Community default is 120 KV, and that's at 12–14S. Moving to 16S changes the
arithmetic, because no-load RPM is KV × volts:

| Setup | No-load RPM | vs V1 | Current for same thrust |
|---|---|---|---|
| 14S / 120 KV (V1) | 7,056 | baseline | baseline |
| 16S / 120 KV | 8,064 | +14% top end | ~12% less |
| 16S / 100 KV | 6,720 | −5% | **~17% less** |

Lower KV means higher torque per amp. So:

- **16S + 120 KV** — more top speed, less current. Serves pillar 1 (fast top end).
- **16S + 100 KV** — same speed as today, meaningfully less current and heat
  everywhere. The efficiency play.

Note the community's 120 KV preference is about *getting up* on lower-voltage
packs. At 16S that argument weakens, because the volts make up the RPM.

---

## ESC

All of these clear 16S (67.2 V). Bluetooth column matters because the
integrated BLE on the current ESC is confirmed working and is worth keeping.

| ESC | Rating | Bluetooth | Notes |
|---|---|---|---|
| **Flipsky 75200 Pro V2** | 75 V / 200 A, 84 V max | Integrated BLE | Incumbent. Proven at 4.1 kW / 47.4 °C in this exact build. Community gripes about Flipsky build quality; uses low-side shunts. Cheapest credible option. |
| **Spintend Ubox V2.1** | 75 V / 200 A, <80 V peak | 2.4 GHz BT module | "Well designed, works out of the box" is the recurring community line. Dual-motor board, so half is wasted here. |
| **Spintend single Ubox alu** | 85 V / 150 A | Module | ~$139. More voltage headroom than the 75 V parts; 150 A is above V1's 153 A motor peak but not by much. |
| **Tryforce A200S v4.1** | ~200 A | — | ~40 °C passive. Small. Strong support reputation (free out-of-warranty replacement reported). Significantly more expensive. |
| **JetFleet6 (20S)** | 150 A cont / 350 A peak | — | 60 × 80 × 20 mm — tiny. "Excellent FETs, unmatched thermals." From the onewheel world. |
| **Trampa VESC** | varies | — | Phase shunts rather than low-side — better current sensing. Premium price. |
| **MakerX Hi200** | — | — | Discontinued. |

**Community consensus, paraphrased:** every other brand is better built than
Flipsky; Flipsky can do the power but takes more tuning and understanding to
get there. Water ingress, not ESC capability, is the failure mode that
actually kills eFoil ESCs.

---

## This is a second board, not a rebuild

V1 stays intact and rideable, so V2 buys a complete second powertrain. Two
things follow.

### 16S is now free

Every argument against 16S was a switching cost, and switching costs vanish
when nothing is being switched:

| | 14S | 16S | Delta |
|---|---|---|---|
| Cells | 126 | 128 | +2 of the 130 on hand |
| Charger | new, 58.8 V | new, 67.2 V | same cost |
| BMS | new | new | same part family (JK 8–24S) |
| ESC | 75200 (84 V max) | 75200 (84 V max) | unchanged |

Nothing costs more. **Go 16S.**

### Budget

Board figures are efoil-8's; powertrain is reconstructed from the V1 spend.

| | Low | High |
|---|---|---|
| EPS blank + CNC | $230 | $550 |
| PVC foam core, G10 | $170 | $235 |
| E-glass + biax | $180 | $270 |
| Epoxy + fillers | $390 | $490 |
| Vacuum pump + consumables + practice panels | $310 | $520 |
| Hardware, O-ring stock, connectors, door, sealants | $195 | $250 |
| Finishing | $150 | $240 |
| **Board subtotal** | **$1,625** | **$2,555** |
| Motor + ESC + remote | $558 | $558 |
| BMS + charger | $119 | $150 |
| Cells (130 × 21700) | $585 | $780 |
| Nickel, glands, fuse, filament, alu plate | $150 | $200 |
| **Powertrain subtotal** | **$1,412** | **$1,688** |
| Gong foil | $975 | $975 |
| **Total** | **$4,012** | **$5,218** |

**The foil is the single biggest line, and it may be optional.** The Gong
already fully separates for transport — four M6 bolts and five connector
housings, zero wires tethering. If V2 replaces V1 as the board being ridden
rather than running alongside it, one foil serves both and the build drops to
**$3,037–$4,243**. That is not salvaging V1; the foil bolts back on in
minutes.

The vacuum pump and practice panels are one-time. Every hand tool is already
owned.

### Where not to spend

The improvement list for V2 is weight, size, exterior shape, layup quality,
lid and O-ring, and cavity simplicity. **Every one of those is board-side.**
Flying Rodeo (+$700) and Tryforce buy top-end and build quality that no item
on that list asks for. Repeat V1's powertrain choices — they are proven in
this exact application with logged data behind them — and put the money into
the hull.

---

## Assessment

Nothing here is a decision, but the shape of it:

- **BMS** — stay with JK. Common-port is exactly what the new architecture
  wants, the Bluetooth is genuinely useful, and V1's data (2–6 mV spread, zero
  OCP events) says the current one is doing its job. Check whether the existing
  board does 20S before buying anything.
- **Motor** — 65161, not 65162; the weight is the wrong trade for V2. KV is the
  real decision and it depends on whether top speed or thermals matters more.
  Flying Rodeo only if the budget stretches and top end is the priority.
- **ESC** — the honest answer is the incumbent already does the job with a 33 °C
  thermal margin. The case for changing is build quality and support, not
  capability. Spintend is the value alternative; Tryforce is the buy-once
  option; JetFleet6 is the one to look at if cavity space gets tight.

**For a rental/lessons fleet, weight the support relationship heavily.** A
board down for three weeks waiting on a warranty claim costs more than the
price difference between any two of these.

---

## Open

- Confirm BD6A20S15P maximum series count in the JK app
- Flying Rodeo current pricing and specs — not published clearly; ask directly
- Whether 16S changes the prop (higher RPM at 120 KV may want less pitch)
- Tryforce / JetFleet6 current pricing and availability
