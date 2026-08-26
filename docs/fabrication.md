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

> **Watch it first.** `model/animate_build.py` renders these steps as a
> two-minute animation straight out of the model — the CNC setups, the flip,
> the bonding order, the module going together and dropping in. Every frame is
> the real geometry, so if the animation and this file disagree, one of them
> has drifted and it is worth finding out which:
>
> ```
> blender -b model/efoil_v2.blend --python model/animate_build.py -- --res 1600
> ```

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
`M6 penny washer O18 A4 DIN9021`

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

> **Four layers, not three — but only just, and that is worth knowing.**
> Three sheets are 152.4 mm against a 153.7 mm envelope, so they miss by
> **1.3 mm**, and the miss lands on the rocker where there is no material to
> borrow. When this was decided the board was 153.8 thick and three sheets
> were 11.4 mm short; the board has slimmed since and nobody re-checked. It
> still points the same way. If it ever loses another 2 mm, re-open it — a
> whole sheet a board and an even 2+2 machining split ride on this.
> `blank_three_sheets_short_by_mm` tracks it now, so it cannot go stale again.

### Step 5. Machine the core — one booking, both boards

**Blocks on:** steps 2, 4
**Uses:** `1/2 in O-flute up-spiral, foam roughing` · `1/2 in ball nose, finishing pass` ·
`1/2 in spiral, 3 in cutting length - cavity wall` ·
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

> **CUTTER REACH — two bits, and take both.** The deepest pocket is the
> cavity's lower half at **71.6 mm**, and the Freud O-flute has a *cutting*
> length of **31.8 mm** — that is flute, not overall.
>
> **That does not matter for roughing.** Z-level passes clear the whole
> pocket at every level, so by the time the tool is 71.6 mm down its shank is
> travelling through open air, not down a slot. The Freud roughs the lot.
>
> **It matters for the wall finish**, which is one pass down a finished wall
> with 12.7 mm of smooth shank rubbing EPS above the cutting edge. Foam has
> no strength to resist it but it does melt and glaze, and a glazed wall is a
> bond surface you cannot wet out. That is what the **3 in spiral** is in the
> BOM for: **76.2 mm of flute against 71.6 mm of wall.** It has been on the
> list all along; earlier drafts of this box told you to go buy one.

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
`6061-T651 1/2in x 12 x 18 - mast plates` · `M6 x 1.0 tap + 5.0 mm drill set` ·
`M6 x 1.0 BOTTOMING tap, 4-flute` · `Transfer punch set, metric 1-13 mm`

The CNC already cut the pockets. Bond the H-80 mast block and leash pad in,
flush.

> **Bed the wire blocker before the plate goes on.** A printed part: **Ø30.4 ×
> 4 body** that fills the top of the plate's bore, a **Ø23.6 × 12 spigot** up
> into the foam's, and a **22 × 7 slit** for the leads.
>
> **This is what gives the wire bung a stop that exists.** The bung is squeezed
> by the mast plate and something has to take that push. **Nothing is machined
> into the alu for it** — the plate keeps its one straight Ø30.8 bore. The
> dense block is simply **bored narrower, at Ø24**, and the ring of foam that
> leaves showing inside the plate's bore is what the blocker lands on. That is
> the only change of diameter anywhere in this conduit.
>
> It backs the bung across **95%** of its face. Without it the bung pushes
> against an open bore and most of the squeeze extrudes up the channel.
>
> **Bed the spigot properly on 4200 — that bond is the load path, not the foam
> ring.** The ring is 293 mm² at **2.17 MPa against H-80's 1.4**, so it would
> crush in on its own; the bond up the side of the spigot is 890 mm² in shear
> at **2.8×**. Skimp the bond and the ring is all that is left.
>
> **The slit is clearance, not a seal** — a slot rather than three holes,
> because the leads arrive in a row and a slot prints without bridging. The
> leads pull up through it at step 18 and only the bung grips them.

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

**Position comes off the real mast, not off the drawing.** The 165 × 90 in
the CAD is unverified layout, and a perfectly machined plate on the wrong
pattern is still scrap. Clamp the mast to the blank and spot all four holes
with the **9 mm transfer punch** — it is a slip fit in Gong's own clearance
holes, so it marks true centre within a few hundredths. A 6.8 mm tap drill
rattling around inside that same 9 mm hole does not, and the whole positional
budget here is 0.25 mm. Then indicate off the four punch marks and machine to
them.

That splits the job the way it wants splitting: **the mast owns position, the
machine owns angle and depth**, and neither is asked to do the other's part.

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
drops inside the ring's inner edge and stands the **full height from cavity
floor to ledge** — board thickness less the lid, the ring and the floor. Take
the number off part 13 in [cut-list.md](../cnc/cut-list.md) rather than from
here; it moves whenever the lid stack or the ring does, and this paragraph
used to carry a hard 100.1 that was two geometries out of date.

That height is the point. The caul was once specified at the *module's*
height, which is a different measurement and several millimetres short. It
stopped below the ledge, so the wall-to-ledge corner — concave, exactly where
a bag bridges — got pressure from neither caul nor bag. That corner is where
the ring sits and where the seal ends up.

### Step 11a. Lay up the two lids

