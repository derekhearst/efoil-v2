# eFoil Build — Electrical & Battery (V7)

**Last updated:** August 7, 2026 (pack validated in service; kill switch status corrected)

---

## Battery Pack Design

**Configuration:** 14S9P, 126 cells (4 spares), 45Ah, ~2,331 Wh, 135A max continuous

**VALIDATED IN SERVICE (Aug 2026):**
- Cell spread **2 mV at rest, 6 mV under load** — the all-welded stacked-nickel architecture delivered exactly the uniform current distribution it was designed for
- **Zero overcurrent events** in the entire BMS log history
- Under a 78.8 A draw, pack voltage sagged only 56.8 V → 52.8 V. That is ~8.7 A per cell against a 15 A rating — the cells are barely working.
- Peak temp 31 °C charging, 26.9 °C discharging
- **Operating limits set to 100 A** at the VESC (~11 A/cell). BMS trip stays at 120 A as last-resort protection, deliberately above the operating ceiling so it never fires in normal riding.
- Cell type in the JK app is correctly set to **NCM/NCA** — this *is* lithium-ion; the BMS labels by cathode chemistry (NCM/NCA vs LFP vs LTO), not by the generic Li-ion umbrella.
- Charger: 58.8 V / 5 A, custom XT150 pigtail. Small connection spark on plug-in is normal inrush to the input capacitors, not a fault.

**Pack dimensions:** 211mm × 339mm × 82mm (9 cells wide × 14 rows deep in Heyiarbeit spacer brackets, single layer flat, cells standing upright. Cell spacing 22.3mm center-to-center within a row, 24.2mm row-to-row. Height includes nickel strips, 8AWG jumpers, Kapton, and shrink wrap on both faces. Confirmed via Onshape model.)

**Layout:** Zigzag serpentine pattern. Cells alternate orientation row-by-row — Row 1 has positive terminals facing up, Row 2 is rotated 180° (negatives up), Row 3 matches Row 1, etc. Series connections between adjacent rows are made via 9 individual bridging nickel strips per row boundary, with the 2 edge bridging strips reinforced for current capacity.

> **AS BUILT — the copper jumpers were not used.** The design below specifies 26 8AWG copper jumpers soldered along the edge bridging strips. The pack that was actually built reinforced those strips with **a second welded layer of nickel** instead, which is why the summary above calls it an all-welded stacked-nickel architecture. No solder went near a cell. Measured result was 2 mV spread at rest and 6 mV under load, so the substitution worked. **V2 follows the as-built version, not the design.** The copper-jumper section that follows is kept because its current-distribution analysis is still the reason the edges need reinforcing at all — only the method changed.

**Interconnect method — P-group strips + individual bridging strips:**

- **Nickel strip material:** SUIDI 0.2mm × 10mm × 5m pure nickel (99.6%), Amazon B0961Q1VVR. Two rolls ordered to cover the full pack (~7m needed total). 0.2mm is the sweet spot for the Battery Hookup capacitor spot welder (rated 0.3mm pure nickel max, performs best at 0.2mm), and 10mm width allows 2 weld spots per cell in a line down the center of each cell terminal.

- **28 P-group strips (parallel connections within each row):**
  - 14 strips on TOP face (one per row, running along all 9 cells of that row, ~210mm long)
  - 14 strips on BOTTOM face (one per row, ~210mm long)
  - Each P-group strip ties together the 9 cell terminals of its row into a parallel group
  - Every cell gets ONE weld on top face (to its row's top P-group strip) AND ONE weld on bottom face (to its row's bottom P-group strip)

- **117 individual bridging strips (series connections between rows):**
  - 13 row boundaries × 9 bridging strips per boundary = 117 strips
  - Each bridging strip is small (~30mm long × 10mm wide) and connects ONE cell in Row N to its partner cell in Row N+1
  - **Bridging strips alternate faces per boundary to prevent shorts:**
    - R1-R2 boundary: 9 bridging strips on TOP face
    - R2-R3 boundary: 9 bridging strips on BOTTOM face
    - R3-R4 boundary: 9 bridging strips on TOP face
    - ...alternating, 7 boundaries on top + 6 boundaries on bottom = 13 total
  - Why alternate: if both faces had bridging strips at the same boundary, you'd short the pack through the cells
  - Each cell gets a SECOND weld on one face (to a bridging strip) in addition to its P-group strip weld on that same face

