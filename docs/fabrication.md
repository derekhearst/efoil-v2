# Fabrication plan — how this board actually gets made

Written for someone who has **never run a CNC**. The honest summary first, then
the sequence, then the parts of it that will bite.

---

## The honest assessment

Machining a board core is not a beginner CNC job. But it splits into two very
different halves, and only one of them is hard:

| | Difficulty |
|---|---|
| **Running the machine** | Low. Maker Shop includes free tool training, and foam cuts with almost no force — you cannot break a cutter or crash hard enough to hurt the machine. |
| **CAM — generating the toolpaths** | This is the real work. Two-sided 3D surfacing with flip registration is an intermediate job, and it is done at a computer before you ever touch the machine. |

You are not learning to *cut*. You are learning to *program a cut*. Budget your
effort accordingly.

**Everything internal to this board is 2D.** The cavity, the rebate, the mast
pocket, the handle pockets, the leash pad — all of them are prismatic shapes
that a router and a template can make. Only the **outside of the hull** genuinely
needs 3D machining. If the CNC falls through entirely, the board is still
buildable; it just gets hand-shaped like V1 was.

---

## The finding that changes the whole sequence

**Do not machine the cavity into a glued-up blank.**

| Feature | Reach below the deck |
|---|---|
| Rim rebate / ledge | 27.0 mm |
| Handle pocket floor | 29.3 mm |
| Leash pad floor | 19.8 mm |
| **Cavity floor** | **117.3 mm** |

A 1/2 in endmill has 25–76 mm of flute. **Nothing you can buy off a shelf
reaches 117 mm**, and a tool that long in foam would deflect and chatter anyway.

The core is three glued layers of 2 in (50.8 mm) EPS. Cut the cavity **before**
glue-up and the problem evaporates:

| Layer | z | What it needs |
|---|---|---|
| 1 (bottom) | 0 – 50.8 | cavity floor pocket, **20.8 mm deep** |
| 2 (middle) | 50.8 – 101.6 | cavity outline, **through-cut** |
| 3 (top) | 101.6 – 152.4 | cavity outline through-cut; rebate 32.1 mm; handles 34.4 mm; leash 25.0 mm |

Nothing deeper than **34.4 mm**. All of it reachable with a standard 1/2 in
cutter.

The deck sits at z = 147.3 and layer 3 tops out at 152.4, so there is only
**5.1 mm of stock to surface off the deck** — the layer stack was already
almost the right thickness.

---

## The good news: no undercuts

Checked at 21 stations. The rail's widest point is the parting line — above it
the surface is reachable from straight above, below it from straight below, and
the half-width is **monotonic in both directions at every station**.

That means the hull is a clean **two-sided 3-axis part**. No 4th axis, no
tilted fixtures, no unreachable geometry. The parting line is not at a constant
height (11.5 mm at the tail, 23.6 mm mid-board, 137.5 mm at the nose) but that
does not matter — it only matters that nothing overhangs.

---

## Envelope

Axiom AR8 Pro V5: **1219 × 610 mm, 165 mm gantry clearance.**

| | Needs | |
|---|---|---|
| Longer core half (seam at x=1030) | 1030 × 560 | fits, 189 mm spare in X |
| Shorter core half | 370 × 560 | fits |
| Rebate footprint | 591 × 386 | fits easily |
| Whole board in one piece | 1400 × 560 | **no** — hence the seam |

`SEAM_X = 1030` exists precisely so both halves clear a 1219 mm bed. **Y is the
tight axis**: 560 mm in a 610 mm bed leaves 25 mm each side, which is fine for
tape-down but leaves no room for clamps beside the part.

---

## Sequence

### Before the machine

1. Cut three EPS layers per board, oversize to ~1420 × 580.
2. **Cavity through-cut in layers 2 and 3.** A 2D profile through 50.8 mm.
   Jigsaw and a template is fine; the glass and the rim ring set the finished
   dimension, not this cut.
3. **Layer 1: cavity floor pocket and the mast/dense-block pocket.** 2D
   pockets, router and template.
