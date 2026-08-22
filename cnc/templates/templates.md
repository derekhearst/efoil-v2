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
| `T02_cavity_opening` | 525 x 319 | BEARING | through-cut in layers 2 and 3, and the floor pocket wall in layer 1. Same outline all three times. |
| `T03_rim_rebate` | 593 x 387 | BEARING | the ledge the G10 rim ring beds into, cut to the RIM_T depth. CHANNEL line is the cavity opening for reference - do not cut it. |
| `T04_mast_block_pocket` | 430 x 355 | BEARING | dense-foam block pocket in the hull underside. CHANNEL rectangle is the G10 plate footprint - that is T05, cut deeper inside this one. |
| `T05_mast_plate_pocket` | 250 x 175 | BEARING | plate pocket, and it doubles as the drill guide for the four bushing bores. |
| `T06_handle_strip` | 150 x 22 | BEARING | one template, used both sides. NOT a pocket - the handles are a webbing strap bolted to the rail surface. This locates the shallow milled facet the G10 strip beds into, and drills the two inserts. Strip centreline sits 223 mm off the board centreline, where the rail is at 12.7 mm thick stock; facet is only ~1.6 mm deep because the strip is narrow. |
| `T07_leash_pad` | 70 x 70 | BEARING | pad pocket; HOLES circle is the FCS plug bore, cut after the pad is bonded in. |
| `T08_station_07` | 377 x 146 | GAUGE | section at x = 100 mm (7% of length). Shape gauge, not a router template. |
| `T08_station_14` | 457 x 152 | GAUGE | section at x = 200 mm (14% of length). Shape gauge, not a router template. |
| `T08_station_21` | 504 x 154 | GAUGE | section at x = 300 mm (21% of length). Shape gauge, not a router template. |
| `T08_station_29` | 534 x 154 | GAUGE | section at x = 400 mm (29% of length). Shape gauge, not a router template. |
| `T08_station_36` | 551 x 154 | GAUGE | section at x = 500 mm (36% of length). Shape gauge, not a router template. |
| `T08_station_43` | 559 x 154 | GAUGE | section at x = 600 mm (43% of length). Shape gauge, not a router template. |
| `T08_station_50` | 559 x 154 | GAUGE | section at x = 700 mm (50% of length). Shape gauge, not a router template. |
| `T08_station_57` | 550 x 154 | GAUGE | section at x = 800 mm (57% of length). Shape gauge, not a router template. |
| `T08_station_64` | 530 x 154 | GAUGE | section at x = 900 mm (64% of length). Shape gauge, not a router template. |
| `T08_station_71` | 498 x 155 | GAUGE | section at x = 1000 mm (71% of length). Shape gauge, not a router template. |
| `T08_station_79` | 452 x 156 | GAUGE | section at x = 1100 mm (79% of length). Shape gauge, not a router template. |
| `T08_station_86` | 388 x 158 | GAUGE | section at x = 1200 mm (86% of length). Shape gauge, not a router template. |
| `T08_station_93` | 293 x 161 | GAUGE | section at x = 1300 mm (93% of length). Shape gauge, not a router template. |
| `T09_rocker_and_deck` | 1400 x 164 | GAUGE | centreline profile. Solid is the hull bottom (rocker), CHANNEL is the deck. Cut as two separate gauges or one long one. |

## The one number that is not from the model

`GUIDE_OFF = 5 mm` is the guide-bushing offset, and it depends on **your** bushing and cutter, not on the design. Every `BEARING` template above avoids it entirely by using a flush-trim bit instead - which is why they are all cut at finished size. Only the two seal-groove templates (parts 14 and 15, in `cnc/`) need it.

