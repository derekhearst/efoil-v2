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

It also checks the guide's NUMBERS, which drift the same way and cost more.
A guide that quotes a torque, a squeeze or a bolt force the model no longer
computes reads exactly as authoritative as one that is right. Found by hand
in one sweep: a bung "6.35 mm proud" that is 4.0, "113 N a bolt" that is 159,
a caul standing "100.1 mm" against a drawing that cuts it 85.8, a blank
envelope of 166.8 against 153.7, handles on "110 mm centres" against 152.6,
and four separate report strings still calling Gong's M6 screws M8 months
after that was corrected everywhere a builder would look.

So: every BOLDED number-with-a-unit in the guide has to appear somewhere in
report.json, or be listed in NOT_FROM_MODEL below with a reason. Bolded, not
every number - the bold is the author saying "this figure matters", which is
exactly the set worth binding to the model. Prose arithmetic and worked
examples stay free.

Reports three directions:
  - guide references a BOM line that no longer exists  -> ERROR
  - guide bolds a number the model does not know       -> ERROR
  - BOM line that no step consumes                     -> listed, not an error
    (plenty of lines are tools, freight or tax and belong to no single step)
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GUIDE = os.path.join(ROOT, "docs", "fabrication.md")
BOM = os.path.join(ROOT, "docs", "bom.md")
REPORT = os.path.join(ROOT, "model", "report.json")
BOMSTATS = os.path.join(ROOT, "model", "bom_stats.json")
# README.md is checked too. It is the front door and the most-read file in the
# repo, and it was carrying a mast plate "M8 tapped, 2.6x margin" months after
# both halves of that were corrected everywhere else, plus a stale board mass,
# displacement, cavity size, cost and line count. Nothing was watching it.
PROSE = (os.path.join(ROOT, "docs", "fabrication.md"),
         os.path.join(ROOT, "README.md"))

# Bolded figures that are deliberately NOT model-derived. Each one needs a
# reason, because "add it to the allowlist" is how a check like this dies.
NOT_FROM_MODEL = {
    67.2: "the charger's own nameplate - an external spec, not ours",
    58.8: "the WRONG charger, quoted so it can be recognised and avoided",
    3.65: "Li-ion cell full charge, a chemistry constant",
    2.5: "the fallback groove cutter's diameter, a bought size",
    1.5: "generic - ratios, clearances, hand measurements",
    0.5: "generic",
    1.3: "three-sheet shortfall, printed from blank_three_sheets_short_by_mm",
}
# Small integers and round figures carry no information - they are counts,
# ratios, page numbers and hand measurements, not model output.
GENERIC = set(range(0, 13)) | {
    14, 15, 16, 18, 20, 24, 25, 30, 40, 45, 50, 60, 90, 100, 120, 180, 250,
    300, 360, 500, 1000}

# Lines that are not parts you pick up and use in a step.
NOT_A_STEP_ITEM = ("sales tax", "shipping", "customs", "import duty")


