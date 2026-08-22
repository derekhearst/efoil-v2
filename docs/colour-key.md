# Model colour key

Every part in `model/blender_board.py` is coloured by the **material it is made
from**, not by which object it is. Two parts sharing a colour is a statement
that they get cut from the same stock. The palette lives in one place —
`PALETTE` in `blender_board.py` — and the model prints this table on every run,
so it cannot drift from what is actually rendered.

Renders: `renders/v2_exploded_iso.png` is the one to read first.

| Swatch | Key | What it is | Where it appears |
|---|---|---|---|
| `#E0E2E5` | `hull_glass` | E-glass / H80 / E-glass shell, vacuum bagged | hull skin (drawn transparent so the internals read) |
| `#F4F4ED` | `eps` | EPS blank, 2 lb/ft³ | hull core, CNC milled in two halves |
| `#F2DB6B` | `h80` | H80 PVC foam, 5 lb/ft³ | sandwich cores in both lids |
| `#3372CC` | `dense` | H200/H250 dense PVC foam | mast block, full depth, G10 let into its underside |
| `#D8AD47` | `g10` | G10 laminate, general | miscellaneous G10 |
| `#B77223` | `g10_rim` | G10, 12 mm | hatch rim ring — glassed into a square foam rebate |
| `#8C4914` | `g10_mast` | G10, 20 mm | mast plate (blind M8 inserts) and the mast-wire conduit |
| `#F2C67F` | `flange` | G10, 20 × 10 mm | module flange rails — module lid bolts land here |
| `#9EA8B7` | `enclosure` | G10, 3 mm | module shell walls and floor |
| `#59CCE0` | `lid` | glass 1 / H80 12 / glass 1 | hatch lid sandwich |
| `#9E66C6` | `lid_mod` | glass 1 / H80 6 / glass 1 | module lid sandwich |
| `#289E60` | `cell` | BAK N21700CG-50 | the 128 cells, 16S8P |
| `#191C21` | `wrap` | heat-shrink and kapton | pack wrap |
| `#0C4C23` | `pcb` | DALY Smart BMS 16S 200A, 164 × 66 × 21 | strapped to the module's outboard wall, fuse abreast |
| `#333D8C` | `esc` | Flipsky 75200 Pro | in the strip beside the pack |
| `#E5720C` | `fuse` | fuse / main breaker | in the strip, abreast of the BMS |
| `#CCCED3` | `nickel` | nickel interconnect strip | pack welds |
| `#9EA0A8` | `steel` | A4 stainless | bolts, mast inserts, the conduit gland, motor can |
| `#474C54` | `alu_anod` | anodised aluminium | foil mast and fuselage |
| `#111114` | `carbon` | carbon | front wing, stabiliser, prop |
| `#D82659` | `seal` | O5 / O3 silicone cord, or pour-in-place | hatch groove 6 × 4, module groove 4 × 2.4 |

Metals are given `Metallic = 1.0`, so under Workbench's studio light they read
brighter than their base colour — that is the material behaving like metal, not
a wrong swatch.

## Foil

The foil is **the one Derek actually owns** — bought Apr 2026.
It is modelled so ride height, prop clearance and the mast bolt pattern can be
checked against the board rather than taken on trust. The *sections* are still
NACA-symmetric stand-ins, not Gong's actual profiles, but every dimension below
is off Gong's published technical sheet unless marked estimated.

Until 15 Aug 2026 this block was a made-up "Allvator Veloce" and was wrong in
every dimension. `model/performance.py` reads these values directly, so a
guess here becomes a wrong power figure downstream.

