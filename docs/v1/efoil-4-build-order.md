> **V1 reference — not the current design.** This describes the board that was
> built, or early planning that predates the model. V2 is generated from
> `model/blender_board.py`; where the two disagree, the model and the docs
> linked from the [README](../../README.md) are correct.

# eFoil Build — Build Order & 3D Printing (V9)

**Last updated:** August 7, 2026

---

## CURRENT STATUS (Aug 7, 2026)

**Build is complete. In shakedown testing.**

| Phase | Status |
|---|---|
| 1 — Battery | ✅ Complete. Pack welded, BMS commissioned, charged and validated. **2–6 mV cell spread** under load and at rest — excellent. Zero OCP events in the BMS log, ever. |
| 2 — 3D printing / enclosures | ✅ Complete. Both enclosures sealed and **proven dry through three flooded-cavity tests.** |
| 3 — Foam & shaping | ✅ Complete |
| 4 — Fiberglass & finish | ✅ Complete. Painted, gasket in, traction pad on. |
| 5 — Electronics & assembly | ✅ Complete. Foil mounted, wires routed, full electrical test passed. |
| Water testing | 🔄 In progress — 3 sessions, all leak paths found and repaired, power problem diagnosed and fixed |

**Outstanding:**
- ❗ **Reed switch kill system not installed.** Parts on hand. This is the one real safety gap. Required before any beginner rides the board.
- Confirm cavity is dry after the latest round of sealing
- First successful foiling session

**Key corrections vs. the original plan:**
- Cam latches and PETG strike plates **abandoned** — lid is bolt-down with 6× M5 hex-drive inserts
- Hatch lid fiberglass **skipped** — epoxy hot coat only, so the hot coat is the sole water barrier
- Mast bolt pattern discrepancy (165 vs 190 mm) **resolved by using the Gong plate itself as the drill template** — no measurement needed
- Motor mount rods cut to **~171 mm**, not the 155 mm estimate
- VESC current limits raised from 80 A to **180 A motor / 100 A battery** — the 80 A motor limit was why the board wouldn't foil

---

## Build Order

### Phase 1: Battery

**1a. Cell prep & layout**
- Test all cells with multimeter — record voltages, reject any outliers (<3.5V or >3.7V out of box, or >20mV spread from pack average)
- Mark + terminal of every cell with sharpie dot (prevents orientation errors during assembly)
- Assemble Heyiarbeit 22.3mm spacer brackets into 9×14 grid (two spacer layers — top and bottom — holding cells from both ends)
- Load cells into holders with correct serpentine orientation: Row 1 positive up, Row 2 positive DOWN (rotated 180°), Row 3 positive up, Row 4 positive down, etc. Verify every row before moving to welding.

**1b. Cut nickel strips**

From SUIDI 0.2mm × 10mm × 5m rolls (2 rolls), cut:
- **28 P-group strips:** 10mm × ~210mm each. One for each row face (14 rows × 2 faces). Label each strip by row and face (e.g., "R1-top", "R1-bot", "R2-top", etc.).
- **117 bridging strips:** 10mm × ~30mm each. These connect individual cells between adjacent rows. Cut extras — small pieces are easy to lose or misalign.
- **Total nickel used:** (28 × 210mm) + (117 × 30mm) = 5,880mm + 3,510mm = 9,390mm = ~9.4m. Two 5m rolls = 10m total, leaves ~0.6m for mistakes/spares.

**1c. Pre-solder the 26 edge bridging strips with 8AWG jumpers (bench work, no cells)**

Of the 117 bridging strips, 26 will get 8AWG copper jumpers soldered along them (the 2 edge strips at each of the 13 row boundaries). Do this on the bench before any welding:

- Cut 26 short pieces of 8AWG silicone wire, each ~30mm long
- For each of the 26 edge bridging strips: lay the 8AWG wire along the length of the bridging strip and solder it down with good flux and plenty of solder. Pre-tin both surfaces first.
- Pull-test each solder joint — it should be strong enough that you can pull the wire moderately without it breaking off
- Label these 26 reinforced bridging strips distinctly from the 91 plain bridging strips

Middle bridging strips (91 of them) are left as plain nickel, no jumpers needed.

**1d. Prepare Pack + and Pack − end collector strips**

