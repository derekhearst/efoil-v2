> **Superseded planning document.** This predates the parametric model and its
> numbers no longer hold — thickness, module material and cavity size have all
> changed since. Kept because the reasoning is useful and the conclusions are
> not. See the [README](../../README.md) for the current design.

# eFoil V2 — Design & Build Planning

**Created:** August 7, 2026
**Status:** Concept. V1 still in shakedown; V2 starts after a season of riding data.

---

## The Three Pillars

1. **Fast top end**
2. **Light weight**
3. **Sealed, serviceable, charge-in-place**

These reinforce each other. Light helps speed; sealed removes the failure mode that dominated V1.

---

## What V1 Taught Us (each failure maps to a V2 fix)

| V1 problem | V2 fix |
|---|---|
| Water wicked through unsealed laminate cut edges | Neat epoxy on **every** cut edge, always. Cheap step, would have prevented the whole leak saga. |
| Delamination at sharp inside corners | **CNC-milled radii** in the core — no hand-filleting, no sharp corners for glass to bridge |
| Hinge tilt crushed the lid and pulled an insert | **No hinge.** Bolt-down panel with tethered lid. Straight-down compression, even load. |
| Threaded inserts in plywood pulled out | **G10 hardpoints laminated into the layup**, not fasteners drilled into wood after the fact |
| Plywood crushed under bolt load | No plywood anywhere. Fender washers as standard. |
| Uneven gasket compression | **O-ring in a machined groove** — compression set by geometry, not by bolt feel |
| Resin-rich hand layup, heavy | **Vacuum-bagged wet layup** — better fibre ratio, lighter, more uniform |
| Board is ~25–30 kg | Target well under that. Weight is the design goal, not an afterthought. |

---

## Construction

**Method: hand wet layup + vacuum bag.** Not infusion.

