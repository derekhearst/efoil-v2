# eFoil V2 - full bill of materials

For **2 boards**, 1 pack of cells already on hand. Regenerate with `python model/bom.py 2`.

Sheet counts come from the live cut list and fastener counts from the model, so they cannot drift from the design. `verified` means read off the supplier's page or your own receipt; `estimate` means my number.

## 1  Core and shaping

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| EPS rigid foam 2in x 48in x 8ft (HD 202532856) | 3 | sheet | $27.68 | $83.04 | verified | HD Meridian, 30 in stock, aisle 29 bay 020; $23.53 at 32+. EPS, not the XPS V1 used - deliberate, ~$90 cheaper across both boards, and the shear it gives up is covered by H-80 at the hardpoints. See the note at RHO_EPS in blender_board.py |
| PL300 / Gorilla Glue, layer glue-up | 2 | tube | $8.00 | $16.00 | estimate |  |
| Maker Shop Boise Basic month | 1 | month | $150.00 | $150.00 | verified | month-to-month; confirm it cancels cleanly |
| **subtotal** | | | | **$249.04** | | |

## 2b Aluminium

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| 5052 1/8in x 12 x 24, 2-pack - module floors | 1 | pk | $61.99 | $61.99 | verified | your Apr 2026 receipt (MorningRo/Huaiian). One sheet is one floor, so this pack does both boards |
| 6061-T651 1/2in x 12 x 18 - mast plates | 1 | sheet | $88.92 | $88.92 | verified | speedymetals.com 61p.5; both plates nest, 2 x 6.89in of 18, 4.2 spare. Saw-cut edge, +/-1/4in - profile it yourself |
| **subtotal** | | | | **$150.91** | | |

## 3  Structural foam

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| Divinycell H-100 1/4in quarter 21x42, hatch lid cores - 2 sheets bonded to 1/2in | 2 | sheet | $49.59 | $99.18 | verified | fiberglasssupply.com; no 1/2in H-100 is made |
| Divinycell H-80 1/4in quarter 24x48, module lid cores | 1 | sheet | $53.94 | $53.94 | verified | L18-1070; nobody stands on this one |
| Divinycell H-80 3/4in quarter sheet 24x48, mast block + leash pad | 1 | sheet | $100.26 | $100.26 | verified | L18-1112, 24x48. Was 2 sheets when it carried 2 shear ribs |
| **subtotal** | | | | **$253.38** | | |

## 4  Laminate

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| E-glass 6 oz, 50in x 12ft, 2-pack | 2 | pack | $19.07 | $38.14 | verified | your receipt |
| 1708 biax, 50in wide | 6 | yd | $12.50 | $75.00 | verified |  |
| TotalBoat 5:1 gallon kit, slow hardener | 2 | kit | $159.99 | $319.98 | verified | 2.51 m2 laminate = 4.8 kg mixed = 1 kit/board |
| TotalBoat 5:1 quart kit, fillets and bonding | 1 | kit | $68.99 | $68.99 | verified |  |
| TotalBoat silica thickener, large | 1 | ea | $27.99 | $27.99 | verified | fillets and structural bonding |
| **subtotal** | | | | **$530.10** | | |

## 5  Vacuum bagging

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| Pittsburgh 3 CFM 2-stage pump (HF 61176) | 1 | ea | $139.99 | $139.99 | verified | one-time |
| VR20 vacuum regulator | 1 | ea | $52.00 | $52.00 | verified | one-time |
| Bagging starter kit - film, peel ply, tape, breather, connector | 1 | kit | $127.40 | $127.40 | verified | one-time + first board |
| Vac bag film, 5 yd | 1 | roll | $24.95 | $24.95 | verified |  |
| Breather / bleeder cloth | 4 | yd | $13.95 | $55.80 | verified |  |
| Low-temp release film | 4 | yd | $11.28 | $45.12 | verified |  |
| **subtotal** | | | | **$445.26** | | |

