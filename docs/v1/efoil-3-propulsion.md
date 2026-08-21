# eFoil Build — Propulsion (V3)

**Last updated:** August 7, 2026 (as-built — mount assembled, prop mounted, real performance data)

---

## Motor
- Flipsky 65161 120KV (round, threaded shaft)
- Threaded 12mm shaft for community prop STL compatibility

## ESC
- Flipsky 75200 Pro V2.0 (aluminum PCB, 130×68×41mm)
- Built-in power button (not used — BMS switch handles power on/off)

## Remote
- Flipsky VX3 Pro remote + wireless receiver module

## Foil
- Gong Allvator V2 complete setup (Bons Plans):
  - Alu Mast V2 85cm (hollow — rubber plugs for wire access)
  - Top Plate Alu V2
  - Mast Fuselage Connector V2
  - Pro Alu Fuselage V2 (Regular)
  - Front Wing X-Over V2 XL (1,650 cm²)
  - Stab X-Over V2 48cm (335 cm²)
  - Complete Screw Kit Alu Foil V2

---

## Propeller
- Flipsky 65161 Propeller — 160mm diameter, 1.1 pitch, 3-blade
- Designed for the 12mm threaded shaft with M8 nut — plug-and-play, no adapter needed
- STL source: MakerWorld https://makerworld.com/en/models/433274
- Community reports: very good tolerances, snug shaft fit, blades thicker than aluminum equivalents (good for printed rigidity)
- Print: Lime green PETG, 0.4mm nozzle, 0.12mm layer height, 100% infill
- Post-processing: Sand 120→220 → brush coat TotalBoat epoxy → cure → wet sand 400→600-800 → second epoxy coat → wet sand → balance check (hang on bolt through center bore, sand heavy blade)
- Print 4-5 copies as spares

**Prop decision notes:** Community (DutchFoiler, Foilguy on foil.zone) recommended Flite prop ($45) with bore modification (ream to 12mm + pin adapter, ~$70 all-in). Decided to start with the MakerWorld 3D printed prop since it's plug-and-play for our shaft and free to print. Flite prop remains a backup option if printed props don't perform well. Flipsky's stock aluminum prop is universally considered poor for eFoils — skip it. DutchFoiler shared Flite prop drill guide STL: https://www.printables.com/model/583026-flite-prop-drill-guide

---

## Motor Mount
- jkoljo's FS65161 motor mount for Gong V2 mast (community-designed, proven, multiple builders confirmed fit)
- Thingiverse: https://www.thingiverse.com/thing:5996522
- **Configuration: No tail support, no shroud** — reduces drag, simplifies assembly
- Mount can be assembled without removing motor wires from mast
- Files to download (STEP format — Bambu Studio imports STEP natively):
  1. Gong_V2_mast_front_clamp.STEP
  2. Gong_V2_mast_rear_clamp_rev2.STEP (use rev2 — updated June 2023, fixes bolt pattern)
  3. Gong_V2_mast_clamp_nose_cone.STEP
  4. Gong_V2_mast_clamp_cable_cover.STEP
