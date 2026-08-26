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

## The one number that is not from the model

`GUIDE_OFF = 5 mm` is the guide-bushing offset, and it depends on **your** bushing and cutter, not on the design. Every `BEARING` template above avoids it entirely by using a flush-trim bit instead - which is why they are all cut at finished size. Only the two seal-groove templates (parts 14 and 15, in `cnc/`) need it.