4. **Glue up** with alignment pins so the layers cannot creep.
5. **Split the blank at x = 1030.**

### On the machine, per half

6. **Op A — bottom.** Fixture deck-down on a sacrificial sheet. Surface the
   hull bottom, finish the mast pocket.
7. **Flip. Op B — top.** Surface the deck, cut the rebate, both handle
   pockets, the leash pad.

### After

8. Glue the halves, fair the seam.
9. Bond in the **printed ASA rim ring** (six dovetailed segments, acetone-welded), the **6061 mast plate**, and the handle/leash hardpoints.
10. Glass.
11. Rout both seal grooves off templates 14 and 15 — **after** glassing.

---

## Templates for everything

Nothing on this board should be hand-traced or laid out with a tape.
`python model/templates.py` emits **14 templates** to `cnc/templates/`, all
derived from the same parametric model as the board, so they cannot disagree
with it.

| | |
|---|---|
| `T01_planform_half` | board outline, flipped on the centreline |
| `T02_cavity_opening` | the through-cut in layers 2 and 3, and the layer-1 floor pocket |
| `T03_rim_rebate` | the ledge the rim ring beds into |
| `T04_mast_block_pocket` | dense-foam block in the underside |
| `T05_mast_plate_pocket` | plate pocket. **No longer a bushing drill guide** — the 6061 plate is tapped M8 direct, so there are no bushings to bore |
| `T06_handle_pocket` | one template, used both sides |
| `T07_leash_pad` | pad pocket + the FCS bore |
| `T08_station_*` (×6) | section gauges to check the machined shape |
| `T09_rocker_and_deck` | centreline profile, bottom and deck |

All the router templates are **BEARING** type — cut at finished size, used with
a flush-trim bit whose bearing rides the template edge. That deliberately
sidesteps the guide-bushing offset, which is the one number in the whole set
that depends on your tooling rather than on the design. Only the two seal-groove
templates need it.

Every template carries the centreline and station ticks on a `REG` layer, so it
can only sit one way on the blank. `CHANNEL` lines are reference, never cuts.

**These are also the fallback.** If the CNC falls through, T01 plus the six
station gauges and the rocker profile are exactly how V1 was shaped by hand.

## Workholding

Foam cannot be clamped — it crushes, and there is no room beside the part
anyway. Standard practice:

- **Sacrificial sheet** of MDF screwed to the machine bed.
- **Spray adhesive or double-sided carpet tape** to stick the blank down.
- Leave the blank **oversize** so the tape sits outside the finished profile.
- Cut a **perimeter tab** the part stays attached by, and cut it free by hand.

Ask the shop before doing this — it puts adhesive on their spoilboard.

---

## Two-sided registration — the part that goes wrong

When you flip the part for Op B, the machine has no idea it moved. Get this
wrong and the deck is offset from the bottom, and the mast pocket ends up in
the wrong place relative to the deck.

The standard fix is **dowel pins**: drill two holes through the blank *and*
into the spoilboard during Op A, at known coordinates well outside the finished
profile. Drop dowels in. Flip about the axis through both dowels. The part can
only go back one way.

Mirror the X or Y axis in CAM for the flipped op — **which one depends on which
way you flip**, and getting it backwards machines a mirror-image board. Dry-run
in the air first.

---

## Tooling

Foam wants the opposite of metal: large chip clearance, high feed, and a sharp
single flute so it cuts rather than melts.

| Op | Tool |
|---|---|
| Roughing | 1/2 in single-flute upcut, or a foam-specific rougher |
| 3D finishing | 1/2 in ball nose |
| Pockets, rebate | 1/4 or 1/2 in single-flute |
| Cavity through-cut | anything with ≥ 51 mm of flute |

**Do not use a downcut bit** — it packs melted foam into the cut.

Ask the shop what they have. Do not assume; a 1/2 in ball nose long enough for
the deck surfacing is not a given.

---

## Vacuum bagging — the actual session

### The number that shapes everything: 20 minutes

TotalBoat 5:1 with **slow** hardener has a **20-minute pot life at 75 °F**. That
is not much time to wet out 2.51 m² of laminate, and it is the single thing
most likely to go wrong.