## 6  Hatch and seal

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| Solid silicone cord, 3 mm round - BOTH seals | 8 | m | $2.00 | $16.00 | estimate | buy long - splice on a straight run, never a corner |
| Silicone adhesive, bonding the cord into groove | 1 | tube | $12.00 | $12.00 | estimate | a thin continuous bead under the cord. It cannot then migrate, lift out, or be pinched under the lid in a dark car park |
| M5 x 16 A4 stainless socket cap | 24 | ea | $0.55 | $13.20 | estimate |  |
| REMOVED - M5 wire-thread insert, 50 pc | 1 | pack | $24.00 | $24.00 | estimate | 24 needed |
| M5 A4 hex nut, CAPTIVE - printed into the ring | 34 | ea | $0.22 | $7.48 | estimate | dropped in at a print pause at Z=6.0; steel thread, so a hatch that comes off every ride never wears anything out |
| REMOVED - M5 STI tap + tangless tool | 1 | set | $38.00 | $38.00 | estimate | one-time; the STI tap is oversize and a normal M5 tap will NOT do |
| MDF 12 mm, full template set (14 templates) | 2 | sheet | $35.00 | $70.00 | estimate | one-time; cut once, used on both boards and any future one |
| **subtotal** | | | | **$180.68** | | |

## 7  Module

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| M4 x 12 A4 stainless socket cap | 36 | ea | $0.35 | $12.60 | estimate |  |
| M4 A4 washer O9, 100 pk | 1 | pk | $8.00 | $8.00 | estimate | 36 needed, under every lid bolt |
| M4 x 8 brass heat-set insert, 100 pc | 1 | pack | $12.00 | $12.00 | estimate | 36 needed; 5.6 mm printed pilot |
| ASA filament, printed rim ring | 2 | kg | $24.00 | $48.00 | estimate | 6 dovetailed pieces/board at ~90% infill, 710 g of part each; PRINT SEAL FACE DOWN - the bed is flatter than any top surface |
| Acetone, solvent-welding the printed joints | 1 | qt | $14.00 | $14.00 | estimate | ASA dissolves in it like ABS - a brushed acetone/scrap slurry makes the joint one piece of plastic, not an adhesive line |
| ASA filament, printed module shell | 3 | kg | $24.00 | $72.00 | estimate | 4 L-pieces/board, ~1.13 kg of part + supports and brim; largest piece 226 x 146 fits the A1 bed |
| Neoprene sheet 1/8in, module + mast gaskets | 1 | sheet | $16.00 | $16.00 | estimate | TORRAMI 18x24 or similar - you kept a part sheet from V1 |
| PG11 cable gland IP68, 10 pk | 1 | pk | $9.99 | $9.99 | verified | 6 needed; one wire per gland - three in one gland deforms the insert into a clover and leaks between them |
| EPDM/neoprene sheet 1/2in, conduit bungs | 1 | sheet | $14.00 | $14.00 | estimate | cut O33 plugs for a O32 bore, punch 3 x O5 for 6.5 mm lead - interference fit, soap them through |
| 3M 4200 FC, fillet over the bung | 1 | tube | $18.00 | $18.00 | estimate | does both boards; 4200 NOT 5200 - 5200 never comes out |
| 25 mm webbing loop, module lift handle | 2 | ea | $6.00 | $12.00 | estimate | through the two printed bosses on the forward wall - the module is ~14 kg in a cavity with 12 mm of side clearance, so there is no way to get a hand beside it |
| M12 IP68 membrane vent plug | 2 | ea | $9.95 | $19.90 | verified | NOT optional on a sealed lithium box |
| M12 IP68 momentary panel button | 1 | ea | $12.49 | $12.49 | verified | 1 on hand; this line buys the second board's |
| SP17 2-pin IP68 flange receptacle + cap | 2 | ea | $11.00 | $22.00 | estimate | 67.2 V 5 A charge; O17 panel hole, 2 x M3 flange screws |
| M3 heat-set insert + M3 x 8 A4, port flange | 4 | set | $0.60 | $2.40 | estimate |  |
| **subtotal** | | | | **$293.38** | | |

## 8  Mast hardpoint

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| M8 x 1.25 tap set + 6.8 mm drill | 1 | set | $18.00 | $18.00 | estimate | 8 blind holes; a BOTTOMING tap is the one that matters - blind at 10 mm in a 12.7 plate |
| Tef-Gel or Duralac, galvanic barrier | 1 | ea | $22.00 | $22.00 | estimate | every mast bolt, every time it goes back in |
| **subtotal** | | | | **$40.00** | | |

