"""Trace real eFoil board silhouettes out of manufacturer ortho renders.

Reads a 3-view product image (deck / bottom / side, all to the same scale),
splits it into the three views, and extracts:

  * planform  - half width vs station, normalised
  * profile   - thickness vs station, plus the deck and bottom rocker lines

Everything is reported with station 0 = tail, 1 = nose, so it drops straight
into blender_board.py's parameter space.
"""
import json
import sys

import numpy as np
from PIL import Image

N = 41  # stations reported


def load_mask(path):
    im = Image.open(path).convert("RGBA")
    a = np.asarray(im).astype(np.float32) / 255.0
    alpha = a[..., 3]
    rgb = a[..., :3]
    # Product renders sit on transparency with a soft drop shadow underneath.
    # Keep only near-opaque pixels, and drop the grey shadow by requiring the
    # pixel to be either bright (white hull) or dark (carbon rail) but not the
    # low-contrast shadow grey.
    solid = alpha > 0.85
    return solid, rgb


def column_groups(mask, min_w=40, min_h=4):
    on = mask.sum(axis=0) > min_h
    groups, s = [], None
    for i, v in enumerate(on):
        if v and s is None:
            s = i
        elif not v and s is not None:
            if i - s > min_w:
                groups.append((s, i))
            s = None
    if s is not None and len(on) - s > min_w:
        groups.append((s, len(on)))
    return groups


def extents(mask, x0, x1, n=N):
    """Per-station min/max extent across a single view.

    Station 0 is the *bottom* of the image (tail), 1 is the top (nose).
    """
    sub = mask[:, x0:x1]
    rows = np.where(sub.any(axis=1))[0]
    ytop, ybot = int(rows[0]), int(rows[-1])
    lo, hi, mid = [], [], []
    for k in range(n):
        y = int(round(ybot - (ybot - ytop) * k / (n - 1)))
        r = np.where(sub[y])[0]
        if len(r) == 0:
            lo.append(np.nan); hi.append(np.nan); mid.append(np.nan)
        else:
            lo.append(float(r[0])); hi.append(float(r[-1]))
            mid.append(0.5 * (r[0] + r[-1]))
    return dict(px_len=ybot - ytop + 1, lo=np.array(lo), hi=np.array(hi),
                mid=np.array(mid))


def area_fraction(mask, x0, x1):
    sub = mask[:, x0:x1]
    rows = np.where(sub.any(axis=1))[0]
    cols = np.where(sub.any(axis=0))[0]
    box = (rows[-1] - rows[0] + 1) * (cols[-1] - cols[0] + 1)
    return float(sub.sum()) / float(box)


def main(path, length_mm, width_mm, thick_mm, volume_L):
    mask, _ = load_mask(path)
    groups = column_groups(mask)
    if len(groups) < 3:
        print("expected 3 views, found", len(groups), groups)
        return
    # widest two views are deck/bottom, narrowest is the side profile
    widths = [g[1] - g[0] for g in groups]
    side_i = int(np.argmin(widths))
    plan_i = [i for i in range(len(groups)) if i != side_i][0]

    plan = extents(mask, *groups[plan_i])
    side = extents(mask, *groups[side_i])

    px_per_mm = plan["px_len"] / length_mm
    w_px = np.nanmax(plan["hi"] - plan["lo"] + 1)
    t_px = np.nanmax(side["hi"] - side["lo"] + 1)

    out = {
        "board": dict(length_mm=length_mm, width_mm=width_mm,
                      thick_mm=thick_mm, volume_L=volume_L),
        "scale_check": {
            "width_from_px_mm": round(w_px / px_per_mm, 1),
            "thick_from_px_mm": round(t_px / px_per_mm, 1),
        },
        "planform_area_fraction": round(area_fraction(mask, *groups[plan_i]), 4),
        "profile_area_fraction": round(area_fraction(mask, *groups[side_i]), 4),
    }

    stations = np.linspace(0.0, 1.0, N)
    halfw = (plan["hi"] - plan["lo"] + 1) / w_px
    thick = (side["hi"] - side["lo"] + 1) / t_px
    # side view: hi = bottom of board in image = board's underside
    bottom = (side["hi"] - np.nanmin(side["hi"])) / t_px
    deck = (side["hi"] - side["lo"]) / t_px

    out["stations"] = [round(float(s), 3) for s in stations]
    out["halfwidth_norm"] = [round(float(v), 4) for v in halfw]
    out["thickness_norm"] = [round(float(v), 4) for v in thick]
    out["rocker_norm"] = [round(float(v), 4) for v in bottom]

    # derived design numbers
    i_wide = int(np.nanargmax(halfw))
    i_thick = int(np.nanargmax(thick))
    out["derived"] = {
        "wide_point_station": round(stations[i_wide], 3),
        "thick_point_station": round(stations[i_thick], 3),
        "width_at_tail": round(float(halfw[0]), 3),
        "width_at_nose": round(float(halfw[-1]), 3),
        "thick_at_tail": round(float(thick[0]), 3),
        "thick_at_nose": round(float(thick[-1]), 3),
        "bbox_fill_pct": round(volume_L * 1e6
                               / (length_mm * width_mm * thick_mm) * 100, 1),
    }
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]),
         float(sys.argv[4]), float(sys.argv[5]))