- Print: Lime green PETG, 0.6mm nozzle, 0.25mm layer height, 5 perimeters, 3 top/bottom layers, 40% triangular infill. Consider higher infill on front clamp (taking load without tail support).
- Optional: sand and epoxy coat mount parts to match board finish (purely cosmetic — they're underwater)

**Motor mount hardware — AS BUILT:**
- 4× M5 threaded rod cut from LWCUSNJ M5 × 250 mm stock. **Cut to ~171 mm (6¾"), measured off the real assembled stack — not the 155 mm estimate.** Always dry-assemble with one uncut rod and mark the actual length before cutting all four.
- 4× M5 nyloc nuts (ZQZ assortment)
- 4× M6 × 20 mm fender washers under the nylocs (GDFYMI, on hand — the 6.4 mm bore clears the 5 mm rod fine and the 20 mm OD spreads load). Documented substitution for M5 fenders.
- 4× M3 × 6 button head socket cap screws + 4× M3 brass heat-set inserts for the nose cone. **Heat-set at 230–250 °C for PETG** — start low, press straight, sink flush, let cool fully before threading.
- **Loctite 242 on the rod ends that thread into the motor** (no nut there, so thread engagement is all that holds them). The nyloc end does not need threadlocker — nyloc and Loctite solve the same problem two ways and doubling up is redundant.

**Cutting the rod:** hacksaw or a reinforced metal cutoff wheel in the rotary tool. Thread a nut on below the cut line first and back it off over the fresh end afterward to clean the mashed threads, then chamfer the tip. A burred end is what cross-threads the motor's aluminium.

**Prop shaft drive pin:** the shaft has a cross-hole and the printed prop has a matching slot. This is a drive/shear pin — it transmits torque and breaks before the shaft does on a strike. **Measure the hole with calipers rather than trusting a spec** (community 4 mm figures are for the plain 12 mm shaft, not necessarily the threaded variant). Use a stainless roll pin or dowel of the measured size. Never ream the shaft hole larger to fit a bigger pin.

**Prop nut:** M8 nyloc, stainless, with a washer under it against the printed hub. Snug against the shaft shoulder — **do not over-torque against PETG.** Set motor direction so running rotation tightens the nut. To hold the shaft while torquing, grip the prop body (the drive pin locks it to the shaft), not the rotor.

**Epoxy coating on the printed prop was skipped** for V1 — running it raw as a test article with 4–5 spares available. Trade-off accepted: layer lines add drag, and bare PETG slowly takes on water. **Do still balance-check it** (hang on a bolt through the centre bore, sand the heavy blade) — an unbalanced prop puts vibration straight into the motor bearings and the front clamp, which is carrying the load alone with no tail support.

---

## Performance — MEASURED (Aug 7, 2026)

Original estimates replaced with real logged data. See `efoil-7-vesc-config.md` for the full diagnosis.

| Mode | Power | Battery current | Source |
|---|---|---|---|
| Takeoff (measured, static water) | **4,169 W** | 78.8 A | VESC log, 150 A motor limit |
| Takeoff (expected at current limits) | ~5.3 kW | ~100 A | 180 A motor / 100 A battery |
| Foiling cruise (estimated) | 1,000–1,600 W | 20–30 A | X-Over XL 1,650 cm² is a large, low-speed wing |
| Plowing / displacement | 2,000–3,000+ W | 40–60 A | Worst case — this is what eats the battery |

**Why takeoff costs ~3× cruise:** at rest the hull is plowing with a huge wetted area and the foil produces almost no lift (lift scales with velocity squared). Once the foil lifts the hull clear, drag collapses by roughly 70–80 %. It's a threshold, not a gradient — which is why 1,271 W felt like nothing was happening rather than "almost."

**Realistic session:** ~30–45 min of motor-on time for early sessions, since failed water starts and plowing dominate. Not battery-limited — rider stamina and repeated restarts are the real limit. Turn around at ~46–48 V.

**Thermal:** peak FET 47.4 °C over a 66-minute session with repeated 4 kW pulls, settling to 37–38 °C. Cutoff starts at 80 °C. Passive cooling is performing better than expected.

**Board weight: MEASURED 66 lb / 29.9 kg** (17 Aug 2026, board complete with battery and electronics, foil off; noted as a minimum, so treat 29.9 kg as a floor). This replaces the earlier ~25-30 kg estimate, which was a guess and sat at the bottom of the real figure.

Back-calculating from it: bare hull ~15.4 kg, which puts the hand layup at ~3.0 kg/m2 against V2's vacuum-bagged 1.82 kg/m2 - the hand layup carried about 1.7x the resin per unit area. That single number is where most of V2's weight saving comes from.

V2 computes at 24.3 kg in the same configuration: **12.4 lb / 5.6 kg lighter, 19%**. Split: glass -3.8, plywood-to-G10 -1.2, foam -0.4.