## 9  Electrical

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| Flipsky 65161 120KV motor | 2 | ea | $298.00 | $596.00 | verified |  |
| Flipsky 75200 Pro V2 ESC | 2 | ea | $150.00 | $300.00 | verified |  |
| Flipsky VX3 remote | 2 | ea | $71.00 | $142.00 | verified |  |
| DALY Smart BMS Li-ion 16S 60V 150A | 2 | ea | $159.00 | $318.00 | verified | batteryint.com; confirm it is <= 164 x 66 x 21 mm |
| Charger 67.2 V 5 A, 16S  (NOT 58.8 V) | 2 | ea | $45.99 | $91.98 | verified | Amazon B0DK6FTB1P, aluminium case + fan |
| BAK N21700CG-50, 130-cell case (BatteryHookup) | 1 | case | $260.00 | $260.00 | verified | new overstock |
| BAK N21700CG-50 singles, spares | 15 | ea | $2.50 | $37.50 | verified | 7% margin on a spot-welded pack |
| 21700 cells already on hand | 128 | ea | $0.00 | $0.00 | on hand |  |
| Pure nickel 0.2 x 10 mm, 5 m roll | 4 | roll | $14.83 | $59.32 | verified |  |
| 21700 spacer brackets | 0 | set | $0.00 | $0.00 | on hand |  |
| ANL 150 A fuse + holder | 2 | ea | $10.59 | $21.18 | verified |  |
| 8 AWG silicone wire, 5 m red + 5 m black | 2 | set | $22.00 | $44.00 | estimate | motor supplies its own phase leads + bullets |
| Heat shrink, Kapton, pack wrap | 2 | set | $18.00 | $36.00 | estimate |  |
| **subtotal** | | | | **$1,905.98** | | |

## 9b Small but essential

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| Capacitor spot welder | 1 | ea | $0.00 | $0.00 | on hand | used on V1 |
| M8 x 30 A4 mast bolts, spares | 8 | ea | $0.90 | $7.20 | estimate | Gong supplies its own; these are spares |
| Silicone grease for the seal cord | 1 | tube | $9.00 | $9.00 | estimate | stops the cord bonding to the lid in storage |
| Cyanoacrylate for the cord splice | 1 | ea | $6.00 | $6.00 | estimate |  |
| Water-ingress alarm | 2 | ea | $12.00 | $24.00 | estimate | V1 carried one - finds a leak before the cells do |
| Coiled ankle leash | 2 | ea | $14.99 | $29.98 | verified | you trust the remote failsafe; this is so the board stays with you |
| FCS-pattern leash plug | 2 | ea | $9.00 | $18.00 | estimate |  |
| Kayak-style webbing carry handle, 4 pk | 1 | pk | $13.89 | $13.89 | verified | 4 needed; 2 x M6 into the 6061 strip in the rail pocket |
| M6 x 16 A4 + M6 insert, strap mounts | 8 | set | $1.40 | $11.20 | estimate |  |
| **subtotal** | | | | **$119.27** | | |

## 9c Pack wiring

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| Solder + flux, bus bars and jumpers | 0 | set | $0.00 | $0.00 | on hand | on hand from V1; only the ring lugs and balance leads need it now - the bridges are welded, not soldered |
| Balance harness, 17-wire | 2 | ea | $0.00 | $0.00 | on hand | DALY ships one - CONFIRM before you need it |
| 16 AWG wire, charge port and power button runs | 2 | set | $9.00 | $18.00 | estimate |  |
| Dielectric grease, terminals | 1 | tube | $8.00 | $8.00 | estimate |  |
| Cable ties, lacing, adhesive mounts | 2 | set | $11.00 | $22.00 | estimate |  |
| Silicone sealant, BMS anti-vibration dabs | 1 | tube | $7.00 | $7.00 | estimate | V1 did this; stops the BMS walking |
| CESFONJER IP68 M25 inline housing, 3 pk | 2 | pk | $15.00 | $30.00 | estimate | 3 per board, one per phase; SIZE UNVERIFIED - Amazon blocks scraping. Check they fit the 60 x 318 bay before ordering wire |
| 5.5 mm bullets + adhesive shrink, ESC side | 2 | set | $12.00 | $24.00 | estimate | motor pigtails arrive with their own |
| Fish tape / pull cord for the mast conduit | 1 | ea | $12.00 | $12.00 | estimate |  |
| **subtotal** | | | | **$121.00** | | |