The Pack + strip is the Row 1 top P-group strip. The Pack − strip is the Row 14 bottom P-group strip. Both need a full-length 8AWG bus wire soldered along their length for low-resistance pack terminals:

- Pack + strip: 10mm × ~250mm (slightly longer than standard P-group strip to leave tail for termination). Solder full-length 8AWG wire (~280mm, runs past each end) along the entire nickel strip.
- Pack − strip: Same — full-length 8AWG bus wire soldered along the entire Row 14 bottom P-group strip.
- Pull-test solder joints.

**1e. Spot weld bottom face — P-group strips first**

Flip the 9×14 cell assembly upside down. Now you're accessing what will become the pack bottom.

- For each row, lay the bottom P-group strip over the 9 cells of that row and spot weld it down. 2 weld spots per cell in a line down the center of the strip (18 welds per P-group strip × 14 rows = 252 welds)
- Welder settings for 0.2mm pure nickel: Pulse 1 = 5-7, Space = 10ms, Pulse 2 = 15-18, Delay = 1s. Test on scrap first. Increase pulse strength if welds pull off; decrease if strip discolors or burns through.
- Row 14 bottom P-group strip is the Pack − (already has 8AWG bus wire pre-soldered) — weld it normally, the bus wire doesn't affect the welding.

**1f. Spot weld bottom face — bridging strips (alternating boundaries)**

Only 6 of the 13 row boundaries have bridging strips on the bottom face: R2-R3, R4-R5, R6-R7, R8-R9, R10-R11, R12-R13.

For each of these 6 boundaries:
- Place 9 bridging strips between the two rows, one per cell pair. Each bridging strip spans from one cell terminal in Row N to the corresponding cell terminal in Row N+1.
- 2 of the 9 bridging strips (leftmost and rightmost) are the ones with 8AWG jumpers pre-soldered. Place those at the edges.
- The 7 middle bridging strips are plain nickel.
- Weld each bridging strip with 2 spot welds per cell — 2 welds on the Row N side, 2 on the Row N+1 side. 4 welds per bridging strip.
- 9 bridging strips × 6 boundaries × 4 welds = 216 welds for bottom bridging