def bom_items():
    """Every item name in bom.md, with its markdown link stripped.

    TWO SETS, because the file answers two different questions with them.

    "Does this guide reference a line that exists?" has to count ON-HAND
    lines: something you already own is still consumed by a step, and a $0
    row is not an absent row. Skipping them made the first guide reference to
    an on-hand item - the hollow punch - fail against a line sitting right
    there in bom.md.

    "Is there a BOM line no step claims?" should NOT count them, because that
    report is about unaccounted SPEND, and an on-hand line is not spend.
    """
    out, spend = set(), set()
    for line in io.open(BOM, encoding="utf-8"):
        if not line.startswith("|") or line.startswith("| **"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5 or cells[0] in ("Item", ""):
            continue
        name = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", cells[0])
        if set(name) <= set("- :"):            # table rules, not items
            continue
        out.add(name)
        try:
            if float(cells[4].replace("$", "").replace(",", "")) > 0:
                spend.add(name)
        except ValueError:
            spend.add(name)                    # unparseable: treat as spend
    return out, spend


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


def model_numbers():
    """Every number the model knows, including ones embedded in its strings."""
    vals = set()

    def add(x):
        try:
            vals.add(round(float(x), 2))
        except (TypeError, ValueError):
            pass

    def walk(v):
        if isinstance(v, bool):
            return
        if isinstance(v, (int, float)):
            add(v)
        elif isinstance(v, dict):
            for x in v.values():
                walk(x)
        elif isinstance(v, (list, tuple)):
            for x in v:
                walk(x)
        elif isinstance(v, str):
            for m in re.findall(r"-?\d+(?:\.\d+)?", v):
                add(m)

    walk(json.load(io.open(REPORT, encoding="utf-8")))
    # bom.py's numbers are a second contract - the README quotes its cost,
    # its verified percentage and its line counts, and blender_board.py has
    # never known any of them.
    if os.path.exists(BOMSTATS):
        walk(json.load(io.open(BOMSTATS, encoding="utf-8")))
    return vals


# The multiplication sign counts as a unit: "**17 x O12 through the core**"
# is a claim about a count, and a count is exactly the sort of thing that
# goes stale when a bolt ring is regenerated.
UNIT = r"(?:mm|MPa|Nm|kg|Wh|kN|N|A|V|%|x|×|in)(?![a-zA-Z])"
CLAIM = re.compile(r"\*\*(\d+(?:\.\d+)?)\s*" + UNIT)
# ...and BOLDED MONEY, separately, because a dollar sign is not a unit and the
# pattern above walked straight past "**$3,917/board**" - which was $123 out
# by the time anyone looked. Cost is the most-quoted number in the repo, so it
# gets its own pattern rather than relying on someone writing a unit after it.
MONEY = re.compile(r"\*\*\$([\d,]+(?:\.\d+)?)")


def stale_numbers():
    """Bolded figures in the prose that trace to nothing the scripts compute."""
    vals = model_numbers()
    out = []
    for path in PROSE:
        short = os.path.basename(path)
        for i, line in enumerate(
                io.open(path, encoding="utf-8").read().split("\n"), 1):
            for rx in (CLAIM, MONEY):
                for m in rx.finditer(line):
                    raw = m.group(1).replace(",", "")
                    n = round(float(raw), 2)
                    if n in vals or n in GENERIC or n in NOT_FROM_MODEL:
                        continue
                    # ROUNDING IS NOT STALENESS. Prose says "$4,040/board" and
                    # "23.6 kg"; the scripts hold 4039.76 and 23.63. Demanding
                    # an exact hit would push every honest round number into
                    # NOT_FROM_MODEL, and an allowlist that fills up with
                    # false positives stops being read. So a claim matches if
                    # ANY known value rounds to it AT THE CLAIM'S OWN
                    # PRECISION - "143.7" has to agree to a tenth, "4040" only
                    # to the unit, which is exactly how much each one asserts.
                    dp = len(raw.split(".")[1]) if "." in raw else 0
                    if any(round(v, dp) == n for v in vals):
                        continue
                    out.append((f"{short}:{i}", m.group(0),
                                line.strip()[:70]))
    return out


def main():
    (items, spend), refs = bom_items(), guide_refs()
    stale = stale_numbers()
    missing = [(i, s) for i, s in refs if i not in items]
    used = {i for i, _s in refs}
    orphan = sorted(i for i in spend - used
                    if not any(k in i.lower() for k in NOT_A_STEP_ITEM))

    print(f"build guide references {len(refs)} BOM lines "
          f"({len(used)} distinct) out of {len(items)}, "
          f"{len(spend)} of which are spend")
    if orphan:
        print(f"\n{len(orphan)} BOM lines no step claims - tools, spares and "
              f"consumables mostly, but worth a glance:")
        for i in orphan:
            print("   ", i[:66])
    if stale:
        print(f"\nERROR: {len(stale)} bolded figure(s) the model does not "
              f"know. Either the guide has gone stale, or the number is "
              f"genuinely not ours and belongs in NOT_FROM_MODEL WITH A "
              f"REASON - an unreasoned allowlist is how a check like this "
              f"quietly stops checking:")
        for ln, tok, ctx in stale:
            print(f"    {ln:26} {tok:12} |  {ctx}")
    if missing:
        print(f"\nERROR: {len(missing)} reference(s) match no BOM line:")
        for i, s in missing:
            print(f"    step {s}: {i}")
    if missing or stale:
        return 1
    print("\nevery referenced line exists, and every bolded figure "
          "traces to the model")
    return 0


if __name__ == "__main__":
    sys.exit(main())
