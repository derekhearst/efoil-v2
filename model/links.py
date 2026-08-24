"""item name -> (Amazon ASIN, price seen, listing title).

GENERATED - regenerate rather than hand-edit. Every entry is a real
listing that was opened and read, not a guess. bom.py turns the ASIN
into a link on the item name and reports any priced line that has no
entry here as "verified but NOT yet linked".
"""

LINKS = {
    "1/2 in O-flute up-spiral, foam roughing":
        ("B001J9I6D4", 66.05, "Freud 73-214 1/2in Dia O-Flute Up Spiral Bit 1/2in Shank"),
    "1/2 in ball nose, finishing pass":
        ("B00KZM3GSG", 41.95, "YONICO Carbide Ball Nose End Mill 1/2in Dia 1/2in Shank"),
    "1/2 in spiral, 3 in cutting length - cavity wall":
        ("B0BTY16K5P", 82.99, "SpeTool Compression Spiral Router Bit 1/2in Shank 3in Cutting Length"),
    "1/4 in torque wrench, 10-50 in-lb":
        ("B0D7PWP7YF", 25.97, "1/4in Drive Click Torque Wrench 10-50 IN-LB Dual-Direction"),
    "16 AWG silicone, 6 colours x 5 ft":
        ("B089CPH72F", 14.49, "16 AWG Stranded Silicone Wire Spool 5 ft Each 6 Colors"),
    "1708 biax, 50in x 10 yd roll":
        ("B07RJWHPKG", 79.95, "Fiberglass 1708 Biaxial Mat Cloth 50in x 360in 10 Yard"),
    "2 mm glass beads or shim wire, bond-line control":
        ("B0FVSHYP99", 7.19, "uxcell 2000Pcs 2mm Solid Round Clear Glass Beads"),
    "2.5 mm straight cutter - fallback":
        ("B0GWSZ2KV2", 7.99, "Straight Router Bit 1/8in Shank 2.5x22mm Carbide 2 Flute"),
    "21700 cell holder, 1x2 brick, 50 pk":
        ("B092PSRGZ6", 9.99, "Heyiarbeit 50Pcs 2 x Cell 21700 Battery Holder Bracket Cell Spacer"),
    "3M 4200 FC 3 oz tube, fillet over the bung":
        ("B00MJ9K78A", 17.99, "3M 05260 Marine Adhesive/Sealant Fast Cure 4200 3 Fl Oz"),
    "3M 60923 organic vapour / acid gas P100, pair":
        ("B00AEFCKKY", 17.99, "3M P100 Respirator Cartridge/Filter 60923, NIOSH Approved, 1 Pair"),
    "3M Fastbond 1077 water-based, CNC hold-down":
        ("B0GRSV587N", 26.02, "3M Fastbond Water-Base Multipurpose Adhesive 1077 Low VOC 8.2 oz"),
    "5.5 mm gold bullets, 20 pair":
        ("B096DJKR5Y", 12.99, "20 Pairs Gold-Plated 5.5MM Bullet Male and Female Connectors"),
    "5052 1/8in x 12 x 24, 2-pack - module floors":
        ("B0D3TH4TTC", 61.99, "2 Pack 5052 Aluminum Sheet Metal 1/8in x 12in x 24in"),
    "6061-T651 1/2in x 12 x 18 - mast plates":
        ("https://www.speedymetals.com/pc-2411-8360-12-6061-t651-aluminum-plate.aspx", 88.92, "1/2in 6061-T651 Aluminum Plate 12in x 18in"),
    "8 AWG marine ring lugs, 20 pk":
        ("B0CWGXB4NB", 9.99, "haisstronica 20PCS Battery Cable Lug and Heat Shrink Kit 8 AWG M6"),
    "8 AWG silicone, 10 ft red + 10 ft black":
        ("B0BYJRDT19", 21.99, "8 AWG Silicone Wire 10 ft Red and 10 ft Black"),
    "ANL 150 A fuse + holder":
        ("B0B6ZHJR7D", 9.99, "BOJACK 0/2/4 Gauge ANL Fuse Holder with 150 Amp Fuse"),
    "ASA filament, printed module shell":
        ("B09DKPYYBP", 24.49, "Polymaker ASA Filament 1.75mm Black 1KG UV Resistant"),
    "ASA filament, printed rim ring":
        ("B09DKPYYBP", 24.49, "Polymaker ASA Filament 1.75mm Black 1KG"),
    "Acetone, solvent-welding the printed joints":
        ("https://www.homedepot.com/p/Klean-Strip-1-qt-Acetone-Thins-Fiberglass-Resins-Epoxy-and-Adhesives-QAC18/100144922", 11.48, "Klean-Strip 1 qt Acetone Thins Fiberglass Resins Epoxy and Adhesives"),
    "Adhesive-lined heat shrink 3:1, 400 pc kit":
        ("B0BVVMCY86", 13.99, "400Pcs Heat Shrink Tubing Kit 3:1 Adhesive Lined"),
    "Adjustable hand sanding block":
        ("B0D4LNDYXD", 15.99, "Adjustable Hand Sanding File Block with Hook and Loop"),
    "BAK N21700CG-50 singles, spares":
        ("https://batteryhookup.com/products/new-3-6v-5000mah-bak-n21700cg-50-2170-lithium-ion-cells?variant=46196788756642", 2.50, "New 3.6v 5000mAh BAK N21700CG-50 2170 Cells - Single Cell"),
    "BAK N21700CG-50, 130-cell case (BatteryHookup)":
        ("https://batteryhookup.com/products/new-3-6v-5000mah-bak-n21700cg-50-2170-lithium-ion-cells?variant=46196788789410", 260.00, "New 3.6v 5000mAh BAK N21700CG-50 2170 Cells - Full Case (130)"),
    "Bag connector w/ ball valve, 1/4 in QD":
        ("B0FSKGGL8H", 19.59, "Vacuum Bag Connector with Ball Valve 1/4in Quick Release"),
    "Breather / bleeder cloth":
        ("B015NM0B8K", 13.95, "Breather Bleeder Cloth 1 Yard Elite Lab Vacuum Bagging"),
    "Cable ties, lacing, adhesive mounts":
        ("B08RMS5H25", 9.99, "140 Pack 3/4in Zip Tie Adhesive Mounts with Ties"),
    "Charger 67.2 V 5 A, 16S  (NOT 58.8 V)":
        ("B0DK6FTB1P", 45.99, "67.2V 5A Fast Charger for 16S 60V Li-ion, C13 3-Pin IEC"),
    "Chip brushes 2 in, 36 pk":
        ("B078XJ2DCJ", 17.99, "Pro Grade 2in Chip Brushes Disposable 36 Pack"),
    "Coiled ankle leash":
        ("B096VL3DHV", 14.99, "Coiled SUP Leash Premium Paddle Board Ankle Leash"),
    "Leash plug 30 x 12.5, stainless pin, 2 pk":
        ("B0C6XLK8L9", 6.99, "E-outstanding Surf Leash Plug 2PCS 30x12.5mm "
                             "Surfboard Longboard Leash Plug Round Board Cup"),
    "Cyanoacrylate for the cord splice":
        ("B0DKP4TVSF", 5.39, "Thin CA Glue 20g Cyanoacrylate Super Glue with 3 Droppers"),
    "DALY Smart BMS Li-ion 16S 60V 150A":
        ("https://www.amazon.com/dp/B0CXXFQT9S", 147.70, "DALY Smart BMS 16S 60V 150A Li-ion WiFi Bluetooth CAN RS485"),
    "Dielectric grease, terminals":
        ("B0D6R543V2", 8.99, "BTAS Dielectric Grease for Electrical Connectors 1oz"),
    "Divinycell H-100 1/4in quarter 21x42, hatch lid cores - 2 sheets bonded to 1/2in":
        ("https://fiberglasssupply.com/1-4-in-h-100-divinycell-quarter-sheet-21-x-42/", 49.59, "1/4 in H-100 Divinycell Quarter Sheet 21in x 42in (L20-1894)"),
    "Divinycell H-80 1/4in quarter 24x48, module lid cores":
        ("https://fiberglasssupply.com/quarter-sheet-1-4-h-80-divinycell-plain-sheet/", 53.94, "Quarter Sheet 1/4in H-80 Divinycell Plain Sheet (L18-1070)"),
    "Divinycell H-80 3/4in quarter sheet 24x48, mast block + leash pad":
        ("https://fiberglasssupply.com/quarter-sheet-3-4-h-80-divinycell-plain-sheet/", 100.26, "Quarter Sheet 3/4in H-80 Divinycell Plain Sheet (L18-1112)"),
    "Dowel pins + drill, two-sided registration":
        ("B0GS2R3F5G", 12.99, "284Pcs 8-Size Wood Dowels Kit with 3 Drill Bits"),
    "E-glass 6 oz, 50in x 12ft, 2-pack":
        ("B0CQY5KX84", 19.99, "2 Packs 6 oz 12ft x 50in Fiberglass Cloth E-Glass Plain Weave"),
    "Transfer punch set, metric 1-13 mm":
        ("B005379HJA", 24.99, "TP-03 1-13mm Metric Transfer Punch Set - 25 Pieces"),
    "Transfer screw set M3-M6":
        ("B01IUBRSLO", 24.99, "HHIP 3601-0516 28 Piece Transfer Screw Set, M3 X .5, M4 X .7, M5 X .8, M6 X 1"),
    "M5 x 25 button head ISO 7380, 50 pk":
        ("B07JQ6ZC6B", 15.99, "Fastenere Button Head Socket Cap Screws M5-0.80 x 25MM 50-Pack Stainless 18-8 ISO 7380 - head O9.5 x 2.75 high"),
    "Neoprene sheet 3/4in, wire bung":
        ("B07Y5K1VHK", 26.00, "USA Sealing Neoprene Rubber Sheet, No Adhesive, 60A, 3/4in x 12in x 12in"),
    "Hollow punch set 3/16-1-3/8in, for the O31.75 bung":
        ("B07PQYRG9K", 32.99, "ABN Hollow Punch Kit Leather Punches Tools Hole Punch Set Gasket Punch Set Gasket Cutter 3/16 to 1-3/8in (5-35mm)"),
    "EPS rigid foam 2in x 48in x 8ft (HD 202532856)":
        ("https://www.homedepot.com/p/Henry-2-in-x-48-in-x-8-ft-R-7-7-EPS-Rigid-Foam-Board-Insulation-320825/202532856", 27.68, "Henry 2 in x 48 in x 8 ft R-7.7 EPS Rigid Foam Board Insulation"),
    "FOCEAN EVA deck sheet 2400 x 600 x 5.8":
        ("https://www.amazon.com/dp/B0BTLW75FL", 54.14, "FOCEAN EVA Foam Deck Sheet Camo Lake 94.5 x 23.6 x 0.23 in self-adhesive"),
    "Fish tape / pull cord for the mast conduit":
        ("B0FGCY7XPS", 9.99, "Fish Tape 16.4ft Wire Puller Electrical Snake"),
    "Flex longboard sander, 16-1/2 x 2-3/4":
        ("B0CPR1CGQV", 19.99, "Adjustable Radius Flex Longboard Hand Sanding Block H&L and PSA"),
    "Flipsky 65161 120KV motor":
        ("https://flipsky.net/products/brushless-motor-sensorless-amphibious-fully-waterproof-motor-65161-120kv-100kv-6000w-for-efoil-ejet-boards-ebike-electric-surfboard", 298.00, "Flipsky Waterproof Motor 65161 120KV 6000W for Efoil"),
    "Flipsky 75200 Pro V2 ESC":
        ("https://flipsky.net/products/flipsky-75200-pro-v2-0-with-aluminum-pcb-based-on-vesc-for-electric-skateboard-electric-scooter-ebike-speed-controller", 150.00, "Flipsky 75200 Pro V2.0 Aluminum PCB VESC ESC"),
    "Flipsky VX3 remote":
        ("https://flipsky.net/products/flipsky-fully-waterproof-remote-vx3-controller-for-efoil-esurf-esk8", 71.00, "Flipsky Fully Waterproof Remote VX3 Controller"),
    "Folding sawhorses, pair, 700 lb":
        ("B0G4CH7SKB", 39.99, "Saw Horses 2 Pack Folding Plastic 700 LBS/Pair"),
    "Gebildet PG11 gland, M18x1.5, 30 pk":
        ("B0B8NJR62L", 9.99, "30Pcs PG11 Cable Gland IP68 Waterproof Adjustable 5.0-10mm"),
    "Gong Foil Setup X-Over V3 Atmo Perf Series - XL, Alu 85":
        ("https://www.gong-galaxy.com/en-us/products/gong-foil-setup-x-over-atmo?variant=57158084231543", 702.00, "Foil Setup X-Over V3 Atmo Perf Series - Aluminium / XL / Black"),
    "Hydraulic lug crimper, 10 ton, 12-2/0 AWG":
        ("B0CFV249X3", 39.99, "YUZES 10-Ton Hydraulic Crimping Tool, 12 to 2/0 AWG"),
    "IP68 M25 inline housing, 5 pk":
        ("B0DPKM5HF7", 15.98, "Linkstyle 5PCS IP68 Waterproof Junction Box Inline Connectors"),
    "Inline 10 A fuse + holder, charge lead":
        ("B0F2YXV41Q", 7.59, "3 Pack Inline Waterproof Fuse Holder with 10A/15A ATC Blade Fuses, 16 AWG Pre-"),
    "JST GH 1.25 mm pigtail pair, BMS switch":
        ("B07FP2FCYC", 5.99, "10 Pairs 1.25mm JST 2 Pin Micro Male and Female Connector Plug with 80mm Wire"),
    "Kapton tape, pack insulation":
        ("B006ZFQNT6", 8.25, "1/2in x 36 Yds 1 Mil Polyimide High Temp Electrical Tape"),
    "Kayak/board grab handle, 2 pk + screws":
        ("B0FBW3XT5D", 9.99, "Yluvaok Kayak Handle, 2 handles + 8 screws + driver bit, rubber/webbing"),
    "Laminating bubble roller kit, 4 pc":
        ("B07FCLTHY6", 17.99, "Fiberglass Roller Tools Kit 4pcs Laminating Bubble Roller Set"),
    "Loctite 242":
        ("B000I1RSNS", 6.98, "Loctite Threadlocker Blue 242 Removable Medium Strength 6ml"),
    "Longboard PSA sandpaper 120-180 grit, 20 yd roll":
        ("B001AVC8ZI", 20.99, "Dura-Gold Gold PSA Longboard Sandpaper 150 Grit 20 Yard Roll 2-3/4in"),
    "Longboard PSA sandpaper 80 grit, 20 yd roll":
        ("B0CQ7CVGK6", 15.99, "PSA Sandpaper Roll 80 Grit 2-3/4in x 20 Yards Longboard"),
    "M12 IP68 membrane vent plug":
        ("B0FXSNDGTV", 9.95, "ANGSTROM M12 Waterproof Air Vent Plug IP68 Nylon Breather"),
    "M12 IP68 momentary panel button":
        ("B0FPQP7CP9", 32.65, "5Pcs 12mm Momentary Push Button Switch IP68 SPST NO 3A"),
    "M3 heat-set insert kit, 361 pc":
        ("B0G8JLX1HR", 13.98, "361Pcs M3 Heat Set Insert with Screws Brass Threaded"),
    "M3 x 8 A4 stainless, 10 pk":
        ("B07DVMFMJZ", 6.76, "M3 x 8mm Socket Head Screws DIN 912 Marine Grade Stainless 10 Pack"),
    "M4 A4 washer, 316, 100 pk":
        ("B0DZ5BVLP5", 6.79, "uxcell 100Pcs M4 Flat Washer 316 Stainless 4.3 ID x 12 OD"),
    "M4 x 12 A4 socket cap DIN912, 10 pk":
        ("B07DVPC7HT", 7.10, "M4 x 12mm Socket Head Screws DIN 912 Marine Grade SS 10 Pack"),
    "M6 x 12.7 brass heat-set insert, 50 pc":
        ("B077PGD6X2", 12.00, "initeq M6-1.0 Threaded Heat Set Inserts for 3D Printing, 50, LONG"),
    "M4 x 12.7 LONG brass heat-set insert, 50 pc":
        ("B07473ZV71", 14.00, "initeq Qty 50 M4-0.7 Threaded Heat Set Inserts for 3D Printing (LONG)"),
    "M5 A4 hex nut DIN934, 50 pk - CAPTIVE in the ring":
        ("B084HLMN7B", 9.19, "M5 Hex Nuts DIN 934 Marine Grade Stainless 50 Pack"),
    "M5 nyloc nut 316, 150 pk":
        ("B0BP2T6Z4Q", 8.99, "M5 Stainless Lock Nuts 150pcs 316 Hex Nylon Insert"),
    "M6 penny washer O18 A4 DIN9021":
        ("B0DB8RBY3N", 12.99, "M6X18 Metric Din 9021 Large OD Washer A4 Stainless Steel - ECS-M6D9021A4"),
    "M5 x 250 threaded rod, 4 pk (cut to ~171 mm)":
        ("B0CMZR9L1Y", 9.99, "4pcs M5 x 250mm Fully Threaded Rod 304 Stainless"),
    "M6 x 16 A4 button head, 10 pk":
        ("B07DVRLQTK", 8.06, "M6 x 16mm Button Head Screws ISO 7380 Marine Grade SS 10 Pack"),
    "M6 x 20 fender washer, 100 pk":
        ("B0DPMPJW4H", 9.49, "M6 x 20mm Fender Washers Stainless 100 Pcs"),
    "M8 316 washer, prop nut":
        ("B0DDGRXHT7", 7.69, "uxcell 10Pcs M8 Flat Washer 316 Stainless 8.4 ID x 24 OD x 2mm"),
    "M8 nyloc nut 316, 30 pk - prop nut":
        ("B0BP2R3YHY", 8.99, "M8 Stainless Lock Nuts 30pcs 316 Hex Nylon Insert"),
    "M6 x 1.0 BOTTOMING tap, 4-flute":
        ("https://www.amazon.com/s?k=Drill+America+M6+x+1.0+HSS+4-Flute+Bottoming+Tap", 8.78, "Drill America M6 x 1.0 HSS 4-Flute Bottoming Tap - same family, pick the M6"),
    "M6 x 1.0 tap + 5.0 mm drill set":
        ("B0GSG4FGYW", 9.99, "M6 Tap and 5.0mm Drill Bit Kit, M6x1.0 HSS Metric Drill and Tap Set, 4Pcs"),
    "M6 x 30 A4 mast bolts, 50 pk - spares":
        ("B00BNCFV4Y", 10.82, "Metric DIN 912 M6X30 Socket Head Cap Screw Stainless Steel A4, 50 pcs"),
    "MDF 12 mm, 4 check gauges":
        ("https://www.homedepot.com/p/ProWood-1-2-in-x-2-ft-x-4-ft-Medium-Density-Fiberboard-Project-Panel-109097/202093821", 30.73, "ProWood 1/2 in x 2 ft x 4 ft MDF Project Panel"),
    "Maker Shop Boise Basic month":
        ("https://www.makershopboise.com/membership", 150.00, "Maker Shop Boise Membership - Basic"),
    "Closed-cell sponge EPDM 1/8in, module lid gasket":
        ("B07FWQM34V", 13.99, "XCEL Pure EPDM Sponge Rubber Sheet 60in x 17in "
                              "x 1/8in Thick, closed cell"),
    "Nitrile gloves 6 mil, 100 pk":
        ("B0C3SSXL4K", 14.44, "Inspire Black Nitrile Gloves HEAVY DUTY 6 Mil Chemical Resistant"),
    "PETG filament 1 kg, mast clamp set":
        ("B0D41Y3WWZ", 12.99, "ELEGOO PETG Filament 1.75mm Black 1KG"),
    "PETG for props, 4-5 spares per board":
        ("B0D41Y3WWZ", 12.99, "ELEGOO PETG 3D Printer Filament 1.75mm Black 1KG"),
    "PL300 / Gorilla Glue, layer glue-up":
        ("B0009XEGVC", 6.59, "Loctite PL300 Latex Projects & Foamboard Adhesive, 10 oz Cartridge"),
    "PVC pack wrap, 200 mm lay-flat":
        ("B09SVFL33L", 13.99, "200mm PVC Heat Shrink Wrap Tube for 18650/21700 Battery Packs"),
    "Paste wax, releasing the groove filler":
        ("B0GVCGHZFR", 16.99, "Honey Wax 250 Mold Release Wax 11 oz Carnauba Paste"),
    "Peel ply, 60in":
        ("B0H5JTMTZ3", 18.99, "60in x 1-Yard Nylon Peel Ply Release Cloth"),
    "Pipe lagging or carpet, sawhorse padding":
        ("B0CBYST37N", 8.99, "Pipe Insulation Foam Tube 1-1/8 inch 6FT Pre-Slit"),
    "Plastic sheeting + masking tape, bench protection":
        ("B0GF2BWRC6", 9.99, "Pre-Taped Masking Film 70in x 66ft Painters Plastic with Tape"),
    "Pure nickel 0.2 x 10 mm, 5 m roll":
        ("B0961Q1VVR", 14.99, "SUIDI Nickel Strip 0.2x10mm 5M Pure Nickel Roll for 21700"),
    "Release wax / PVA for the cavity caul":
        ("B0HB5VXRY1", 19.90, "Clear PARTALL Paste #2 Mold Release Wax Silicone Free"),
    "Roll pin assortment M1.5-M6, 220 pc":
        ("B09MPWY8L4", 12.99, "220pcs Roll Pin Set Stainless Slotted Spring Pin M1.5-M6"),
    "Rosin paper roll, floor and bench":
        ("B0FXJDFW2B", 27.95, "Floor Protection Natural Brown Rosin Paper 18in x 166 ft"),
    "Rotary-tool router base + collets, if needed":
        ("B0000DEZK4", 24.63, "Dremel 335-01 Plunge Router Attachment for Rotary Tool"),
    "SP17 2-pin IP68 flange receptacle":
        ("B0CDH5R8P4", 13.20, "SP17 2 Pin Waterproof Connector Panel Mount Socket IP68"),
    "Sacrificial MDF, CNC spoilboard":
        ("https://www.homedepot.com/p/1-4-in-x-2-ft-x-4-ft-Medium-Density-Fiberboard-1508104/202089069", 16.23, "1/4 in x 2 ft x 4 ft Medium Density Fiberboard"),
    "Sealant tape, 50 ft roll":
        ("B0GF25BPN6", 19.99, "50ft High-Temp Vacuum Seal Tape, Yellow Tacky Tape"),
    "Sika Aktivator-PRO 250 ml + daubers":
        ("B0D9KTLC1M", 28.95, "Aktivator-PRO Cleaning and Activating Agent 250ml with Daubers"),
    "Sikaflex-292 marine structural PU":
        ("B008F8VYMM", 28.99, "Sikaflex-292 Marine Adhesive Sealant PU 10.1 fl oz White"),
    "Silica gel, indicating, 50 g per module":
        ("B0DSBCXHT3", 13.99, "2.2 LBS Orange Silica Gel Desiccant Beads Reusable Indicating"),
    "Silicone adhesive, bonding the cord into groove":
        ("B0002UEN1U", 7.56, "Permatex 82180 Ultra Black Max Oil Resistance RTV Silicone Gasket Maker"),
    "Silicone grease for the seal cord":
        ("B0BN82MJVK", 9.99, "KEZE Silicone Grease Waterproof Food Grade for Valve/O-Ring"),
    "Silicone sealant, BMS anti-vibration dabs":
        ("B0F4MT4FW6", 7.49, "Visbella Gasket Maker Neutral RTV Silicone Sealant, Non-Corrosive"),
    "Solid silicone cord, 1/8 in (3.175 mm) - the spare size":
        ("B00QVB0KE8", 15.39, ".125in (1/8in Actual) Silicone O-Ring Cord Stock 70A 10ft"),
    "Solid silicone cord, 3 mm round - BOTH seals":
        ("B096N67R2D", 17.59, ".118 in (3 MM) Silicone 70 Durometer O-Ring Cord Stock 10 FEET"),
    "Test cap + tubing, module leak test":
        ("B0DPWRP6FR", 22.99, "84 PCS Vacuum Lines Kit 6.6FT Silicone Vacuum Hoses with caps"),
    "Thermal pad 1 mm non-conductive, 100 x 100":
        ("B0GTLRJJGT", 9.99, "Thermal Pad 15.8 W/mK 100x100x1mm Non Conductive"),
    "Thermometer / hygrometer, 2 pk":
        ("B086PC5962", 17.99, "TempPro TP49 2 Pack Digital Hygrometer Indoor Thermometer"),
    "TotalBoat 5:1 FAST hardener 6 oz, cold days":
        ("B00HRHA59K", 27.99, "TotalBoat 5:1 Marine Epoxy Fast Hardener 6 oz for 1 Quart Resin"),
    "TotalBoat 5:1 gallon kit, slow hardener":
        ("B00HR8515C", 149.99, "TotalBoat 5:1 Marine Epoxy Resin 1 Gallon Kit Slow"),
    "TotalBoat 5:1 quart kit, fillets and bonding":
        ("B00HR8517A", 58.99, "TotalBoat 5:1 Marine Epoxy Resin 1 Quart Kit Slow Hardener"),
    "TotalBoat Premium Marine Topside Primer":
        ("B00HS4YY7G", 46.99, "TotalBoat Marine Topside Boat Paint Primer White Quart"),
    "TotalBoat TotalFair epoxy fairing compound":
        ("B00S9RBWIA", 45.99, "TotalBoat TotalFair Epoxy Fairing Compound - 2 Pint Kit"),
    "TotalBoat Wet Edge topside paint, colour":
        ("B00HQP5D9A", 53.99, "TotalBoat Wet Edge Topside Marine Paint Black Quart"),
    "Ultra Tef-Gel, galvanic barrier":
        ("B01606TCAG", 39.00, "Ultra Tef-Gel Anti Corrosion Lubricant for Rigging Hardware"),
    "VECOTOOLS 4.5 CFM single-stage pump, oil incl.":
        ("B0GZVLP3PL", 57.99, "4.5CFM 1/3HP Vacuum Pump for HVAC Systems, Single Stage, Foldable Handle"),
    "VR20 vacuum regulator":
        ("https://www.easycomposites.us/vacuum-regulator-for-vacuum-bagging", 52.00, "VR20 Vacuum Regulator - integrated gauge, 1/4in BSP, bracket"),
    "Vac bag film, 5 yd":
        ("B079MBL5TX", 24.95, "Vac Bag Film 5 Yards Elite Lab Vacuum Bagging Supplies"),
    "Vacuum gauge, -30 inHg, 1/4 NPT, glycerin":
        ("B00VQSOZFQ", 10.50, "HFS -30 inHg Vacuum Pressure Gauge Glycerin Filled 2in Dial 1/4in NPT"),
    "Vacuum hose + hose clamps":
        ("B0FH52FT4G", 11.61, "10FT 1/2in ID Steel Wire Suction Hose with 4 Stainless Clamps"),
    "Water-ingress alarm, 2 pk":
        ("B09DCMCB8D", 12.99, "2 Pack Water Leak Detectors 100dB Sensor Alarms"),
    "Wet/dry sandpaper assortment, 45 pc":
        ("B0GHND351C", 8.99, "45 PCS Wet Dry Sandpaper 80-5000 Grit Sheets"),
}

