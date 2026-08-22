# Build guide — every step, in order

How this board actually gets made, start to finish. Each step says what you
do, what it needs finished first, and **exactly which BOM lines it consumes**.

- **Uses:** lines quote BOM item names verbatim. `model/check_build_guide.py`
  verifies every one still exists, so this file cannot quietly drift from
  [bom.md](bom.md) the way the old colour key drifted from the model.
- **Blocks on:** what must be done first. Anything with no blocker can start
  today.
- Step numbers are stable. Add with letters (`4a`) rather than renumbering.

Two boards are being built. Almost everything below is "×2" — the exceptions
are the shop kit, which is bought once, and the CNC session, which does both
cores in one booking.

---

## The shape of the job

Three chains run in parallel and only meet at the end. **Start all three on
day one** — the board chain is the long one, and the other two are pure
waiting if you leave them late.

| Chain | What | Wall time | On the critical path? |
|---|---|---|---|
| **A — Board** | core → laminate → fair → paint | ~8 weekends | **Yes.** Everything else waits on it |
| **B — Printing** | rim rings, module shells, props, clamps | ~120 print hours | No, *if started first* |
| **C — Pack** | cells → weld → BMS → wiring | ~2 weekends | No |

The two things that will actually delay you are **not** in the shop:

1. **The foil ships from France** and US customs arrives *after* delivery as a
   courier invoice. Order it first.