**Blocks on:** step 9
**Uses:** `Divinycell H-100 1/4in quarter 21x42, hatch lid cores - 2 sheets bonded to 1/2in` ·
`Divinycell H-80 1/4in quarter 24x48, module lid cores` ·
`E-glass 6 oz, 50in x 12ft, 2-pack` · `TotalBoat 5:1 gallon kit, slow hardener` ·
`Peel ply, 60in` · `Breather / bleeder cloth` ·
`1/4 in composite bit - lid profiles` · `1/8 in composite bit - lid bolt holes` ·
`Maker Shop day pass - post-layup lid session`

Both lids are flat sandwiches — glass / foam / glass — so they bag on the
bench and **do not need the board**. Do them alongside a hull session while
the pump is already set up and mixed resin is going spare.

The hatch lid core is **H-100**, and it is two ¼ in sheets bonded to ½ in
because no ½ in H-100 is made. That grade is deliberate: you stand on this
one. The module lid is H-80 — nobody stands on it.

**Both cores get their epoxy plugs first — hatch and module alike.** The
hatch lid's are written up in detail under
[step 13](#the-plugs-are-cast-into-the-bare-core-before-the-skins-go-on)
(the operation belongs here, at layup — that write-up sits later in the
document than the step that performs it) and the
module lid's are the same operation at a smaller size: **18 × Ø12 through the
bare H-80 sheet, tape one face, pour thickened epoxy, cure, sand both faces
flush**, then lay up over it. The module lid used to say *drill Ø12 through
the top skin and core only, leave the bottom skin* — that is a
**depth-controlled cut into a bagged laminate**, whose thickness is whatever
the bag gave you that day, and 0.5 mm too deep opens the face that seals the
module. Same trap the hatch lid was pulled out of; it just took longer to
find here.

**Both cores are cut OVERSIZE — 6 mm all round — not inset.** Parts 03 and 11
are bigger than the lids they go inside. The profile is machined through
glass / core / glass in one pass after cure, so there is no skin wrapping the
edge to preserve; [step 12](#step-12-seal-every-cut-edge)'s neat epoxy is
what protects the exposed core. Cutting the core inset *and* machining to
profile were mutually exclusive and the drawings asked for both.

#### Trimming them needs a machine, a bit, and a second visit

Trim to net profile after cure (parts 02 and 10 — their cores 03 and 11 are
inside the sandwich by now), and face the hatch lid's underside flat in the
same setup: it has to bottom evenly on the seal land.

**This is the one operation in the build that cuts cured glass**, and none of
the cutters bought for the core will do it. Foam bits are ground for foam;
glass does not blunt a bit so much as sand it round, and there are **6.6 m of
laminated edge** here across two boards. Two composite bits are on the list:

| | |
|---|---|
| Profiles | **¼ in Amana 46094** — 19 mm of cutting height on a 15.2 mm lid |
| All 29 holes a board | **⅛ in Amana 46091**, and *the ⅛ in shank is the spec* |

Ø5.0 and Ø5.6 are smaller than the profile bit, so they cannot be
circle-milled with it. A ⅛ in cutter on a ¼ in shank is no good either — the
shank stops on the hole at 12.7 mm and the hatch lid is 15.2 thick. A ⅛ in
shank is 3.175 and goes straight down a Ø5.0. **Check the shop has a ⅛ in
collet before the day** — it is a $15 part and a wasted trip.

**Budget a day pass for this.** The Basic month is spent on the cores, and
the lids do not exist until these layups are cured — which is weeks later, by
design ("let the layups follow the weather"). The foam cores go inside the
month; the cured sandwiches come back afterwards.

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
`2.5 mm straight cutter, opening the seal groove` ·
`M5 x 25 button head TORX TX25, 25 pk` · `Transfer screw set M3-M6` ·
`Solid silicone cord, 1/8 in (3.175 mm) - the spare size`

The ring went in at step 10a and has been glassed over since — **the whole
face, under 0.6 mm of laminate, bolt holes included.** Two different jobs
to open it again, and they are deliberately not the same job.

**The groove is ROUTED, off template 14.** The filler strip prints **flush**,
so the laminate over the seal land is flat — no step for the glass to bridge
at. Locate the template on the **rebate wall**: 34 mm of CNC ledge with a
vertical wall running the whole perimeter, true by construction and
continuous round the corners where a straight fence could not follow. A
**2.5 mm cutter in the 4 mm groove** leaves **0.75 mm** of lateral slop each
side before it can reach the land. Set the depth to just break into the
filler — you will feel it go soft — then pick the filler out and the
**printed walls are the finished groove**.

> **Why flush and not proud.** An earlier scheme printed the filler 0.5 mm
> proud so the glass draped over a ridge you could sand down to. Self-finding
> and no template — but it ran a 0.5 mm step **1.8 m along the sealing land**,
> and glass bridges at the two inside corners of a step. That seeds a pair of
> void-prone lines either side of the groove, in the one band of laminate the
> cord has to land on, and sanding back to the ring face lands about *at*
> those corners rather than safely past them.

**The twelve bolt holes are marked by DIMPLES, 0.5 mm deep — recessed, never
proud.** The glass bridges each dip and leaves a resin lens you can see and
feel; drill it out and you are into the ring's own bolt hole. Without some
mark, all twelve captive M5 nuts are buried with nothing to aim at, and
transfer screws do not help — a transfer screw has to be threaded *into* the
nut to mark anything.

> **Nothing on this face is ever proud, and here is what that rule is worth.**
> Raised pips were the obvious way to find the holes, and they fail twice.
> A 0.5 mm pip that survives to assembly holds the lid **0.5 mm off the ring
> face** — the cord stands only 0.6 proud of its groove, so squeeze goes from
> 20% to **3%**, under the 10% floor, and the seal is dead. And even sanded
> away, the glass that bridged around it leaves a **void at r = 3–5 mm** —
> inside the Ø18 washer, in the crush path, under the most loaded hardware on
> the board.
>
> The failure modes settle it. A dimple that does not show clearly costs you
> a hunt with the template. A pip that does not sand away costs you a seal,
> and you find out when there is water inside.

**Wet the opened groove with neat epoxy before the cord goes in.** Sanding or
routing leaves cut glass ends in the seal itself, which is the same wick that
flooded V1. Silicone adhesive does not stop a wick; epoxy does.

Bond the cord in on a thin continuous bead. Splice on a straight run, never a
corner.

**Measure the finished groove before choosing cord.** Nominal is 2.4 mm deep,
which the 3 mm cord squeezes 20%. If it routs deep the 3 mm only reaches 10%
and you want the 1/8 in spare instead — that is what it is for. Guessing the
cord before the groove exists is how you end up at 10%.

**The twelve heads sit proud, and there is nothing under them but a plug.**
The bolt ring is in the only bare band on the whole deck — the deck pad stops
20 mm outboard of the rim, the lid's own pad sits inboard — so it is the most
visible hardware on the board. It is also the most loaded.

**The load under the head is the PRELOAD, not what the seal needs.** The cord
only wants **182 N** a bolt. At the 1.2 Nm spec each bolt actually delivers
**1200 N**, and the surplus does not evaporate — it goes into the lid under
the head, on 32 mm².

The 1 mm skin does not pass that straight down; it carries it sideways into
the core for about **16 mm past the edge** of whatever presses on it — the
same beam-on-elastic-foundation model the heel check uses. Even crediting
that:

| Seat | Pressure | vs H100's 2.0 MPa |
|---|---|---|
| Bare M5 **button** head, Ø9.5 | 1.92 MPa | passes, 1.04× — the bolt actually specced, and it is *this* close |
| Bare M5 socket cap, Ø8.5 | 2.06 MPa | **fails, 0.97×** — a narrower head is worse, and a cap head is what an earlier draft had |
| Ø18 penny washer | 1.12 MPa | passes, 1.79× |
| **On the epoxy plug, Ø18 washer** | **6.8 MPa vs epoxy's ~50** | **7.4×, and the foam carries none** |

> **Why the lid needs a hardpoint at all.** It is glass / H100 foam / glass,
> and a bolt clamped straight onto that crushes the foam. So at every bolt the
> core is replaced by a plug of solid resin, and the lid reads glass / **solid
> epoxy** / glass instead of glass / foam / glass. Same trick every deck
> fitting on a boat or a surfboard uses. V1 never needed it: that lid was
> solid plywood all the way through.

#### The plugs are cast into the bare core, before the skins go on

That timing is the whole trick. The core is a flat sheet on the bench with
nothing laminated to it yet, so making twelve hardpoints is **pour, cure,
sand** — no pocket milled to depth in a finished panel, no bolt hole filled in
and re-drilled, and nothing to hunt for under a cured skin afterwards.

1. **CNC the core** oversize, with twelve Ø16 through-holes.
2. **Tape one face, fill them with thickened epoxy**, cure, and **sand both
   faces flush.** A plug left proud prints through a 1 mm skin under vacuum
   and you get twelve bumps in the deck.
3. **Lay up** glass / core / glass and bag it. The plugs are invisible now and
   it does not matter.
4. **Machine the profile and drill all twelve Ø5.6**, one setup — straight
   through skin / resin / skin.

Twelve holes bored in one setup are mutually accurate to the machine, so
lining the lid up on the ring is a single **rigid-body fit**: get two to pick
up and the rest already are.

**The core can drift 4.2 mm at layup** and the bolt still lands inside its
plug with resin all round it. That is what buys you the freedom to place the
core by hand.

**A Ø18 penny washer goes under each head, and it is not decoration.** A bare
M5 button head on resin is 37 MPa — 75% of ultimate — and epoxy cold-flows under
permanent preload. On the washer it is 6.8, or 14%. Same washer as the one
captive under the nut, so it is one size in the drawer and two per bolt.

**Button heads, proud, on washers — no countersink.** The head is domed and
2.75 tall against a cap head's square-edged 5.0, and the whole stack finishes
1.5 mm *below* the deck pad beside it. This is a band you walk on barefoot.

**Torx, and this is the only joint on the board that gets it.** The hatch is
the one thing opened *every ride*, in sand. A packed hex socket lets the key
bottom early and the head rounds — and a rounded head here means drilling a
bolt out of a lid you cannot easily replace. Torx tolerates a partly-seated
driver, which is exactly that failure.

The module lid (M4, inside the cavity, opened twice a year), the rail handles
(fitted once) and the drivetrain all stay hex — each would only add a driver
size for nothing. **Keep both Torx keys with the board: T30 is Gong's, for the
mast. T25 is the hatch.**

**If one hole still will not pick up**, that is what the transfer screws are
for: mark the real nut, open that hole, and leave the other eleven alone. The
plug is 5.2 mm bigger than the bolt all round, so there is room to move it.

**Seal the bores** with neat epoxy as [step 12](#step-12-seal-every-cut-edge)
did for the rest — the drill cuts both skins, and those are fresh fibre ends.

### Step 14. Build the module

**Blocks on:** step 3
**Uses:** `5052 1/8in x 12 x 24, 2-pack - module floors` ·
`Sikaflex-292 marine structural PU` · `Sika Aktivator-PRO 250 ml + daubers` ·
`2 mm glass beads or shim wire, bond-line control` ·
`M4 x 12.7 LONG brass heat-set insert, 50 pc` · `M6 x 12.7 brass heat-set insert, 50 pc` ·
`Closed-cell sponge EPDM 1/8in, module lid gasket` · `Hollow punch set 1/8-1/2in + cutting mat` ·
`Gebildet PG11 gland, M18x1.5, 30 pk` · `GORE PolyVent Stainless M12x1.5, module vent` ·
`M12 IP68 momentary panel button` · `JST GH 1.25 mm pigtail pair, BMS switch` · `SP17 2-pin IP68 flange socket + mating plug` ·
`M3 heat-set insert kit, 361 pc` · `M3 x 8 A4 stainless, 10 pk`

> **The 18 lid inserts, and the torque that goes with them.** Derek pulled a
> heat-set out of V1 while fixing it, so this is a measured failure, not a
> margin exercise — and the fix is two things, of which the insert is the
> smaller.
>
> **Longer, not fatter.** Pull-out goes as π × D × L, but *diameter also has
> to fit the flange land* and length doesn't — it just goes down into rail
> that was doing nothing:
>
> | Insert | Pull-out | |
> |---|---|---|
> | M4 × 8 (V1's) | 800 N | |
> | M5 × 9.5 | 1086 N | starts crowding the land |
> | M6 × 12.7 | 1860 N | **fails two land checks** — 2.4 mm of ASA left outboard, gasket band running into the bore |
> | **M4 × 12.7** | **1270 N** | same bolt, same Ø5.6 pilot, same gasket punch, same board thickness |
>
> The flange rail goes 9.5 → 14.5 mm deep to swallow it, with 1.8 mm of
> backing under. That costs nothing: the rail hangs on the *outside* of the
> wall, so it grows down into a gap that was already there.
>
> **And the torque matters more than the insert does.** This lid has never had
> a spec, and an M4 is unforgiving about it:
>
> | | Preload | On the insert |
> |---|---|---|
> | 0.5 Nm | 625 N | **2.0×** |
> | 1.0 Nm | 1250 N | 1.0× — at its limit |
> | 2.0 Nm | 2500 N | 0.5× — **this is how you pull one out** |
>
> 2 Nm is barely a wrist on an M4. **Spec is 0.5 Nm**, which is below any
> torque wrench, so it is a feel spec: shortest key you own, two fingers, stop
> as soon as it stops turning easily. That is still **4.1× what the seal
> actually needs** — the squeeze is geometric, the lid lands on the flange,
> and there is nothing to gain past that point and an insert to lose.


Acetone-weld the four printed L-pieces into a shell. Bond it to the 5052
floor on a **2 mm controlled bond line** — glass beads set the gap, fillet
both sides. It must be flexible PU, not epoxy: ASA and aluminium differ by
66 µm/m·K, which is 0.60 mm of movement from the centre over 40 °C. A rigid
line sees 299% shear strain and tears itself apart.

Heat-set the lid inserts into the printed flange. The M3 kit's screws are
plain steel — use the A4 ones for the port flange, which lives in the wet.

**Four M5 inserts go in at the same time**, two into each lift-handle pad on
the aft wall, 18 mm apart. Do them while the shell is on the bench and open —
they are 8 mm-proud pads on the outside of a box you are about to seal, and
the soldering iron wants room.

### Step 15. Leak-test the module empty

**Blocks on:** step 14
**Uses:** `Test cap + tubing, module leak test` ·
`Bag connector w/ ball valve, 1/4 in QD` · `Gebildet PG11 gland, M18x1.5, 30 pk`

**The module has no test port — and does not need one. A gland is a test
port.** At this stage no cables are fitted and all three PG11 glands are
empty. A gland is a compression seal on a round thing, so feed one of the
test kit's smaller hoses through it and tighten. Blank the other two glands
and the vent boss. No extra hole, no special fitting.

*(The first plan here was an M12 × 0.75 barb into the vent boss. That is a
fine pitch nobody stocks — and it was the wrong problem: the sealing hardware
you already have does the job.)*

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
loads that way. It is also unsafe: 0.2 bar across a 443 × 314 lid is about
**2.8 kN**.

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
`ANL 150 A fuse + holder` · `Inline 10 A fuse + holder, charge lead` ·
`8 AWG marine ring lugs, 20 pk` ·
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

### Step 18. Run the mast conduit and fit the wire bung

**Blocks on:** steps 7, 17
**Uses:** `Fish tape / pull cord for the mast conduit` ·
`IP68 M25 inline housing, 5 pk` · `Neoprene sheet 1/2in, wire bung` ·
`Hollow punch set 3/16-1-3/8in, for the O30 bung` ·
`3M 4200 FC 3 oz tube, skim over the bung`

Motor leads part **in the cavity**, one housing per phase — without that the
mast is bolted on for life.

> **The conduit is two straight bores, and you drill the second one.** One
> goes **straight up** from the mast plate, 32 mm of it. The other is drilled
> **down from inside the cavity at 48°**, 43 mm of it, and they meet in the
> foam at z=30 — **3.8 mm above the blocker's spigot**, so it does not break
> into it.
>
> An earlier version of this drawing had a swept curve through the foam. That
> was not a buildable part: this channel is cut **by hand at step 18**, into a
> board that has been assembled since step 7, and no drill makes a radius
> through a bonded-in block from either end.
>
> **The lead does not need a bend radius — it cuts the corner.** The bores are
> Ø22 and the lead is 6.5, so it can arc through the junction at an effective
> **116 mm radius, 4.5× what 8 AWG wants**. Ease the corner with a round file
> anyway before you pull.

**The bung's first job is not sealing, it is spacing.** The three phase leads
come out of the mast *touching*, in a line along the chord — an alu mast's
internal cavity is only about 12–14 mm across, so 6.5 mm leads cannot lie any
other way in there. Three touching jackets are three capillary paths: sealant
bridges the gaps between them instead of going round each lead. The bung
holds them **in that same line** with 1.5 mm of rubber between every pair,
and *that* is what makes the seal possible.

A triangle would pack smaller, and the bore was originally shrunk around one.
But it asks all three leads to twist through 90° in the few millimetres
between the mast top and the bung, by hand, upside down, in 8 AWG silicone.
Matching how they arrive is worth more than the packing.

**What the row used to cost, and no longer does:** a row is wider than the
round bore it feeds, so the outer lead has always had to converge slightly on
its way up. At a 2.0 mm wire gap it left the bung 11.75 mm off the axis
against a bore that allows **11.0 mm** and had to bend into a 24 mm effective
radius — under the 26 mm this cable wants. At 1.5 it was 11.25 and a 72 mm
radius, 2.8×, fine.

At the **7.5 mm pitch** the gap is 1.0 and the outer lead leaves the bung
**10.75 mm** off the axis — *inside* the bore before it gets there. **It does
not converge at all.** The failure mode is not smaller, it is gone, and that
is what the half millimetre bought.

**Where the compression comes from.** There are **two aluminium plates** at
this joint. The board's hardpoint is bonded into the hull bottom at step 7 and
never moves again. **The Gong mast has its own plate**, with four *clearance*
holes, and its bolts pass up through them into the tapped hardpoint — so that
plate is the part that travels, and tightening draws it face to face with the
bottom of the board. Anything standing proud of that face gets squeezed, with
four M6s behind it. That is the only travel in the whole mast joint.

1. Punch Ø30.0 discs from the 3/4 in sheet and drill 3 × **Ø5.5 in a row at
   7.5 pitch**, along the chord — the order the leads leave the mast in, so
   not one of them has to be twisted. The holes are drilled **undersize on
   purpose**: 5.5 into a 6.5 lead is the 15.4% interference that *is* the
   seal.
2. Thread the leads through on the bench and soap them.
3. Feed the bung up the plate's straight **Ø30.8 bore**. It butts the epoxy
   liner's end face where the foam channel steps down, and hangs **4.0 mm
   proud** of the wetted face.
4. Bolt the mast on. Its plate squeezes that 4.0 mm out, and the rubber —
   with nowhere useful to go — closes onto the jackets and the bore wall.
   **Start all four bolts by hand before torquing any of them**, or the plate
   rocks on the bung. 159 N a bolt to close it.

| | |
|---|---|
| Disc | **Ø30.0 × 12.7**, punched from 1/2 in neoprene |
| Holes | 3 × **Ø5.5** in a row at 7.5 pitch — **15.4%** under the lead |
| Bore | the plate's own **Ø30.8**, one straight pass, no step |
| Rubber wall | **4.25 mm at the ends of the row**, 11.75 at the sides |
| Backed above | **95%**, by the blocker |
| Proud | **4.0 mm** below the wetted face |
| Grip on the leads | **8.7 mm** at 15.4% interference |

> **Why it is round and not a rectangle.** A row of holes inside a circle is
> fat where it needn't be and thin exactly where the outer two leads sit — at
> Ø26 that was 9.75 mm of rubber at the sides and **1.75 at the ends**. A
> rectangular bore would even that out. It would also be **milled instead of
> drilled and reamed**, and that bore's *finish is the seal*, with corners for
> leak paths. Growing the circle to Ø30 fixes the same problem for 4 mm of
> hole in a plate with 63 mm of clearance to its nearest bolt.

> **What seals here, in order.** Three mechanical barriers in series, and no
> sealant is load-bearing:
>
> 1. **The Ø5.5 holes at 15.4% on the leads.** A grommet seal — it does not
>    need the squeeze at all, which is why they are drilled that tight.
> 2. **The bung's OD closing onto the plate's bore**, driven by the squeeze
>    the blocker now makes possible: **95% backed** instead of 30%.
> 3. **The blocker bedded on 4200** into the foam counterbore, which seals the
>    annulus round it — an adhesive use, not a wire seal.
>
> Nothing in the *channel* is a sealant barrier. That was the
> point of the blocker: an earlier version had the bung butting an epoxy liner
> step that **has no geometry** — the dense block is bored clean through — and
> had it existed it would have been a 365 mm² ring carrying 1.72 MPa into H-80
> that gives up at 1.4. The stop was imaginary and undersized at once.

> **The bung has to be wider than the mast's wire slot**, or the plate has
> nothing to push on. Derek's slot is **20.4 × 7**, cut just wide enough for
> the three leads, and it sits wholly under the bung — so it costs only its
> own 143 mm² and the plate keeps **89% of the bung's face**. No follower, no
> flange, no spotface.
>
> **Open the slot to 22.5 mm** while you are at it. The leads reach the bung's
> holes at 7.5 pitch, which puts the outer two 10.75 mm off the axis against a
> slot that reaches 10.2 — they would bear on its ends. Not a leak path, but a
> chafe point on something that vibrates. It costs 2 points of land.

It also holds itself in at about **253 N** of friction against the **37 N** a 5 m
water column pushes up under it — 6.8×. It comes out the way it went in: cut the fillet,
pull the leads and the bung down together.

Fillet 4200 over the underside. **4200 not 5200** — 5200 never comes out.

> **Why the pocket is 2.25 mm bigger than the disc.** Rubber does not
> compress, it *moves*. A bung squeezed in a bore it exactly fills cannot be
> squeezed at all — it becomes a solid spacer and the four M6s fight it for
> nothing. The clearance annulus is the only place the displaced rubber can
> go, so it is relief, not slop, and it is sized to swallow the 1 mm squeeze
> *plus* a hand-punched disc coming out a millimetre over.

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
**Uses:** `Kayak/board grab handle, 2 pk + screws` · `M6 x 16 A4 button head, 10 pk` ·
`M6 x 16 A4 button head, 10 pk` ·
`Leash plug 30 x 12.5, stainless pin, 2 pk` · `Coiled ankle leash` ·
`M4 x 12 A4 socket cap DIN912, 10 pk` · `M4 A4 washer, 316, 100 pk`

**Three handles a board, all the same part:** two on the rails into the 6061
strip, one on the electronics module. Drill the handle's reinforcing holes to
suit rather than using the supplied screws anywhere: **M6** into the tapped
6061 on the rails, **M5** into the module's heat-set pads. The supplied screws
are self-tappers, and a self-tapper in a brass insert is a stripped insert.

**Measure the handle's tabs before you drill the module one.** The rail pair
is on 152.6 mm centres and has room either side; the module's pads are on 70 mm
and cannot move — outboard of them is 5 mm of clearance to the gland nuts. If
the bought handle's tabs are much wider than 70 mm, put a webbing loop through
the same two pads on the module and keep the bought handles for the rails.

> **Still open: what holds the module down in the cavity?** Its 18 bolts hold
> its own lid on, not the module into the board. A 14 kg module loose in a
> cavity is the heaviest thing aboard with nothing restraining it. **Decide
> before the cavity is glassed** — anything bonded in has to go in before the
> laminate does.

### Step 23. Mount the foil and drivetrain

**Blocks on:** steps 7, 22
**Uses:** `M6 x 22 A4 countersunk DIN7991, mast screws` · `Ultra Tef-Gel, galvanic barrier` ·
`M5 x 250 threaded rod, 4 pk (cut to ~171 mm)` · `M6 x 20 fender washer, 100 pk` ·
`M5 nyloc nut 316, 150 pk` · `Loctite 242` · `Roll pin assortment M1.5-M6, 220 pc` ·
`M8 nyloc nut 316, 30 pk - prop nut` · `M8 316 washer, prop nut` ·
`1/4 in torque wrench, 10-50 in-lb`

**Tef-Gel every mast bolt, every time.** Aluminium plate, A4 bolts, wet
cavity — that is the whole galvanic mitigation and it is not optional.

> **The mast screws are M6, and Gong supplies them.** The setup ships with
> *7 × M6×30 mast screws, 4 M6 brass square nuts, 4 M6 cup washers and a T30
> Torx key.* The square nuts are for a US-rail board and you will not use
> them; the cup washers and the screws you will. **T30 Torx, not hex** — the
> spares line is hex-drive A4, so keep Gong's key with the board.
>
> This model said M8 until it was checked against Gong's own contents list.
> The correction costs real margin — **the joint is 1.44× on the roll case,
> not 2.63×** — but not margin anyone here can buy back, and that is the
> point. M6 A4-70 proofs at 9.0 kN against the 6.3 kN that case demands.
>
> **The screw is the weak link, and it is Gong's.** Our side of the joint is
> 10 mm of tapped 6061 in a 12.7 plate at **13.2 kN — 46% stronger than the
> screw going through it.** Their own system reacts that same screw into a
> brass square nut floating in a US box, which is weaker than this. So V2's
> mast joint is stronger than the boards Gong designed the fitting for, and
> tapping deeper or fatter buys nothing.
>
> The 1.44× is also against **proof** load — the point permanent set begins —
> not ultimate. Against actual failure it is around 2.0×.

**No gasket goes under the mast base**, and there is none in the BOM.

**V1 had one, and it was doing a job V2 does somewhere else.** On V1 that
gasket was the waterproofing for the mast penetration. V2 seals the hole the
wires actually run up instead — the Ø26 conduit gets a punched EPDM bung and
a 4200 fillet in
[step 18](#step-18-run-the-mast-conduit-and-fit-the-wire-bung) — so the
barrier sits at the bore, not under the plate. Sealing both would be sealing
it twice.

Which leaves nothing for a gasket here to do: the mast bolt holes are
**blind**, so there is no path into the board through them, and the faying
faces are aluminium on aluminium — the galvanic couple is the A4 bolts.
Smear Tef-Gel across the mating faces as well as the threads and pull the
plate down metal to metal.

And a gasket would cost something real. This is the highest-loaded joint on
the board — an 850 mm lever with rider weight and foil lift at the end.
Rubber under 4 × M6 creeps, the bolts lose preload, and the plate starts to
rock. Compressible is the wrong property here in either material.

**Measure** the prop shaft cross-hole rather than trusting the 4 mm figure;
that is why the roll pin line is an assortment.

The torque wrench is a **calibration tool**: set the drill clutch with it,
then use the clutch. Hatch spec is 1.2 Nm — 10.6 in-lb, which is *below* the
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
| Shop will not run fibreglass on the CNC | Ask on the same call as the EPS one. Fallback: jigsaw the lid profiles to a line, and transfer-drill the holes off the ring |
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

Grounded in what V1 actually ran, which is written up in
[efoil-2-electrical.md](v1/efoil-2-electrical.md). Three things in an earlier
draft of this appendix were wrong and are corrected below: the fuse is on the
**negative**, the positive **never touches the BMS**, and the charge port is
**already dead when the BMS is off** — no BMS change needed.

## The rule everything follows from

**A common-port BMS switches the NEGATIVE rail only. Pack positive is a
straight pass-through that never enters the BMS.**

**Confirmed against DALY's own wiring diagram** for this unit, which settles
three things that were open:

| Question | Answer from the diagram |
|---|---|
| Is there a B+ terminal? | **No.** The board has exactly two power terminals, **B−** and **P−**. Pack positive never lands on the BMS at all |
| Common or separate port? | **Common.** The load and the recharger both hang off the same **P+ / P−** pair |
| How is pack positive sensed? | Through the **sampling cable** — the same harness that taps each series junction |

So V1's JK and this DALY behave identically. Anything below that says "if
fitted" about a B+ terminal is now settled: there is none.

## The current path

V1's, with one change: V1 ran the charger and the ESC through the *same*
XT150 pair. V2 has a dedicated SP17 charge port, so each leg now branches.

```
   PACK +  ─── 8 AWG ───────► P+ ──┬── 8 AWG ──► ESC  V+
   (straight through,              │
    never enters the BMS)          └── 16 AWG ─► 10 A fuse ──► CHARGE  +

   PACK −  ─── 8 AWG ───────► B−  ─┐
                                    │  MOSFETs  (this is the switch)
                              P−  ◄─┘
                               │
                               ├── 8 AWG ──► ANL 150 A ──► ESC  V−
                               │
                               └── 16 AWG ─────────────────► CHARGE  −

   SAMPLING CABLE: taps every series junction AND the overall positive.
                   This is how the BMS sees pack + - there is no B+ wire.
   BUTTON:         2-wire to the BMS switch input - NOT in the main path
```

## Where the splits go — your question, answered

**You already own the splitter. It is P+ and P−.**

DALY's diagram draws both as terminal blocks with the load *and* the
recharger landing on them — that is the design intent, not an improvisation.
Everything meets there:

- **P+** — pack positive in, ESC positive out, charge positive out
- **P−** — from the MOSFETs, ESC negative out, charge negative out

**Fuse each leg for what it carries, rather than sharing one.** V1 shared a
single XT150 so both went through the 150 A ANL; with a dedicated charge port
there is no reason to, and a 150 A fuse never protected a 16 AWG lead anyway:

- **ANL 150 A** in the ESC negative, between **P−** and ESC V−
- **Inline 10 A** in the charge positive, off **P+**

### How to physically make the split

| | |
|---|---|
| **Stacked ring lugs on P+ / P−** *(recommended)* | 8 AWG under 16 AWG, star washer between. This is what the terminals are for — no new part, no new bay space |
| **2-post busbar** | Only if you want separately torqued, labelled landings. The bay is 75 mm deep, so it costs room you do not have much of |
| ~~Dual-barrel lug~~ | **No.** One barrel crimped onto 8 AWG *and* 16 AWG compresses neither properly. That is the joint that fails a year later |

## Joint by joint

| # | From | To | Wire | Termination |
|---|---|---|---|---|
| 1 | Pack + collector | **P+** | 8 AWG | ring lug, hydraulic crimp |
| 2 | **P+** | ESC V+ | 8 AWG | ring lug |
| 3 | **P+** | 10 A fuse → charge port + | 16 AWG | ring lug — stacks on joint 1/2 |
| 4 | Pack − collector | **B−** | 8 AWG | ring lug |
| 5 | **P−** | ANL fuse IN | 8 AWG | ring lug |
| 6 | ANL fuse OUT | ESC V− | 8 AWG | ring lug |
| 7 | **P−** | Charge port − | 16 AWG | ring lug — stacks on joint 5 |
| 8 | Sampling cable | 17 series taps + overall + | 22 AWG harness | as supplied — **this replaces any B+ wire** |
| 9 | BMS key-switch input | Panel button | 2 × 22 AWG | **JST GH 1.25 mm** at the BMS end |
| 10 | ESC phases | Motor, in the cavity | motor's own | 5.5 mm bullets + IP68 housing |

**On joint 8:** there is **no B+ power lead** on this BMS, and none is
missing. Pack positive reaches the board only through the sampling cable,
exactly as V1's JK did through balance wire #15. If you find yourself looking
for somewhere to land a pack-positive wire on the BMS, you are looking for a
terminal that does not exist — it goes to P+.

Every 8 AWG lug: **hydraulic crimp, then adhesive-lined heat shrink** over
the barrel and onto the insulation. Not soldered — solder wicks up the
strands and the stiff point it creates is where vibration breaks the wire.

## The charge port IS dead when the BMS is off

Correcting this appendix again, in your favour. Charge − returns through
`BMS P− → MOSFETs → B− → pack −`. **With the BMS off, those MOSFETs are open
and there is no return path**, so nothing can flow between the port's two
pins no matter what bridges them. You do not need a separate-port BMS, and
you do not need a switch in the charge leg.

What remains true, and worth knowing rather than worrying about:

- The **+ pin sits at pack potential** whenever cells are connected, because
  nothing switches the positive on any common-port design.
- **With the BMS ON**, bridging the two port pins *is* a short across the
  pack through the discharge FETs — same as shorting the ESC leads. Do not
  probe a live port with the BMS on.
- The port is inside the module, inside the cavity, under twelve M5s. It is
  not a bystander hazard; it is a you-with-a-multimeter hazard.

## Two mistakes that kill a BMS

1. **Never connect the balance harness before the main leads.** Main first
   (B−, then B+ if fitted), balance last. Disconnect in reverse: **balance
   off first.** With balance plugged in and B− floating, pack current returns
   through 22 AWG balance wires and takes the BMS with it.
2. **Meter the balance harness before plugging it in.** B0 is pack
   most-negative, B16 most-positive. Against B0 you should read a clean
   ladder, ~3.6 V per step. One transposed pair is a dead BMS and possibly a
   dead group.

## There is only one switch, and it is the BMS

**Nothing is plugged or unplugged in normal use.** The ESC and the charge
port are both permanently wired to P+ / P−, and the BMS's MOSFETs gate the
negative for both at once. Turn the BMS off and load *and* charge die
together — there is no separate load switch and no need for one.

The panel button is **not** in the power path. It lands on the BMS's
low-current **switch terminal** — JK calls it that, and it is what V1 used —
and all it does is tell the board to turn its FETs on or off. It carries
milliamps. The 92 A goes through the MOSFETs, which is what they are for.

> ### ✔ The DALY does have a key switch input — confirmed
>
> The Amazon listing never mentions one, which is why this was open. **DALY's
> own documentation does:** *"The default function of the key switch is to
> activate the BMS; other logic functions can be customized."* So the button
> has somewhere to land, and the design stands.
>
> Three things that follow, worth knowing before you wire it:
>
> - **It is a JST GH 1.25 mm connector, not a screw terminal.** DALY sell a
>   ready-made key switch for about $5 that plugs into it. Our M12 panel
>   button is bare wires, so it needs a **JST GH 1.25 mm pigtail** to marry
>   the two — a part worth having before the module closes, because
>   crimping GH 1.25 by hand is unpleasant and it is a $6 problem now versus
>   opening a sealed module later.
> - **The behaviour is configurable in the app.** Default is "activate the
>   BMS". Another option is *control discharge MOS and sleep* — contacts
>   open, the BMS opens the discharge MOSFET and sleeps. Pick that one and
>   the button behaves like a power switch rather than a wake button.
> - **Bluetooth is the fallback, not the plan.** The app can switch the
>   charge and discharge MOSFETs directly, so a failed button never strands
>   you — but starting the board should not require getting a phone out with
>   wet hands, which is exactly why the physical button is in the design.
>
> *(Connector type and the $5 key switch are community-sourced; DALY's own
> page confirms the switch input but not the connector. Check what is in the
> box before ordering a pigtail.)*

> A note on the term: "switch input" means *the input on the BMS that a
> switch connects to*, not switching the input side of anything. Nothing on
> the pack side is ever switched.

**So there is no precharge problem in service — and this BMS confirms it in
writing.** Its listing names a **"Pre-charging function"** among the upgrades,
so the surge of the FETs closing into the ESC's input capacitors is
soft-started by the board itself. That closes the one question the BOM had
left open on this ("worth checking once: some smart DALYs carry precharge").
It does.

The classic arc comes from mating a connector across a live pack into
discharged capacitors, and here that connector does not exist at all.

The one moment it *is* a real connection is **assembly** — landing the B−
lead for the first time with the ESC already wired will charge the caps
through that joint. Connect **B− last**, and if you want it gentle, bridge it
through a resistor for a second first. One-time, at the bench, with the lid
off.

## Sanity checks before the lid goes on

- Pack voltage at the collectors: ~57.6 V nominal, 67.2 V full.
- Charge port polarity, metered, with the pack live and the BMS on.
- ANL 150 A is in the **negative** leg, between P− and the ESC.
- Inline 10 A is in the **charge positive**, off P+.
- Button goes to the BMS **switch terminal** — two thin wires, nothing else.
- Tug every crimp. One that moves is one that failed.
- Dielectric grease on every terminal, then leak-test again with the vent
  blanked before the cells go in for good.