# Where the linked listing actually lives. Set from the link, not
# guessed from the item name - that guess is what once filed
# Amazon-priced peel ply under Fibre Glast.
LINK_VENDOR = {
    "1/2 in O-flute up-spiral, foam roughing": "Amazon",
    "1/2 in ball nose, finishing pass": "Amazon",
    "1/2 in spiral, 3 in cutting length - cavity wall": "Amazon",
    "1/4 in torque wrench, 10-50 in-lb": "Amazon",
    "16 AWG silicone, 6 colours x 5 ft": "Amazon",
    "1708 biax, 50in x 10 yd roll": "Amazon",
    "2 mm glass beads or shim wire, bond-line control": "Amazon",
    "2.5 mm straight cutter - fallback": "Amazon",
    "21700 cell holder, 1x2 brick, 50 pk": "Amazon",
    "3M 4200 FC 3 oz tube, fillet over the bung": "Amazon",
    "3M 60923 organic vapour / acid gas P100, pair": "Amazon",
    "3M Fastbond 1077 water-based, CNC hold-down": "Amazon",
    "5.5 mm gold bullets, 20 pair": "Amazon",
    "5052 1/8in x 12 x 24, 2-pack - module floors": "Amazon",
    "6061-T651 1/2in x 12 x 18 - mast plates": "Speedy Metals",
    "8 AWG marine ring lugs, 20 pk": "Amazon",
    "8 AWG silicone, 10 ft red + 10 ft black": "Amazon",
    "ANL 150 A fuse + holder": "Amazon",
    "ASA filament, printed module shell": "Amazon",
    "ASA filament, printed rim ring": "Amazon",
    "Acetone, solvent-welding the printed joints": "Home Depot / hardware",
    "Adhesive-lined heat shrink 3:1, 400 pc kit": "Amazon",
    "Adjustable hand sanding block": "Amazon",
    "Bag connector w/ ball valve, 1/4 in QD": "Amazon",
    "Breather / bleeder cloth": "Amazon",
    "Cable ties, lacing, adhesive mounts": "Amazon",
    "Charger 67.2 V 5 A, 16S  (NOT 58.8 V)": "Amazon",
    "Chip brushes 2 in, 36 pk": "Amazon",
    "Coiled ankle leash": "Amazon",
    "Leash plug 30 x 12.5, stainless pin, 2 pk": "Amazon",
    "Cyanoacrylate for the cord splice": "Amazon",
    "DALY Smart BMS Li-ion 16S 60V 150A": "Amazon",
    "Dielectric grease, terminals": "Amazon",
    "Divinycell H-100 1/4in quarter 21x42, hatch lid cores - 2 sheets bonded to 1/2in": "Fiberglass Supply",
    "Divinycell H-80 1/4in quarter 24x48, module lid cores": "Fiberglass Supply",
    "Divinycell H-80 3/4in quarter sheet 24x48, mast block + leash pad": "Fiberglass Supply",
    "Dowel pins + drill, two-sided registration": "Amazon",
    "E-glass 6 oz, 50in x 12ft, 2-pack": "Amazon",
    "Transfer punch set, metric 1-13 mm": "Amazon",
    "Transfer screw set M3-M6": "Amazon",
    "M5 x 25 button head ISO 7380, 50 pk": "Amazon",
    "Neoprene sheet 3/4in, wire bung": "Amazon",
    "Hollow punch set 3/16-1-3/8in, for the O31.75 bung": "Amazon",
    "EPS rigid foam 2in x 48in x 8ft (HD 202532856)": "Home Depot / hardware",
    "FOCEAN EVA deck sheet 2400 x 600 x 5.8": "Amazon",
    "Fish tape / pull cord for the mast conduit": "Amazon",
    "Flex longboard sander, 16-1/2 x 2-3/4": "Amazon",
    "Flipsky 65161 120KV motor": "Flipsky",
    "Flipsky 75200 Pro V2 ESC": "Flipsky",
    "Flipsky VX3 remote": "Flipsky",
    "Folding sawhorses, pair, 700 lb": "Amazon",
    "Gebildet PG11 gland, M18x1.5, 30 pk": "Amazon",
    "Gong Foil Setup X-Over V3 Atmo Perf Series - XL, Alu 85": "Gong",
    "Hydraulic lug crimper, 10 ton, 12-2/0 AWG": "Amazon",
    "IP68 M25 inline housing, 5 pk": "Amazon",
    "Inline 10 A fuse + holder, charge lead": "Amazon",
    "JST GH 1.25 mm pigtail pair, BMS switch": "Amazon",
    "Kapton tape, pack insulation": "Amazon",
    "Kayak/board grab handle, 2 pk + screws": "Amazon",
    "Laminating bubble roller kit, 4 pc": "Amazon",
    "Loctite 242": "Amazon",
    "Longboard PSA sandpaper 120-180 grit, 20 yd roll": "Amazon",
    "Longboard PSA sandpaper 80 grit, 20 yd roll": "Amazon",
    "M12 IP68 membrane vent plug": "Amazon",
    "M12 IP68 momentary panel button": "Amazon",
    "M3 heat-set insert kit, 361 pc": "Amazon",
    "M3 x 8 A4 stainless, 10 pk": "Amazon",
    "M4 A4 washer, 316, 100 pk": "Amazon",
    "M4 x 12 A4 socket cap DIN912, 10 pk": "Amazon",
    "M6 x 12.7 brass heat-set insert, 50 pc": "Amazon",
    "M4 x 12.7 LONG brass heat-set insert, 50 pc": "Amazon",
    "M5 A4 hex nut DIN934, 50 pk - CAPTIVE in the ring": "Amazon",
    "M5 nyloc nut 316, 150 pk": "Amazon",
    "M6 penny washer O18 A4 DIN9021": "Amazon",
    "M5 x 250 threaded rod, 4 pk (cut to ~171 mm)": "Amazon",
    "M6 x 16 A4 button head, 10 pk": "Amazon",
    "M6 x 20 fender washer, 100 pk": "Amazon",
    "M8 316 washer, prop nut": "Amazon",
    "M8 nyloc nut 316, 30 pk - prop nut": "Amazon",
    "M6 x 1.0 BOTTOMING tap, 4-flute": "Amazon",
    "M6 x 1.0 tap + 5.0 mm drill set": "Amazon",
    "M6 x 30 A4 mast bolts, 50 pk - spares": "Amazon",
    "MDF 12 mm, 4 check gauges": "Home Depot / hardware",
    "Maker Shop Boise Basic month": "Maker Shop Boise",
    "Closed-cell sponge EPDM 1/8in, module lid gasket": "Amazon",
    "Nitrile gloves 6 mil, 100 pk": "Amazon",
    "PETG filament 1 kg, mast clamp set": "Amazon",
    "PETG for props, 4-5 spares per board": "Amazon",
    "PL300 / Gorilla Glue, layer glue-up": "Amazon",
    "PVC pack wrap, 200 mm lay-flat": "Amazon",
    "Paste wax, releasing the groove filler": "Amazon",
    "Peel ply, 60in": "Amazon",
    "Pipe lagging or carpet, sawhorse padding": "Amazon",
    "Plastic sheeting + masking tape, bench protection": "Amazon",
    "Pure nickel 0.2 x 10 mm, 5 m roll": "Amazon",
    "Release wax / PVA for the cavity caul": "Amazon",
    "Roll pin assortment M1.5-M6, 220 pc": "Amazon",
    "Rosin paper roll, floor and bench": "Amazon",
    "Rotary-tool router base + collets, if needed": "Amazon",
    "SP17 2-pin IP68 flange receptacle": "Amazon",
    "Sacrificial MDF, CNC spoilboard": "Home Depot / hardware",
    "Sealant tape, 50 ft roll": "Amazon",
    "Sika Aktivator-PRO 250 ml + daubers": "Amazon",
    "Sikaflex-292 marine structural PU": "Amazon",
    "Silica gel, indicating, 50 g per module": "Amazon",
    "Silicone adhesive, bonding the cord into groove": "Amazon",
    "Silicone grease for the seal cord": "Amazon",
    "Silicone sealant, BMS anti-vibration dabs": "Amazon",
    "Solid silicone cord, 1/8 in (3.175 mm) - the spare size": "Amazon",
    "Solid silicone cord, 3 mm round - BOTH seals": "Amazon",
    "Test cap + tubing, module leak test": "Amazon",
    "Thermal pad 1 mm non-conductive, 100 x 100": "Amazon",
    "Thermometer / hygrometer, 2 pk": "Amazon",
    "TotalBoat 5:1 FAST hardener 6 oz, cold days": "Amazon",
    "TotalBoat 5:1 gallon kit, slow hardener": "Amazon",
    "TotalBoat 5:1 quart kit, fillets and bonding": "Amazon",
    "TotalBoat Premium Marine Topside Primer": "Amazon",
    "TotalBoat TotalFair epoxy fairing compound": "Amazon",
    "TotalBoat Wet Edge topside paint, colour": "Amazon",
    "Ultra Tef-Gel, galvanic barrier": "Amazon",
    "VECOTOOLS 4.5 CFM single-stage pump, oil incl.": "Amazon",
    "VR20 vacuum regulator": "Easy Composites",
    "Vac bag film, 5 yd": "Amazon",
    "Vacuum gauge, -30 inHg, 1/4 NPT, glycerin": "Amazon",
    "Vacuum hose + hose clamps": "Amazon",
    "Water-ingress alarm, 2 pk": "Amazon",
    "Wet/dry sandpaper assortment, 45 pc": "Amazon",
}
