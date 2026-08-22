> **V1 reference — not the current design.** This describes the board that was
> built, or early planning that predates the model. V2 is generated from
> `model/blender_board.py`; where the two disagree, the model and the docs
> linked from the [README](../../README.md) are correct.

# eFoil Build — Board Design (V4)

**Last updated:** August 7, 2026 (as-built — hatch design changed from cam latches to bolt-down; leak history added)

## Overview
Single-cavity layout modeled on Gustav's Danish eFoil V2 build (foil.zone). Shared birch plywood base plate serves as both mast hardpoint and electronics floor. Board shape refined based on foil.zone community feedback: DutchFoiler (less bulky/brick-like), sat_be (sharp bottom edges at tail for takeoff), Kian (Flite-style board shape inspiration). Hatch uses strap hinges on the nose edge + a 6-bolt bolt-down lid (cam latches were designed but abandoned — see Hatch Design). Full CAD model in Onshape.

---

## Dimensions
1600mm × 600mm × 153mm (63" × 23.6" × 6").

**Volumes (from Onshape, post-CAD-finalization):**
- **Foam volume: 75.3L** (measured via mass properties, post-cavity-cut and post-chamfer/fillet). This is the material to buy and shape, and the buoyancy the board provides if the hatch leaks.
- **Cavity internal volume: ~21.3L** (660 × 280 × 115mm — cavity footprint through all 3 foam layers, depth from plywood base plate top to hatch lid underside).
- **Full sealed displacement: ~96.6L** (foam + sealed cavity air when hatch is closed and watertight). This is what matters for buoyancy during riding.

At 86 kg rider weight + ~96.6L sealed displacement, reserve buoyancy is ~10.6 kg — classic "sinker" board. Rider will not float above the waterline while standing on the board. Water start required (lie on board, knee up, stand up as speed builds). This is standard for performance eFoil builds.

---

## Exterior Shape

**Top-down outline (three-zone geometry, confirmed in Onshape):**

| Zone | Length (from tail) | Start width | End width | Rail arc |
|---|---|---|---|---|
| Tail taper | 0 → 400mm | 200mm (flat tail) | 600mm (full) | R500 concave (curves inward) |
| Parallel midsection | 400 → 1000mm | 600mm | 600mm | straight |
| Nose taper | 1000 → 1600mm | 600mm | 100mm (flat nose) | R845 concave (curves inward) |

- **Tail:** 200mm flat base at the very end. Rails curve inward via R500 concave arcs, tapering down from full 600mm width to the 200mm flat over 400mm of length. Same concave geometry as the nose, just with a tighter radius (R500 vs R845) over a shorter length (400mm vs 600mm) — the tighter/shorter taper is what gives the tail its blunter character compared to the more drawn-out nose.
- **Midsection:** 600mm of parallel 600mm width. This is where the rider stands and where the cavity sits.
- **Nose:** Rails curve inward via R845 concave arcs over 600mm of length, tapering down to a 100mm flat nose tip. The long, drawn-in nose taper gives the swept/eFoil-style profile (vs a symmetric elliptical "pill" shape).
- Tail is blunter and wider than the nose — nose is narrower (100mm vs 200mm) and taper is more gradual (600mm vs 400mm). Asymmetric in the classic eFoil way.
- **Edge treatment (4 operations, applied in CAD order — matches Onshape feature tree):**
  1. **Chamfer 1 — Top perimeter chamfer, 40mm × 60°**, tangent-propagated around the entire top edge (long rails + nose end + tail end, one continuous chamfer). In Onshape "Distance and angle" mode: 40mm measured along the deck face, 60° angle from deck, so the chamfer consumes 40mm of deck width and drops ~69mm of vertical rail height (40 × tan 60°). Creates the Flite-inspired wedge cross-section where the deck is significantly narrower than the hull footprint.
  2. **Fillet 1 — Nose rail rounding, R50**, applied to the two top-chamfer-to-side edges along the nose R845 arc region only, tangent propagation on. Softens the nose-rail corner where the deck chamfer meets the side face. Dies out naturally where the nose curve straightens into the parallel midsection.
  3. **Chamfer 2 — Nose tip bottom chamfer, 40mm × 60°** on the single edge where the nose vertical face meets the hull underside (at the bottom of the 23mm flat). Softens the front-bottom nose corner so the board doesn't stuff its nose on touchdowns after foiling — the first surface to contact water during a nose-down landing is a 60° ramp, not a sharp 90° corner. This is the ONLY chamfer or fillet anywhere on the bottom of the board.
  4. **Fillet 2 — Top perimeter soft edge, R20**, tangent-propagated around the entire top perimeter (both long rails + tail end + nose end + both Fillet 1 edges). Rounds the deck-to-chamfer corner everywhere. On the nose, it blends between the Fillet 1 R50 and the deck. On the straight rails and tail, it rounds what would otherwise be a sharp 90° deck-to-chamfer corner. Full-perimeter softening of the deck edge for rider comfort and clean visual lines.
- **Bottom edges stay sharp 90°** on all long rails, tail end, tail corners, and the bottom of the nose taper region. No bottom chamfer anywhere except the single Chamfer 2 at the nose tip. This preserves clean water release during takeoff (per sat_be's feedback about sharp bottom rails being essential at the tail).
- **Cross-section summary:** Flat bottom with sharp 90° bottom rails, flat side face, 40mm × 60° top chamfer rounded into the deck with R20 fillet, narrow flat deck. A truncated wedge — visually thicker at the hull and narrower at the deck, with soft deck edges and crisp bottom edges.
- **Nose bevel (side profile):** Bottom surface kicks up starting at 1000mm from tail (600mm from nose tip), sweeping upward along a **Rho 0.5 conic (parabolic) curve** that rises 130mm over the 600mm of length. The curve is tangent to the flat hull at its start (no kink — smooth transition) and reaches the 130mm rise at the nose tip. Board thickness at tip after bevel: 153mm − 130mm = **23mm flat vertical face at the nose tip**. Top of this face is rounded into the deck by the combined Chamfer 1 + Fillet 1 + Fillet 2 sequence. Bottom of this face is rounded into the hull underside by Chamfer 2. Top deck stays full length. This whole sequence keeps the nose from catching during takeoff planing and touchdowns.
- Flat bottom through the tail and midsection (from tail to 1000mm mark — 62.5% of board length).
- Flat deck — no crown. Simpler to build, EVA pad provides grip.
- Tail: flat bottom, sharp bottom edges for clean water release.

---

## 3-Layer Foam Construction
All internal cuts done on flat sheets with hand tools (box cutter, chisel, surform rasp) BEFORE gluing layers together. No jigsaw needed — all cavity and channel cuts are done while each layer is a flat slab on the workbench. Gustav used a hot wire cutter against 1:1 templates printed from Fusion 360 — if you can rig a hot wire (nichrome + power supply), it gives cleaner cuts on XPS. Otherwise, box cutter for straight lines, surform rasp + orbital sander for shaping.

**Board layout from tail to nose (all dimensions from tail):**

| Zone | Position (from tail) | Description |
|---|---|---|
| Tail | 0 - 300mm | Solid foam. Structural, takes impact during water re-entry. Rear foot zone. |
| Main cavity | 300 - 960mm | 660mm × 280mm footprint. Full through-cut on ALL three layers (same width). Shallow 3/4" recess in Layer 3 top face around opening for hatch lid to sit flush. 3/4" birch plywood base plate overlaps ~50mm under foam on all sides, epoxied into a shallow recess in Layer 1, flush with hull surface. Contains: sealed battery enclosure (forward), sealed ESC enclosure (mid, forward of mast bolts), IP68 connector housings, power button (on battery enclosure), water alarm. BMS and fuse mounted side by side in battery enclosure (BMS on edge). Mast bolts in rear section of plywood (bolt pattern centered at 400mm from tail). Wire pass-through hole for phase wires aligned with Gong top plate. |
| Nose | 960 - 1600mm | Solid foam. Buoyancy and structural. Bottom surface kicks up starting at 1000mm from tail. |

---

## Layer Details

**Layer 1 (Hull/Bottom, 2" / 51mm XPS):**
- Full through-cut for main cavity (660 × 280mm, starting 300mm from tail)
- Shallow 19mm recess around cavity opening for plywood base plate overlap — plywood extends ~50mm beyond cavity opening on all sides, bonding under the foam with epoxy
- Plywood epoxied into recess, flush with hull surface
- M6 bolt holes (6.5mm clearance) and wire pass-through hole drilled AFTER fiberglassing — use Gong V2 top plate as template
- Plywood IS the cavity floor — accessible from above when hatch is open

**Layer 2 (Middle, 2" / 51mm XPS):**
- Full through-cut for main cavity — same footprint as Layer 1 (660 × 280mm)
- This layer provides the cavity walls (51mm tall)
- Rounded corners on cavity cuts (easier to fiberglass, stronger)

**Layer 3 (Deck/Top, 2" / 51mm XPS):**
- Full through-cut for main cavity — SAME footprint as Layers 1-2
- Shallow recess (~3/4" deep) carved into top face around the cavity opening perimeter for hatch lid to sit flush: Trim-Lok X2897BT EPDM ribbed sponge seal (0.300" × 0.500") bonded to the recess floor (not the lid), compressed between recess floor and lid underside when latched
- Plywood backing blocks (80×45×19mm, cut from 3/4" birch plywood) epoxied to the recess ledge at 2 hinge locations (nose-side short edge). Blocks sit on the ledge outside the cavity wall, butting up against the lid edge. Centered at 60mm from each corner of the 280mm cavity width (146mm center-to-center). Provides solid screw-holding for hinge deck-side leaf — foam alone won't hold screws under repeated load.
- Reed switch pocket in deck foam behind cavity (~250mm from tail, in solid foam)

---

## Mast Hardpoint (Integrated into Cavity Floor)
- 3/4" birch plywood base plate spans entire cavity floor — mast bolts go through the REAR section, centered at 400mm from tail
- Bolt pattern: 90mm × 165mm rectangle, 4× M6 bolts (standard foil top plate spacing)
- Through-bolt mounting: M6 hex bolts insert from below through hull fiberglass + plywood, nyloc nuts tightened from inside cavity
- Clearance holes: 6.5mm diameter (standard M6 clearance), drilled through all
- No threaded inserts needed — just bolts and nuts, replaceable if stripped
- All holes drilled AFTER fiberglassing is complete — use Gong V2 top plate as template held against hull to mark exact positions, drill through fiberglass + plywood in one shot
- Seal bolt holes with marine sealant or gasket between Gong top plate and hull
- Battery enclosure sits on the FORWARD section of the same plywood plate
- ESC enclosure sits in the MID section, FORWARD of mast bolts (no longer sitting on bolt heads)

---

## Hatch Design — AS BUILT

**Changed from the original design.** Cam latches and PETG strike plates were designed but never used. The lid is a **bolt-down panel** with hinges retained on the nose edge for alignment and to stop the lid getting lost.

**Lid:**
- 3/4" birch plywood, **epoxy hot-coat only — the fiberglass layup was skipped.** The hot coat is therefore the sole water barrier on the lid; all edges and every penetration must stay sealed.
- Drops into the shallow 3/4" recess in Layer 3, flush with deck
- Perimeter edges beveled for clearance (the ledge opening shrank slightly when thickened epoxy was applied during leak repair). **Bevel the outer edge only — the flat underside sealing band stays untouched.**
- Bevel doubles as a lead-in so the lid slides onto the gasket instead of catching it

**Fasteners:**
- **6× M5 bolts** through the lid into **M5-0.8 hex-drive threaded inserts** set in the ledge blocking
- Insert spec: originally EZ-LOK 400-M5 (25/64" drill). **Switched to hex-drive inserts** (rivodeco M5-0.8 × 12 mm) — driven from the hex socket with a bit in a drill, which fixes both the "bolt seizes in the insert" problem and the vertical-alignment problem the bolt-driver method caused.
- Lid clearance holes: **7/32" (5.56 mm)**, drilled off the *installed* inserts so they can't drift
- **Fender washers under every bolt head.** The plywood lid crushed under bolt load before an insert pulled out — load spreading is required, not optional.
- Insert rims sealed after driving

**Hinges (nose-side short edge):**
- 2× Pyntrax 316 SS strap hinges (6" × 1.18"), centers 60 mm from each corner of the 280 mm cavity width (146 mm center-to-center)
- **Hinge knuckle must sit directly over the lid/board seam** so the lid closes parallel onto the gasket rather than pivoting into it
- **Printed PETG spacer under the deck-side leaf** to lift the hinge by roughly the gasket's compressed height. **Shim empirically with the gasket in place — do not use a calculated number.** An oversized spacer tilts the lid, which forces over-torquing at the free edge, which is what crushed the plywood and pulled an insert.
- Screws: #8 × 1" flat-head stainless (304 is fine for freshwater), piloted ~5/64", pilot holes epoxy-sealed, hand-driven

**Gasket:**
- Trim-Lok X2897BT EPDM ribbed sponge, 0.300" × 0.500", **ledge-mounted** (not on the lid) so water drains outward when opening
- Uncompressed 7.6 mm → target compressed ~4.6 mm (~40 % compression, top of the 25–40 % window)
- **Corners are mitred, not bent.** A solid extrusion buckles and twists around tight inside radii — four mitred segments with RTV-bonded butt joints lay flat. Joints never land on a corner or under a bolt.
- Poured-in-place silicone (2-part, ~$35 kit, Shore 20–30A) remains the fallback if the extrusion won't seal. Platinum-cure silicone can be inhibited by amine-cured epoxy — wash blush thoroughly first.
- A bead of 3M 4200 around the *outer* edge of the seal, bonding it to the epoxied ledge, closes the path where water travels **under** the gasket

**Pull loop:**
- Short flat nylon/polyester webbing loop, anchored under the two free-edge lid bolts (opposite the hinges), exiting through the seam gap in the traction pad
- Low profile — just enough to get a fingertip under

---

## Leak History and Repairs (Aug 2026)

Three water tests. Each found a different path. Worth keeping because the same failure modes will apply to V2.

**Test 1 — hatch leak, hinge geometry.**
Oversized hinge spacers tilted the lid so the gasket was crushed at the hinge and light at the free edge. Bolts were over-torqued trying to pull the proud edge down; the plywood crushed and one insert pulled out.
*Fix:* thinner spacers shimmed empirically, insert re-bedded in epoxy, fender washers under all bolt heads. **Epoxy held the insert where 4200 had not.**

**Test 2 — water through the laminate, not the gasket.**
The gasket sealed correctly. Water was entering through **unsealed fiberglass cut edges at the cavity ledge** and wicking through the XPS foam. Confirmed by pouring water on isolated sections of the ledge.
*Fix:* thickened epoxy (Cab-O-Sil) over the ledge edges at entry and exit points, plus everywhere with similar exposed edge.
*Lesson:* **cured laminate is not waterproof at a cut edge.** Exposed fibre ends wick. Every cut edge needs neat epoxy — this is cheap and would have prevented the whole episode.

**Test 3 — reduced but not eliminated.**
Remaining seepage traced no further with pour testing.
*Fix:* thickened epoxy over the entire cavity interior, 3M 4200 in the hinge screw holes (an unsealed penetration nobody had accounted for), and a Flex Seal Liquid coat over the cavity interior as a belt-and-suspenders membrane.
*Caveats on Flex Seal:* it does not bond to cured epoxy the way epoxy does, and it must be kept off the gasket land, bolt bores, and insert faces — a compressible layer at any clamping surface undoes the seal geometry.

**Validated separately:** with the lid off and the hull pushed under, no water entered through the mast penetration or wire holes. The mast gasket and wire pass-throughs are sound.

**Both enclosures held** — *through the August tests.* The ESC and battery boxes stayed dry through every test recorded above, including the sessions where the cavity flooded.

**Test 4 — the enclosures did NOT hold (Aug 2026, after this doc was written).**
The cavity flooded again and **water got into both the ESC and battery enclosures.** No gasket, gland or fastener path was identified. Derek's read is that **water seeped through the printed PETG wall itself**, and then sat trapped inside.

*Two candidate mechanisms, and the second now looks more likely:*

**(a) Porosity.** An FDM wall is extruded beads laid side by side, and the valleys between them form a connected path through it. More perimeters make the path longer, not closed — these ran four wall loops.

**(b) The enclosures were SUBMERGED.** This fits the record better. The August tests said "both enclosures held" when the cavity took shallow water; they failed once it flooded deeply. A gasket that shrugs off splash behaves very differently under 100 mm of standing head, and both enclosure lids used the same squashed-strip-with-no-hard-stop arrangement as the hatch. **On this reading the enclosures did not fail independently — they failed because the cavity did**, which makes the hatch the single thing worth fixing.

*Lesson: fix the cavity first.* The hatch is the barrier everything else sits behind, and V1's was **6 bolts at 313 mm pitch on an EPDM sponge strip squashed against a flat ledge, with strap hinges** — no groove, no hard stop, so squeeze depended entirely on how hard each of six bolts was done up, and Test 1 records exactly that going wrong. V2 is 12 bolts at 141 mm (bow goes as pitch⁴, so **25× less**), an O3 cord in a machined groove, and **no hinge at all**.

*Secondary lesson, still worth the twenty minutes:* **a printed enclosure is not a pressure boundary on its own.** It needs a continuous barrier applied to it — a brushed coat of neat epoxy on both faces, outside first, since stopping water entering the wall beats catching it once it is already travelling inside one. And it needs to be **proved before it is trusted**, not discovered by riding: seal it empty, pull a vacuum, watch the gauge, then repeat submerged so any path pulls water *in* where you can see it.

**Repair — 4 more hatch bolts (Aug 2026).**
Two at the upper corners and two at the midpoints of the long sides, taking the lid from **6 bolts to 10**. Each new hardpoint was made by **plugging with epoxy, then drilling undersized for a threaded insert** — the same principle V2 uses for its potted lid holes, and the right way to put a fastener into plywood or laminate.

*Effect:* pitch goes 313 mm → 188 mm, and bow between fasteners goes as pitch⁴, so this is a **7.7× reduction**. V2 is 141 mm for comparison, so V1 still bows about 3× more than V2 will.

*But the seals are not comparable, and it matters:* V1's EPDM sponge is 7.6 mm tall and compresses 25–50%, so it has **1.9–3.8 mm of travel**. V2's Ø3 cord at 20% squeeze has **0.60 mm**. In absolute terms V1's seal can swallow far more bow than V2's can — which says the bolt count was probably not the whole story on V1.

**Observed pattern (Derek, Aug 2026):** upper corners sitting slightly low or not reaching full compression; **the hinges applying compression** on their edge; **the long-side midpoints running long** — i.e. proud and under-compressed. That is the classic hinge-edge-over / free-edge-under signature, and it is exactly where the four new bolts went.

**Diagnose before modifying — use a witness.** Smear a thin film of grease, chalk or marker on the lid's sealing face, close and torque normally, then open. Where it transferred, the seal made contact; where it did not, it did not. That maps compression right round the perimeter in five minutes with no parts and no guessing, and it will tell you whether the four new bolts actually fixed the midpoints or just moved the light spot.

**A hard stop for V1 is possible without rebuilding anything:** a **spacer at each bolt**, landing on the ledge outboard of the seal. The ledge is 38 mm wide and the seal is 12.7, so there is **25 mm of spare ledge** to land on. The seal is 7.6 mm tall, so:

| Target compression | Lid bottoms at | Spacer |
|---|---|---|
| 25% | 5.7 mm | 5.7 mm |
| **30%** | **5.3 mm** | **5.3 mm** |
| 35% | 5.0 mm | 5.0 mm |

Build them from washer stacks and tune once — the same method already used to shim the hinges. What this buys is not less compression at the hinge, it is **permission to pull every other bolt down hard** without fear of crushing the hinge edge, which is precisely the "midpoints running long" complaint. It is a stop at the bolts only, so it does not force compression at midspan on its own — but with 10 bolts at 188 mm it does not need to.

**What is still unfixed on V1: the hinges.** Test 1 was a *tilt*, not a bow — oversized spacers held one edge proud and left the gasket light at the free edge. A tilt puts an edge out by millimetres, which is the order the sponge actually struggles with, and adding bolts does not straighten a lid that is being held crooked. **Worth checking the lid sits parallel before the next session, and worth telling Kev.**

*This supersedes the "layered defence worked as designed" conclusion above.* The layers were the same material with the same flaw — a printed box inside a glassed cavity is two barriers only if the printed one is actually a barrier.

---

## Exterior Shaping (after foam glue-up)

1. Cut outline from cardboard half-template using box cutter (score deeply, snap) or surform rasp to rough shape. Template geometry (half-width from centerline as a function of station-from-tail): **100mm flat tail** at station 0mm → R500 concave arc from 100mm half-width at the tail up to 300mm half-width (full board width) at station 400mm → straight 300mm half-width through the midsection (stations 400-1000mm) → R845 concave arc from 300mm half-width at station 1000mm down to **50mm flat nose** at station 1600mm. Both tapers are concave (arc centers outside the board outline, rail curves toward centerline). Tail taper is shorter and tighter (R500 over 400mm) and ends at a wider flat (200mm full-width); nose taper is more drawn-out (R845 over 600mm) and ends at a narrower flat (100mm full-width).
2. Shape nose bevel (side profile): from the 1000mm-from-tail station forward, carve the bottom surface upward along a Rho 0.5 parabolic curve that rises 130mm over the 600mm of length, ending at a 23mm-tall flat vertical face at the nose tip. The deck stays full length — only the hull shortens. **Template-assisted approach:** print a side-profile template (thin sheet with the target curve cut into one edge, half-width so it hugs the board centerline) and use it as a guide to check depth at multiple stations as you remove foam with the surform rasp. Alternatively, step-cut method: generate intermediate depth marks from the CAD at every 100mm station along the bevel (target rise from hull: ~2mm at 100mm, ~9mm at 200mm, ~22mm at 300mm, ~40mm at 400mm, ~64mm at 500mm, ~94mm at 600mm — Rho 0.5 approximation), carve to each mark, then fair the curve between marks with the orbital sander.
3. Shape edges — 4 operations, in CAD order:
   - **3a. Chamfer 1: Top perimeter chamfer (40mm × 60°).** Mark a line 40mm inboard from the deck edge all the way around the board with a sharpie. Mark a second line on the side face 69mm below the deck surface all the way around. Remove foam between the two lines with the surform rasp to create a continuous chamfer around the entire top perimeter. This is a large cut — expect a lot of foam dust. Check cross-section consistency with a printed profile template.
   - **3b. Fillet 1: Nose rail fillet (R50).** Round the two nose-region top chamfer-to-side-face corners with a 50mm radius, only along the R845 nose arc region. Hand-shape with coarse sandpaper wrapped around a curved block (tennis ball, sanding sponge, or a PVC pipe section of appropriate diameter). Precision not critical — shape by eye to match the CAD render. Start the fillet where the nose arc begins (1000mm from tail) and carry it smoothly to the nose tip. It should blend naturally, with no abrupt transition into the parallel-midsection rail.
   - **3c. Chamfer 2: Nose tip bottom chamfer (40mm × 60°).** At the bottom of the nose vertical face, where the 23mm flat meets the nose-bevel hull underside, take a 40mm × 60° chamfer. Mark 40mm up the nose vertical face from the bottom and 69mm (approx) back along the hull underside, remove material between the marks. This is a single edge only — stops where the nose bottom corner meets the nose rails on each side. Do NOT extend onto the long rails or the tail.
   - **3d. Fillet 2: Top perimeter R20 softening.** Round the entire top deck-to-chamfer corner with a 20mm radius, all the way around the perimeter — long rails, tail end, nose end, blending smoothly over the R50 Fillet 1 areas on the nose. This is a final smoothing pass after the top chamfer is cut. Use sandpaper wrapped around a 40mm-diameter dowel or similar curved block. All top edges should feel smoothly rounded — no sharp corners anywhere on the deck edge.
   - **Note: bottom edges stay sharp 90°** everywhere except the single Chamfer 2 at the nose tip. Do not round or chamfer the long bottom rails, tail bottom edge, or tail bottom corners. Sharp bottom edges are essential for clean water release during takeoff (per sat_be feedback).
4. Smooth everything with orbital sander, 80 grit → 120 grit. Fill any dings or voids with thickened epoxy.
5. Optional: use 3D-printed cross-section templates at key stations (tail, mid-body, bevel start, mid-bevel, nose) to check rail profile consistency while shaping. Most useful for the top 40×60° chamfer which benefits from a consistent angle along the whole length.

---

## Fiberglass Layup — No Vacuum Bag Method

**Technique:** Following Gustav's Danish V2 approach — one surface at a time, one layer at a time. This is more sessions but produces strong, clean results without vacuum bagging. Gustav's V2 uses 4 layers per side which he says is "plenty strong and will last forever."

**Key principles:**
- Fillet all inside corners with thickened epoxy BEFORE glassing (fiberglass won't conform to sharp inside corners without bridging/voids — the fillet gives it a smooth radius to follow)
- One layer at a time, full cure between layers
- Between each layer: wash amine blush with warm water + sponge → dry → sand 80-120 grit → wipe with IPA → next layer
- Drape dry cloth over surface and smooth into position before wetting out. Work from center outward to avoid wrinkles.
- TotalBoat 5:1 epoxy with SLOW hardener throughout (30+ min working time)

**Glassing sequence (each step = one session, cure overnight between):**

**Phase A — Internal Cavity (3-4 sessions)**

A1. Thicken epoxy with chopped fibers or colloidal silica. Trowel fillets into ALL inside corners of cavity and hatch recess area. Aim for ~10mm radius fillets. Epoxy plywood backing blocks (80×45×19mm offcuts) to recess ledge at 2 hinge locations on nose-side short edge, centered 60mm from each corner. Let cure.

A2. Glass cavity interior — 2 layers 6oz on floor (plywood) and walls. Drape cloth, wet out with epoxy. Use a plastic bag filled with water set inside the cavity to press cloth into corners and against walls while curing.

A3. Glass hatch recess area in Layer 3 — 3 layers 6oz for strength. This is the surface the gasket compresses against and where the hinge plywood blocks and lid threaded inserts land. Needs to be beefy. **Seal every cut edge here with neat epoxy** — unsealed laminate edges at this ledge were the source of the Test 2 leak.

A4. Seal any remaining internal surfaces with a coat of neat epoxy or one light layer of glass. Every internal surface must be waterproofed.

**Phase B — Hull / Bottom (4 sessions)**

B1. Layer 1 bottom — first layer 6oz. Drape cloth, smooth into position, wet out. Wrap cloth up and over the rails about 2-3" onto the sides.

B2. Layer 2 bottom — second layer 6oz. Same process, offset the cloth edge slightly from Layer 1 for stagger.

B3. Layer 3 bottom — third layer 6oz. Offset again.

B4. Layer 4 bottom — fourth layer 6oz. Final bottom layer. After cure, sand smooth 80→120 grit.

**Phase C — Deck / Top (4 sessions)**

C1. Layer 1 deck — first layer 6oz. Drape over the deck, wrapping down over the rails to overlap the cured bottom layup by 2-3". Sand the cured bottom rail overlap zone well before this step (80 grit + IPA wipe). Cut opening for hatch area — or glass over and cut open after cure.

C2. Layer 2 deck — second layer 6oz. Same process.

C3. Layer 3 deck — third layer 6oz.

C4. Layer 4 deck — fourth layer 6oz. After cure, sand smooth. The rails now have 8 layers total (4 bottom wrapping up + 4 deck wrapping down) — this is the strongest part of the board.

**Phase D — Hatch & Finishing (3-4 sessions)**

D2. Fabricate hatch lid — cut 3/4" birch plywood to fit the Layer 3 recess. Lay up 3-4 layers 6oz on one face, cure overnight, flip, 3-4 layers 6oz on the other face. Sand smooth. Seal edges with neat epoxy. Finish-sand the underside contact zone (38mm-wide perimeter ring that presses on the gasket) to 220 grit and apply one neat epoxy hot coat — smooth, glass-like surface for the gasket to compress against. **Do NOT bond gasket to lid** — gasket goes on the ledge in a later step (D5).

D3. Install 2× Pyntrax strap hinges on nose-side short edge — deck-side leaf into plywood-backed recess ledge, lid-side leaf into plywood lid. Add 3D printed shims as needed to tune gasket compression. Set M5 hex-drive inserts in the ledge blocking, then drill 7/32" lid clearance holes off the installed inserts.

D4. Open/clean hatch opening if glassed over. Clear mast bolt holes through fiberglass. Sand and prep all surfaces.

D5. Install hatch gasket on ledge. (Do this AFTER all paint/clear coat is fully cured — typically end of Phase E, but listed here with the rest of the hatch work for continuity. If paint hasn't happened yet, delay this step until after E4.) Surface prep: lightly scuff the 38mm-wide sealing ledge with 220 grit to kill the glossy epoxy/paint surface, wipe twice with IPA, let flash off completely. Peel PSA release liner from Trim-Lok X2897BT seal. Starting at the midpoint of a long straight edge (NOT a corner), press seal into position with firm finger pressure. Bend seal around inside corners — do NOT cut and butt-joint at corners (corner joints leak). Continue around perimeter until back at the start, cut to length with ~1mm compression fit, and close the loop with a butt joint at the starting midpoint. Put a tiny dab of thin cyanoacrylate on the two cut faces before butting them together to lock the joint. Apply silicone grease to the TOP surface of the seal (the side that contacts the lid) to prevent the compressed EPDM from bonding to the fiberglassed lid underside over long storage periods. **Leave hatch OPEN for 72 hours** for acrylic PSA to reach full cure before first compression. **Do not latch the hatch shut during this cure period.**

**Phase E — Finishing (3-4 sessions)**

E1. Epoxy hot coat — thin coat of neat epoxy over entire board to fill weave texture. Sand 120→220 grit.

E2. Spray filler primer (gray) — 2 coats. Sand 320→400 grit. Inspect for imperfections, fill and re-prime as needed.

E3. Lime green base coat — 3 coats spray paint. Light sand 400 grit between coats.

E4. Clear coat — 2-3 coats. Final wet sand 600-800 grit if desired for gloss, or leave satin.

E5. Apply traction pad. **As built:** one continuous pad across the whole deck including over the lid, cut into two pieces along the hatch seam (deck piece + lid piece) with a 1–2 mm relief gap so the lid still hinges. Cutouts at the 6 lid bolt positions for driver access, and a gap at the free edge for the pull loop to exit. Template on the deck, cut the foam on a bench (never over the paint), peel the PSA *after* cutting, and only stick it down once the clear coat is genuinely hard — days, not hours.

**Total glassing sessions: ~14-16 sessions over 3-4 weeks** (one session per evening, cure overnight, sand/prep next morning, glass next evening).

**Epoxy usage estimate:** 4 layers each side + cavity + hot coat + hatch lid ≈ 2.5-3 quart kits of TotalBoat 5:1. You have 2 ordered — will likely need a third.
