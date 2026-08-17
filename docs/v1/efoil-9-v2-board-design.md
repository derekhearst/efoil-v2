# eFoil V2 — Complete Board Design

**Created:** August 8, 2026
**Status:** Design spec. Build starts after a season of V1 riding data.
**Companion files:** `board_gen.py` (parametric hull generator), `blender_board.py`, `efoil_v2_hull.stl`, `efoil-8-v2-planning.md`

---

## 1. Design Philosophy

Every V1 failure traced to **hand-executed geometry being inconsistent**, not to bad design decisions. V2 attacks that directly with three changes:

| Change | What it removes |
|---|---|
| **CNC-milled core** | Hand-fillets, uneven cavity walls, out-of-plane gasket lands |
| **Grooved O-ring** | Compression tuning by feel — seal squash becomes a machined dimension |
| **Vacuum bagging** | Resin-ratio variability, and the weight that came with it |

**The difficulty moves from the build to the setup.** CAD, milling, and bagging prep get harder and more front-loaded. Assembly gets much easier and far more predictable.

---

## 2. Dimensions

| | V1 | **V2** | Δ |
|---|---|---|---|
| Length | 1600 mm | **1400 mm** | −200 |
| Width | 600 mm | **570 mm** | −30 |
| Thickness | 153 mm | **150 mm** | −3 |
| Volume | 96.6 L | **53.9 L** | −42.7 |
| Weight (est.) | 25–30 kg | **16–18 kg** | ~−10 |

