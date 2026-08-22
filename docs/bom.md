# eFoil V2 - full bill of materials

For **2 boards**, 1 pack of cells already on hand. Regenerate with `python model/bom.py 2`.

Sheet counts come from the live cut list and fastener counts from the model, so they cannot drift from the design. `verified` means read off the supplier's page or your own receipt; `estimate` means my number.

## 1  Core and shaping

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| [EPS rigid foam 2in x 48in x 8ft (HD 202532856)](https://www.homedepot.com/p/Henry-2-in-x-48-in-x-8-ft-R-7-7-EPS-Rigid-Foam-Board-Insulation-320825/202532856) | 4 | sheet | $27.68 | $110.72 | verified | HD Meridian, 30 in stock, aisle 29 bay 020; $23.53 at 32+. EPS, not the XPS V1 used - deliberate, ~$90 cheaper across both boards, and the shear it gives up is covered by H-80 at the hardpoints. See the note at RHO_EPS in blender_board.py |
| [PL300 / Gorilla Glue, layer glue-up](https://www.amazon.com/dp/B0009XEGVC) | 2 | tube | $6.59 | $13.18 | estimate |  |
| [Maker Shop Boise Basic month](https://www.makershopboise.com/membership) | 1 | month | $150.00 | $150.00 | verified | month-to-month; confirm it cancels cleanly. Only ONE part truly wants a CNC - the EPS core - but the pass covers the lids and the MDF gauges too, so cut everything inside the 30 days and let the layups follow the weather afterwards |
| **subtotal** | | | | **$273.90** | | |

## 2b Aluminium

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| [5052 1/8in x 12 x 24, 2-pack - module floors](https://www.amazon.com/dp/B0D3TH4TTC) | 1 | pk | $61.99 | $61.99 | verified | your Apr 2026 receipt (MorningRo/Huaiian). One sheet is one floor, so this pack does both boards |
| [6061-T651 1/2in x 12 x 18 - mast plates](https://www.speedymetals.com/pc-2411-8360-12-6061-t651-aluminum-plate.aspx) | 1 | sheet | $88.92 | $88.92 | verified | speedymetals.com 61p.5; both plates nest, 2 x 6.89in of 18, 4.2 spare. Saw-cut edge, +/-1/4in - profile it yourself |
| **subtotal** | | | | **$150.91** | | |

## 3  Structural foam

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| [Divinycell H-100 1/4in quarter 21x42, hatch lid cores - 2 sheets bonded to 1/2in](https://fiberglasssupply.com/1-4-in-h-100-divinycell-quarter-sheet-21-x-42/) | 2 | sheet | $49.59 | $99.18 | verified | fiberglasssupply.com; no 1/2in H-100 is made |
| [Divinycell H-80 1/4in quarter 24x48, module lid cores](https://fiberglasssupply.com/quarter-sheet-1-4-h-80-divinycell-plain-sheet/) | 1 | sheet | $53.94 | $53.94 | verified | L18-1070; nobody stands on this one |
| [Divinycell H-80 3/4in quarter sheet 24x48, mast block + leash pad](https://fiberglasssupply.com/quarter-sheet-3-4-h-80-divinycell-plain-sheet/) | 1 | sheet | $100.26 | $100.26 | verified | L18-1112, 24x48. Was 2 sheets when it carried 2 shear ribs |
| **subtotal** | | | | **$253.38** | | |

## 4  Laminate

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| [E-glass 6 oz, 50in x 12ft, 2-pack](https://www.amazon.com/dp/B0CQY5KX84) | 2 | pack | $19.99 | $39.98 | verified | your receipt |
| [1708 biax, 50in x 10 yd roll](https://www.amazon.com/dp/B07RJWHPKG) | 1 | roll | $79.95 | $79.95 | verified | 6 yd needed across both boards; $8.00/yd against Fibre Glast's $12.50 and no freight |
| [TotalBoat 5:1 FAST hardener 6 oz, cold days](https://www.amazon.com/dp/B00HRHA59K) | 1 | ea | $27.99 | $27.99 | verified | min 40-45 F against slow's 60. In a cold shop this is the one that cures, and the cold gives the pot life back. 6 oz catalyses ONE QUART of resin, which is about a single hull session - if the shop turns out to be cold for the whole build, the 25 oz at $61.99 does a full gallon and is the cheaper way to get there |
| [TotalBoat 5:1 gallon kit, slow hardener](https://www.amazon.com/dp/B00HR8515C) | 2 | kit | $149.99 | $299.98 | verified | 2.51 m2 laminate = 4.8 kg mixed = 1 kit/board |
| [TotalBoat 5:1 quart kit, fillets and bonding](https://www.amazon.com/dp/B00HR8517A) | 1 | kit | $58.99 | $58.99 | verified |  |
| Fumed silica thickener | 0 | off | $0.00 | $0.00 | on hand | plenty on hand from V1 |
| **subtotal** | | | | **$506.89** | | |

## 5  Vacuum bagging

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| [VECOTOOLS 4.5 CFM single-stage pump, oil incl.](https://www.amazon.com/dp/B0GZVLP3PL) | 1 | ea | $57.99 | $57.99 | verified | your listing, ASIN B0GZVLP3PL. Was a $139.99 Pittsburgh 2-stage plus $15 of oil - $97 for ultimate vacuum we must not use |
| [VR20 vacuum regulator](https://www.easycomposites.us/vacuum-regulator-for-vacuum-bagging) | 1 | ea | $52.00 | $52.00 | verified | one-time. Holds the bag at 5-10 inHg, which is the whole ball game: EPS crushes around 150 kPa and full vacuum is 101. Hose tails are +$4.70 if you want them |
| [Bag connector w/ ball valve, 1/4 in QD](https://www.amazon.com/dp/B0FSKGGL8H) | 2 | ea | $19.59 | $39.18 | verified | THE BALL VALVE IS THE POINT: shut it and the bag is isolated from the pump, so leak-down is a real measurement and not a guess about whether the pump is keeping up. Two of them - a 1400 mm hull bag pulls down far faster from both ends, and one is a spare |
| [Vacuum hose + hose clamps](https://www.amazon.com/dp/B0FH52FT4G) | 1 | set | $11.61 | $11.61 | estimate | 1/2 in tubing pump-to-bag plus clamps; the other half of what the deleted kit was actually carrying |
| [Test cap + tubing, module leak test](https://www.amazon.com/dp/B0DPWRP6FR) | 1 | set | $22.99 | $22.99 | estimate | PROVE THE MODULE BEFORE THE CELLS GO IN, and prove it the way the failure actually happens: run one of the kit's smaller hoses through an empty PG11 gland and tighten it - that is your test port - blank the other glands and the vent boss, seal it empty, pull 5 inHg, shut the ball valve and watch the gauge for 30 min - porosity reads as a slow bleed. Then do it again SUBMERGED: under vacuum any path pulls water IN and you see exactly where. V1 found its leaks by riding |
| [Vacuum gauge, -30 inHg, 1/4 NPT, glycerin](https://www.amazon.com/dp/B00VQSOZFQ) | 1 | ea | $10.50 | $10.50 | verified | reads the BAG, not the pump - tee it in at the bag end. The regulator sets the level; this is how you know it worked. GLYCERIN FILLED on purpose: a dry needle flutters with every pump stroke and you cannot read 7 inHg off it, which is the one number that matters |
| [Vac bag film, 5 yd](https://www.amazon.com/dp/B079MBL5TX) | 3 | roll | $24.95 | $74.85 | verified | 3.06 m2 a hull session; 2 hulls + 4 lids + a practice piece + one re-do. Single-use on the hull, reusable on flat parts. Same Elite Lab product Fibre Glast sells, at the same price, with free delivery |
| [Peel ply, 60in](https://www.amazon.com/dp/B0H5JTMTZ3) | 6 | yd | $18.99 | $113.94 | verified | was only in the starter kit, and one kit's worth does not cover 6.12 m2 of part |
| [Breather / bleeder cloth](https://www.amazon.com/dp/B015NM0B8K) | 6 | yd | $13.95 | $83.70 | verified | $13.95/yd cut; a 5 yd roll at $59.99 is $12.00/yd if you would rather buy the roll |
| [Sealant tape, 50 ft roll](https://www.amazon.com/dp/B0GF25BPN6) | 2 | roll | $19.99 | $39.98 | verified | 31 m of bag perimeter across the project. 2 x 50 ft at $19.99 replaced 4 x 25 ft at $12 - same tape, fewer joins |
| **subtotal** | | | | **$506.74** | | |

## 6  Hatch and seal

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| Neat epoxy, sealing every cut laminate edge | 0 | off | $0.00 | $0.00 | on hand | off the laminating kit. Groove walls, lid perimeter, all 12 lid bores, every machined edge. This is V1's Test 2 verbatim - water came in through unsealed fibre ends at the cavity ledge, and its own note reads: cured laminate is NOT waterproof at a cut edge |
| [Solid silicone cord, 1/8 in (3.175 mm) - the spare size](https://www.amazon.com/dp/B00QVB0KE8) | 1 | pc | $15.39 | $15.39 | verified | 10 ft piece, 70A. Fitted ONLY if the routed groove measures deep. Gives 24% squeeze at the nominal 2.4 depth and 15% at a bad 2.7 - the true 3.5 mm that would give 23% at 2.7 is an industrial-supply size, so if the groove really comes out at 2.7 the answer is to fix the groove, not to chase cord |
| [Solid silicone cord, 3 mm round - BOTH seals](https://www.amazon.com/dp/B096N67R2D) | 2 | pc | $17.59 | $35.18 | verified | 10 ft (3.05 m) pieces, 70A. Buy long - splice on a straight run, never a corner |
| [Paste wax, releasing the groove filler](https://www.amazon.com/dp/B0GVCGHZFR) | 1 | ea | $16.99 | $16.99 | estimate | the filler must NOT bond - it comes back out after the glass goes over it |
| [2.5 mm straight cutter - fallback](https://www.amazon.com/dp/B0GWSZ2KV2) | 1 | ea | $7.99 | $7.99 | estimate | only if you would rather cut the groove open than sand down to a proud filler strip. Undersize in a 4 mm groove on purpose |
| [Silicone adhesive, bonding the cord into groove](https://www.amazon.com/dp/B0002UEN1U) | 1 | tube | $7.56 | $7.56 | estimate | a thin continuous bead under the cord. It cannot then migrate, lift out, or be pinched under the lid in a dark car park |
| [M5 x 25 A4 socket cap, 20 pk](https://www.amazon.com/dp/B0CJFMMF58) | 2 | pk | $15.99 | $31.98 | verified | 24 needed. A4/316 - every cheaper listing is A2/304, which pits in salt water |
| [M5 penny washer O15 DIN9021, 150 pk](https://www.amazon.com/dp/B0G58KQN6L) | 1 | pk | $7.99 | $7.99 | verified | 34 needed. DIN9021 is what confirms the large 15 mm OD. Goes in at the SAME print pause as the nut, underneath it |
| [M5 A4 hex nut DIN934, 50 pk - CAPTIVE in the ring](https://www.amazon.com/dp/B084HLMN7B) | 1 | pk | $9.19 | $9.19 | verified | 34 needed. Dropped in at a print pause at Z=6.0; steel thread, so a hatch that comes off every ride never wears anything out |
| [MDF 12 mm, 4 check gauges](https://www.homedepot.com/p/ProWood-1-2-in-x-2-ft-x-4-ft-Medium-Density-Fiberboard-Project-Panel-109097/202093821) | 1 | sheet | $30.73 | $30.73 | estimate | 3 station sections + the rocker/deck profile. Was a 14-template set at $70 - the router templates go with the CNC pass. The caul is an EPS offcut and the groove guide is fallback-only, so this sheet is now the whole MDF requirement |
| **subtotal** | | | | **$163.00** | | |

## 7  Module

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| Epoxy wash coat, BOTH faces of the printed shell | 0 | off | $0.00 | $0.00 | on hand | off the laminating kit. Outside face first - that is the wet one. Keep it OFF the gasket flange and the insert faces; a soft film at a clamping surface undoes the seal geometry, which is V1's own warning about Flex Seal |
| [M4 x 12 A4 socket cap DIN912, 10 pk](https://www.amazon.com/dp/B07DVPC7HT) | 4 | pk | $7.10 | $28.40 | verified | 36 needed. A4/316 again - the $0.09/ea listings are all A2/304 |
| [M4 A4 washer, 316, 100 pk](https://www.amazon.com/dp/B0DZ5BVLP5) | 1 | pk | $6.79 | $6.79 | verified | 36 needed, under every lid bolt. NOTE the OD is 12 mm, not the 9 mm this line specced - the only 9 mm-OD listing is 304. Took the alloy over the diameter because this sits in the wet cavity; check 12 mm clears the lid pocket before ordering |
| [M4 x 8 brass heat-set insert, 100 pc](https://www.amazon.com/dp/B0D9QHBG6G) | 1 | pack | $9.99 | $9.99 | estimate | 36 needed; 5.6 mm printed pilot |
| [ASA filament, printed rim ring](https://www.amazon.com/dp/B09DKPYYBP) | 2 | kg | $24.49 | $48.98 | verified | 6 dovetailed pieces/board at ~90% infill, 710 g of part each; PRINT SEAL FACE DOWN - the bed is flatter than any top surface |
| [Acetone, solvent-welding the printed joints](https://www.homedepot.com/p/Klean-Strip-1-qt-Acetone-Thins-Fiberglass-Resins-Epoxy-and-Adhesives-QAC18/100144922) | 1 | qt | $11.48 | $11.48 | estimate | ASA dissolves in it like ABS - a brushed acetone/scrap slurry makes the joint one piece of plastic, not an adhesive line |
| [ASA filament, printed module shell](https://www.amazon.com/dp/B09DKPYYBP) | 3 | kg | $24.49 | $73.47 | verified | 4 L-pieces/board, ~1.13 kg of part + supports and brim; largest piece 226 x 146 fits the A1 bed |
| [Sikaflex-292 marine structural PU](https://www.amazon.com/dp/B008F8VYMM) | 1 | tube | $28.99 | $28.99 | verified | ~6-8 MPa vs 4200's ~2. Fillet BOTH sides of the joint - on a flexible bond the fillets are what stop it peeling |
| [Sika Aktivator-PRO 250 ml + daubers](https://www.amazon.com/dp/B0D9KTLC1M) | 1 | ea | $28.95 | $28.95 | verified | abrade + solvent wipe + activate the 5052; scuff the ASA. Aktivator-205 is DISCONTINUED - Aktivator-PRO replaces it. UPGRADE PATH: full Primer-206 G+P is the belt-and-braces answer for immersed PU on metal but is $67/250 ml on Amazon. Skipping it is defensible HERE only because the bond line is mechanically backed by the flange bolts and the gasket - not the PU - is the water barrier |
| [2 mm glass beads or shim wire, bond-line control](https://www.amazon.com/dp/B0FVSHYP99) | 1 | ea | $7.19 | $7.19 | estimate | clamping a PU joint metal-to-plastic squeezes the line out and puts you back to a rigid joint that will fail |
| [Neoprene sheet 1/8in, module + mast gaskets](https://www.amazon.com/dp/B08DLP2DBF) | 1 | sheet | $22.65 | $22.65 | estimate | TORRAMI 18x24 or similar - you kept a part sheet from V1 |
| [Gebildet PG11 gland, M18x1.5, 30 pk](https://www.amazon.com/dp/B0B8NJR62L) | 1 | pk | $9.99 | $9.99 | verified | your listing: M18x1.5 thread (matches the 18.5 hole) and 5-10 mm cable, against our 6.5 mm 8 AWG. 6 needed of 30 - one wire per gland; three in one gland deforms the insert into a clover and leaks between them |
| [EPDM/neoprene sheet 1/2in, conduit bungs](https://www.amazon.com/dp/B00P5VFKCC) | 1 | sheet | $15.77 | $15.77 | estimate | cut O33 plugs for a O32 bore, punch 3 x O5 for 6.5 mm lead - interference fit, soap them through |
| [3M 4200 FC 3 oz tube, fillet over the bung](https://www.amazon.com/dp/B00MJ9K78A) | 1 | tube | $17.99 | $17.99 | verified | does both boards; 4200 NOT 5200 - 5200 never comes out |
| 25 mm webbing loop, module lift handle | 0 | ea | $0.00 | $0.00 | on hand | cut from the 6 yd webbing pack in 10c - it is the same 1 in strap. Through the two printed bosses on the forward wall; the module is ~14 kg in a cavity with 12 mm of side clearance, so there is no way to get a hand beside it |
| [M12 IP68 membrane vent plug](https://www.amazon.com/dp/B0FXSNDGTV) | 2 | ea | $9.95 | $19.90 | verified | NOT optional on a sealed lithium box |
| [M12 IP68 momentary panel button](https://www.amazon.com/dp/B0FPQP7CP9) | 1 | ea | $32.65 | $32.65 | verified | 1 on hand; this line buys the second board's |
| [JST GH 1.25 mm pigtail pair, BMS switch](https://www.amazon.com/dp/B07FP2FCYC) | 1 | pk | $5.99 | $5.99 | verified | connects the panel button to the BMS key-switch input. CHECK THE BOX FIRST - DALY ship a ready-made key switch with some units |
| [SP17 2-pin IP68 flange receptacle](https://www.amazon.com/dp/B0CDH5R8P4) | 2 | ea | $13.20 | $26.40 | verified | 67.2 V 5 A charge; O17 panel hole, 2 x M3 flange screws. $2.49, not the $11 this carried. CHECK THE CAP IS INCLUDED before ordering - on a board that gets submerged the cap is the part that does the sealing when nothing is plugged in |
| [M3 heat-set insert kit, 361 pc](https://www.amazon.com/dp/B0G8JLX1HR) | 1 | kit | $13.98 | $13.98 | verified | covers the port flange (4 sets) and the nose cone. The kit's screws are PLAIN STEEL - buy M3 x 8 A4 separately for the flange, which lives in the wet cavity |
| [M3 x 8 A4 stainless, 10 pk](https://www.amazon.com/dp/B07DVMFMJZ) | 1 | pk | $6.76 | $6.76 | verified | the kit's screws are not stainless and this joint is submerged |
| **subtotal** | | | | **$416.32** | | |

## 9  Electrical

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| [Silica gel, indicating, 50 g per module](https://www.amazon.com/dp/B0DSBCXHT3) | 1 | pk | $13.99 | $13.99 | estimate | ~40 g is a season at 50 breathing cycles; a token sachet is worth about six. Bake it dry when the indicator turns |
| [Flipsky 65161 120KV motor](https://flipsky.net/products/brushless-motor-sensorless-amphibious-fully-waterproof-motor-65161-120kv-100kv-6000w-for-efoil-ejet-boards-ebike-electric-surfboard) | 2 | ea | $298.00 | $596.00 | verified |  |
| [Flipsky 75200 Pro V2 ESC](https://flipsky.net/products/flipsky-75200-pro-v2-0-with-aluminum-pcb-based-on-vesc-for-electric-skateboard-electric-scooter-ebike-speed-controller) | 2 | ea | $150.00 | $300.00 | verified |  |
| [Thermal pad 1 mm non-conductive, 100 x 100](https://www.amazon.com/dp/B0GTLRJJGT) | 1 | ea | $9.99 | $9.99 | verified | 15.8 W/mK. One 100 x 100 sheet cuts both boards' baseplates. The ESC PCB face goes DOWN onto the floor, same as V1 did onto its alu bottom plate |
| [Flipsky VX3 remote](https://flipsky.net/products/flipsky-fully-waterproof-remote-vx3-controller-for-efoil-esurf-esk8) | 2 | ea | $71.00 | $142.00 | verified |  |
| [DALY Smart BMS Li-ion 16S 60V 150A](https://www.amazon.com/dp/B0CXXFQT9S) | 2 | ea | $147.70 | $295.40 | verified | batteryint.com; confirm it is <= 164 x 66 x 21 mm |
| [Charger 67.2 V 5 A, 16S  (NOT 58.8 V)](https://www.amazon.com/dp/B0DK6FTB1P) | 2 | ea | $45.99 | $91.98 | verified | Amazon B0DK6FTB1P, aluminium case + fan |
| [BAK N21700CG-50, 130-cell case (BatteryHookup)](https://batteryhookup.com/products/new-3-6v-5000mah-bak-n21700cg-50-2170-lithium-ion-cells?variant=46196788789410) | 1 | case | $260.00 | $260.00 | verified | new overstock |
| [BAK N21700CG-50 singles, spares](https://batteryhookup.com/products/new-3-6v-5000mah-bak-n21700cg-50-2170-lithium-ion-cells?variant=46196788756642) | 15 | ea | $2.50 | $37.50 | verified | 7% margin on a spot-welded pack |
| 21700 cells already on hand | 128 | ea | $0.00 | $0.00 | on hand |  |
| [Pure nickel 0.2 x 10 mm, 5 m roll](https://www.amazon.com/dp/B0961Q1VVR) | 3 | roll | $14.99 | $44.97 | verified | 6.9 m a board derived from the pack, not guessed. YOU ALREADY OWN 3 ROLLS (SUIDI, ordered Apr 16 x2 and May 6) - check the drawer before buying more. There is also a 5 m roll of 0.2 x 27 mm uxcell from Apr 12: too wide for bridges, but it is the right stock for the two terminal collectors and for doubling the edges without stacking two thin layers |
| 21700 spacer brackets | 0 | set | $0.00 | $0.00 | on hand |  |
| [ANL 150 A fuse + holder](https://www.amazon.com/dp/B0B6ZHJR7D) | 2 | ea | $9.99 | $19.98 | verified | in the NEGATIVE leg, between BMS P- and the ESC - that is where V1 ran it and it is the node the charge negative branches from too |
| [Inline 10 A fuse + holder, charge lead](https://www.amazon.com/dp/B0F2YXV41Q) | 1 | pk | $7.59 | $7.59 | verified | at SPLIT A on the charge positive. The ANL is sized for the motor and cannot protect 16 AWG |
| [8 AWG silicone, 10 ft red + 10 ft black](https://www.amazon.com/dp/B0BYJRDT19) | 1 | pk | $21.99 | $21.99 | verified | one pack covers BOTH boards - the longest run in the module is the 278 mm ESC-to-fuse, so 10 ft a side is already 10x what the runs need. Motor supplies its own phase leads + bullets. Amazon 8 AWG 10+10 spans $18.88-$23.99; the 25 ft pack at $49.99 was buying 40 ft of wire to use about 3 |
| [PVC pack wrap, 200 mm lay-flat](https://www.amazon.com/dp/B09SVFL33L) | 1 | roll | $13.99 | $13.99 | verified | wide enough to sleeve a 16S brick; one roll does both |
| [Kapton tape, pack insulation](https://www.amazon.com/dp/B006ZFQNT6) | 1 | roll | $8.25 | $8.25 | estimate |  |
| **subtotal** | | | | **$1,863.63** | | |

## 8  Mast hardpoint

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| [M8 x 1.25 tap + 6.8 mm drill set](https://www.amazon.com/dp/B0GD1YF5PL) | 1 | set | $8.63 | $8.63 | verified | 8 blind holes |
| [M8 x 1.25 BOTTOMING tap, 4-flute](https://www.amazon.com/dp/B00DLCTUDM) | 1 | ea | $8.78 | $8.78 | verified | the one that actually matters - blind at 10 mm in a 12.7 plate, and the taper tap in the set above cannot reach the bottom |
| [M8 thread repair kit (Time-Sert / helicoil)](https://www.amazon.com/dp/B09WN4QTNL) | 0 | kit | $14.59 | $0.00 | on hand | NOT NEEDED for the build - the plate is machined. Buy it only if a thread ever galls in service. B09WN4QTNL, $14.59 |
| [Ultra Tef-Gel, galvanic barrier](https://www.amazon.com/dp/B01606TCAG) | 1 | ea | $39.00 | $39.00 | verified | every mast bolt, every time it goes back in. DEARER than the $22 this was carried at - and do not reach for the small tube to save it: the 3cc syringe is $31.51, so it is 80% of the price for a fraction of the gel |
| **subtotal** | | | | **$56.41** | | |

## 9b Small but essential

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| Capacitor spot welder | 1 | ea | $0.00 | $0.00 | on hand | used on V1 |
| [M8 x 30 A4 mast bolts, 10 pk - spares](https://www.amazon.com/dp/B07HZKSP72) | 1 | pk | $10.82 | $10.82 | verified | Gong supplies its own; these are spares. Only listing confirming marine A4/316; head is ISO 7380 button, not socket cap - check that suits the counterbore |
| [Silicone grease for the seal cord](https://www.amazon.com/dp/B0BN82MJVK) | 1 | tube | $9.99 | $9.99 | estimate | stops the cord bonding to the lid in storage |
| [Cyanoacrylate for the cord splice](https://www.amazon.com/dp/B0DKP4TVSF) | 1 | ea | $5.39 | $5.39 | estimate |  |
| [Water-ingress alarm, 2 pk](https://www.amazon.com/dp/B09DCMCB8D) | 1 | pk | $12.99 | $12.99 | verified | Geevon 100 dB pucks - the 2-pack covers BOTH boards. Put the SENSOR on the module floor in the lowest corner, not up on the pack - it is only useful where water collects |
| [1/4 in torque wrench, 10-50 in-lb](https://www.amazon.com/dp/B0D7PWP7YF) | 1 | ea | $25.97 | $25.97 | verified | 1.1-5.6 Nm. RANGE MATTERS: our hatch spec is 2 Nm = 17.7 in-lb, which is BELOW the 20 in-lb floor of the common 20-200 in-lb wrenches - they cannot read our number at all. CALIBRATION TOOL - set the drill clutch with it, then use the clutch. The hatch is captive nuts in ASA against a hard stop; past the stop more torque only loads the nut pockets |
| [Coiled ankle leash](https://www.amazon.com/dp/B096VL3DHV) | 2 | ea | $14.99 | $29.98 | verified | you trust the remote failsafe; this is so the board stays with you |
| [FCS-pattern leash plug](https://www.amazon.com/dp/B0F1F97R4D) | 2 | ea | $8.59 | $17.18 | estimate |  |
| [Kayak-style webbing carry handle, 4 pk](https://www.amazon.com/dp/B08BC6Q7ZW) | 1 | pk | $13.89 | $13.89 | verified | 4 needed; 2 x M6 into the 6061 strip in the rail pocket |
| [M6 x 16 A4 button head, 10 pk](https://www.amazon.com/dp/B07DVRLQTK) | 1 | pk | $8.06 | $8.06 | verified | 8 needed, strap mounts. The M6 THREADED INSERT IS NOT INCLUDED - separate line below |
| [M6 heat-set insert, strap mounts](https://www.amazon.com/dp/B0DNJNLP95) | 1 | pk | $9.99 | $9.99 | verified | not supplied with the screws above |
| **subtotal** | | | | **$144.26** | | |

## 9c Pack wiring

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| Solder + flux, bus bars and jumpers | 0 | set | $0.00 | $0.00 | on hand | on hand from V1; only the ring lugs and balance leads need it now - the bridges are welded, not soldered |
| Balance harness, 17-wire | 2 | ea | $0.00 | $0.00 | on hand | DALY ships one - CONFIRM before you need it |
| [16 AWG silicone, 6 colours x 5 ft](https://www.amazon.com/dp/B089CPH72F) | 1 | kit | $14.49 | $14.49 | verified | charge port and power button runs are short; one kit does both boards and the colours keep them straight |
| [Dielectric grease, terminals](https://www.amazon.com/dp/B0D6R543V2) | 1 | tube | $8.99 | $8.99 | estimate |  |
| [Cable ties, lacing, adhesive mounts](https://www.amazon.com/dp/B08RMS5H25) | 2 | set | $9.99 | $19.98 | estimate |  |
| [Silicone sealant, BMS anti-vibration dabs](https://www.amazon.com/dp/B0F4MT4FW6) | 1 | tube | $7.49 | $7.49 | estimate | V1 did this; stops the BMS walking |
| [IP68 M25 inline housing, 5 pk](https://www.amazon.com/dp/B0DPKM5HF7) | 2 | pk | $15.98 | $31.96 | verified | 3 per board, one per phase, 2 spare. M25 bodies take 4-14 mm cable against our 6.5 mm 8 AWG, so the size class is confirmed. Still CHECK THE BODY LENGTH against the 60 x 318 bay before ordering wire - diameter fits, length is the risk |
| [5.5 mm gold bullets, 20 pair](https://www.amazon.com/dp/B096DJKR5Y) | 1 | pk | $12.99 | $12.99 | verified | 3 pair a board, so one pack covers both with spares. Motor pigtails arrive with their own |
| [Fish tape / pull cord for the mast conduit](https://www.amazon.com/dp/B0FGCY7XPS) | 1 | ea | $9.99 | $9.99 | estimate |  |
| **subtotal** | | | | **$105.89** | | |

## 10 Foil

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| [Gong Foil Setup X-Over V3 Atmo Perf Series - XL, Alu 85](https://www.gong-galaxy.com/en-us/products/gong-foil-setup-x-over-atmo?variant=57158084231543) | 2 | ea | $702.00 | $1,404.00 | verified | complete: FW + matched stab + V3 alu 85/17 mast + V3 MFC + fuselage + V3 top plate + all screws + foil bag. Current range, not end-of-line like the non-Atmo V3 |
| Gong shipping to Idaho, ONE order, both foils | 1 | order | $268.63 | $268.63 | verified | quoted at checkout for 2 x XL Alu setups. PER ORDER, not per foil - ordering the two separately would roughly double it |
| US customs / import duty on the Gong order | 0 | allow | $0.00 | $0.00 | estimate | UNQUANTIFIED - carried at zero on purpose so it is never mistaken for a verified figure. Budget ~$210 if a 15% rate holds, and expect it as a courier invoice AFTER delivery, not at checkout |
| **subtotal** | | | | **$1,672.63** | | |

## 10b Drivetrain

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| [PETG filament 1 kg, mast clamp set](https://www.amazon.com/dp/B0D41Y3WWZ) | 2 | kg | $12.99 | $25.98 | verified | 4 STEP files; 0.6 nozzle, 5 perims, 40% infill |
| [M5 x 250 threaded rod, 4 pk (cut to ~171 mm)](https://www.amazon.com/dp/B0CMZR9L1Y) | 2 | pk | $9.99 | $19.98 | verified | a 4-pack is exactly one board's worth. Dry-assemble and mark before cutting |
| [M6 x 20 fender washer, 100 pk](https://www.amazon.com/dp/B0DPMPJW4H) | 1 | pk | $9.49 | $9.49 | verified | 8 needed |
| [M5 nyloc nut 316, 150 pk](https://www.amazon.com/dp/B0BP2T6Z4Q) | 1 | pk | $8.99 | $8.99 | verified | a separate pack from the washers above - they do not come together |
| M3 x 6 button head + heat-set, nose cone | 0 | set | $0.00 | $0.00 | on hand | off the 361-pc M3 kit bought in section 7 - one kit does both |
| [Loctite 242](https://www.amazon.com/dp/B000I1RSNS) | 1 | ea | $6.98 | $6.98 | estimate | rod ends into the motor only - nyloc end does not need it |
| [PETG for props, 4-5 spares per board](https://www.amazon.com/dp/B0D41Y3WWZ) | 2 | kg | $12.99 | $25.98 | verified | 0.4 nozzle, 100% infill; balance-check on a bolt, then epoxy-coat - V1 skipped the coat and layer lines cost drag |
| [Roll pin assortment M1.5-M6, 220 pc](https://www.amazon.com/dp/B09MPWY8L4) | 1 | kit | $12.99 | $12.99 | verified | 4 needed. An ASSORTMENT on purpose: the note says MEASURE the shaft cross-hole rather than trust the 4 mm figure, and a kit means the measurement does not cost another order |
| [M8 nyloc nut 316, 30 pk - prop nut](https://www.amazon.com/dp/B0BP2R3YHY) | 1 | pk | $8.99 | $8.99 | verified | 2 needed. 316 not 304 - this one is permanently submerged. WASHER NOT INCLUDED, see below |
| [M8 316 washer, prop nut](https://www.amazon.com/dp/B0DDGRXHT7) | 1 | pk | $7.69 | $7.69 | verified | only 2 needed; sold in 10s |
| [8 AWG marine ring lugs, 20 pk](https://www.amazon.com/dp/B0CWGXB4NB) | 2 | pk | $9.99 | $19.98 | verified | 28 needed; on M6 studs - nothing to solder |
| [M6 stainless stud/busbar hardware](https://www.amazon.com/dp/B0DP79B987) | 0 | set | $11.99 | $0.00 | on hand | DELETED - the fuse holder's input stud is the positive node and the BMS's P- is the negative one. See Appendix D in fabrication.md |
| [Hydraulic lug crimper, 10 ton, 12-2/0 AWG](https://www.amazon.com/dp/B0CFV249X3) | 1 | ea | $39.99 | $39.99 | verified | one-time; this is what replaces soldering XT150s |
| [Adhesive-lined heat shrink 3:1, 400 pc kit](https://www.amazon.com/dp/B0BVVMCY86) | 1 | kit | $13.99 | $13.99 | verified | marine grade, glue-lined - plain heat shrink over a joint in a wet cavity is decoration |
| **subtotal** | | | | **$201.03** | | |

## 10c Restraint & fitout

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| G10 chocks, equipment plate, pack tabs | 0 | off | $0.00 | $0.00 | on hand | cut from 1/8 and 1/2 in offcuts |
| [1 in polyester webbing 6 yd + 6 buckles](https://www.amazon.com/dp/B0FBRMSRLK) | 1 | kit | $5.99 | $5.99 | verified | 2 straps per board, plus the module lift loops in section 7, all out of the one 6 yd pack |
| [EVA bedding pads](https://www.amazon.com/dp/B0GG9H6VS2) | 0 | set | $16.99 | $0.00 | on hand | cut from the roll the deck and lid pieces do not use - same material, already self-adhesive, already bought |
| **subtotal** | | | | **$5.99** | | |

## 10d Shop consumables

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| [Thermometer / hygrometer, 2 pk](https://www.amazon.com/dp/B086PC5962) | 1 | pk | $17.99 | $17.99 | estimate | one in the shop, one by the part. Slow needs 60 F, fast needs 40-45, and below ~35 nothing cures at all |
| [3M Fastbond 1077 water-based, CNC hold-down](https://www.amazon.com/dp/B0GRSV587N) | 1 | ea | $26.02 | $26.02 | verified | WATER-BASED because the blank is EPS - solvent sprays like Super 77 eat polystyrene. Foam is taped/tacked down, not clamped |
| [Sacrificial MDF, CNC spoilboard](https://www.homedepot.com/p/1-4-in-x-2-ft-x-4-ft-Medium-Density-Fiberboard-1508104/202089069) | 1 | sheet | $16.23 | $16.23 | estimate | buy it local, a 4x8 sheet does not travel well |
| [Release wax / PVA for the cavity caul](https://www.amazon.com/dp/B0HB5VXRY1) | 1 | set | $19.90 | $19.90 | estimate |  |
| [Dowel pins + drill, two-sided registration](https://www.amazon.com/dp/B0GS2R3F5G) | 1 | set | $12.99 | $12.99 | estimate |  |
| [1/2 in O-flute up-spiral, foam roughing](https://www.amazon.com/dp/B001J9I6D4) | 1 | ea | $66.05 | $66.05 | verified | Freud 73-214, 1/2 in shank. SINGLE flute for chip clearance - EPS chips are bulky and a 2- or 3-flute packs the gullets and starts melting the blank. ONLY if the makerspace does not supply tooling |
| [1/2 in ball nose, finishing pass](https://www.amazon.com/dp/B00KZM3GSG) | 1 | ea | $41.95 | $41.95 | verified | 1/2 in shank. ONLY if the makerspace does not supply tooling |
| [1/2 in spiral, 3 in cutting length - cavity wall](https://www.amazon.com/dp/B0BTY16K5P) | 1 | ea | $82.99 | $82.99 | verified | 76.2 mm of FLUTE - the only reach found that clears the 71.6 mm cavity wall in one pass. It is a COMPRESSION bit, which is not the ideal geometry for foam: if a plain upcut or a reduced-shank necked bit turns up at this reach, prefer it. Needed ONLY for the wall finish - rough with the Freud |
| [Rotary-tool router base + collets, if needed](https://www.amazon.com/dp/B0000DEZK4) | 1 | set | $24.63 | $24.63 | estimate | you have the tool; this is only if the base you have will not hold depth over the groove run |
| **subtotal** | | | | **$308.75** | | |

## 10e Layup kit

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| [Chip brushes 2 in, 36 pk](https://www.amazon.com/dp/B078XJ2DCJ) | 1 | pk | $17.99 | $17.99 | verified | disposable, 2-4 a session across 6 sessions. The 12 pk at $7.19 is dearer per brush and runs out mid-build |
| [Laminating bubble roller kit, 4 pc](https://www.amazon.com/dp/B07FCLTHY6) | 1 | kit | $17.99 | $17.99 | verified |  |
| [Nitrile gloves 6 mil, 100 pk](https://www.amazon.com/dp/B0C3SSXL4K) | 2 | box | $14.44 | $28.88 | verified |  |
| Respirator | 1 | ea | $0.00 | $0.00 | on hand |  |
| [3M 60923 organic vapour / acid gas P100, pair](https://www.amazon.com/dp/B00AEFCKKY) | 2 | pr | $17.99 | $35.98 | verified | $18.39/pr on Amazon against $31.49 at envirosafetyproducts. Cartridges EXPIRE - buy these near the layup, not with the rest of the order |
| [Acetone, 1 gal, cleanup](https://www.homedepot.com/p/Klean-Strip-1-Gal-Acetone-Flammable-Paint-Solvent-GAC18/100141096) | 0 | gal | $20.98 | $0.00 | on hand | DELETED - see comment. The quart in section 7 covers the real uses |
| [Rosin paper roll, floor and bench](https://www.amazon.com/dp/B0FXJDFW2B) | 1 | roll | $27.95 | $27.95 | estimate | absorbs instead of pooling. This is the actual upgrade over a tarp, and it is $24 |
| [Folding sawhorses, pair, 700 lb](https://www.amazon.com/dp/B0G4CH7SKB) | 1 | pair | $39.99 | $39.99 | verified | ~30 in high. Racks buy height for planing, and this core comes machined - so they buy nothing here |
| [Pipe lagging or carpet, sawhorse padding](https://www.amazon.com/dp/B0CBYST37N) | 1 | set | $8.99 | $8.99 | estimate | bare sawhorse tops mark foam and wet laminate |
| [Plastic sheeting + masking tape, bench protection](https://www.amazon.com/dp/B0GF2BWRC6) | 1 | set | $9.99 | $9.99 | estimate |  |
| [Flex longboard sander, 16-1/2 x 2-3/4](https://www.amazon.com/dp/B0CPR1CGQV) | 1 | ea | $19.99 | $19.99 | verified | adjustable radius, hook-and-loop + PSA |
| [Adjustable hand sanding block](https://www.amazon.com/dp/B0D4LNDYXD) | 1 | ea | $15.99 | $15.99 | verified | rails, nose, tail and anywhere the longboard will not reach |
| **subtotal** | | | | **$223.74** | | |

## 11 Finishing

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| [TotalBoat TotalFair epoxy fairing compound](https://www.amazon.com/dp/B00S9RBWIA) | 2 | kit | $45.99 | $91.98 | verified | smallest kit, one per board |
| [TotalBoat Premium Marine Topside Primer](https://www.amazon.com/dp/B00HS4YY7G) | 1 | kit | $46.99 | $46.99 | verified | one covers both |
| [TotalBoat Wet Edge topside paint, colour](https://www.amazon.com/dp/B00HQP5D9A) | 2 | kit | $53.99 | $107.98 | verified | one-part polyurethane, quart |
| [FOCEAN EVA deck sheet 2400 x 600 x 5.8](https://www.amazon.com/dp/B0BTLW75FL) | 1 | sheet | $54.14 | $54.14 | verified | 3 pieces a board - aft of the hatch, forward of it, and one on the lid - using 818 mm of the 2400 roll each. Self-adhesive EVA, 55 shore. CUT LONG AND TRIM ON THE BOARD from the centreline outward: with no seams, the crown's arc excess has to go into stretch and into the trim at the rail |
| [Longboard PSA sandpaper 80 grit, 20 yd roll](https://www.amazon.com/dp/B0CQ7CVGK6) | 1 | roll | $15.99 | $15.99 | verified | 2-3/4 in, self-adhesive, fits the longboard above. 80 is the fairing grit - it cuts fair, it does not finish |
| [Longboard PSA sandpaper 120-180 grit, 20 yd roll](https://www.amazon.com/dp/B001AVC8ZI) | 1 | roll | $20.99 | $20.99 | verified | after 80 has the shape right |
| [Wet/dry sandpaper assortment, 45 pc](https://www.amazon.com/dp/B0GHND351C) | 1 | pk | $8.99 | $8.99 | verified | 80-400 for detail and between primer coats |
| **subtotal** | | | | **$347.06** | | |

## 12 Freight and tax

| Item | Qty | Unit | Unit $ | Ext $ | | Note |
|---|---:|---|---:|---:|---|---|
| Shipping - Divinycell, 6061 plate, VR20 | 1 | allow | $120.00 | $120.00 | estimate | STILL THE BIGGEST UNVERIFIED LINE - it wants three real carts to settle. Was $220 when it covered G10 sheet and hazmat epoxy, both of which are now out of the build entirely |
| Idaho sales tax, 6% (Ada County, no local) | 1 | allow | $439.23 | $439.23 | verified |  |
| **subtotal** | | | | **$559.23** | | |

## Totals

| | |
|---|---:|
| **Grand total, 2 boards** | **$7,759.76** |
| Per board | $3,879.88 |
| Of which verified | $7,214.73  (93%) |
| Of which estimated | $545.03 |
| Linked to a real listing | 130 lines |
| Priced but NOT linked | 0 lines, $0.00 |
| Not linkable, but MEASURED (freight quotes) | 2 lines, $707.86 |
| Not linkable and still estimated | 1 lines, $120.00 |

## What is a board, and what is a shop

Some of the total above is not the cost of a board at all - it is tools, jigs and templates that exist afterwards and do not repeat. Splitting them out is the difference between "a board costs $3,880" and "a board costs $3,489 and I now own a vacuum rig, a crimper and a full template set".

| | |
|---|---:|
| One-time tooling (incl. its share of tax) | $781.41 |
| **Marginal cost of a board** | **$3,489.17** |
| Cost of the NEXT board after these 2 | $3,489.17 |

| One-time item | $ |
|---|---:|
| Maker Shop Boise Basic month | $150.00 |
| VECOTOOLS 4.5 CFM single-stage pump, oil incl. | $57.99 |
| VR20 vacuum regulator | $52.00 |
| Bag connector w/ ball valve, 1/4 in QD | $39.18 |
| Vacuum hose + hose clamps | $11.61 |
| Vacuum gauge, -30 inHg, 1/4 NPT, glycerin | $10.50 |
| M8 x 1.25 tap + 6.8 mm drill set | $8.63 |
| M8 x 1.25 BOTTOMING tap, 4-flute | $8.78 |
| 1/4 in torque wrench, 10-50 in-lb | $25.97 |
| Hydraulic lug crimper, 10 ton, 12-2/0 AWG | $39.99 |
| Dowel pins + drill, two-sided registration | $12.99 |
| 1/2 in O-flute up-spiral, foam roughing | $66.05 |
| 1/2 in ball nose, finishing pass | $41.95 |
| 1/2 in spiral, 3 in cutting length - cavity wall | $82.99 |
| Rotary-tool router base + collets, if needed | $24.63 |
| Rosin paper roll, floor and bench | $27.95 |
| Folding sawhorses, pair, 700 lb | $39.99 |
| Flex longboard sander, 16-1/2 x 2-3/4 | $19.99 |
| Adjustable hand sanding block | $15.99 |