Three things buy you time, and you want all of them:

| | |
|---|---|
| **Work cool** | 62–68 °F. Slow hardener's minimum is 60 °F. Cooler is longer, right down to the limit |
| **Mix small** | 300–400 g batches. Pot life is measured **in the pot**, where the exotherm feeds itself — spread thin on the cloth it lasts much longer |
| **Get a second pair of hands** | one person wets out, one person keeps mixing |

Pot life is not working time. A batch that is going off in the cup is still
fine on the cloth. What kills you is mixing a big pot and then finding it
warm.

### Building through a Boise winter

This build runs autumn into spring, and that changes the hardener from a
decision to a **daily thermometer reading**:

| | Minimum temp | Notes |
|---|---|---|
| **Slow** hardener | **60 °F** | 20-min pot life at 75 °F |
| **Fast** hardener | **40 °F** (45 to be safe) | shorter at the same temp — but in a 50 °F shop the cold hands the working time back |

**Below about 35–40 °F epoxy cannot generate enough heat to cure at all.** It
does not go slowly — it stays soft permanently. **A cold laminate is not a slow
laminate, it is a ruined one.** Buy both hardeners and pick on the morning.

### The hot box

On this schedule it is not optional. A poly-sheet tent over the bagged part
with a thermostatic heater holds 70 °F while the garage sits at 45, and it
fixes three separate problems:

1. **The epoxy cures, and cures fully**
2. **Sealant tape tacks.** Cold tape does not stick — that is a bag that leaks
   at hour three, discovered too late
3. **Amine blush**, which is much worse cold and damp, gets far milder

EPS is happy to ~75 °C, so a 20 °C box is nothing to it. Leave the pump
*outside* the tent.

**Wash the blush off with water and a scotchbrite before any secondary bond.**
Winter epoxy blushes more, and blush is the classic reason a second layer
delaminates.

### "Both bottom layers at once" — yes, and always

All plies of one skin go on **wet-on-wet in a single bag cycle**: 2 × 6 oz plus
the 1708 biax, laid straight onto each other while wet, bagged once. Never cure
between plies of the same skin — you would be creating a secondary bond, with
blush, where the design assumes a monolithic laminate.

What you should **not** do is both *boards* in one session. That is 5 m² of
wet-out inside a 20-minute pot life, and the second hull would be curing before
you bagged it.

**One skin, one board, one session.** Six sessions total.

### Dry-run the bag before you mix anything

**This is the step people skip and it is the one that saves a hull.**

Put the part in the bag with the breather, seal it, pull it down, set the
regulator, and **watch the gauge for ten minutes**. Find the leaks now — with
the pump off, a good bag should lose only a couple of inHg over several
minutes. Chase leaks with a wetted finger along the tape line, listening.

You will not find leaks with epoxy going off.

### Target: 5–10 inHg, and never more

The core is **EPS, and it crushes at 130–200 kPa. Full vacuum is 101.** So
"as much as it will pull" would collapse the blank.

Set the regulator to **7 inHg** and confirm it on the gauge **at the bag**, not
at the pump. This is the whole reason there is a gauge on the list.

### Sequence

**Cut everything first.** Glass plies, peel ply, breather, film, tape — all to
size, laid out in the order they go on, before any resin is mixed.

1. Dry-run the bag (above). Un-bag.
2. Mix batch one. Wet out the core, lay glass, wet through. Work in batches.
3. **Peel ply** over the whole laminate, smoothed down. No release film — the
   peel ply bleeds into the breather on its own.
4. **Breather** over that, lapping past the part everywhere.
5. Film over, sealant tape round, **through-bag connector** in — its base sits
   on the breather inside, the threaded top clamps down through the film.
6. Pull down **slowly**, watching the gauge. Stop at 7 inHg.
7. **Work the bridges out.** Rail transitions and the nose are where the film
   spans a concave corner instead of pressing into it, and a bridge is a void.
   Pleat the film into the corners with your fingers and re-seat the tape.

### Bagging the internal cavity — the caul does it, not the bag