2. **The makerspace has not confirmed it allows EPS.** If the answer is no,
   step 4 changes completely — see [Appendix C](#appendix-c--if-the-cnc-falls-through).

---

# Phase 0 — Before anything

### Step 1. Order the long-lead items

Everything else can wait a week. These cannot.

**Uses:** `Gong Foil Setup X-Over V3 Atmo Perf Series - XL, Alu 85` ·
`Gong shipping to Idaho, ONE order, both foils` ·
`BAK N21700CG-50, 130-cell case (BatteryHookup)` ·
`BAK N21700CG-50 singles, spares` ·
`Flipsky 65161 120KV motor` · `Flipsky 75200 Pro V2 ESC` ·
`Flipsky VX3 remote` · `DALY Smart BMS Li-ion 16S 60V 150A`

Both foils go in **one** Gong order — shipping is charged per order, not per
foil. Budget for import duty separately; it is not quoted at checkout.

### Step 2. Phone the makerspace — do not email

Email got no reply twice. **(208) 254-6151.** Ask, in this order:

1. **Will you allow EPS foam on the CNC?** Mess, static, clogs extraction.
   This one can stop the plan.
2. What is the clearance under the gantry? The split sequence needs ~110 mm,
   so this is now a nice-to-know rather than a blocker.
3. Which CAM do you use, and can I bring my own toolpaths?

**Uses:** `Maker Shop Boise Basic month`

Basic is **8 shop visits a month, not unlimited** — a budget, not a door key.
Unlimited is $250, a day pass $99. Month-to-month, 10 days notice to cancel.

### Step 3. Start the printers, and do not stop them

~120 hours of printing. Start now and it is never the thing you are waiting
for; start in week six and it is the only thing you are waiting for.

**Uses:** `ASA filament, printed rim ring` · `ASA filament, printed module shell` ·
`PETG filament 1 kg, mast clamp set` · `PETG for props, 4-5 spares per board` ·
`M5 A4 hex nut DIN934, 50 pk - CAPTIVE in the ring` ·
`M5 penny washer O15 DIN9021, 150 pk`

Print order, longest first: module shells → rim rings → props → clamps.

**The rim ring prints seal-face DOWN.** The bed is flatter than any top
surface, and that face is the sealing land. **Pause at Z = 6.0 mm**, drop 12
M5 nuts and their washers into the pockets, resume. Get this wrong and the
hatch has no threads.

---

# Phase 1 — The core

### Step 4. Glue up two sub-stacks per board

Not one stack. **Four EPS layers become two 2-layer slabs**, because the
glued 4-layer stack is 203.2 mm and the gantry is 149.9 mm.

**Blocks on:** —
**Uses:** `EPS rigid foam 2in x 48in x 8ft (HD 202532856)` ·
`PL300 / Gorilla Glue, layer glue-up`

Four sheets cover both boards. Cut layers oversize to ~1420 × 580 — two nest
per 1219 × 2438 sheet. Glue **layers 1+2** and **layers 3+4** as separate
slabs, 101.6 mm each. Keep both faces flat; they are the machining datum.

> Four layers, not three. Three is 152.4 mm against a 166.8 mm envelope,
> because the rocker adds ~10 mm the old three-sheet figure never counted.

### Step 5. Machine the core — one booking, both boards

**Blocks on:** steps 2, 4
**Uses:** `1/2 in O-flute up-spiral, foam roughing` · `1/2 in ball nose, finishing pass` ·
`3M Fastbond 1077 water-based, CNC hold-down` · `Sacrificial MDF, CNC spoilboard` ·
`Dowel pins + drill, two-sided registration`

**Five setups, one flip, no cradle.** The full table is in
[cut-list.md](../cnc/cut-list.md); the short version:

| Piece | Setups | Cut |
|---|---|---|
| `Aft_Lower` | 2 | cavity lower half (top); rocker + mast pocket (bottom) — **the flip** |
| `Aft_Upper` | 1 | deck crown, cavity through, rim ledge, leash pocket |
| `Fwd_Lower` | 1 | rocker |
| `Fwd_Upper` | 1 | deck crown |

Every setup beds on a flat face, so **tape or vacuum down — never clamp from
the edges**, there is only 24.8 mm a side.

> **CUTTER REACH — settle this before you book.** The deepest pocket is the
> cavity's lower half at **71.6 mm**. The O-flute above has a *cutting* length
> of **31.8 mm** — that is flute, not overall — so it is **39.8 mm short and
> cannot reach the floor.** Buy a long-reach ½ in spiral with 75 mm+ of
> flute, or rough that pocket with the ball nose. Do not discover this with
> the foam taped down.

Water-based adhesive only. **Super 77 is solvent-based and dissolves EPS.**

### Step 6. Bond the core solid

**Blocks on:** step 5
**Uses:** `PL300 / Gorilla Glue, layer glue-up`

Mid-plane first — Lower to Upper, each side of the seam — which gives two
full-thickness halves you can handle on a bench. Then butt those at the
vertical seam (1030 mm). Dowel pins keep the halves registered.

### Step 7. Fit the hardpoints

**Blocks on:** step 6
**Uses:** `Divinycell H-80 3/4in quarter sheet 24x48, mast block + leash pad` ·
`6061-T651 1/2in x 12 x 18 - mast plates` · `M8 x 1.25 tap + 6.8 mm drill set` ·
`M8 x 1.25 BOTTOMING tap, 4-flute` ·
`M8 thread repair kit (Time-Sert / helicoil)`

The CNC already cut the pockets. Bond the H-80 mast block and leash pad in,
flush.

> **MACHINE THE MAST PLATE. Do not hand-drill it.** This guide used to say
> the Gong plate was jig enough — clamp, spot through, drill, tap. That
> reasoned from V1, where the holes were THROUGH holes with a nut on the far
> side and clearance quietly absorbed every error of position, angle and
> depth. **None of that is true here.** These are blind tapped holes: the
> thread *is* the fastener, and all four bolts must start at once.
>
> | | |
> |---|---|
> | Radial slop in Gong's clearance hole | 0.50 mm |
> | True position the pattern must hold | **0.25 mm** — errors at opposite corners add, they do not cancel |
> | Wander from a hole just 2° off | **0.35 mm** — more than the entire budget, on its own |
> | Solid alu left above the tap | **2.7 mm** before you breach the plate keeping the cavity dry |
>
> A hand-held drill is routinely 3–5° off. The arithmetic rules it out; this
> is not a matter of care.

**Route, in order of preference:**

1. **Job-shop it.** A 250 × 175 rectangle with four tapped holes is a trivial
   job, and cheap against the cost of getting it wrong.
2. **The makerspace CNC — if they permit aluminium.** It is a woodworking
   shop, so this is a question, not an assumption. Ask on the same call as
   the EPS one.
3. **Drill press**, with a bought drill bushing, a tapping guide and the
   depth stop set. Acceptable as a fallback. It is not the plan.

**Measure the real Gong plate first and machine to what you measured** — not
to the 165 × 90 nominal in the drawing, which is unverified layout only. A
perfectly machined plate on the wrong pattern is still scrap.

The bottoming tap still matters: blind at 10 mm in a 12.7 plate, and the
taper tap in the set cannot reach. Both plates nest on one 12 × 18 sheet.

Temper matters — this must say **T651**. 6061-O has about a fifth the yield,
and this plate carries 6.3 kN.

---

# Phase 2 — Laminate

Read [Appendix A](#appendix-a--vacuum-bagging-in-detail) before the first
session. The whole phase is governed by one number: **20 minutes of pot life.**

### Step 8. Set up the shop

**Blocks on:** —  *(do this while the printers run)*
**Uses:** `Folding sawhorses, pair, 700 lb` · `Pipe lagging or carpet, sawhorse padding` ·
`Rosin paper roll, floor and bench` · `Plastic sheeting + masking tape, bench protection` ·
`Thermometer / hygrometer, 2 pk` · `3M 60923 organic vapour / acid gas P100, pair` ·
`Nitrile gloves 6 mil, 100 pk`

Two padded sawhorses at ~30 in, rosin paper down. Cartridges expire — buy
them near the layup, not with the rest of the order.

### Step 9. Prove the vacuum rig before it matters

**Blocks on:** step 8
**Uses:** `VECOTOOLS 4.5 CFM single-stage pump, oil incl.` · `VR20 vacuum regulator` ·
`Vacuum gauge, -30 inHg, 1/4 NPT, glycerin` · `Bag connector w/ ball valve, 1/4 in QD` ·
`Vacuum hose + hose clamps` · `Vac bag film, 5 yd` · `Sealant tape, 50 ft roll`

Bag a scrap dry, pull down, **shut the ball valve** and watch the gauge for
30 minutes. That valve is why leak-down is a measurement and not a guess
about whether the pump is keeping up.

**Target 5–10 inHg, never more.** EPS crushes around 150 kPa and full vacuum
is 101 — the regulator is what stops the bag destroying the core.

### Step 10. Bottom skin

**Blocks on:** steps 7, 9
**Uses:** `E-glass 6 oz, 50in x 12ft, 2-pack` · `1708 biax, 50in x 10 yd roll` ·
`TotalBoat 5:1 gallon kit, slow hardener` · `Peel ply, 60in` ·
`Breather / bleeder cloth` · `Chip brushes 2 in, 36 pk` ·
`Laminating bubble roller kit, 4 pc`

**Both bottom layers in one session, always.** A second session onto cured
laminate is a secondary bond that needs sanding and washing first, and buys
nothing.

### Step 10a. Fit the rim ring — **before** you glass anything

**Blocks on:** steps 3, 7
**Uses:** `Acetone, solvent-welding the printed joints` ·
`Paste wax, releasing the groove filler`

**The ring is glassed IN, not bonded on afterwards.** Acetone-weld the six
printed segments into one ring — a brushed acetone/ASA slurry makes it one
piece of plastic, not an adhesive line — then seat it on its ledge with the
printed filler strip **waxed** into the seal groove.

It stays there through the cavity layup. The laminate runs up the cavity
wall, across the ledge and over the ring in one continuous piece, which is
the whole reason the groove is filled first: glass drapes over a 4 mm ridge
you can see and feel, instead of into a channel you then have to dig out.

**Dry-fit the caul now, with the ring in.** That is the only moment it is
free to discover the caul fouls something.

### Step 11. Deck skin and cavity

**Blocks on:** step 10 cured
**Uses:** `E-glass 6 oz, 50in x 12ft, 2-pack` · `1708 biax, 50in x 10 yd roll` ·
`TotalBoat 5:1 gallon kit, slow hardener` · `Peel ply, 60in` ·
`Breather / bleeder cloth` · `Release wax / PVA for the cavity caul`

The cavity is a **concave box** — a bag bridges it like a drum skin and
touches nothing inside. The caul does the work, not the bag: it is a male
plug (an EPS offcut, part 13) that drops onto the wet laminate so the bag
presses on *it*. Wax and PVA it properly; a caul bonded into a cured cavity
is not recoverable.

**The ring is in place for this**, so the caul is cut to fit around it: it
drops inside the ring's inner edge and stands the **full 100.1 mm** from
cavity floor to ledge. That height matters — the caul used to be specified at
the *module's* height, 93.6 mm, which is a different measurement and 6.5 mm
short. It stopped below the ledge, so the wall-to-ledge corner — concave,
exactly where a bag bridges — got pressure from neither caul nor bag. That
corner is where the ring sits and where the seal ends up.

### Step 11a. Lay up the two lids

**Blocks on:** step 9
**Uses:** `Divinycell H-100 1/4in quarter 21x42, hatch lid cores - 2 sheets bonded to 1/2in` ·
`Divinycell H-80 1/4in quarter 24x48, module lid cores` ·
`E-glass 6 oz, 50in x 12ft, 2-pack` · `TotalBoat 5:1 gallon kit, slow hardener` ·
`Peel ply, 60in` · `Breather / bleeder cloth`

Both lids are flat sandwiches — glass / foam / glass — so they bag on the
bench and **do not need the board**. Do them alongside a hull session while
the pump is already set up and mixed resin is going spare.

The hatch lid core is **H-100**, and it is two ¼ in sheets bonded to ½ in
because no ½ in H-100 is made. That grade is deliberate: you stand on this
one. The module lid is H-80 — nobody stands on it.

Trim to net profile after cure (parts 02, 03, 10, 11), and face the hatch
lid's underside flat in the same setup — it has to bottom evenly on the seal
land.

### Step 12. Seal every cut edge

**Blocks on:** step 11
**Uses:** `TotalBoat 5:1 quart kit, fillets and bonding`

Neat epoxy into groove walls, the lid perimeter, all 12 lid bores, every
machined edge. **This is V1's leak, verbatim** — its own notes read *"cured
laminate is NOT waterproof at a cut edge."* Water came in through unsealed
fibre ends at the cavity ledge.

---

# Phase 3 — Hatch and module

### Step 13. Open the groove and bond the cord in

**Blocks on:** steps 10a, 11
**Uses:** `Acetone, solvent-welding the printed joints` ·
`Paste wax, releasing the groove filler` ·
`Solid silicone cord, 3 mm round - BOTH seals` ·
`Silicone adhesive, bonding the cord into groove` ·
`Cyanoacrylate for the cord splice` · `2.5 mm straight cutter - fallback` ·
`M5 x 25 A4 socket cap, 20 pk` ·
`Solid silicone cord, 1/8 in (3.175 mm) - the spare size`

The ring went in at step 10a and has been glassed over since. Now sand the
ring face flat — it is the sealing land, so it has to be flat anyway — and
the filler strip shows through as a line along the whole groove. Pick it out
and the printed walls are the finished groove.

**Wet the opened groove with neat epoxy before the cord goes in.** Sanding or
routing leaves cut glass ends in the seal itself, which is the same wick that
flooded V1. Silicone adhesive does not stop a wick; epoxy does.

Bond the cord in on a thin continuous bead. Splice on a straight run, never a
corner.

**Measure the finished groove before choosing cord.** Nominal is 2.4 mm deep,
which the 3 mm cord squeezes 20%. If it routs deep the 3 mm only reaches 10%
and you want the 1/8 in spare instead — that is what it is for. Guessing the
cord before the groove exists is how you end up at 10%.

### Step 14. Build the module

**Blocks on:** step 3
**Uses:** `5052 1/8in x 12 x 24, 2-pack - module floors` ·
`Sikaflex-292 marine structural PU` · `Sika Aktivator-PRO 250 ml + daubers` ·
`2 mm glass beads or shim wire, bond-line control` ·
`M4 x 8 brass heat-set insert, 100 pc` · `Neoprene sheet 1/8in, module + mast gaskets` ·
`Gebildet PG11 gland, M18x1.5, 30 pk` · `M12 IP68 membrane vent plug` ·
`M12 IP68 momentary panel button` · `SP17 2-pin IP68 flange receptacle` ·
`M3 heat-set insert kit, 361 pc` · `M3 x 8 A4 stainless, 10 pk`

Acetone-weld the four printed L-pieces into a shell. Bond it to the 5052
floor on a **2 mm controlled bond line** — glass beads set the gap, fillet
both sides. It must be flexible PU, not epoxy: ASA and aluminium differ by
66 µm/m·K, which is 0.60 mm of movement from the centre over 40 °C. A rigid
line sees 299% shear strain and tears itself apart.

Heat-set the lid inserts into the printed flange. The M3 kit's screws are
plain steel — use the A4 ones for the port flange, which lives in the wet.

### Step 15. Leak-test the module empty

**Blocks on:** step 14
**Uses:** `Test cap + tubing, module leak test` ·
`M12 x 0.75 male to hose barb, test port` · `Bag connector w/ ball valve, 1/4 in QD`

**The module has no test port — and does not need one. Use the vent boss.**
In service that threaded hole carries the M12 membrane vent; for the test it
carries an M12 × 0.75 male-to-barb adapter. Same hole, no extra penetration.

**The vent must be OUT while you test.** An ePTFE membrane passes air by
design — that is the entire point of it — so with the vent fitted the module
cannot hold vacuum and there is nothing to measure. That is not the vent
defeating the design, it is the vent defeating the *test*, which is why the
test comes first and the vent goes in after. The two jobs are different:

- the **seals** stop liquid water
- the **vent** passes air, so the module breathes through a filtered path
  instead of pumping through a marginal gasket every time it goes from cold
  water to hot sun

**Vacuum, not pressure.** Submerged, the module sees external pressure
pushing the lid *onto* its gasket — vacuum inside reproduces that direction.
Pressure inside tests the opposite and would fail a joint the board never
loads that way. It is also unsafe: 0.2 bar across a 451 × 292 lid is about
**2.6 kN**.

**Prove it before the cells go in.** Seal it empty, pull 5 inHg, shut the
ball valve, watch the gauge 30 minutes — porosity reads as a slow bleed. Then
do it **submerged**: under vacuum any path pulls water *in* and shows you
exactly where. V1 found its leaks by riding.

---

# Phase 4 — Pack and electronics

Runs entirely in parallel with Phases 1–3.

### Step 16. Build the pack

**Blocks on:** step 1
**Uses:** `BAK N21700CG-50, 130-cell case (BatteryHookup)` ·
`BAK N21700CG-50 singles, spares` · `Pure nickel 0.2 x 10 mm, 5 m roll` ·
`Kapton tape, pack insulation` · `PVC pack wrap, 200 mm lay-flat` ·
`DALY Smart BMS Li-ion 16S 60V 150A` · `Silicone sealant, BMS anti-vibration dabs`

16S8P, 128 cells, 2,304 Wh, 9.22 kg. Confirm the BMS is **Li-ion, not
LiFePO4** — different chemistry and pack voltage, and it is the easy wrong
answer at a glance. Silicone dabs stop the BMS walking; V1 needed them.

### Step 17. Wire the module

**Blocks on:** steps 15, 16
**Uses:** `8 AWG silicone, 10 ft red + 10 ft black` · `16 AWG silicone, 6 colours x 5 ft` ·
`ANL 150 A fuse + holder` · `8 AWG marine ring lugs, 20 pk` ·
`Hydraulic lug crimper, 10 ton, 12-2/0 AWG` ·
`Adhesive-lined heat shrink 3:1, 400 pc kit` · `5.5 mm gold bullets, 20 pair` ·
`Dielectric grease, terminals` ·
`Cable ties, lacing, adhesive mounts` · `Thermal pad 1 mm non-conductive, 100 x 100` ·
`Silica gel, indicating, 50 g per module` · `Water-ingress alarm, 2 pk`

Crimped, not soldered. The thermal pad **must be non-conductive** — the ESC
PCB face goes down onto an aluminium floor and a metal-loaded pad is a dead
short. Put the leak alarm's sensor on the module floor in the lowest corner,
not up on the pack.

**The full topology, every joint and every crimp, is
[Appendix D](#appendix-d--wiring).** Read it before you cut a single lead —
it answers where P+ splits, what the fuse protects, and the two mistakes
that kill a BMS.

### Step 18. Run the mast conduit

**Blocks on:** steps 7, 17
**Uses:** `Fish tape / pull cord for the mast conduit` ·
`IP68 M25 inline housing, 5 pk` · `EPDM/neoprene sheet 1/2in, conduit bungs` ·
`3M 4200 FC 3 oz tube, fillet over the bung`

Motor leads part **in the cavity**, one housing per phase — without that the
mast is bolted on for life. Cut Ø33 bungs for the Ø32 bore, punch three Ø5
holes, soap them through, then fillet over with 4200. **4200 not 5200** —
5200 never comes out.

---

# Phase 5 — Finishing

### Step 19. Fair

**Blocks on:** step 12
**Uses:** `TotalBoat TotalFair epoxy fairing compound` ·
`Flex longboard sander, 16-1/2 x 2-3/4` · `Adjustable hand sanding block` ·
`Longboard PSA sandpaper 80 grit, 20 yd roll` ·
`Longboard PSA sandpaper 120-180 grit, 20 yd roll`

**Flex longboard, not a rigid block.** The deck is crowned and the bottom
rockered; a rigid block bridges the curve and cuts flats you then have to
fair back out. 80 grit cuts fair, it does not finish.

### Step 20. Prime and paint

**Blocks on:** step 19
**Uses:** `TotalBoat Premium Marine Topside Primer` ·
`TotalBoat Wet Edge topside paint, colour` · `Wet/dry sandpaper assortment, 45 pc`

Wash before any secondary bond — amine blush comes off with **water**, not
solvent. Acetone smears it around.

### Step 21. Deck pad

**Blocks on:** step 20
**Uses:** `FOCEAN EVA deck sheet 2400 x 600 x 5.8`

Three pieces per board — aft of the hatch, forward of it, and one on the lid.
One sheet does both boards. Pattern is part 15 in
[cut-list.md](../cnc/cut-list.md).

Cut **long** and trim on the board; with no seams the crown's arc excess goes
into stretch and the trim at the rail. Peel the backing progressively from
the centreline outward — a 5.8 mm sheet laid in one go traps air it will not
give back.

---

# Phase 6 — Assembly and first water

### Step 22. Fit out

**Blocks on:** steps 18, 21
**Uses:** `Kayak-style webbing carry handle, 4 pk` · `M6 x 16 A4 button head, 10 pk` ·
`M6 heat-set insert, strap mounts` · `1 in polyester webbing 6 yd + 6 buckles` ·
`FCS-pattern leash plug` · `Coiled ankle leash` ·
`M4 x 12 A4 socket cap DIN912, 10 pk` · `M4 A4 washer, 316, 100 pk`

Webbing is **polyester, not nylon** — nylon absorbs water and stretches, so
what you tightened on the beach is loose on the water.

### Step 23. Mount the foil and drivetrain

**Blocks on:** steps 7, 22
**Uses:** `M8 x 30 A4 mast bolts, 10 pk - spares` · `Ultra Tef-Gel, galvanic barrier` ·
`M5 x 250 threaded rod, 4 pk (cut to ~171 mm)` · `M6 x 20 fender washer, 100 pk` ·
`M5 nyloc nut 316, 150 pk` · `Loctite 242` · `Roll pin assortment M1.5-M6, 220 pc` ·
`M8 nyloc nut 316, 30 pk - prop nut` · `M8 316 washer, prop nut` ·
`1/4 in torque wrench, 10-50 in-lb`

**Tef-Gel every mast bolt, every time.** Aluminium plate, A4 bolts, wet
cavity — that is the whole galvanic mitigation and it is not optional.

**Measure** the prop shaft cross-hole rather than trusting the 4 mm figure;
that is why the roll pin line is an assortment.

The torque wrench is a **calibration tool**: set the drill clutch with it,
then use the clutch. Hatch spec is 2 Nm — 17.7 in-lb, which is *below* the
floor of the common 20–200 in-lb wrenches, hence the 10–50 one.

### Step 24. Seal, charge, and go

**Blocks on:** step 23
**Uses:** `Silicone grease for the seal cord` · `Charger 67.2 V 5 A, 16S  (NOT 58.8 V)`

Grease the cord so it does not bond to the lid in storage. Confirm the
charger is **67.2 V** — a 58.8 V charger is a 14S charger and will never fill
this pack.

First session: bag-test the module one more time, then ride it shallow.

---

# Appendix A — Vacuum bagging in detail

### The number that shapes everything: 20 minutes

Slow hardener is 20 minutes of pot life at 75 °F. That is the entire design
constraint on every session — how much you can mix, how much you can wet out,
how far you can be from the bag when it starts to go off.

Mix in **small batches**, never one big pot. A full pot goes off in the pot.

### Building through a Boise winter

| Hardener | Minimum | Pot life |
|---|---|---|
| Slow | 60 °F | 20 min @ 75 °F |
| Fast | 40–45 °F | shorter, but the cold gives it back |

Below ~35–40 °F epoxy **cannot cure at all** — it does not go slowly, it
stays soft forever. A cold laminate is not a slow laminate, it is a ruined
one. **Uses:** `TotalBoat 5:1 FAST hardener 6 oz, cold days`

### Dry-run the bag before you mix anything

Full rehearsal: cloth dry, caul in, bag sealed, pump on, gauge watched. Every
problem you find dry is free. Every one you find wet costs a laminate.

### The bag does not press the part onto the table

Envelope bagging puts the same pressure on every face of a closed body, so
the **net force is zero** — it consolidates from all sides and pushes the
part nowhere. The table only ever carries the board's weight. A blanket under
it is a nicety, not a requirement.

### What good looks like at de-bag

Even, dull peel-ply texture. No shiny patches (resin-rich), no white ones
(dry). Breather uniformly stained, not soaked in one corner.

---

# Appendix B — Machine envelope and workholding

Maker Shop runs an **Axiom AR8 Pro V5: 609.6 × 1209.8 × 149.9 mm.**

| | Needs | |
|---|---|---|
| Longer core half | 1030 × 560 | fits, 180 mm spare |
| Shorter core half | 370 × 560 | fits |
| Whole board in one piece | 1400 × 560 | **no** — hence the vertical seam |
| Glued 4-layer stack | 203.2 tall | **no** — hence the horizontal split |

**Y is the tight axis:** 560 mm in a 609.6 mm bed leaves 24.8 mm a side. Fine
for tape-down, no room for clamps.

**Two-sided registration** matters exactly once — only `Aft_Lower` flips.
Drill the dowel holes in the spoilboard and in the waste perimeter *before*
any 3D work starts.

---

# Appendix C — If the CNC falls through

The mast plate does not need a machine (step 7). For the core:

1. **Hot-wire the rocker and plan-shape, hand-shape the crown.** How every
   home-built board was made before CNC. Slow, forgiving in EPS.
2. **Job-shop just the core.** Send the STL; keep everything else in-house.
3. **Another makerspace or a maker with a large-format router.**
4. **Buy a shaped blank** and adapt the cavity by hand.

The check gauges exist for exactly this case — station sections you can
offer the shape up to. **Uses:** `MDF 12 mm, 4 check gauges`

---

# Risks, honestly

| Risk | Mitigation |
|---|---|
| **Shop bans EPS** | Ask before buying a pass. Appendix C |
| **Cutter cannot reach the cavity floor** | Known: 39.8 mm short. Buy long-reach or rough with the ball nose |
| Never having run a CNC | Test piece in scrap first; foam is unbreakable |
| Flip registration wrong | Dowel pins; dry-run in air; check the mirror axis |
| Blank too tall for the gantry | Solved by sequence — 101.6 mm halves, bonded after |
| Running out of shop visits | Basic is 8/month, not unlimited; a day pass is $99 |
| Epoxy too cold to cure | Fast hardener + hot box; below 35 °F do not start |
| Crushing the core in the bag | Regulator at 5–10 inHg. Never "as much as it pulls" |
| Cavity cures with voids | The caul, not the bag. Wax and PVA it |
| Seam misalignment | Both halves off the same fixture and datum |

---

# Appendix D — Wiring

## The one thing to understand first

**A common-port BMS switches the NEGATIVE side only.** Pack positive is never
interrupted — it runs straight from the cells to a busbar and stays live at
pack voltage forever. Everything below follows from that, including the
hazard at the charge port.

**CONFIRM YOUR DALY IS COMMON PORT** before wiring. DALY sell both. A
separate-port unit has distinct charge and discharge negatives and the
charge port wires somewhere else entirely. Common port is the usual for
e-boards and is what this assumes.

## The current path

**There is no busbar.** An earlier version of this appendix said there was,
and built the whole topology on the BOM line `M6 stainless stud/busbar
hardware` — which is a $14 line with no note, never specified, and matched to
a distribution block by a guess. Nothing was designed around it. There is no
room budgeted for it either.

**The positive node is the ANL fuse holder's input stud**, which already
exists and is already in the module. Three ring lugs land on it. That is the
whole of it.

```
        CELLS 16S8P                              ┌── ANL 150 A ──► ESC  V+
             │                                   │   (fuse OUT)
   B+ ───────┴───────────► FUSE HOLDER IN stud ──┤
   (pack positive)         3 ring lugs           ├── 16 AWG ─────► CHARGE  +
                                                 │
                                                 └── thin lead ──► BMS  B+
                                                                   (sense)

   B- ──────► BMS  B-  ──► P-  ──┬── 8 AWG ─────► ESC  V-
                     (switched)  │
                                 └── 16 AWG ────► CHARGE  −   [see below]

   BALANCE: 17-wire harness, B0 … B16, one tap per series junction
   BUTTON:  2-wire momentary to the BMS switch input — NOT in the main path
```

**So P+ does not "split into" a BMS lead and a charge lead — it is one node**,
and that node is a stud you already own. Charge current is 5 A, so it does
not pass the 150 A fuse and does not need to; the charger limits itself and
the lead is 100 mm of 16 AWG inside a sealed box.

## Joint by joint

| # | From | To | Wire | Termination |
|---|---|---|---|---|
| 1 | Pack B+ collector | Fuse holder IN stud | 8 AWG | ring lug both ends, hydraulic crimp |
| 2 | Fuse holder IN stud | Charge port + | 16 AWG | ring lug at stud, solder at port |
| 3 | Fuse holder IN stud | BMS B+ | per BMS | as supplied |
| 4 | Fuse holder OUT stud | ESC V+ | 8 AWG | ring lug |
| 5 | — | — | — | *(three lugs share the IN stud: 1, 2, 3)* |
| 6 | Pack B− collector | BMS B− | 8 AWG | ring lug, hydraulic crimp |
| 7 | BMS P− | ESC V− | 8 AWG | ring lug |
| 8 | BMS P− *(common port)* or **C−** *(separate port)* | Charge port − | 16 AWG | ring lug |
| 9 | — | — | — | *(two lugs share P−: 7, and 8 if common port)* |
| 10 | BMS balance | 17 series taps | 22 AWG harness | JST at BMS, welded tab at pack |
| 11 | BMS switch | Panel button | 2 × 22 AWG | as the BMS specifies |
| 12 | ESC phases | Motor, in the cavity | motor's own | 5.5 mm bullets + IP68 housing |

Every 8 AWG lug: **hydraulic crimp, then adhesive-lined heat shrink over the
barrel and onto the insulation.** Not soldered — a soldered lug goes stiff
where the solder wicks, and that stiff point is where vibration breaks it.

## The fuse goes at the source

The ANL protects the **wire**, not the ESC. It belongs as close to pack
positive as it can physically go — joint 2, immediately off the busbar. A
fuse at the ESC end leaves the whole run between pack and ESC unprotected,
which is the run buried in a sealed module you cannot reach.

## Two mistakes that kill a BMS

1. **Never connect the balance harness before the main leads.** Main first
   (B−, then B+), balance last. Disconnect in reverse: **balance off first.**
   With the balance plugged in and B− floating, pack current finds its way
   through the balance wires — 22 AWG — and takes the BMS with it. This is
   the single most common way these die.
2. **Check the balance harness order before it goes on.** B0 is pack
   most-negative, B16 most-positive, and every tap in between is a series
   junction in order. Meter each pin against B0 before plugging in: you
   should read a clean ladder, ~3.6 V per step. One transposed pair is a
   dead BMS and possibly a dead group.

## Making the charge port dead when the BMS is off

Derek's requirement, and it is the right one. It also needs a correction to
what this appendix said before, which over-stated the hazard: **the charge
port is not on the outside of the board.** It is panel-mounted through the
module's aft wall, inside the cavity, under a hatch held by twelve M5s. To
reach it you open the board. Nobody brushes against it on a beach.

That said, "live pins inside a sealed box full of wiring" is still not what
you want, and the fix is a **BMS choice, not a wiring trick**:

| | Common port | **Separate port** |
|---|---|---|
| Charge − | shares P− with the load | its own **C−**, switched by the charge FET |
| Short the two port pins together | dead short across the pack through the discharge FET — you are relying on the BMS's overcurrent trip to save you | **nothing happens.** The return path is open |
| Port pins with BMS off | + live, − live | + live, **− open** |

**A port is only dangerous if both of its pins can pass current between
them.** Separate port opens the return, so the port cannot deliver anything
no matter what touches it. That is a real difference in kind, not a degree —
and it is the answer to "off when the BMS is off".

Be honest about what it does not do: the **+ pin is still at pack potential**,
because nothing switches the positive side on either type. What changes is
that it can no longer source current through the port.

**Action: confirm which DALY you have before wiring, and buy separate-port if
there is a choice.** The two variants look identical and differ by one
terminal. Getting this wrong is not recoverable by rewiring — it is the BMS.

If you end up on common port anyway: keep the screw cap on as a guard, and
never probe the port with the pack connected.

## Precharge — decide this before first power-up

A 75200 ESC's input capacitors are effectively a short circuit at the instant
of connection. On a 67 V pack that means a hard arc, pitted contacts, and
occasionally a welded pair.

**If the DALY's switch output is what energises the ESC**, the BMS FETs take
that inrush and there is nothing more to do — the button *is* the anti-spark.
**If the ESC is hard-wired across P−** and the BMS is simply always on, then
every connection of the pack arcs, and you need either an anti-spark
connector in the loop or a precharge resistor across the switch.

**Confirm which one you have built before the first connection**, not after.
This is the one item in this appendix that the model cannot tell you — it
depends on the DALY variant in your hand.

## Sanity checks before the lid goes on

- Meter pack voltage at the busbars: ~57.6 V nominal, 67.2 V full.
- Meter the charge port with the pack live — polarity, and that + really is +.
- Confirm the fuse is on the **positive** side, pack-side stud.
- Tug every crimp. A crimp that moves is a crimp that failed.
- Dielectric grease on every terminal, then the leak test again with the
  vent blanked before the cells go in for good.
