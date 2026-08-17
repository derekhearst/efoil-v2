# Snapshot — rail "A", rounded, chine aft

Taken before applying the three research-driven changes (chine extent, rail
apex, bottom vee). This is the state Derek said he liked the look of.

## Hull shape
| param | value |
|---|---|
| LENGTH x WIDTH x THICK | 1400 x 600 x 144.9 |
| DECK_WIDTH_F | 0.72 |
| BOT_WIDTH_F | 0.88 |
| RAIL_APEX | 0.42  (rounded, mid-height apex) |
| BOTTOM_VEE / VEE_MAX_F | 16.0 / 0.12 |
| CHINE_HARD_X0 / X1 | 0.30 / 0.62 |
| CHINE_HARD_DEG / SOFT_DEG | 72 / 3 |
| N_TAIL / N_NOSE | 2.30 / 1.90 |

## Reported state
FAILS: none - interference: none
displacement 97.93 L - board 24.7 kg - rig 32.0 kg
net float -20.1 kg - deck 40 mm under
CG 47.1% from tail - cavity 527 x 306 x 89

## Restore
    cp snapshots/2026-08-12-railA-rounded/blender_board.py model/