- **26 × 8AWG copper jumpers (current capacity reinforcement):**
  - 2 jumpers per row boundary (on the leftmost and rightmost bridging strips of that boundary)
  - Each jumper is a short piece of 8AWG silicone wire (~25-30mm), soldered along the length of the bridging strip to add copper in parallel with the nickel
  - 13 boundaries × 2 edge jumpers = 26 jumpers total
  - Middle bridging strips (the 7 inner ones at each boundary) are pure nickel only — no jumpers needed because 9 parallel nickel paths already distribute current well

- **Weld count per cell:** Each cell has 2 terminals (top and bottom). Each terminal gets:
  - 1 weld to its P-group strip (parallel connection)
  - 1 weld to a bridging strip (series connection to next row) — but only on ONE face per boundary
  - Total: 4 welds per cell (2 on top, 2 on bottom) × 2 spot welds per point = ~8 spot welds per cell × 126 cells = ~1,000 welds total
  - Actually refined count: 252 cell terminal positions × 2 welds per P-group connection + 252 cell terminal positions × 2 welds per bridging strip connection = ~1,008 welds

- **Pre-weld workflow:** Pre-solder the 26 edge bridging strips with their 8AWG jumpers on the bench BEFORE welding to cells. No soldering heat near cells, ever. Middle bridging strips go in plain (no jumpers).

**End collectors (pack terminals):**

- **Pack +** on top face of Row 1: the Row 1 top P-group strip itself IS the Pack + terminal — a full-length 8AWG bus wire soldered along its length provides the low-resistance current path out of the pack. Terminates in XT150 positive pigtail exiting the battery enclosure.
- **Pack −** on bottom face of Row 14: the Row 14 bottom P-group strip IS the Pack − terminal — full-length 8AWG bus wire soldered along its length. Routes to BMS B− terminals (see wiring chain below).

**Balance leads:** JK BMS ships with pre-made 15-wire balance harness. Wires solder directly to the P-group strip of each row at the series junction points. Wires 1 and 15 double as pack voltage sensing (no separate B+ power terminal needed — see "Common-port BMS" section below).

**Main leads:** 8AWG silicone wire, XT150 connectors on short pigtails exiting the battery enclosure through cable glands.

**Pack wrapping sequence:**
1. Kapton tape over all exposed nickel + solder joints on both faces of pack
2. Heat shrink wrap around entire cell pack (top, bottom, sides) — single PVC shrink tubing sleeve
3. BMS sits on top of shrink-wrapped pack (NOT inside shrink wrap — BMS must remain separable for diagnostics/replacement)
4. Small dabs of silicone sealant between BMS corners and pack top to hold BMS in position against vibration

**Current demands:** Cruising ~15-25A battery, water-start extended 60-120s at 50-70A, takeoff peaks ~70-100A (1-5s bursts). Per cell at takeoff: ~8-11A (well under 15A rating).

**Why this architecture handles current well:**
- **Series current distributes across 9 parallel bridging strips per junction.** At 100A pack peak, each bridging strip carries ~11A — well within the 25A continuous rating of 0.2×10mm pure nickel.
- **The 2 edge bridging strips have 8AWG copper jumpers soldered along them.** At those 2 locations, copper (16.6 mm² via single 8AWG) is in parallel with nickel (2.0 mm²). Copper is ~4× more conductive per mm², so conductance ratio is ~8:1 copper vs nickel per edge strip. Copper carries ~89% of the current at edge bridges.
- **Effective current split across 9 bridging strips at a junction:**
  - 2 edge strips each carry ~25A total (23A copper + 2A nickel)
  - 7 middle strips each carry ~11A (all nickel)
  - Total: 2×25A + 7×11A = 127A capacity vs 100A peak demand — 27% margin
- **P-group nickel strips only carry parallel balancing current** (milliamps to low amps between cells), not pack-level current. Width is not a bottleneck.
- **Redundancy:** If any single bridging strip or jumper fails, 8 others continue carrying current. No single point of failure.
- This approach is community-standard on foil.zone for high-current builds.
- Alternative approaches considered and rejected: true copper-nickel sandwich (welder power inadequate), nickel-plated copper (requires separate nickel layer on top to weld reliably), wider/thicker pure nickel strip (not needed given 9-parallel-strip redundancy).