Volume figure is from `board_gen.py`, calibrated against published Lift specs (model gives 1400 × 570 → 53.9 L; Lift 4'7 LIFTX is 1400 × 520 → 49 L).

### ⚠️ The volume trade-off — read before committing

**You cannot have short, narrow, thin, and high-volume.** Real shaped boards fill only ~45–47 % of their bounding box.

| L × W × T | Volume | vs V1 thickness |
|---|---|---|
| 1400 × 560 × 118 | 41.7 L | −35 mm |
| **1400 × 570 × 150** | **53.9 L** | **−3 mm** |
| 1400 × 560 × 180 | 63.6 L | +27 mm |
| 1500 × 600 × 145 | 59.9 L | −8 mm |

At 86 kg rider + ~17 kg board, 53.9 L is **−49 kg net** versus V1's −16 kg. Lift ships 49 L boards for *advanced* riders on 7.9 kg carbon hulls.

**If takeoffs prove difficult on V1 this season, build the 1500 × 600 × 145 (60 L) instead** — still thinner and shorter than V1, much closer to how Lift positions the Laird 5'2 for heavier riders.

### Planform / profile parameters
```
WIDE_POINT   0.48    (fraction of length from tail)
NOSE_PULL    1.75    TAIL_PULL    2.20
TAIL_WIDTH   0.84    NOSE_WIDTH   0.16
NOSE_ROCKER  78 mm   TAIL_ROCKER  6 mm    ROCKER_START 0.55
THICK_POINT  0.46    THICK_NOSE   0.30    THICK_TAIL   0.88
RAIL_HEIGHT  0.34    BOTTOM_FLAT  5.0     DECK_CROWN   3.0
```
Hard-ish chine rails (flat bottom turning sharply at the rail) for release on takeoff, per sat_be's V1 feedback.

---

## 3. Core Construction

### Material zones — dense material follows point loads, skins do the structural work

```
        ┌──────────────────────────────────────┐
        │           EPS ~2 lb/ft³              │  ← everywhere else
        │   ┌──────────────────────────────┐   │
        │   │  H200/H250 dense transition  │   │  ← ring, +80–100 mm beyond G10
        │   │      ┌──────────────┐        │   │
        │   │      │  G10 plate   │        │   │  ← bolts land here only
        │   │      └──────────────┘        │   │
        │   └──────────────────────────────┘   │
        └──────────────────────────────────────┘
```

**Taper or step-lap the density transitions.** A butt joint between H250 and 2 lb EPS is still a stiffness discontinuity — mill a chamfer on the mating faces so stiffness steps down gradually rather than falling off a cliff.

### CNC seam
- **Seam at 1000 mm from tail** → halves of 1000 mm and 400 mm
- Both under a 1219 mm (4×4) makerspace bed
- Deliberately clear of both the mast hardpoint and the cavity — put the joint where the loads aren't
- **No structural insert at the joint.** The core isn't carrying the load; skins are. A hard slug creates a stress riser and telegraphs through the finish. Butt-glue with thickened epoxy, clamped flat on a reference surface.
- Optional: dowels purely for alignment during glue-up, not structure
- A band of biax across the seam, under the main skins

---

## 4. Mast Hardpoint

The highest-load feature on the board. Four M6 bolts at 8–10 N·m against a gasket, plus mast bending under rider weight.

- **Position: 350 mm from tail** (scales V1's 400/1600 ratio) — verify against your actual wing's centre of lift
- **Single fixed bolt position** (per decision — no track box). Gong Allvator mounts on a fixed 4-bolt top plate, so a foil box buys nothing structurally and adds a large recess with more cut edges to seal.
- **G10 plate** sized to the Gong top-plate footprint plus margin for bolt heads and washers
- **H200/H250 dense ring** extending 80–100 mm beyond the G10 in every direction
- **Compression column** of the same dense foam running from the G10 hardpoint straight up to the deck skin

### Why the compression column matters
Mast bolts pull *up* against the hull; the rider stands *down* on the deck directly above. Without a column, the deck skin spans that load alone and the core between crushes over time — you get a dished deck and progressive loss of bolt preload, which shows up as a leaking mast gasket.

V1's 3/4" plywood plate did this job implicitly by being thick and stiff. Going to G10 + foam loses that, so **the column is what replaces it.**

- Column footprint at least as large as the G10, ideally slightly wider at the deck end
- Bonded to the G10 below and the deck skin above with thickened epoxy — continuous load path
- **Mill as one piece with the surrounding dense ring** rather than gluing in a separate block

### ⚠️ Clash check — resolve in CAD first
Confirm the compression column does not collide with the cavity floor. If it does, either shift the cavity forward or make the cavity floor itself the load path — the latter changes how the floor is built, so decide early.

---

## 5. Cavity

**No stringer** — it would dead-end at the cavity anyway. The cavity walls become the structural spine once skinned.

| Element | Material | Reasoning |
|---|---|---|
| **Ledge / rim** | **G10 ring, laminated in** | 6 hatch bolts and threaded inserts land here. This is exactly where V1 failed (plywood crushed, insert pulled). Foam of any density won't hold a threaded insert. |
| **Walls** | Normal EPS + **extra biax** | Stiffness comes from skins, not core density. Invest in glass, not heavy foam. |
| **Floor** | Depends on layout | If it sits above the mast hardpoint it's in the load path → dense core. If offset (as V1), it carries ~12 kg of battery over a large area → normal core is fine. |

**Every inside corner gets a generous milled radius.** Sharp inside corners in a high-stress region is precisely the combination that delaminated V1's deck.

**Starting dimensions (from V1, proven):** ~620 mm long × 300 mm wide. **Revisit after the pack decision** — a 16S pack changes cell count and therefore enclosure size.

---

## 6. Hatch Lid

V1's lid was 3/4" plywood with epoxy hot coat only and no glass — the hot coat was the sole water barrier on the wettest part of the board, and the plywood crushed under a bolt head.

**V2: glass skin / PVC foam core / glass skin sandwich**
- Core: **Divinycell H80, 10–12 mm**. Closed-cell, so a breach doesn't wick like plywood.
- Skins: glass both faces, **wrapped around the perimeter so no cut edge is ever exposed**
- **G10 pucks let into the core at each of the 6 bolt positions**, laminated in — this is what stops the crush-and-pull failure
- **Fender washers under every bolt head**, even with G10 pucks
- Perimeter bevel on the outer edge as a lead-in, so the lid slides onto the seal rather than catching it

**Stiffness matters as much as strength.** A lid that bows between bolts breaks gasket compression mid-span and no amount of gasket tuning fixes it. Sandwich stiffness comes from skin separation — 10–12 mm core with thin skins is far stiffer *and* lighter than solid material.

### ⚠️ Decide in CAD: flush vs. proud
- **Flush in a recess** (V1 style) looks better and the traction pad runs over cleanly, but recess depth and lid thickness must match precisely — and any epoxy buildup on the rim shrinks the opening. This is exactly what forced the V1 lid to be beveled after the leak repair.
- **Proud on top of the rim** is uglier but far more forgiving to build.

---

## 7. Sealing System

### Grooved O-ring — the single biggest reliability upgrade
Compression is set by **groove depth and O-ring cross-section**, not by feel. The lid bottoms laminate-to-laminate on the rim and the seal squashes to exactly the design amount, everywhere, every time.

- Machine the groove into the G10 rim — **the highest-value CNC operation in the entire build**
- Lid underside must be a true flat plane; machine or carefully fair it, don't accept whatever the bag gives
- **No hinge.** The hinge is what caused V1's tilt → over-torque → ply crush → insert pullout chain. Bolt-down with a tether so the lid can't be lost.

### Charge port + switch (removes the routine reason to ever open the board)
- **Charge port:** ~5 A, so trivially easy to seal — waterproof marine/industrial or magnetic connector. **The connector is the water barrier, not the door.** The board must stay watertight with the access door hanging open in the rain.
- **Magnetic switch:** reed or hall sensor **bonded behind the laminate**. Zero penetrations. Strictly better than any physical switch.
- Both behind a small spring-open weatherproof panel door

### Pressure vent
**Design the mounting boss even if you don't fit one initially.** A sealed air volume going from a hot deck to cold water sees real pressure differential acting on the weakest seal, and drives condensation. Five-minute retrofit if the boss exists; a redesign if it doesn't.

### Mast penetration
**Don't redesign what worked.** V1's neoprene gasket under the plate with undersized collar holes passed submersion testing. Carry it over unchanged.

### Non-negotiable rule
**Neat epoxy on every cut edge, always.** V1's leak came from unsealed laminate cut edges at the cavity ledge wicking into the foam. Costs nothing; prevents the entire failure mode.

---

## 8. Layup

**Method: hand wet layup + vacuum bag.** Not infusion — roughly 80 % of infusion's quality for ~40 % of the process risk, and it works with TotalBoat 5:1 rather than requiring special low-viscosity resin.

**Fabric: E-glass, not carbon.** Saves $300–500 and is far more forgiving. With a proper sandwich and bagging, glass is plenty stiff for a foil board.

### Schedule (starting point — sanity-check against foil.zone builds)
| Area | Layers |
|---|---|
| Hull | 2 × 6 oz + 1 × 1708 biax |
| Deck | 2 × 6 oz + 1 × 1708 biax |
| Cavity walls | +1 × 1708 biax |
| Mast hardpoint region | +2 × 1708 biax, staggered/stepped edges |
| Seam | biax band across the joint, under main skins |
| Rails | wrap continuous, no cut edges |

### Bagging
- **Moderate vacuum, 10–15 inHg** — enough to compact, gentle enough not to crush EPS. Conveniently sidesteps the core-crush problem that makes full-vacuum infusion tricky on foam.
- **One face per session, two sessions total.** All that face's layers wet-on-wet in a single bag if pot life allows; 2+2 if it feels rushed. Never both faces at once.
- **Cavity:** mill a **caul/plug from the same CAD file**, release-taped, so the bag presses cavity laminate against something solid. Otherwise the bag tents over the void and applies no pressure to the walls.
- Peel ply the whole layup — uniform matte surface with tooth, and it pulls excess resin
- Pleat the bag and use extra tacky tape at inside corners so it presses in rather than bridging

### ⚠️ Practice first
**Bag two or three flat scrap panels before touching the real board.** Bagging is easier to get *consistent* but not easier to get *right the first time* — it adds vacuum integrity, corner pleating, and a hard timing constraint (wet out, peel ply, breather, seal the bag, all before gel). Learn that on something disposable.

---

## 9. Finish

1. Peel ply → uniform matte with tooth
2. Fill/high-build coat **thick enough to sand flat without ever touching fibre** (sand into the glass and it's unrecoverable)
3. Wet sand 400 → 800 → 1200 → 2000 on a block
4. 2K automotive clear, or compound and polish

**Post-cure before finishing** so shrinkage happens before you make the surface perfect, not after.

**Paint lessons from V1:** respect the recoat window absolutely — within ~1 hour or after full cure, never the 1–24 hour dead zone. Thin coats, sweep past the edges, never linger on a rail. V1's tail wrinkled because clear went onto color that had only cured 48 hours in 100 °F heat.

---

## 10. Build Sequence

1. **CAD everything first** — hull, cavity, hardpoint pockets, compression column, O-ring groove, all penetrations. Resolve the column/cavity clash.
2. **Confirm makerspace CNC bed size and whether they allow EPS** — this is a hard design constraint
3. Mill core halves, cavity plug/caul, G10 parts
4. Bond core halves flat on a reference surface
5. Bond in G10 hardpoints, dense-foam ring, compression column; fair flush
6. **Seal all cut edges with neat epoxy**
7. Practice-bag scrap panels
8. Bag hull skin (with cavity plug in place)
9. Flip, bag deck skin
10. Cut cavity opening; **seal every cut edge**; glass cavity walls (hand-consolidated)
11. Machine the O-ring groove in the G10 rim
12. Build the lid panel separately; machine flat; laminate G10 pucks
13. Set threaded inserts in the G10 rim
14. Fill coat → sand → clear
15. Fit charge port, magnetic switch, vent boss
16. **Submersion test, sealed and EMPTY, before any electronics go in**
17. Traction pad last, after clear is genuinely hard

---

## 11. Open Questions

- **Volume:** 53.9 L or the 60 L option? Decide after a season on V1 — if takeoffs are hard, go bigger.
- **Makerspace CNC:** actual bed dimensions, and do they allow foam?
- **Pack architecture:** 14S vs 16S+ determines cell count, enclosure size, and therefore cavity dimensions
- **Cavity floor:** in the mast load path or not? Determines whether it needs dense core
- **Wing centre of lift:** verify 350 mm mast position against the wing you'll actually run most
- **Lid flush vs proud**

---

## 12. What This Fixes

| V1 problem | V2 solution |
|---|---|
| Water wicked through unsealed laminate cut edges | Neat epoxy on every cut edge, always |
| Delamination at sharp inside corners | CNC-milled radii |
| Hinge tilt → over-torque → ply crush → insert pullout | No hinge; bolt-down with grooved O-ring |
| Threaded inserts pulled out of plywood | G10 hardpoints laminated in during layup |
| Uneven gasket compression | Groove depth sets compression, not feel |
| Resin-rich, heavy | Vacuum-bagged, ~10 kg lighter |
| Lid flexed and had no glass | Sandwich panel with G10 bolt pucks |
| Deck could dish over the mast | Dense-foam compression column |
| Had to open the hatch to charge | Charge port + magnetic switch behind an access door |
