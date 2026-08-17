# Templates

Cut from **12 mm MDF**. Every one comes off the parametric model, so nothing here needs measuring or tracing.

| Kind | Meaning |
|---|---|
| `BEARING` | cut at FINISHED size - flush-trim bit, bearing rides the template edge |
| `BUSHING` | cut OVERSIZE by the guide-bushing offset |
| `GAUGE` | not a router template - a shape gauge to check against |

Every template carries the centreline and station ticks on the `REG` layer. **`CHANNEL` lines are reference, not cuts.**

| Template | Size mm | Kind | What it does |
|---|---|---|---|
| `T01_planform_half` | 1400 x 280 | BEARING | half outline - flip on the centreline for the other side. Marks are the seam, the mast axis and both ends of the cavity. |
| `T02_cavity_opening` | 523 x 318 | BEARING | through-cut in layers 2 and 3, and the floor pocket wall in layer 1. Same outline all three times. |
| `T03_rim_rebate` | 591 x 386 | BEARING | the ledge the G10 rim ring beds into, cut to the RIM_T depth. CHANNEL line is the cavity opening for reference - do not cut it. |
| `T04_mast_block_pocket` | 430 x 355 | BEARING | dense-foam block pocket in the hull underside. CHANNEL rectangle is the G10 plate footprint - that is T05, cut deeper inside this one. |
| `T05_mast_plate_pocket` | 250 x 175 | BEARING | plate pocket, and it doubles as the drill guide for the four bushing bores. |
| `T06_handle_strip` | 150 x 22 | BEARING | one template, used both sides. NOT a pocket - the handles are a webbing strap bolted to the rail surface. This locates the shallow milled facet the G10 strip beds into, and drills the two inserts. Strip centreline sits 223 mm off the board centreline, where the rail is at 12.7 mm thick stock; facet is only ~1.6 mm deep because the strip is narrow. |
| `T07_leash_pad` | 70 x 70 | BEARING | pad pocket; HOLES circle is the FCS plug bore, cut after the pad is bonded in. |
| `T08_station_10` | 414 x 143 | GAUGE | section at x = 140 mm (10% of length). Shape gauge, not a router template. |
| `T08_station_25` | 521 x 147 | GAUGE | section at x = 350 mm (25% of length). Shape gauge, not a router template. |
| `T08_station_40` | 557 x 147 | GAUGE | section at x = 560 mm (40% of length). Shape gauge, not a router template. |
| `T08_station_55` | 554 x 147 | GAUGE | section at x = 770 mm (55% of length). Shape gauge, not a router template. |
| `T08_station_70` | 505 x 148 | GAUGE | section at x = 980 mm (70% of length). Shape gauge, not a router template. |
| `T08_station_85` | 395 x 151 | GAUGE | section at x = 1190 mm (85% of length). Shape gauge, not a router template. |
| `T09_rocker_and_deck` | 1400 x 157 | GAUGE | centreline profile. Solid is the hull bottom (rocker), CHANNEL is the deck. Cut as two separate gauges or one long one. |

## The one number that is not from the model

`GUIDE_OFF = 5 mm` is the guide-bushing offset, and it depends on **your** bushing and cutter, not on the design. Every `BEARING` template above avoids it entirely by using a flush-trim bit instead - which is why they are all cut at finished size. Only the two seal-groove templates (parts 14 and 15, in `cnc/`) need it.