**1g. Voltage test bottom face so far**
- At this point, the pack has Row 2-3, Row 4-5, etc. connected in series pairs on the bottom face
- Not a fully connected pack yet — top face strips still needed
- Do a sanity check with multimeter at a few random bridging strips — should read ~3.6V across any series junction (next cell's voltage)

**1h. Flip pack, spot weld top face — P-group strips**

Flip cell assembly back right-side up.

- Weld all 14 top P-group strips (same process as bottom: 2 welds per cell, 252 welds total)
- Row 1 top P-group strip is the Pack + (already has 8AWG bus wire pre-soldered)

**1i. Spot weld top face — bridging strips (alternating boundaries)**

7 row boundaries have bridging strips on the top face: R1-R2, R3-R4, R5-R6, R7-R8, R9-R10, R11-R12, R13-R14.

- 9 bridging strips per boundary × 7 boundaries = 63 bridging strips on top face
- Same process as bottom: 2 edge strips have 8AWG jumpers (pre-soldered), 7 middle strips are plain
- 4 welds per bridging strip × 63 strips = 252 welds for top bridging

**1j. Voltage test fully assembled pack**
- Full pack voltage (Pack + to Pack −) should read ~50V (14 cells × ~3.6V) before charging
- Verify each cell group voltage individually by probing across each series junction — should read ~3.6V across each junction
- If any junction reads 0V, inspect the 9 bridging strips at that junction for bad welds

**1k. Balance lead attachment**
- Solder JK BMS balance harness wires to each of the 15 measurement points (Pack −, then each P-group + through the pack in sequence, ending at Pack +)
- Each balance wire solders directly to the P-group strip of the corresponding row — use the end of the strip near an edge where there's solid nickel (not on a weld spot)
- Route wires neatly along one long edge of the pack for later connection to BMS

**1l. Pack wrapping**
- Apply Kapton tape over all nickel + solder on BOTH faces of pack (top and bottom), covering all weld spots and solder joints
- Apply heat shrink tubing (300mm flat width PVC) around entire pack — shrink with heat gun until tight
- Cut small slits in shrink wrap at one short end to expose Pack + and Pack − bus wire ends for XT150 pigtail attachment
- Cut slit near balance harness exit point

**1m. BMS mounting and wiring**
- Place BMS flat on top of shrink-wrapped pack, centered on long axis
- 4 small dabs of silicone sealant between BMS corners and pack top — cure 24hrs to hold BMS in position against vibration
- Connect 2× 8AWG wires from Pack − bus to BMS B− terminals (parallel)
- Connect 2× 8AWG wires from BMS P− terminals to 150A ANL fuse (parallel on BMS side, combined into single 8AWG after fuse)
- Connect balance harness to BMS balance connector
- Connect NTC temperature sensor from BMS to pack surface (taped to cell body mid-pack)

**1n. Terminal pigtails & bench test**
- Solder XT150 connectors to short (~150mm) pigtails exiting the pack
- Pack + → XT150 positive pigtail (direct, no BMS interaction)
- Fuse output → XT150 negative pigtail
- Configure BMS via Bluetooth app: 14S Li-ion, current limits, temperature cutoffs
- Bench test: full pack voltage measurement, verify BMS reports all 14 cell voltages correctly, test push-button on/off switching
- Full pack should read 50-58V depending on state of charge

**Weld count summary:**
- P-group welds: 252 (bottom) + 252 (top) = 504 welds
- Bridging strip welds: 216 (bottom) + 252 (top) = 468 welds
- **Total spot welds: ~972**
- Plus 26 solder joints (8AWG jumpers to edge bridging strips) + 2 full-length solder joints (Pack +/- bus wires) + 15 balance lead solders + BMS connections

Plan for ~6-8 hours of welding spread across 2 evenings to avoid fatigue.

### Phase 2: 3D Printing — Enclosures

**Prerequisite:** Battery pack must be built, wrapped, and measured BEFORE committing enclosure CAD to print. Current dimensions (247×415×110mm exterior) are placeholders — real pack + BMS stackup drives final numbers.

**Battery enclosure (4-piece L-corner print):**
1. Measure assembled + wrapped pack with BMS silicone-mounted on top. Record footprint and total height.
2. Update Onshape enclosure model with measured values. Preserve 4mm walls + 10×10mm external vertical ribs + 20-bolt perimeter pattern (6 per long side + 4 per short side, corners dedicated).
3. Verify midpoint wall joints land in rib gaps (each corner piece ends at a full vertical rib that pairs with matching rib on mating piece for epoxy bond).
4. Print ONE corner piece first as test article (0.6mm nozzle, 0.24mm layer, 4 walls, 15% gyroid, ~233g/piece, ~6-8hr/piece). Test: rib cleanness, heat-set insert fit in scrap hole, joint dry-fit with a second test print later.
5. If test piece good, print remaining 3 corner pieces. **Mix materials** — 2 corner pieces in OVERTURE PETG green, 2 in ASA (UV + temp + printability balance). ASA pieces need draft shield + brim + 105°C bed on open-frame A1.
6. Install M4 × 8mm brass heat-set inserts in rib holes (5.2mm × 10mm deep). Soldering iron 220-230°C, 3-5 sec per insert, sink until d1 flush, let cool 30 sec before removing iron. Practice on scrap first.
7. Bond 4 corner pieces with thickened epoxy (TotalBoat + Cab-O-Sil). Scuff rib bond faces + wall overlap zone with 120 grit, wipe IPA. Assemble as 2× L-shape first, cure overnight, then bond L-shapes into full rectangle. Check diagonals for square while epoxy still green.

**ESC enclosure (single-piece print):**
1. Print single piece on A1 bed (fits at ~184 × 134mm footprint).
2. Install M4 × 6mm heat-set inserts (smaller stock, 5.3mm × 8mm deep holes) in rib positions — 8-10 bolts around perimeter.
3. No joint bonding needed (monolithic print).

**Aluminum plates (top + bottom, both enclosures):**
- 4mm 6061, cut to exterior flange dimensions of assembled enclosure
- Top plate: 20 × M4 clearance holes (4.5mm) matching rib bolt pattern for battery enclosure; 8-10 M4 holes for ESC enclosure
- Bottom plate: no bolt holes (permanent bond)
- Source: SendCutSend with DXF export from Onshape, OR DIY cut with jigsaw + drill (plywood template for hole positions)
- Drill method for DIY: sandwich aluminum between two MDF/plywood pieces, drill through sandwich at low RPM with cutting oil

**TORRAMI neoprene gaskets (top lid seals, both enclosures):**
- Trace aluminum top lid outline onto 1/8" TORRAMI sheet
- Cut perimeter with box cutter
- Punch bolt clearance holes with UNCO 5mm hollow punch (M4 bolt = 4mm shank, 1mm undersize for compression seal around shank)
- No adhesive — gasket sits between aluminum lid and PETG flange top, compressed by bolt torque

**Supporting prints (unchanged):**
- Print hinge shims (PETG, sized to Pyntrax 6" strap hinge leaf) → print motor mount parts (PETG, 0.6mm nozzle) → print props (PETG, 0.4mm nozzle, 100% infill) → sand and epoxy coat props

**NO LONGER NEEDED:** ~~Cam latch strike plates for battery enclosure~~ (was originally planned with Gustav-style toggle latches — replaced by bolt-down design)

### Phase 3: Board — Foam & Shaping
Buy 2 sheets XPS foam from Lowe's (4 blanks, 3 needed + 1 spare) → pre-cut ALL three layers on flat workbench with utility knife and wood chisel (660×280mm cavity through-cut on all layers same width starting 300mm from tail, shallow 19mm recess in Layer 3 top face for hatch lid, shallow 19mm recess in Layer 1 bottom for plywood, reed switch pocket + 30mm wire channel in Layer 3 at 250mm from tail — all done while slabs are flat) → epoxy 3/4" plywood base plate into Layer 1 recess, flush with hull surface → epoxy plywood backing blocks (80×45×19mm offcuts) to Layer 3 recess ledge at 2 hinge locations on nose-side short edge → glue layers with Gorilla Glue (clamp/weight overnight) → factory foam edge = board width (600mm), cut nose and tail outlines from cardboard half-template (three-zone geometry: 200mm flat tail → R500 convex arc to full width over 400mm → 600mm parallel midsection → R845 concave arc from full width to 100mm flat nose over 600mm) → shape nose bevel (bottom surface rises 130mm over 600mm along a Rho 0.5 parabola, starting at 1000mm from tail) → shape edges in CAD order: (1) Chamfer 1: 40mm × 60° top perimeter chamfer, full top edge; (2) Fillet 1: R50 nose rails only; (3) Chamfer 2: 40mm × 60° at bottom of nose vertical face; (4) Fillet 2: R20 full top perimeter — bottom edges stay sharp 90° everywhere except Chamfer 2 → smooth entire board 80→120 grit → fill any foam dings with thickened epoxy

### Phase 4: Board — Fiberglass (No Vacuum Bag, One Layer at a Time)
Fillet all internal cavity corners with thickened epoxy → glass cavity interior (2 layers, water-bag pressure) → glass hatch recess area (3 layers for strength) → seal all internal surfaces → glass hull bottom (4 layers, one at a time, cure/sand between each) → glass deck top (4 layers, one at a time, overlapping cured bottom at rails) → drill mast bolt holes (6.5mm clearance, 90×165mm pattern centered at 400mm from tail) and wire pass-through from below using Gong top plate as template → fabricate hatch lid (3/4" ply + 3-4 layers glass each side; finish-sand underside contact ring 220 grit + neat epoxy hot coat) → install 2× Pyntrax strap hinges on nose-side short edge with shims → set 6× M5 hex-drive inserts in ledge blocking, drill 7/32" lid clearance holes off the installed inserts → hot coat → prime → paint lime green → clear coat → **install hatch gasket on ledge** (scuff ledge 220 grit, double IPA wipe, peel PSA liner, press Trim-Lok X2897BT into continuous loop starting at long-edge midpoint, bend around corners, CA dab on butt joint, silicone grease on top surface, **leave hatch open 72 hours for PSA to cure before first latching**) → install traction pad (two pieces split at the hatch seam, bolt-hole cutouts, pull-loop gap)

### Phase 5: Electronics & Assembly

**Enclosure install in board cavity:**
1. Install sealed battery enclosure on plywood base plate (forward section)
2. Install sealed ESC enclosure on plywood base plate (mid section, forward of mast bolts)
3. Route phase wires from ESC box through plywood wire hole
4. Assemble XT150 connections in CESFONJER IP68 housings (6 housings on hand: 2 battery + 3 phase + 1 spare)
5. Route reed switch wire through foam channel into ESC box
6. Install water alarm sensor low in cavity

**Bench test before mast install:**
7. Motor in bucket of water, run through VESC Tool setup
8. Verify BMS bluetooth app reports all 14 cell voltages correctly
9. Test push-button on/off from battery enclosure
10. Test remote pairing and ESC response

**Mast mount assembly:**
11. **RESOLVED:** the Gong plate arrives pre-drilled — use the plate itself as the drill template rather than measuring. Centre it on the board centreline at 400 mm from the tail, pilot one hole, drop a bolt to lock it, then drill the rest. Drill 1/4" (0.250") through glass + plywood — the 15/64" bit in the Ryobi set is effectively zero-clearance on an M6 shank and will fight you.
12. Trace Gong plate outline onto TORRAMI 1/8" neoprene sheet; mark 4 bolt holes + phase wire pass-through position
13. Cut gasket perimeter with box cutter; punch 4× bolt holes with UNCO 5mm hollow punch (undersized vs 6mm bolt shank for self-seal); cut phase wire pass-through to match Gong plate opening
14. Assemble Gong V2 foil (mast → fuselage → wings → stab per Gong instructions)
15. Mount motor to mast using jkoljo V2 mount (4 parts PETG, already printed)
16. Feed phase wires through hollow mast from top plate end down to motor end
17. Bolt foil to board: 4× Mywish M6 × 50mm button head stainless, up from below through Gong plate → TORRAMI neoprene gasket → hull fiberglass → plywood → cavity fiberglass → GDFYMI M6 × 20mm fender washer → M6 nyloc
18. **Torque 8-10 N·m per bolt, star pattern, two passes** (first pass 5 N·m, second pass 10 N·m) — use 1/4" drive torque wrench
19. No 4200 or dielectric grease anywhere at mast mount — neoprene gasket is the complete seal, fully removable for Prius transport

**Final assembly and ride:**
20. Connect all 5 CESFONJER IP68 housings (XT150 power + phase)
21. Seal hatch — Trim-Lok gasket **mitred at the corners** and RTV-bonded, strap hinges on nose edge with an empirically-shimmed spacer, 6× M5 bolts with fender washers
22. **Submersion test with the cavity sealed but EMPTY** (no battery, no ESC) before trusting any seal
23. Maiden voyage at Lucky Peak Reservoir

---

## 3D Printing Summary

| Part | Material | Nozzle | Layer Height | Infill | Wall Thickness | Qty |
|---|---|---|---|---|---|---|
| Battery enclosure (4-piece L-corner split) | PETG green + ASA mix | 0.6mm | 0.24mm | 15% gyroid | 4mm wall + 10×10mm external ribs | 4 pieces (~233g each, ~932g total) |
| ESC enclosure (single piece) | PETG green | 0.6mm | 0.24mm | 15% gyroid | 4mm wall + 10×10mm external ribs | 1 |
| Hinge shims | PETG green | 0.4mm | 0.2mm | 100% | — | as needed |
| Motor mount (4 parts) | PETG green | 0.6mm | 0.25mm | 5 perimeters, 40% | — | 1 set |
| Propellers | PETG green | 0.4mm | 0.12mm | 100% | — | 4-5 |

**Material notes:**
- OVERTURE PETG Grass Green — 1kg on hand (delivered Apr 14). Covers ESC enclosure + hinge shims + motor mount + props. Split usage with ASA for battery enclosure to avoid running out.
- ASA — near-full roll on hand. Better UV + temp resistance than PETG, marginally harder to print on open-frame A1 (needs draft shield + brim + 105°C bed for warp control). Use for 2 of the 4 battery enclosure corner pieces.
- Heat-set inserts: Ktehloy 400pc kit — use M4 × 8mm for battery enclosure (5.2mm × 10mm deep holes), M4 × 6mm for ESC enclosure (5.3mm × 8mm deep holes).
- Bolts: Mr. Pen 810pc kit — M4 × 16mm button heads for battery enclosure, M4 × 12mm button heads for ESC enclosure.