## 10 Foil

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| Gong Foil Setup X-Over V3 Atmo Perf Series - XL, Alu 85 | 2 | ea | $694.00 | $1,388.00 | verified | complete: FW + matched stab + V3 alu 85/17 mast + V3 MFC + fuselage + V3 top plate + all screws + foil bag. Current range, not end-of-line like the non-Atmo V3 |
| Gong shipping to Idaho, per foil | 2 | ea | $124.00 | $248.00 | verified | 115.50 EUR on order 252112; charged per ORDER, so putting both boards' foils in ONE order saves about $124 |
| **subtotal** | | | | **$1,636.00** | | |

## 10b Drivetrain

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| PETG filament 1 kg, mast clamp set | 2 | kg | $9.99 | $19.98 | verified | 4 STEP files; 0.6 nozzle, 5 perims, 40% infill |
| M5 x 250 threaded rod (cut to ~171 mm) | 8 | ea | $2.20 | $17.60 | estimate | dry-assemble and mark before cutting all four |
| M5 nyloc nut + M6 x 20 fender washer | 8 | set | $0.60 | $4.80 | estimate |  |
| M3 x 6 button head + M3 brass heat-set, nose cone | 8 | set | $0.50 | $4.00 | estimate |  |
| Loctite 242 | 1 | ea | $9.00 | $9.00 | estimate | rod ends into the motor only - nyloc end does not need it |
| PETG for props, 4-5 spares per board | 2 | kg | $9.99 | $19.98 | verified | 0.4 nozzle, 100% infill; balance-check on a bolt, then epoxy-coat - V1 skipped the coat and layer lines cost drag |
| Stainless roll pin, drive pin | 4 | ea | $1.50 | $6.00 | estimate | MEASURE the shaft cross-hole - do not trust the 4 mm figure |
| M8 nyloc + washer, prop nut | 2 | set | $1.50 | $3.00 | estimate |  |
| 8 AWG marine ring lugs, 20 pk | 2 | pk | $16.99 | $33.98 | verified | 28 needed; on M6 studs - nothing to solder |
| M6 stainless stud/busbar hardware | 2 | set | $14.00 | $28.00 | estimate |  |
| Hydraulic lug crimper, 6-70 mm2 | 1 | ea | $38.00 | $38.00 | estimate | one-time; this is what replaces soldering XT150s |
| Adhesive-lined heat shrink, assorted | 1 | kit | $16.00 | $16.00 | estimate |  |
| **subtotal** | | | | **$200.34** | | |

## 10c Restraint & fitout

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| G10 chocks, equipment plate, pack tabs | 0 | off | $0.00 | $0.00 | on hand | cut from 1/8 and 1/2 in offcuts |
| 25 mm webbing + ladder-lock buckles | 2 | set | $20.00 | $40.00 | estimate | 2 straps per board |
| EVA bedding pads | 2 | set | $12.00 | $24.00 | estimate |  |
| **subtotal** | | | | **$64.00** | | |

## 10d Shop consumables

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| Spray adhesive + sacrificial MDF, CNC hold-down | 1 | set | $35.00 | $35.00 | estimate | foam is taped down, not clamped |
| Release wax / PVA for the cavity caul | 1 | set | $20.00 | $20.00 | estimate |  |
| Spare vacuum bagging film | 1 | roll | $40.00 | $40.00 | estimate | a bag that leaks mid-cure ends the session |
| EPS offcut for a CNC test piece | 1 | ea | $15.00 | $15.00 | estimate | prove CAM, workholding and the flip before a real core |
| Dowel pins + drill, two-sided registration | 1 | set | $12.00 | $12.00 | estimate |  |
| 1/2 in single-flute + 1/2 in ball nose | 1 | set | $70.00 | $70.00 | estimate | if the shop does not have foam-suitable tooling |
| Compact router kit, fixed + plunge bases | 1 | ea | $169.00 | $169.00 | estimate | DWP611PK class; PRICE UNVERIFIED - retailers bot-block scraping, check before ordering |
| 1/4in carbide bits + guide bushings | 1 | set | $60.00 | $60.00 | estimate | flush trim, straight, roundover; CARBIDE - G10 destroys HSS. NOT the same bits as the 1/2in CNC line above |
| **subtotal** | | | | **$421.00** | | |