## BMS Placement on Pack

**Position:** BMS sits flat on top of the shrink-wrapped pack, centered on the pack's long axis. Oriented with its long edge parallel to the pack's long axis.

**Clearance for jumpers:** The 26 8AWG jumpers sit along the two long edges of the pack (one pair per row boundary, one on each edge, but alternating which face — so 13 jumpers on top face edges, 13 on bottom face edges). The BMS footprint (162 × 102mm) is narrower than the pack (211 × 339mm), so ~54mm of pack top is exposed on each long edge for jumper routing. BMS does NOT sit on top of jumpers — BMS sits on flat P-group strip area only.

**Common-port BMS configuration:** The JK BD6A20S15P is a common-port (common positive) BMS — it switches only the negative rail. Pack + is a straight pass-through that never goes through the BMS.

**BMS terminal layout (per listing):**
- **2× P−** on one short edge (ESC/load side, downstream of MOSFETs) — parallel wires for high-current capacity
- **2× B−** on opposite short edge (pack side, upstream of MOSFETs) — parallel wires
- **No dedicated B+ terminal** — pack positive is monitored via balance wire #15 (connects to Row 1 top, pack absolute positive)
- **Balance harness** exits the bottom edge of the BMS, fans out to the 15 series junction points

**Current flow (discharge):** Pack + bus bar → XT150 positive (direct, bypasses BMS) → ESC. Pack − bus bar → 2× 8AWG wires → BMS B− terminals (parallel) → through MOSFETs → BMS P− terminals → 150A ANL fuse → XT150 negative → ESC.

**Current flow (charge):** Charger + → XT150 positive → Pack + (direct). Charger − → XT150 negative → fuse → BMS P− → MOSFETs → BMS B− → Pack −. BMS can cut off charge if any cell hits overvoltage.

**Wiring chain:**
```
Pack + bus bar → 8AWG → XT150+ pigtail (direct, never touches BMS)
Pack − bus bar → 2× 8AWG → BMS B− (×2) → BMS MOSFETs → BMS P− (×2) → 2× 8AWG → 150A ANL fuse → 8AWG → XT150− pigtail
XT150 pair (out of battery enclosure) → CESFONJER IP68 housing → XT150 into ESC enclosure → 75200 Pro V2 ESC
3× Phase wires out of ESC → 3× CESFONJER IP68 housings → XT150 phase connectors → plywood wire hole → Gong top plate → hollow mast → motor
```

## Height Stackup (fits in 106mm internal enclosure cavity)

| Component | Height | Running total |
|---|---|---|
| Bottom of cells sitting on silicone-sealed aluminum plate | 0mm | 0mm |
| Cells (bottom nickel strips already welded) | 70.2mm | 70.2mm |
| Top nickel strip on center of pack (under BMS) | 0.2mm | 70.4mm |
| Kapton + heat shrink over pack | 0.5mm | 70.9mm |
| BMS sitting flat on shrink-wrapped pack center | 22mm | 92.9mm |
| Top clearance to aluminum top plate | 13.1mm | **106mm** |

**Jumpers (4.5mm stackup of 8AWG + solder) live in the side margins** alongside the BMS, not under it. They occupy lateral space (~43mm wide per side), not vertical space.

## Anti-Spark Operation

The BMS provides soft-start anti-spark when it turns ON (MOSFETs close gradually over ~1 second). This works ONLY if the XT150 is already mated when the BMS powers on — i.e., BMS must be OFF during connector mating.

**Natural safe workflow (no sparks):**
1. Post-ride: press BMS button OFF → unplug ESC XT150 (no spark, P− open) → plug in charger XT150 (BMS still off) → charge overnight
2. Pre-ride: unplug charger XT150 (BMS still off) → plug in ESC XT150 (no spark, P− still open) → close hatch → press BMS button ON → soft-start ramps up → ride

**Connector mating always happens while BMS is off** — this is the natural sequence, not a special precaution. Sparks only possible if workflow is deviated from.

**If uncertain of BMS state** (e.g., after someone else rode): check JK BMS Bluetooth app before opening hatch. App connects → BMS is on → send power-off command via app before unplugging anything. App doesn't connect → BMS is off → safe to proceed.