This is the deliberate ease-vs-quality choice. Bagging compacts the laminate and squeezes out excess resin (the main win over V1's hand layup) without infusion's one-shot, leak-is-fatal risk. Roughly 80 % of infusion's quality for ~40 % of the process risk. Also lets us keep using TotalBoat 5:1 — infusion needs special low-viscosity, long-pot-life resin.

**Fabric: fiberglass, not carbon.** Saves ~$300–500 and is far more forgiving to work. With a proper sandwich and vacuum bagging, glass is plenty stiff for a foil board.

**Vacuum level:** moderate (10–15 inHg), not full. Enough to compact the laminate, gentle enough not to crush the EPS core — which conveniently sidesteps the core-crush problem that makes full-vacuum infusion tricky on foam.

**Sequence: one face per bagging session, two sessions total.** All that face's layers wet-on-wet in a single bag if pot life allows; 2+2 if it feels rushed. Never both faces at once — you can only bag one face against a surface at a time, and doubling the wet-out area while pot life stays fixed is how you get a starved, panicky layup.

**Cavity:** a bag tents over an open cavity and applies no pressure to the walls. Options, in order of preference:
1. Mill a **caul/plug** from the same CAD file, release-taped, so the bag presses cavity laminate against something solid
2. Bag the deck, **hand-consolidate the cavity** (walls aren't carrying deck loads)
3. Skin the faces first, cut and glass the cavity as a secondary operation

**Practice first.** Bag two or three flat scrap panels before touching the real board — learn leak-checking, corner pleating, and timing on something disposable.

---

## What Gets CNC'd

| Part | Stock | Notes |
|---|---|---|
| Board core | High-density EPS blank ~1600×600×120 mm | Full 3D shape + cavity + **milled inside radii** + hardpoint pockets. 1600 mm overruns most hobby routers — needs the makerspace's large router, milling in halves, or a job shop. |
| Cavity plug/caul | MDF (reusable) or foam | Milled from the same file, offset for release film |
| G10 hardpoints | 1/4" G10/FR4 sheet | Mast plate, panel rim ring, insert pads. Small flat 2D profiles — could be hand-cut with a jigsaw and file. **Abrasive dust, respirator required, carbide only.** |
| O-ring groove in the panel rim | — | **Highest-value CNC operation in the build.** A hand-cut groove won't have consistent depth, and consistent depth is exactly what makes a grooved O-ring seal work. |

**Still hand-done:** enclosure boxes (keep 3D printing — printed sealed geometry is genuinely good and V1's worked perfectly), and all final fairing.

---

## Materials

| Material | Purpose |
|---|---|
| **G10 / FR4** | Fiberglass-epoxy laminate sheet. Replaces plywood as the hardpoint material — dimensionally stable, doesn't absorb water, holds threads far better than ply, and bonds chemically into the layup. "Plywood's job, done by something that doesn't swell, crush, or rot." |
| **PVC structural foam** (Divinycell H60–H80, Airex, Corecell) | Closed-cell core for the lid and sandwich areas. Won't absorb water even if the skin is breached — the opposite of V1's XPS. H100+ locally where fasteners clamp. |
| **High-density EPS** | Board core. Epoxy only. |
| E-glass 6 oz + 1708 biax | Skins |

**Principle:** sandwich construction with closed-cell cores, and **solid hardpoints only where fasteners and loads land.** Thin skins provide stiffness, core provides thickness (stiffness scales with the cube of thickness), G10 takes point loads. Dramatically lighter than plywood everywhere, and stiffer where it counts.

---

## Hull Architecture

**Sealed monocoque with two openings, sized by how often they're used.**

### Service panel (opens ~twice a season)
- Bolted, flush, **O-ring in a machined groove**
- 8–10 bolts into threaded inserts set in a **G10 rim laminated in during layup**
- Fender washers under every head
- Panel is a glass/PVC-foam sandwich — stiff enough not to bow between bolts
- Positioned over the battery so a pack swap doesn't mean disassembling the board
- All bolt bores and the opening's cut edge sealed with neat epoxy

### Interface door (opens every charge)
- Small spring-open weatherproof door (marine/powersports panel)
- **Charge port** — low current (~5 A), so this is the easy connector. Waterproof marine/industrial or magnetic. **The connector is the water barrier, not the door** — the board must stay watertight with the door hanging open in the rain.
- **Magnetic switch** — reed or hall sensor bonded *behind* the laminate. Zero penetration. Strictly better than any physical switch.

### Pressure vent
Design the boss for a Gore-Tex equalisation vent even if one isn't fitted initially. A sealed air volume going from a hot deck to cold water sees a real pressure differential that acts on the weakest seal, and drives condensation. Five-minute retrofit if the mounting is already there; a redesign if it isn't.

### Mast penetration
**Don't redesign what worked.** V1's neoprene gasket under the plate with undersized collar holes passed its submersion test. Carry it over.

---

## Powertrain Direction

**Higher voltage is the natural move** — at the same power, more volts means less current, which means less heat, thinner wire, less nickel, and a simpler pack.

Constraints to design around:
- The 75200 Pro tops out around 84 V (20S), so 16S–18S is the practical ceiling on the current ESC. Beyond that needs a different ESC.
- Cell count change means a new BMS, new charger, new balance leads — fine, since V2 gets a fresh pack anyway.
- Diminishing returns above ~16S for a lot of 65161 builds. DutchFoiler ran 15S to ~50 km/h before moving to 16S. Worth asking him about the real 15S→16S delta.
- Higher voltage is less forgiving — insulation, service disconnect, and precharge discipline all matter more.

**Order of decisions:** target speed and ride feel → wing → prop → RPM → voltage → ESC → pack. Voltage is a means, not the goal.

**Let V1 data drive it.** Log real current, temps, and speed vs throttle across a season, then spec V2 off numbers instead of guesses.

---

## Deferred: Hot-Swap Battery

Considered and set aside. The reasoning is worth keeping.

**Why it's attractive:** hot-swapping packs between rental laps, charging off-board on a rack. This is the feature that makes a high-volume rental operation work.

**Why it's deferred:** the hard part isn't the pack, it's **sealing a wet-mateable 100 A connector.** That's the single most novel, expensive engineering problem in the whole concept (Surlok/Amphenol territory — SB50 is only ~50 A continuous and too light). By contrast, a **charge port is ~5 A**, which is trivially easy to seal. Trading the hardest connector on the board for one of the easiest is a very good trade.

**Sequencing, not abandonment:** charge-in-place for the weekend-lessons launch, where boards charge overnight on a rack. Revisit hot-swap only if rental volume actually demands the turnaround. If it ever does, **prototype the dock and connector as a standalone rig before committing it to hull CAD** — it constrains everything around it.

---

## Finish

Target: glass-smooth epoxy under clear.

1. Peel ply the whole layup — uniform matte surface with tooth, and it pulls excess resin
2. Fill/high-build coat thick enough to sand flat **without ever touching fibre** (sand into the glass and it's unrecoverable)
3. Wet sand 400 → 800 → 1200 → 2000 on a block
4. 2K automotive clear, or compound and polish

**Kill print-through** — it's the #1 DIY tell. Beat it with a surfacing layer, a thin and consistent layup, a proper **post-cure before finishing** (so shrinkage happens before you make the surface perfect, not after), and enough surface coat to sand flat.

Note: the boards that look spectacular on foil.zone (e.g. SlipHazard) are **carbon under clear** — the "wow" is the weave itself. That look is not achievable with paint on glass, and it's a different target from a well-finished glass board.

---

## Rough Budget (board only, reusing V1 powertrain)

| Category | Cost |
|---|---|
| EPS blank + CNC milling | $230–550 |
| PVC foam core (quarter sheet H80) | $110–135 |
| G10/FR4 sheet | $60–100 |
| E-glass + biax | $180–270 |
| Epoxy (~3 gal) + fillers | $390–490 |
| Vacuum pump + consumables + practice panels | $310–520 |
| Hardware, O-ring stock, charge connector, access door, reed/magnet, sealants | $195–250 |
| Finishing (paper, 2K clear, traction pad) | $150–240 |
| **Total** | **~$1,600–2,600** (mid ≈ $2,000) |

Fresh higher-voltage powertrain would add roughly **$1,500–2,000** on top.

**Biggest cost swing is CNC** — makerspace self-serve vs. job shop is most of the range.

---

## Fleet Consideration (later)

Once V2.0 proves the shape and systems, the economics shift to a **female mold**: CNC a plug or mill the mold directly, then lay up into it. Two payoffs — the mold surface becomes the part surface (gloss straight out of the bag, no fill-and-sand marathon per board), and layup time per unit drops hard. Real capital step; only worth it across a fleet.

---

## Open Questions

- Does the makerspace have a router that handles a 1600 mm core, and a spindle suitable for foam?
- What's the actual speed target — and is it for personal riding or beginner-safe rental laps? These pull in opposite directions.
- Does V1's thermal data justify a different ESC, or is the 75200 fine at 16S?
- Serviceable-panel vs. truly sealed: for a **rental fleet**, a board that can't be opened is a board that gets scrapped instead of repaired. Bolted panel is the safer call.