## 10e Layup kit

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| TotalBoat flexible spreader set | 2 | set | $5.99 | $11.98 | verified |  |
| Chip brushes and laminating roller | 1 | set | $22.00 | $22.00 | estimate |  |
| Nitrile gloves, 100 pk | 2 | box | $12.00 | $24.00 | estimate |  |
| Respirator | 1 | ea | $0.00 | $0.00 | on hand |  |
| 3M 60923 organic vapour / acid gas P100, pair | 2 | pr | $31.49 | $62.98 | verified | envirosafetyproducts.com; cartridges expire - buy near the layup |
| Acetone, 1 gal, cleanup | 1 | gal | $39.95 | $39.95 | verified |  |
| Plastic sheeting + masking tape, bench protection | 1 | set | $20.00 | $20.00 | estimate |  |
| Sanding blocks + longboard for fairing | 1 | set | $30.00 | $30.00 | estimate |  |
| **subtotal** | | | | **$210.91** | | |

## 11 Finishing

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| TotalBoat TotalFair epoxy fairing compound | 2 | kit | $45.99 | $91.98 | verified | smallest kit, one per board |
| TotalBoat Premium Marine Topside Primer | 1 | kit | $46.99 | $46.99 | verified | one covers both |
| TotalBoat Wet Edge topside paint, colour | 2 | kit | $53.99 | $107.98 | verified | one-part polyurethane, quart |
| Traction pad, 3-piece | 2 | set | $24.95 | $49.90 | verified |  |
| Abrasives, cups, gloves, tape | 2 | set | $40.00 | $80.00 | estimate |  |
| **subtotal** | | | | **$376.85** | | |

## 12 Freight and tax

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| Shipping - G10, Divinycell, epoxy hazmat | 1 | allow | $220.00 | $220.00 | estimate | heavy and hazmat lines |
| Idaho sales tax, 6% (Ada County, no local) | 1 | allow | $445.09 | $445.09 | verified |  |
| **subtotal** | | | | **$665.09** | | |

## Totals

| | |
|---|---:|
| **Grand total, 2 boards** | **$7,863.19** |
| Per board | $3,931.59 |
| Of which verified | $6,091.71  (77%) |
| Of which estimated | $1,771.48 |

## What is a board, and what is a shop

Some of the total above is not the cost of a board at all - it is tools, jigs and templates that exist afterwards and do not repeat. Splitting them out is the difference between "a board costs $3,932" and "a board costs $3,407 and I now own a vacuum rig, a crimper and a full template set".

| | |
|---|---:|
| One-time tooling (incl. its share of tax) | $1,048.75 |
| **Marginal cost of a board** | **$3,407.22** |
| Cost of the NEXT board after these 2 | $3,407.22 |

| One-time item | $ |
|---|---:|
| Maker Shop Boise Basic month | $150.00 |
| Pittsburgh 3 CFM 2-stage pump (HF 61176) | $139.99 |
| VR20 vacuum regulator | $52.00 |
| Bagging starter kit - film, peel ply, tape, breather, connector | $127.40 |
| REMOVED - M5 STI tap + tangless tool | $38.00 |
| MDF 12 mm, full template set (14 templates) | $70.00 |
| M8 x 1.25 tap set + 6.8 mm drill | $18.00 |
| Hydraulic lug crimper, 6-70 mm2 | $38.00 |
| EPS offcut for a CNC test piece | $15.00 |
| Dowel pins + drill, two-sided registration | $12.00 |
| 1/2 in single-flute + 1/2 in ball nose | $70.00 |
| Compact router kit, fixed + plunge bases | $169.00 |
| 1/4in carbide bits + guide bushings | $60.00 |
| Sanding blocks + longboard for fairing | $30.00 |