---

## Charging

58.8V 5A charger (XLR plug removed, rewired to XT150 male). Unplug ESC from battery XT150, plug charger XT150 into same battery connector. Or remove battery box entirely and charge at home. BMS handles active balancing automatically via Bluetooth app monitoring. ~9 hour charge time.

---

## Waterproof Enclosures

**Architecture overview:** Thin-wall (4mm PETG) enclosure with external vertical ribs (10×10mm cross-section) doubling as stiffeners and fastener bosses. Bolt-down aluminum top lid (removable for service) with TORRAMI neoprene gasket; bottom aluminum plate permanently bonded. 4-piece L-shaped corner print split with paired-rib epoxy joints at wall midpoints. All enclosure dimensions are the current Onshape placeholder values — **final dimensions are TBD until pack is built, wrapped, and measured.**

**Battery Enclosure (3D printed PETG + aluminum — bolt-down top):**
- Walls: 4mm PETG (reduced from 8mm — external ribs carry the rigidity load)
- **Ribs: 10mm × 10mm cross-section**, vertical, running full wall height, spaced ~70mm apart around perimeter. Each rib houses a buried M4 brass heat-set insert for the top lid bolts.
- **Flange (outward projection at top edge):** ribs themselves project 10mm outward from the wall — no separate flange needed. Top surface of ribs + walls forms the sealing face for the neoprene gasket.
- Combined wall+rib thickness at bolt locations: 14mm (4mm wall + 10mm rib). Between ribs: 4mm wall only.
- 4-piece print: split into 4 L-shaped corner pieces, each containing half of one long wall + half of one short wall. Joined at wall midpoints with **paired-rib epoxy bonds** — each corner piece ends in a vertical rib at the midpoint, mating corner piece has a matching rib, two rib faces bond with thickened epoxy (TotalBoat + Cab-O-Sil). Wall overlap of ~20-25mm at joint for shear strength.
- **Target exterior dimensions: 247mm × 415mm × ~110mm** (placeholder — will be remeasured after pack build). Fits in 660mm × 280mm board cavity with clearance for mast bolt intrusion (see note below).
- **Aluminum plates:** 4mm 6061 top and bottom. Top plate removable (20 bolt holes, M4 clearance = 4.5mm). Bottom plate permanent (no bolt holes, bonds with 3M 4200 + epoxy). SendCutSend or DIY jigsaw + drill — cutting method TBD.
- **Top lid fastening:** 20× M4 × 16mm button head stainless bolts → 20× M4 × 8mm brass heat-set inserts buried in ribs (Ktehloy kit, 5.2mm × 10mm deep insert holes). Bolt layout: 6 per long side + 4 per short side, corners dedicated (not shared). 20 bolts = exact match to M4 × 8mm insert stock.
- **Top lid gasket: TORRAMI 1/8" neoprene** cut to match perimeter with 20 × 5mm bolt clearance holes (hollow punch). 25-30% compression under M4 bolts torqued to 2-3 N·m. Fully removable and reusable for service — no cured sealant at this joint.
- **Bottom plate seal:** 3M 4200 permanent bond (no service access needed from below).
- Interior contains: battery pack (~211 × 339 × 82mm — measured post-build), JK BMS BD6A20S15P 150A (162 × 102 × 22mm, flat on top of pack), BOJACK 150A ANL inline fuse (123 × 37 × 40mm, mounted on bottom plate at Pack − end), balance wires, NTC temp sensor
- Pack oriented lengthwise in the enclosure. Pack + short end near cable gland exit toward ESC enclosure. Pack − short end has the fuse mounted on the aluminum plate beside the pack.
- 2× XT150 female connectors on short 8AWG pigtails exit through PG11 cable glands (positive + negative) — glands mounted on the short end facing the ESC enclosure
- APIELE 12mm waterproof push button mounted through enclosure wall — wired to BMS switch input
- Battery box sits on a 3/4" Sande plywood base plate inside the board cavity (shared with ESC enclosure)
- Removable — unplug XT150s at CESFONJER housings, remove 20 M4 bolts from top lid for pack access, or lift entire box out through hatch for home charging

