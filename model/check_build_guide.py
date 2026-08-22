"""Verify every BOM line the build guide claims to use actually exists.

    python model/check_build_guide.py

docs/fabrication.md is hand-written - it is a guide, not a report - but it
quotes BOM item names verbatim in its "Uses:" lines. Nothing stops those from
going stale when a BOM line is renamed, and a build guide that sends you
looking for a part that is not on the list is worse than no guide.

This is the same failure the colour key died of: a hand-maintained file
mirroring generated state, drifting quietly, with nothing checking. That one
was 7 palette keys out of 30 wrong before anyone noticed. Here the check is
cheap, so there is no excuse for not running it.

Reports both directions:
  - guide references a BOM line that no longer exists  -> ERROR
  - BOM line that no step consumes                     -> listed, not an error
    (plenty of lines are tools, freight or tax and belong to no single step)
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GUIDE = os.path.join(ROOT, "docs", "fabrication.md")
BOM = os.path.join(ROOT, "docs", "bom.md")

# Lines that are not parts you pick up and use in a step.
NOT_A_STEP_ITEM = ("sales tax", "shipping", "customs", "import duty")


def bom_items():
    """Every item name in bom.md, with its markdown link stripped."""
    out = set()
    for line in io.open(BOM, encoding="utf-8"):
        if not line.startswith("|") or line.startswith("| **"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5 or cells[0] in ("Item", ""):
            continue
        name = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", cells[0])
        if set(name) <= set("- :"):            # table rules, not items
            continue
        try:                                   # skip zero-quantity lines
            if float(cells[4].replace("$", "").replace(",", "")) <= 0:
                continue
        except ValueError:
            pass
        out.add(name)
    return out


def guide_refs():
    """(item, step) for every backticked name on a Uses: line."""
    refs, step, inside = [], "?", False
    for line in io.open(GUIDE, encoding="utf-8"):
        m = re.match(r"#{2,3} Step (\S+)\.", line)
        if m:
            step = m.group(1)
        # A Uses: block is the "**Uses:**" line plus any continuation lines
        # that begin with a backtick. Tracking that explicitly, because
        # "starts with a backtick" alone also matched prose in the intro and
        # reported this very file as a missing BOM part.
        if "**Uses:**" in line:
            inside = True
        elif inside and not line.startswith("`"):
            inside = False
        if not inside:
            continue
        for item in re.findall(r"`([^`]+)`", line):
            # Filter on SHAPE, not length. A "longer than 12 chars" guard was
            # here to skip inline code like `4a`, and it silently dropped
            # "Loctite 242" - eleven characters, and a real BOM line - which
            # then showed up as an unclaimed part. Item names contain a
            # space; identifiers and filenames do not.
            if " " in item and not item.endswith((".py", ".md")):
                refs.append((item, step))
    return refs


def main():
    items, refs = bom_items(), guide_refs()
    missing = [(i, s) for i, s in refs if i not in items]
    used = {i for i, _s in refs}
    orphan = sorted(i for i in items - used
                    if not any(k in i.lower() for k in NOT_A_STEP_ITEM))

    print(f"build guide references {len(refs)} BOM lines "
          f"({len(used)} distinct) out of {len(items)}")
    if orphan:
        print(f"\n{len(orphan)} BOM lines no step claims - tools, spares and "
              f"consumables mostly, but worth a glance:")
        for i in orphan:
            print("   ", i[:66])
    if missing:
        print(f"\nERROR: {len(missing)} reference(s) match no BOM line:")
        for i, s in missing:
            print(f"    step {s}: {i}")
        return 1
    print("\nevery referenced line exists")
    return 0


if __name__ == "__main__":
    sys.exit(main())