The cavity is a **concave box**, and this is the one shape vacuum bagging is
bad at. Atmospheric pressure presses a bag *onto* convex surfaces and
**bridges** it across concave ones — a bag laid over the cavity opening spans
it like a drum skin and touches nothing inside. Every corner and fillet would
cure as a void.

**So the bag never goes into the cavity. A caul does.**

`13_cavity_caul` is a male plug of the cavity, 0.5 mm under size per side
(laminate plus peel ply). It drops in on top of the wet cavity laminate, and
the bag presses on **the caul** — which presses the laminate into the floor,
the walls and the R10 fillets. Pressure gets where a bag cannot reach.

**Order for that session:**

1. **Release the caul properly** — wax and PVA, or packing tape over the whole
   plug. A caul bonded into a cured cavity is not recoverable, and you would be
   digging MDF out of a finished board
2. Break the caul's own edges to the cavity's R10, or it will not seat
3. Wet out the cavity laminate, working the fillets with a brush — stipple,
   don't drag
4. Peel ply into the cavity, pressed into the corners
5. Caul in, firmly
6. Breather and film over the whole board as normal
7. Pull down. The caul takes the load

The caul also **supports the deck skin** across the opening during the same
cycle, which is the other thing that would otherwise bridge.

### How long the pump runs

**Until the resin has gelled hard — not until it looks set.**

Practically: **run it overnight, 8–12 hours.** De-bag in the morning. The rule
underneath that is *hold vacuum past gel*, because a laminate released while
the resin can still move will spring back and reopen the voids you just spent
the session closing.

Once the bag is sealed the pump is barely working — with a sound bag it will
idle, and on a small pump it would cycle a couple of seconds every 10–20
minutes. Leaving a 4.5 CFM pump running overnight is well within its duty.

**Do not sand or recoat for 24 hours** minimum, longer if it is cool. Full cure
is 1–4 days at 75 °F.

### What "good" looks like at de-bag

- Peel ply comes off dry-ish and takes a fuzzy print with it — that is the
  surface you want for the next bond, and **do not sand it smooth**
- Breather is stiff with resin in places. Normal, and more so without release
  film
- No shiny patches. A shiny area is a place the bag bridged and never pressed

### If it goes wrong mid-cure

A bag that fails at hour one is recoverable — re-tape and pull back down. A bag
that fails at hour four is not; the resin has moved. **Which is exactly why the
pump was worth $58 rather than doing this by hand.**

## What to learn, in order

1. **Ask Maker Shop which CAM they use.** Axiom machines commonly ship with
   Vectric VCarve, which handles 3D roughing and finishing from an STL and is
   the easiest path here. Fusion 360 is free for personal use and more capable
   but steeper. Whichever it is, that is the software to learn — and it is the
   only real prerequisite.
2. **Take their tool training.** It is included with membership.
3. **Cut a test piece.** Take one of the 1:12 miniature STLs from `print/`,
   scale it, and machine it in a scrap of the same EPS. It exercises the whole
   chain — CAM, workholding, two-sided flip, tool choice — for the cost of an
   offcut. **Do this before you cut a real core.**
4. Then cut the shorter core half first (370 mm). If it goes wrong you have
   wasted the cheap end.

---

## What to job-shop instead

| Part | Why |
|---|---|
| ~~G10 flat parts~~ | **There are none.** The shell and rim ring print; the floor, mast plate and handle strips are aluminium — a bandsaw and a drill press cover all three. This used to be the biggest reason a shop might turn the job away. |
| **The two MDF templates** | 2D profiles — trivial for anyone with a router table, and not worth machine time. |

---

## Risks, honestly

| Risk | Mitigation |
|---|---|
| Never having run a CNC | Test piece in scrap first; foam is unbreakable |
| Flip registration wrong | Dowel pins; dry-run in air; check the mirror axis |
| Shop bans EPS | Ask before buying a pass. G10 is no longer a question — there is none |
| Bed too small | **Unverified.** The AR8 is 1219 × 610 on paper — confirm |
| Tool reach | Solved by cutting layers before glue-up |
| Seam misalignment | Both halves off the same fixture and datum |