**Material mix for enclosure print:** Plan to mix OVERTURE PETG green (~1kg on hand) with ASA (near-full roll available) across the 4 corner pieces. ASA has better UV resistance and higher temperature capability; PETG has easier printing characteristics on the open-frame A1. Recommended: 2 corner pieces in ASA, 2 in PETG. Epoxy bonds both materials at the midpoint joints if surfaces are scuffed + IPA-wiped.

**Print specs (per corner L-piece):**
- Nozzle 0.6mm, layer height 0.24mm
- 4 wall loops, 15% gyroid infill
- Mass: ~233g per piece → 932g total for 4 pieces
- Print temp per material (PETG 235-245°C bed 70°C; ASA 250-260°C bed 105°C, with draft shield + brim for warp control on open-frame A1)
- Print orientation: walls vertical, ribs vertical (standard orientation, layer lines horizontal)

**ESC Enclosure (3D printed PETG + aluminum — bolt-down top):**
- Same architecture as battery enclosure: 4mm walls + 10×10mm external ribs, bolted aluminum top lid with neoprene gasket, bonded bottom plate
- Interior: ~160 × 110 × 55mm. Exterior (with 4mm walls + 10mm ribs): ~184 × 134 × ~70mm + aluminum plates. Fits on Bambu A1 bed in one piece (single-piece print, not 4-corner split).
- Positioned in mid section of cavity, FORWARD of mast bolts — no longer sitting on bolt heads. ESC aluminum bottom plate rests flat on plywood base plate for clean thermal contact.
- Sized for 75200 Pro V2 (130×68×41mm) with wiring clearance
- ESC aluminum PCB face down against bottom aluminum plate for heat transfer
- VX3 wireless receiver inside this enclosure
- **Top lid fastening:** 8-10× M4 × 12mm button head bolts → M4 × 6mm heat-set inserts (Ktehloy kit). Uses M4 × 6mm stock (d1=6mm, d2=5.4mm — different insert size requires 5.3mm print hole)
- **Top lid gasket:** TORRAMI 1/8" neoprene, same approach as battery enclosure
- Cable glands for all wire pass-throughs:
  - 2× PG11: 8AWG power leads in (from battery XT150 connections)
  - 3× PG11: phase wires out (to motor XT150 connections)
  - 1× PG7: reed switch wires in
  - 1× PG7: water alarm wires (sensor mounted outside box, low in cavity)

**Why this architecture replaces the earlier Gustav-style toggle latch + monolithic wall plan:**
- Bolt-down top lid gives more uniform FIPG/gasket compression across a large lid (415mm × 247mm) than 6 corner toggle latches would
- External ribs give 3x structural benefit: wall stiffness, bolt bosses, print-time self-aligning feature at the 4-piece joints
- 4-piece print split is dimensionally required (415mm enclosure vs 256mm Bambu A1 bed) — same rib layout used for printing also becomes the joint feature for assembly
- Heat-set inserts (vs through-bolts) give single-sided service access (one-handed lid removal from above, no wrenching nuts from below)

---

## Mast Mount Hardware

**4× through-bolts** connect the Gong V2 top plate (below hull) to the 3/4" Sande plywood base plate (inside cavity). Bolts pass through: Gong plate → TORRAMI neoprene gasket → hull fiberglass → plywood → cavity fiberglass → fender washer → nyloc.

**Hardware:**
- **4× Mywish M6 × 50mm button head stainless** (304 SS, black oxide, 2.7mm head height, 12.5mm head OD). Button head bears directly on the underside of the Gong aluminum top plate — no washer under the head (Gong plate is already a wide, flat load-spreading surface).
- **4× GDFYMI M6 × 20mm × 1.5mm fender washers (304 SS)** — under nyloc on the cavity side, spreads nyloc load across the Sande plywood face. Verified that standard flat washers from WEGOUP kit are too small (12mm OD) for proper load distribution on plywood.
- **4× M6 nylocs** from existing ZQZ 140pc assortment kit.

**Sealing — TORRAMI 1/8" neoprene gasket, full Gong plate footprint:**
- Cut from TORRAMI 1/8" × 18" × 24" sheet (KEPT from initial order — no longer being returned)
- Perimeter matches Gong top plate footprint (trace when plate arrives)
- 4× bolt holes cut with UNCO 5mm hollow punch (undersized by 1mm vs 6mm bolt shank — neoprene collars around bolts and self-seals the hole via compression)
- 1× phase wire pass-through hole matching the hole in the Gong plate and hull (undersized vs wire bundle OD for additional seal at wire penetration)
- **No cured sealant anywhere at the mast mount** — gasket is the entire seal, fully removable for Prius transport