| Part | Dimension |
|---|---|
| Mast | **Alu Mast V2, 85 cm** — 120 mm chord, 11.5% thick (chord estimated) |
| Fuselage | **Pro Alu V2, Regular** — 560 mm × 32 mm (length estimated; Gong does not publish it, and the Pro is deliberately cut short with the stab's carbon tail making up the lever arm) |
| Front wing | **X-Over V2 XL** — 950 mm span, 1650 cm², span²/area 5.5, 220 mm root chord |
| Stabiliser | **Stab X-Over V2 XL, 48 cm** — 480 mm span, 335 cm², 7.9 mm thick |
| Motor | Flipsky 65161, 205 × 65 mm, saddle-clamped to the mast trailing edge |
| Prop | 165 mm disc, spinning in the gap between mast and stabiliser |

Orientation matters and is easy to get wrong: **+X is the nose.** The front
wing belongs at high X and the motor and prop at low X. The first version of
this had it mirrored, which puts the prop under the rider's front foot.

## Module joinery

The panels are not butted edge-on — a 3 mm G10 edge gives a 3 mm glue line
with no location, which behaves as a hinge rather than a joint. Instead:

1. The **floor** is machined with a 1.5 mm locating groove around its
   perimeter. The walls drop into it, so the box self-jigs during glue-up and
   the joint loads in shear instead of peel.
2. The **long walls** run the full length; the **end walls** land between them.
   That is a lap, so each end wall bonds on its 3 mm edge *and* against the
   long wall's inner face.
3. There are **no corner posts**. They existed to turn a butted 3 mm G10
   corner into a bonded joint; a printed shell has no butted corners to fix.
4. The **flange prints as part of the wall** — 20 mm wide × 9.525 deep — and
   carries the M4 heat-set inserts for the lid bolts at a 5.6 mm printed
   pilot. A 4 mm wall cannot hold an insert, but a printed wall can simply be
   thicker where it needs to be, which is the whole advantage.
5. Everything is thickened epoxy with a 6 mm glass-tape fillet on the inside
   of every corner.

Total floor-to-wall bond area is 6,952 mm².

## What the divider used to do, and what replaced it

> **The module shell is 3D printed, not cut from G10.** G10 walls were specced
> to save weight and did the opposite: the 3.175 mm G10 shell — walls, bonded
> flange ring, four corner posts — came to 1,323 g against ~1,130 g printed,
> and cost six CNC parts, a bond jig, a four-joint tolerance chain and a seal
> groove that had to be routed after assembly. The module's real weight win
> over V1 is **one box instead of two** (−833 g) and a **sandwich lid instead
> of 4 mm aluminium** (−857 g). Neither needs G10 walls.
>
> In the model these are the `V2_ModPiece_*` objects — the four pieces as they
> come off the printer. The old `V2_Mod_Wall*` / `V2_Mod_Flange*` boxes still
> exist but are hidden: they are how the shell is *described*, not how it is
> *made*, and leaving them visible hid the print split entirely.
>
> The shell prints in **4 L-shaped pieces split at wall midpoints**, not at
> corners, so every corner comes out of the printer solid and each seam lands
> on the flattest, least-loaded part of a wall. Paired 10 × 10 mm external
> ribs at each seam self-align the pieces and double the bond area — that is
> the alignment feature here, not a dovetail: a dovetail needs depth to key
> into and the wall is only 4 mm, while the ribs are 10 × 10 and already sit
> either side of every seam. Largest
> piece is 236 × 156 mm, inside the Bambu A1's 256 mm bed. **ASA, not PETG** —
> ASA creeps far less under sustained bolt load, which is the whole job of a
> gasket flange, and V1 already printed its battery enclosure in it.
>
> The lid seals on a **flat neoprene gasket**, 7 mm band, 3 mm stock squeezed
> to 2.0 (33%) — not an O-ring in a groove. A printed groove holds about
> ±0.2 mm, a third of an O3 cord's squeeze, so the seal would vary bolt to
> bolt. A flat gasket absorbs the irregularity. The hatch keeps its O-ring,
> because the hatch lands G10 on G10 and its squeeze is set by geometry.

| Divider's job | Now done by |
|---|---|
| Stiffening rib | the printed flange and the four seam ribs |
| Keeping ESC heat off the cells | the 28 mm wire raceway as an air gap, plus the ESC's own standoff |
| Tidy wiring | the raceway and the aft wire-loop zone, which are actual space rather than leftover gaps |
| Power crossing between bays | nothing — the bays are one volume, so no glands are needed at all |

Killing it removed three gland penetrations from a wall that was never a
pressure boundary. The only gland left in the boat is the one that matters:
where the mast wires cross from wet to dry at the cavity floor.

## Mast wire route

There was no route at all before — the motor wires left the mast head with
nowhere to go. Now:

1. Wires leave the mast head into a **32 mm OD / 28 mm bore G10 conduit**,
   bonded through the hull skin, the mast plate and the dense-foam ring.
2. The conduit's lower end is **potted solid**. Everything below that point is
   assumed wet.
3. It terminates above the cavity floor in a **25 mm gland** — the single
   penetration of the dry cavity.
4. Wires surface in the **aft service bay**, an 88 x 329 mm zone of cavity
   that sits aft of the module specifically so the conduit does not come up
   through the module floor (which is exactly what the first attempt did).
5. From there they pass through three PG11 glands in the module's aft wall and
   run forward down the 22 mm raceway to the ESC.

The bay is what pushed the module forward, which moved the board CG from 38.5%
to 45.8% of length from the tail.

## Aft service bay and the connector panel

The module's **aft wall is the connector panel**. Every electrical crossing is
a sealed panel-mount fitting through that one wall, facing into the service
bay, so the module stays a closed box and still lifts out in one piece.

| Fitting | Position on the wall | Clear of pack |
|---|---|---|
| 3 x PG11 glands | y 68.9-143.9, z 26, 26 mm pitch | 9.5 mm |
| Power button | y ~82, z 66 | 8.0 mm |
| Charge port | y ~132, z 66 | 53.0 mm |

All of it sits inside the **service strip band** (y 59.5-153.5). That is not
cosmetic: the pack butts the aft wall everywhere else, so a fitting outside
the band would land its body *and its backing nut* straight on the cells, with
nowhere to turn a wire and nowhere to get a spanner.

| Check | mm |
|---|---|
| Gland pitch | 26 (PG11 nut is ~24 A/F - as tight as it goes) |
| Button to port | 15 |
| Fittings above the gland row | 11.5 |
| Fittings below the wall top | 14.5 |
| Bodies protruding into the bay | 40, against an 88 mm bay |

Separately, on the cavity floor in the same bay, the **mast-wire conduit**
surfaces on the centreline and terminates in its own 25 mm gland. That is the
only wet-to-dry crossing on the boat, and the only penetration of the cavity
floor.

Nothing here penetrates the hull. The hatch is still the only way in, so the
button and port are reached by opening the lid.

## Pack datum

The pack no longer floats in the middle of the box. It fills the module's full
internal length and sits hard against one long wall, so all the slack collects
in a single 94 mm service strip down one side instead of an L-shaped gap that
is awkward to use and awkward to strap into.

| | mm |
|---|---|
| Module internal | 377 x 307 x 98 |
| Pack | 349 x 211 x 93 |
| End clearance | 14 each end - set by the corner posts, not by choice |
| Side clearance | 2 (datum face) |
| Service strip | 94 total: 68 ESC + 22 raceway + 4 |

The 14 mm ends are structure, not waste: the pack would foul the corner posts
otherwise.

## Rim ring seat and the glass path

The board is laminated with the **lid off and the cavity an open box**, and the
G10 rim ring is **laid into its rebate before glassing**, not bonded on
afterwards. That single fact decides which edges get a radius and which stay
square, and it is the opposite of what the model used to do.

A radius exists for one reason only: laminate cannot wrap a sharp convex corner
or bridge a sharp concave one. So an edge gets a radius **if and only if the
glass actually crosses it**. Every corner underneath the ring is covered by the
ring — the glass never sees it — so those corners are square, and rounding them
just holds the ring up off its own seat.

| Edge | Treatment | Why |
|---|---|---|
| Deck → lid recess wall | convex R10 | glass runs down into the recess |
| Recess wall → ring top face | thickened epoxy fillet at layup | concave; the ring's outer face is *flush* with the wall above it, so there is no step to machine |
| Rebate wall → ledge | **square** | the ring beds into this corner |
| Ledge → cavity wall | **square** | also under the ring |
| Ring inner top edge | convex R4, **on the G10** | glass turns off the ring and down into the cavity |
| Cavity wall → floor | concave R10 | glass has to get into the corner |
| Cavity vertical corners | R22 | |

The ledge now measures a full **34.0 mm** flat — exactly the ring width — where
the filleted version left only 14 mm of flat with a 10 mm cove each side. The
ring drops in and sits down on its whole footprint.

One thing to note when cutting the ring: **only the inner top edge is broken.**
Rounding the outer edge as well is wrong, and looks right until you section it —
the ring's outer face is coplanar with the foam recess wall above, so a chamfer
there opens a 4 mm triangular void behind the ring for the glass to bridge over,
which is the exact defect the rest of this is avoiding.

## Mast hardpoint

The G10 plate and the dense foam are **let into a pocket milled in the hull
underside**, not sat on top of it. The plate's own bottom face becomes the mast
pad and the finished hull surface.

| | |
|---|---|
| Pad plane | the **highest** point of the underside over the *plate's* footprint |
| Worst recess at the pad edge | 1.5 mm, faired before glassing |
| EPS between mast and G10 | none |
| Dense foam above the plate | 12 mm, up to the cavity floor |
| Fastening | 4 × M8 in Ø12 × 12 **bonded 316 bushings**, from the pad face |
| G10 above each bushing | 4 mm, solid — the only barrier to the cavity |
| Thread engaged in foam | **none** — it is all in G10 |

Two details that both went wrong before and are worth stating plainly:

1. The pad plane comes from the **plate's** footprint, not the dense ring's.
   Taking the highest point over the much larger ring buried the plate 7 mm deep
   with EPS underneath it — soft material directly in the mast's load path.
   Taking the *lowest* point instead put the plate 1.5 mm proud of the skin.
2. The dense ring is **clipped to the hull** rather than given a footprint
   guessed to fit. At 90 mm proud of the plate all round it reaches x = 125 mm,
   which is outside a hull that is only 125 mm from its own tail. The same
   clipped solid is both the pocket cutter and the foam, so the fit is exact by
   construction and the ring cannot break the skin.

### Why bonded bushings and not key-locking inserts

Key-locking inserts lock by driving four hardened keys down into the parent
material. That is the right fastener for aluminium and the wrong one for a
woven-glass laminate: in G10 the keys act as wedges between plies and crack the
bore. A plain 316 bushing bonded with structural epoxy carries the torque on the
bond area instead, and the laminate never sees a wedging load. Bond the bushings
into the plate **on the bench, before the plate goes into the hull** — they are
blind from the pad face and the pad is the finished hull surface.

### Where the thread actually sits

A fair question, because the section makes it look like the fasteners run up
into the foam. They do not — nothing threaded touches foam anywhere:

| z (mm) | |
|---|---|
| 1.5 → 13.5 | bushing, 12 mm, from the pad face |
| 13.5 → 17.5 | solid G10 |
| 17.5 → 29.5 | dense PVC foam |
| 30.0 | cavity floor |

The dense foam's only job is spreading the plate's bearing load into the EPS
over a larger footprint. It carries no fastener and no thread.

## The deck is not flat, and two things assumed it was

`THICK` (144.9 mm) is the deck height **at the thickest station only**. The deck
line rises above it toward the nose — 145.35 mm by the forward edge of the hatch
rebate. Two things were pinned to `THICK` and were wrong because of it:

1. The **rebate cutter** stopped at `THICK`, so forward of x = 770 mm it no
   longer broke the surface. The front ~147 mm of the rebate was capped by a
   wafer of foam feathering from 0.4 mm down to nothing — a curved lip over the
   ring instead of an open rebate. The cutter's top now follows `deck_z_at(x)`
   and overshoots 30 mm past it, so the cut always breaks out and the R10 lands
   on the real deck at every station.
2. **Lid flushness** was measured against `THICK` and so read 0.00 mm at every
   parameter set. Measured against the actual deck the flat lid runs +0.10 mm
   proud at the aft end of the hatch to −0.41 mm sunk at the forward end, which
   is deck curvature over a 567 mm hatch and gets faired.

## Module clearance to the cavity

`ENC_GAP` is now derived as `GLASS_R + 2`, not a flat 8 mm. The cavity's floor
fillet encroaches by up to `GLASS_R` at floor level, so at 8 mm the module floor
sat **0.34 mm inside the fillet** and only came clear above z = 31. It slipped
through because the interference test tolerates 0.005 L and the overlap was
0.0001 L — a real geometric clash reported as a rounding error. There is now an
explicit clearance check that fails outright rather than hiding behind a volume
tolerance.

The cavity is derived from the module (`CAV_WIDTH = ext_w + 2 * ENC_GAP`), so
widening the gap grew the cavity rather than stealing internal volume: module
internal is unchanged at 425 × 284 × 76, cavity went 499 × 306 → 503 × 314, and
rim-edge-to-rail went 45.9 → 41.9 mm.

## The mast hardpoint is nested, not stacked

The dense foam and the G10 share one volume rather than sitting in two layers:

1. The EPS is cut for the **dense block** — full depth, from the hull skin up to
   the cavity floor, clipped to the hull so it cannot break out.
2. The dense block is cut for the **G10 plate**, let into its underside so the
   plate's bottom face is the mast pad and the finished hull surface.
3. The G10 is cut for the **bushings** and the **wire hole**.
4. The dense block and the EPS are cut for the wire hole too.

Stacked, the plate's own level sat in bare EPS, so everything the plate pushed
sideways went straight into 32 kg/m³ foam. Nested, the plate is wrapped in H200
on all four sides as well as above, and the load reaches the EPS only after it
has already been spread by 90 mm of dense foam in every direction.

| | |
|---|---|
| Dense block | full depth, hull skin → cavity floor, footprint clipped to the hull |
| H200 above the plate | 8 mm |
| H200 beside the plate | 90 mm all round |
| EPS touching the plate | none |
| Dense foam mass | 0.68 kg |

One caveat worth keeping in view: the **12 mm above the plate is not a designed
number** — it is whatever was left between the plate's top face and the cavity
floor. Total hardpoint depth of 16 mm G10 + 12 mm core + floor laminate ≈ 30 mm
is reasonable for a 1.4 m board, but it came from arithmetic rather than intent.

### A rendering trap this exposed

Anything built by a boolean inherits the *other* operand's material slots, and
its faces keep pointing at them. The dense block came out of an `INTERSECT` with
the hull carrying `[None, hull_glass, dense]` and rendered as hull glass — pale,
so it read as EPS instead of blue H200 and looked like the change had not
applied. `set_single_material()` now forces one slot and reindexes every
polygon. Worth remembering for any future boolean-derived part.

### Sizing the block

`DENSE_MARGIN` is split into X and Y because they cost different things. It was
90 mm all round, which put the block's forward edge at x = 125 mm — 125 mm from
the tail and 31% of the board's length — for a plate that is 250 × 175.

The block is only ~30 mm deep, so a 45° load spread out of the plate edge is
spent in about 30 mm. The rest of the margin exists to feather the stiffness
step into the EPS instead of ending it at a hard edge that prints through and
starts a crack. 50 mm does both jobs.

| | 90 mm | 50 mm |
|---|---|---|
| Footprint | 430 × 355 | 350 × 275 |
| Share of board length | 31% | 25% |
| Dense foam mass | 0.71 kg | 0.40 kg |

### Never cut a solid with a copy of itself

The hull is cut by the **raw** prism, not by the hull-clipped block. Cutting it
with the clipped solid hands the EXACT boolean solver a cutter whose entire
bottom face is coincident with the hull's own bottom surface, and coincident
faces are precisely what it cannot resolve — the pocket came out with jagged
staircase edges around its rim. Clipping buys nothing for the hull cut anyway,
since there is no hull outside the hull to remove. The clipped solid is still
what becomes the dense foam, where it has to stop at the skin and where the
coincidence is harmless because it is a separate object.

After the fix the hull carries 0 non-manifold edges and the pocket wall reads as
a single clean step (hull surface 2.24 → pocket ceiling 29.50 at x = 165).

## No channel in the rim ring

The ring is glassed in with the foam, so the laminate runs across its top face —
and you cannot laminate over an open 6 × 3 groove and still have a groove. The
only ways to keep a machined channel were to mask the ring during layup (leaving
a glass edge terminating on the sealing face, which lifts) or to route the
channel back out through the cured laminate afterwards, which needs a jig for a
571 × 382 rounded rect.

So the ring's top face stays **flat and gets glassed like everything else**, and
the seal moves to the lid: an adhesive-backed closed-cell EPDM sponge strip,
8 × 3 mm, compressed 40% to 1.8 mm by the hatch bolts. Replaceable without
touching the board, and nothing is machined on either part. The lid recess is
1.8 mm deeper to account for the compressed height, so the lid still finishes
flush with the deck.

Clearances on the ring's 34 mm face: 3.0 mm from the gasket lane to the inner
R3 chamfer, 3.0 mm to the hatch bolt heads.

## Will the G10 hold the mast bolts?

Computed rather than assumed, and the first answer was **no**.

Two demand cases, each taken as a moment reacted by a bolt couple — tension on
the loaded row, bearing on the far side, which is how a bolted base plate
actually works:

| Case | Moment | Per-bolt tension |
|---|---|---|
| Pitch — 3 g lift spike, wing 200 mm ahead of the mast axis | 694 N·m | 2 103 N |
| **Roll — 1 g side load at the foil, 750 mm below the base** | **867 N·m** | **4 817 N** |
| Direct vertical, 3 g / 4 bolts | — | 867 N |

Roll governs, and not narrowly. The Gong pattern is 165 mm fore-aft but only
90 mm across, so the same moment loads a bolt **1.8× harder** about the narrow
axis. That single fact sizes the fastening.

| | Ø12 × 12 in 16 mm plate | Ø20 × 16 in 20 mm plate |
|---|---|---|
| Bond area | 452 mm² | 1 005 mm² |
| Capacity @ 15 MPa design shear | 6 786 N | 15 080 N |
| Demand | 5 694 N | 5 694 N |
| **Margin** | **1.19×** | **2.64×** |

The original 16 mm plate gave 1.19×, which is not enough for a part whose
failure drops the foil off the board. The plate is now **20 mm** with Ø20 × 16
bushings. Governing mode is the epoxy bond (15 MPa design, ~2× knocked down from
DP460's ~30 MPa lap shear on composite), not the G10 itself — G10 interlaminar
shear at 20 MPa design would give 14 080 N.

Plate bearing into the dense foam is a non-issue: 0.079 MPa against H200's
~3.5 MPa compressive, a 44× margin.

**The assumption to argue with is the 1 g side load.** If you think a foil strike
is harsher than that, the margin shrinks proportionally and the answer is a
wider bolt pattern rather than a thicker plate — nothing else moves the number
as fast as that 90 mm.

## Seals: grooves, not squashed strips

A flat gasket has no hard stop, so the seal load ends up depending on how hard
each of 13 bolts was done up. Both lids now land **G10 on G10** with the seal in
a groove, so the squeeze is set by geometry.

| | Hatch | Module lid |
|---|---|---|
| Cord | Ø5 (or pour-in-place) | Ø3 |
| Groove | 6 × 4 | 4 × 2.4 |
| Squeeze | 20% | 20% |
| Groove fill | 82% | 74% |
| Stop | lid face on rim ring face | lid face on flange rail |

Pour-in-place silicone works in the same grooves: poured ~0.7 mm proud, it
compresses to flush as the lid bottoms, and the 18% of unfilled groove is what
accepts it.

### The hatch groove is cut last, not first

The ring is glassed into the foam, so the laminate crosses its face and you
cannot machine the groove before layup and still have a groove afterwards. It is
**routed last, through the cured laminate into the ring**, off an MDF template
(CNC part 14). That keeps one continuous laminate across the ring — no masking,
no glass edge terminating on the sealing surface — and costs no depth, which
matters because the lid recess cannot get deeper without the pack fouling the
lid. Check the template's guide-bushing offset against your own router before
cutting it; the drawing assumes 5 mm.

## The module is now a sealed box in its own right

If the hatch ever lets water into the cavity, the module is what keeps it off
the cells. Three things had to change:

1. **Flange rail 14 → 20 mm.** At 14 the rail held the Ø5.6 insert and nothing
   else. At 20 it takes the groove at 4 mm from the inner edge and the insert at
   13 mm, with 4.2 mm of G10 between them.
2. **Lid bolts moved off the rail centreline.** On the centreline the insert bore
   came within 1.2 mm of the groove. At 13 mm in they clear it by 4.2 mm and the
   rail's outer edge by another 4.2 mm.
3. **A membrane vent.** A sealed lithium box must be able to breathe or it pumps
   its own seal every time the sun comes out, and if a cell ever vents, a closed
   box is a pressure vessel. An M12 Gore-type vent in the aft wall passes gas
   both ways and holds out water. **This is the one fitting that must not be
   left off.**

### And it exposed a fit error that was already there

The pack has to pass **through the lid opening**, which is the internal size less
a flange rail each side — not the internal size. At the old 14 mm rail the
opening was 397 mm against a 397 mm pack: exactly zero clearance, i.e. not
buildable, and nothing in the model was checking it. Module internal length is
now derived from the through-opening as well as the corner posts.

| | was | now |
|---|---|---|
| Flange rail | 14 mm | 20 mm |
| Module internal | 425 × 284 | 443 × 284 |
| Lid opening | 397 × 256 | 403 × 244 |
| Pack clearance through it | **0.0 mm** | **6.0 mm** |
| Cavity | 503 × 314 | 521 × 314 |

### V1 as a calibration datum

V1 is 3/4" plywood through-bolted with washers, and it has ridden a season. That
makes it the only real anchor for the 1 g side-load assumption above.

A through-bolt in plywood does not fail by pulling out. It fails by the **washer
crushing into the panel face**, progressively — which shows up as bolts that
keep needing re-torquing long before anything lets go. So capacity is washer
bearing area × plywood flatwise compression, and it scales directly with washer
outside diameter:

| Washer | Bearing area | Dry (6 MPa) | Damp (4 MPa) |
|---|---|---|---|
| M8 standard, DIN 125, Ø16 | 146 mm² | 874 N | 583 N |
| M8 fender, DIN 9021, Ø24 | 397 mm² | 2 382 N | 1 588 N |
| M8 large fender, Ø32 | 749 mm² | 4 493 N | 2 995 N |

Taking the fender washer as typical, V1's mast mount tops out around **0.49 g of
side load at the foil** — half the V2 design case. It has not let go, which says
normal riding stays below that, and that the 1 g case is a *strike* case rather
than a riding case.

V2's bonded Ø20 × 16 bushing in 20 mm G10 is **6.3× V1's capacity** per bolt
(15 080 N vs 2 382 N), on the same 165 × 90 pattern.

Two things this does not prove. Plywood crushing is progressive, so "V1 has not
failed" is not the same as "V1 has not yielded" — if its mast bolts have needed
re-torquing, that is the washers bedding in, and it puts a real number on the
riding loads. And plywood at a mast box gets damp: at 4 MPa the same fender
washer is down to 1 588 N, or 0.33 g.

### Why the bushings stop at Ø20

Bond area is `π × OD × L`, and `L` is capped by the plate thickness, so **bore
diameter is the cheap lever** — a bigger bore costs a bigger drill and a few
grams of stainless, nothing else.

| Bore | Bond area | Capacity | Margin |
|---|---|---|---|
| Ø14 | 704 mm² | 10 556 N | 1.85× |
| Ø16 | 804 mm² | 12 064 N | 2.11× |
| Ø18 | 905 mm² | 13 572 N | 2.38× |
| **Ø20** | **1 005 mm²** | **15 080 N** | **2.64×** |
| Ø22 | 1 106 mm² | 16 588 N | 2.91× |

Ø20 is where it stops being worth pulling: 15 080 N is **0.92× the M8 bolt's own
proof load** of 16 470 N. Past that the joint is no longer the weak link — the
bolt is, and the bolt is Gong's and not ours to change. Edge distances at Ø20 are
32.5 mm on both axes and 70 mm between the bores, so the plate is not troubled.

### The aluminium alternative, and why not

A 6061-T6 plate tapped M8 directly gives ~36 kN — far more than anything else in
the chain — for about $70 and +0.74 kg. It is rejected on corrosion, not
strength: the plate's bottom face *is* the wetted mast pad, with A4 stainless
bolts through it, which is precisely where aluminium mast plates fail. Fresh
water at Lucky Peak makes that milder than salt, but G10 has no galvanic couple,
no wet-strength loss and no creep, and it already clears the bolt.

## Both seal grooves are routed after the fact

Neither groove is machined into a loose part. They are cut last, off cheap MDF
templates, for the same reason in two different guises:

| | Hatch groove | Module groove |
|---|---|---|
| Cut into | the rim ring, through the laminate | the assembled flange ring |
| Cut after | the board is glassed | the box is bonded and filleted |
| Why | you cannot laminate over an open groove and still have a groove | a groove cut in four loose rails has to line up across four bonded joints to seal |
| Size | 6 × 4, Ø5 cord | 4 × 2.4, Ø3 cord |
| Template | CNC part 14 | CNC part 15 |

The module reason is the one that is easy to miss. The flange ring is four
bonded pieces; any misalignment at a joint becomes a step in the sealing
surface, and a step across an O-ring is a leak path. Routed after assembly it is
one continuous groove and the joints stop mattering — the same argument as
machining a gasket face after welding rather than before.

Both templates assume a **5 mm guide-bushing offset**. Check that against your
own bushing and cutter before cutting either template; it is the one number on
those two drawings that depends on tooling rather than on the design.

## Why the dense block went back to 90 mm

It looked thin at 50, and only half of that was the plan shrink:

| | before | after |
|---|---|---|
| Plan margin | 90 mm | 50 → **90 mm** |
| Footprint | 430 × 355 | 350 × 275 → **430 × 355** |
| Core above the plate | 12 mm | **8 mm** |
| G10 plate | 16 mm | **20 mm** |
| Total under the cavity floor | 28 mm | 28 mm |

The core thinning is the **price of the 2.64× mast bolts** — the plate's top face
rose 4 mm and the cavity floor cannot rise to follow it without the module
fouling the lid. Since the block lost depth it keeps its plan area, which is the
cheaper of the two to buy back: 0.28 kg.

## O-ring cord vs gasket: where I actually land

The groove was the important decision and it is already made — a hard stop, with
squeeze set by geometry rather than by how hard each bolt was done up. What goes
*in* the groove is a smaller decision, and a reversible one: cord and
pour-in-place use the **same groove**, so this can be changed later without
re-machining anything.

| | Cord | Pour-in-place | Flat gasket |
|---|---|---|---|
| Hard stop | yes | yes | **no** |
| Splice | one butt joint | **none** | none |
| Corner behaviour | needs a real radius | conforms to anything | fine |
| Replaceable | yes | dig it out | yes |
| Depends on the builder | no | bead consistency | no |

Flat gasket is out on the hard stop, which was the whole point.

Between the other two, the split is by **how often the lid comes off**:

- **Hatch — cord.** This is the lid that gets opened. A Ø5 silicone cord is
  replaceable in minutes. Cut the splice square, bond it, and put it on a
  straight run, never a corner.
- **Module — pour-in-place is the better bet, cord is fine.** The inner box gets
  opened rarely, and losing the splice on the barrier that protects the cells is
  worth more than easy replacement. Release agent on the lid face or it bonds
  both sides.

Two things that decide this in practice rather than on paper: cheap cord takes a
compression set and goes hard, so buy decent silicone or EPDM; and the splice is
the only real weakness of the cord option, which is exactly why the module —
where a leak matters most and access matters least — is the one to pour.

### The corner radius this exposed

A cord will not turn a sharp corner. It lifts out of the groove and bridges.

| | Groove corner R | Cord bend limit (3 × Ø) | |
|---|---|---|---|
| Hatch | R32 | R15 | fine |
| Module | ~~square~~ → **R15** | R9 | fixed |

The module groove was drawn with square corners, which is unbuildable for a Ø3
cord: a 4 mm groove routed with a 4 mm cutter leaves a 2 mm inside radius
against a ~9 mm bend limit. R15 on the centreline clears it and still keeps the
groove 4 mm off the rail's inner edge the whole way round. Both grooves are now
checked against the cord's bend limit.

## The seal goes inboard of the bolts

The module lid had this backwards. Its groove sat 16 mm from the sealed interior
and its bolt circle only 7 mm — so **every bolt penetration was inside the seal
ring**.

That matters because the lid bolt holes are through-holes opening onto a surface
that is always wet: the module lives inside the cavity, and the whole point of
sealing it is that the cavity might not stay dry. Water tracking down a bolt has
to land on the *wet* side of the seal. With the groove outboard, each of the lid
bolts was a direct path into the box, and the seal was sealing nothing.

Measured outward from the sealed interior — the seal must be the smaller number:

| | Seal | Bolt circle | |
|---|---|---|---|
| Hatch | 10.0 mm | 22.0 mm | correct already |
| Module | ~~16.0~~ → **6.0 mm** | ~~7.0~~ → **13.5 mm** | swapped |

The hatch had it right, which is why only the module showed the problem. Both
are now checked, and a seal outboard of its bolts is a hard failure.

Clearances on the 20 mm rail after the swap: bolt insert 3.7 mm off the wall
face, 2.7 mm of G10 between the insert bore and the groove, and a 4.0 mm land
inboard of the groove for the cord to seat against.

## Foam dimensions are not finished dimensions

Everything cut into the blank is a **foam** dimension. The cavity, the lid
recess and the ring rebate all get laminated afterwards, so every finished
opening is one laminate thickness per face smaller than what the CNC cuts — and
all the fits were being checked against the foam, which is not what the parts
have to go into.

`CAV_LAM = 1.5 mm` is now applied to every module-to-cavity and lid-to-recess
clearance, and the report gives both numbers:

| | As cut (foam) | As finished |
|---|---|---|
| Module to cavity wall | 13.5 mm | **12.0 mm** |
| Module to cavity floor fillet | 3.5 mm | **2.0 mm** |
| Module top to the rim underside | 3.5 mm | **2.0 mm** |
| Hatch lid, each side | 3.0 mm | **1.5 mm** |

Lid *flushness* is not affected — the lid seat and the deck gain the same
laminate, so they move together. What the laminate eats is the lid's plan
clearance, which had none to spare.

## Holding it all down

Neither the module nor anything inside it was actually restrained. A 12 kg
module and a 9 kg pack that are only resting somewhere are the two heaviest
objects on the board and the two most dangerous in a fall.

### The module, in the cavity

| | |
|---|---|
| Fore/aft | G10 chocks at both ends |
| Vertical + fore/aft | 2 × 25 mm webbing straps lengthwise between the chocks |
| Bedding | 4 mm EVA pads under the four corners |
| Sideways | the 12 mm finished gap and the pads |
| Penetrations of the cavity floor | **none** |

The two chocks are mounted differently, and the reason is worth recording. The
end gaps are **not symmetric**: aft is 60 mm (the wire bay), forward is only
`ENC_GAP`. Sizing both off an averaged gap put the forward one 8 mm into the
foam. Worse, once resized to fit the gap it still failed — the floor fillet eats
`GLASS_R + CAV_LAM` of a 13.5 mm gap, leaving 0.5 mm for a chock. So the aft
chock sits on the **floor** and the forward one is bonded to the cavity **wall**,
starting at z = 43.5, above the fillet. Same job, no clash.

### The kit, inside the module

| | |
|---|---|
| ESC and fuse | on a 4 mm G10 equipment plate bonded to the module floor, M4 inserts |
| Pack | 2 × 25 mm straps across, into G10 tabs bonded either side |
| BMS | on edge against the pack flank, captured by the same straps |

The equipment plate exists for the same reason the flange rail does: a 3 mm
floor cannot hold a threaded insert. Nothing fastens to the module shell
directly.

### And the tolerance that kept hiding this

The containment check tolerated 0.005 L, which is 5 cm³ — enough to hide a
0.5 mm interference across a whole face. It hid the module floor clipping the
fillet, and then hid the forward chock doing the same thing. It is now
**0.0005 L**, and both showed up as hard failures rather than as numbers to
squint at.