**Why no 4200 or dielectric grease on bolts:**
- 4200 is semi-permanent — razor-removal required. Wrong choice for a joint that disconnects for transport.
- Dielectric grease (BTAS) was originally specced for bolt shank sealing, but returned Apr 18 — redundant with the neoprene gasket's bolt-hole compression seal. Freshwater (Lucky Peak) doesn't require the belt-and-suspenders.

**Torque spec:** 8-10 N·m per bolt, star pattern, two passes (first pass 5 N·m, second pass 10 N·m).
- Target neoprene compression: 25-30% (0.8-1.0mm compression on 3.2mm uncompressed thickness, leaving 2.2-2.4mm installed)
- Well within M6 stainless yield torque (12-15 N·m)
- Bolt preload at 10 N·m: ~8-10 kN per bolt = 16-20× the peak per-bolt foil lift force (~500N). Joint does not open under peak foil load — no gasket cycling/fatigue risk.

**Neoprene overcompression concern:** Neoprene is elastomeric — extrudes or takes permanent set under excess compression, does NOT fracture. Cannot "snap" a neoprene gasket by over-torquing. Primary failure modes are (a) under-preload allowing joint separation under cyclic load, or (b) compression set over months requiring seasonal re-torque. Both managed by calibrated torque + annual re-torque routine.

**Total bolt length math (stack):**
- Button head below Gong plate: 2.7mm (projecting into water, low drag)
- Gong top plate (estimate): ~8-10mm
- TORRAMI neoprene (compressed): ~2.4mm
- Hull fiberglass: ~3mm
- Sande plywood: 19mm
- Cavity fiberglass: ~2mm
- Fender washer: 1.5mm
- M6 nyloc: 6mm
- **Total consumed: ~44-46mm** out of 50mm bolt length → 4-6mm thread excess past nyloc (acceptable margin, can be trimmed/filed after install if desired)

**Cavity intrusion:** Each mast bolt projects ~12.5mm into the cavity from the plywood surface (washer 1.5mm + nyloc 6mm + thread excess 5mm). The 4 bolt positions sit in the rear section of the plywood base plate, centered at 400mm from tail, in a 90 × 165mm bolt pattern. Battery enclosure (forward) and ESC enclosure (mid, forward of mast bolts) both avoid this zone — verified in Onshape.

**Pre-install checklist (when Gong plate arrives):**
1. Physically verify bolt spacing on Gong plate — documented 165mm vs implied 190mm discrepancy flagged in notes. Measure with calipers.
2. Verify hole geometry on Gong plate (straight through-holes, no counterbore — confirmed)
3. Trace plate footprint onto TORRAMI sheet, mark bolt hole + phase wire hole positions
4. Cut gasket perimeter with box cutter or scissors
5. Punch bolt holes at 5mm, phase wire hole sized to match plate/hull opening

---



All XT150 connections enclosed in CESFONJER IP68 M25 junction box housings. Each housing has cable gland seals on both ends around the wires, with the XT150 pair mated inside the sealed barrel.

| Connection | Housing | Wire Gauge | Purpose |
|---|---|---|---|
| Battery positive | CESFONJER #1 | 8AWG | Battery ↔ ESC power |
| Battery negative | CESFONJER #2 | 8AWG | Battery ↔ ESC power |
| Phase A | CESFONJER #3 | Motor gauge | ESC ↔ Motor |
| Phase B | CESFONJER #4 | Motor gauge | ESC ↔ Motor |
| Phase C | CESFONJER #5 | Motor gauge | ESC ↔ Motor |

To disconnect: unscrew CESFONJER barrel, pull XT150 pair apart. All connections fully IP68 waterproof when assembled via the housing cable gland seals.

10 CESFONJER housings originally ordered, 4 returned Apr 18 — **6 housings kept** (5 in use + 1 spare). Dielectric grease not used (BTAS returned Apr 18) — CESFONJER IP68 housings provide the primary moisture barrier, and XT150 contacts are protected by the housing seal rather than by grease on the pins.

---

## Wire Routing (S-curve layout)
- Power: Battery enclosure (cable gland out rear face) → XT150 pair in 2× CESFONJER IP68 housings → cable gland into ESC enclosure bottom → ESC
- Phase wires: ESC (phase output) → cable gland out ESC enclosure top → XT150 pairs in 3× CESFONJER IP68 housings → short run down through cavity → through plywood wire hole → through Gong top plate → up hollow mast → motor
- S-curve flow: Battery (forward) → power cables rearward → into ESC bottom → out ESC top → down to mast wire hole. Clean flow, no crossing wires.
- Reed switch: Layer 3 foam channel (30mm) → into cavity → cable gland into ESC enclosure → VX3 receiver 5V line
- BMS switch: Push button on battery enclosure wall → BMS switch input (all internal)
- No conduit through foam walls, no separate service cavity routing

---

## Kill Switch (reed switch + magnet) — ⚠️ NOT INSTALLED

**STATUS: designed but never built.** Parts are on hand (MKA10110 reed switches, 20×3 mm neodymium magnets) but the system was never fitted, and the board has been ridden without it.

**What this means in practice:** the only remaining protection is the ESC's **1000 ms UART timeout**, which stops the motor if the radio link drops — out of range, remote battery dies, remote goes underwater. It does **NOT** cover the main hazard: falling off while still holding the trigger. In that case the board keeps driving away under power with nobody on it.

**Interim mitigations while unfitted:** wrist float strap on the remote so it stays in range and under control; deliberately practise releasing the trigger as a reflex; ride well away from people, boats and docks; never ride alone.

**This must be retrofitted before any beginner rides the board** — fall-detection is exactly the protection an inexperienced rider needs most. It also gates any cruise-control feature, which would remove the "let go of the trigger" reflex that is currently the only real safeguard.

### Design as planned (for the retrofit)
- Reed switch embedded in deck foam behind cavity (~250mm from tail, in solid foam section), fiberglassed over
- Invisible from outside — senses magnet through fiberglass
- Steel disc (~30-40mm) embedded above reed switch as magnet target, also fiberglassed over
- Neodymium magnet on ankle leash, sticks to steel disc on deck surface
- Fall off → magnet pulls away → reed switch opens → VX3 receiver loses 5V power → ESC signal timeout → motor stops
- Wire routed through shallow channel (5mm × 5mm) carved in Layer 3 top face, running 30mm from reed switch pocket forward into cavity rear wall → along cavity floor → cable gland into ESC enclosure

---

## Power On/Off
- APIELE 12mm waterproof momentary push button mounted through battery enclosure wall
- Wired to JK BMS BD6A20S15P switch input (BMS handles soft-start / anti-spark)
- Open hatch → press button → BMS powers on → ESC receives power (no spark on XT150 because BMS was off when plugged in)
- Press button again → BMS powers off → safe to unplug XT150 connections (no current flowing)

---

## Pre-Ride Sequence
1. Bolt foil to board (4× M6 bolts from below) — only needed first time or after transport
2. Open hatch (flip 2 cam latches on tail edge, swing lid open on hinges toward nose)
3. Screw together 5× CESFONJER IP68 housings (2 battery + 3 phase) with XT150s mated inside
4. Press power button on battery enclosure (BMS on, anti-spark soft start)
5. Close hatch (swing lid down, flip 2 cam latches)
6. Stick magnet to deck near rear foot
7. Attach ankle leash
8. Ride

## Post-Ride / Charging
1. Open hatch (flip 2 cam latches, swing lid open)
2. Press power button (BMS off)
3. Unscrew 2× battery CESFONJER housings, pull XT150 power connectors apart
4. Option A: Plug charger XT150 into battery enclosure's XT150 female — charge in the board with hatch open
5. Option B: Unscrew 3× phase CESFONJER housings too, lift battery box out entirely, charge at home on fireproof surface
6. Close hatch when done

## Transport (full separation)
1. Open hatch, press power button off
2. Unscrew all 5 CESFONJER housings, separate all XT150 connections
3. Unbolt 4× M6 mast bolts from below
4. Foil completely separates from board — zero wires tethering
5. Board (63") lays flat in Prius with seats folded, mast/foil alongside, battery box in board or separate
