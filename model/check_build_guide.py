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

So: every number-with-a-unit in the prose has to appear somewhere in
report.json or bom_stats.json, or be listed in NOT_FROM_MODEL below with a
reason. This started as bolded-only - the bold being the author saying "this
figure matters" - and the unbolded sweep that followed found three more:
a bung holding at "280 N against 28 N - 10.7x" that the model puts at
253/37/6.8x, a lid seat table whose first two rows were 2.67 and 1.35 MPa
against 1.92 and 2.06, and a README open question still telling you to go buy
a cutter that has been in the BOM for months. Unbolded numbers are where the
stale ones hide, precisely because nobody thought they mattered enough to
bold.

The cost of that reach is an allowlist, and the allowlist is the load-bearing
part: V1 measurements, bought-part sizes, numbers quoted AS history, and
worked arithmetic in comparison tables are all legitimately not ours. Each
entry carries a reason. If you find yourself adding one without being able to
write the reason, the number is probably stale.

Reports three directions:
  - guide references a BOM line that no longer exists  -> ERROR
  - prose states a number the model does not know      -> ERROR
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

# Figures that are deliberately NOT model-derived. Each one needs a reason,
# because "add it to the allowlist" is how a check like this dies.
NOT_FROM_MODEL = {
    67.2: "the charger's own nameplate - an external spec, not ours",
    58.8: "the WRONG charger, quoted so it can be recognised and avoided",
    3.65: "Li-ion cell full charge, a chemistry constant",
    3.6: "Li-ion nominal cell voltage, same",
    2.5: "the fallback groove cutter's diameter, a bought size",
    1.5: "generic - ratios, clearances, hand measurements",
    0.5: "generic",
    1.3: "three-sheet shortfall, printed from blank_three_sheets_short_by_mm",
    # --- bought parts. These are sizes somebody else chose. ---------------
    1.25: "JST GH 1.25 mm - a connector SERIES NAME, not a measurement",
    3.175: "1/8 in, the spare silicone cord size",
    2438: "the EPS sheet's own 8 ft length",
    1219: "the EPS sheet's own 4 ft width",
    # --- the shop, not the board -----------------------------------------
    110: "gantry clearance the split sequence needs - an ask of the shop, "
         "not an output of the model",
    1420: "EPS layer oversize cut - a build allowance, not a part dimension",
    580: "the same, across",
    171: "M5 rod cut length - a build instruction",
    # --- V1. It is a built board; its numbers are MEASUREMENTS, and the
    # README's whole left-hand column is there to be compared against. ----
    1600: "V1 length, measured", 153: "V1 thickness, measured",
    660: "V1 cavity length", 280: "V1 cavity width", 115: "V1 cavity depth",
    2268: "V1 pack energy, 14S9P", 5.22: "V1 ply lid crush, measured",
    # --- superseded numbers quoted AS history, on purpose -----------------
    2.63: "the mast margin before the M6 correction - quoted to be corrected",
    11.4: "three-sheet shortfall when the four-layer call was taken",
    9.75: "rubber at the sides of the old O26 bung",
    365: "the ring area of a foam stop that was never built",
    1.72: "what that stop would have carried - reasoning about a non-part",
    2.25: "pocket-vs-disc clearance from the counterbore era",
    800: "V1's M4 x 8 insert, the catalogue figure the tau back-solve uses",
    1086: "M5 x 9.5 insert option, not taken", 1860: "M6 x 12.7, not taken",
    1250: "M4 preload at 1.0 Nm - worked arithmetic in a warning table",
    2500: "M4 preload at 2.0 Nm, the pull-it-out case",
    299: "shear strain in a bond line that is being argued AGAINST",
    200: "PVC pack wrap lay-flat width - a bought size",
    13.2: "kN of thread capacity, printed from mast_thread_cap_N in newtons",
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
        # NOTE what is NOT here: digits scraped out of report STRINGS. That
        # was the first version, and it made the known-set a soup - any claim
        # matching any digit-sequence in any sentence anywhere passed. Turning
        # it off cost four report keys, which is the right trade: the hatch
        # lid's finished thickness, the seal groove depth, the flange depth
        # and the wire bay length were all quoted in the guide and published
        # only inside prose. They are real numbers and they are keys now. If
        # this check ever demands another, publish it rather than loosening
        # this back up.

    walk(json.load(io.open(REPORT, encoding="utf-8")))
    # bom.py's numbers are a second contract - the README quotes its cost,
    # its verified percentage and its line counts, and blender_board.py has
    # never known any of them.
    if os.path.exists(BOMSTATS):
        walk(json.load(io.open(BOMSTATS, encoding="utf-8")))
    return vals


# The multiplication sign counts as a unit for BOLDED claims: "**17 x O12
# through the core**" is a claim about a count, and a count is exactly the
# sort of thing that goes stale when a bolt ring is regenerated.
#
# It is left OUT of the unbolded pass, because there it matches every "1.79x"
# margin in the file. A margin is arithmetic on two numbers this already
# checks, so flagging it adds noise and catches nothing new.
UNIT_BOLD = r"(?:mm|MPa|Nm|kg|Wh|kN|N|A|V|W|%|x|×|in)(?![a-zA-Z])"
# A, V, W and `in` are OUT of the unbolded set. They are ordinary English
# words or single letters, and they matched "6061 in a 12.7 plate" and
# "20-200 in-lb" as though those were dimensions. Bolded text is deliberate
# enough to keep them; running prose is not.
UNIT_PLAIN = r"(?:mm|MPa|Nm|kN|kg|Wh|N|%)(?![a-zA-Z])"
CLAIM = re.compile(r"\*\*(\d+(?:\.\d+)?)\s*" + UNIT_BOLD)
# Unbolded, with commas allowed - "2,304 Wh" was being read as "304 Wh", which
# is how a stale pack energy would have slipped through unnoticed.
PLAIN = re.compile(r"(?<![\w.$-])(\d[\d,]*(?:\.\d+)?)\s*(" + UNIT_PLAIN + ")")
# Prefix scales, so a claim in kN can be checked against a value in N. The
# plate "carries 6.3 kN" against a modelled 6274 N: same number, and an
# exact-match test would have called it stale forever.
SCALE = {"kN": 1000.0}
# ~~struck through~~ - superseded, and exempt. See stale_numbers().
STRUCK = re.compile(r"~~.*?~~")
# ...and BOLDED MONEY, separately, because a dollar sign is not a unit and the
# pattern above walked straight past "**$3,917/board**" - which was $123 out
# by the time anyone looked. Cost is the most-quoted number in the repo, so it
# gets its own pattern rather than relying on someone writing a unit after it.
MONEY = re.compile(r"\*\*\$([\d,]+(?:\.\d+)?)")


def stale_numbers():
    """Figures in the prose that trace to nothing the scripts compute."""
    vals = model_numbers()
    out = []
    for path in PROSE:
        short = os.path.basename(path)
        for i, line in enumerate(
                io.open(path, encoding="utf-8").read().split("\n"), 1):
            # STRUCK-THROUGH TEXT IS EXEMPT, and this is the escape hatch to
            # reach for instead of NOT_FROM_MODEL. ~~68 mm~~ is the author
            # saying "this was true and is not" in markdown's own vocabulary,
            # it renders as the reader seeing the same thing, and it is scoped
            # to the one sentence - where an allowlist entry silently exempts
            # that number everywhere in both files forever.
            line = STRUCK.sub("", line)
            for rx in (CLAIM, MONEY, PLAIN):
                for m in rx.finditer(line):
                    raw = m.group(1).rstrip(",")
                    unit = m.group(2) if rx is PLAIN else ""
                    n = round(float(raw.replace(",", "")), 2)
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
                    #
                    # The kN case goes through the SAME precision rule, not a
                    # fixed one: "6.3 kN" against a modelled 6274 N is
                    # 6.274 rounded to a tenth, which agrees. Rounding it to
                    # two places instead gave 6.27 and reported the guide
                    # stale against a number it had right.
                    dp = len(raw.split(".")[1]) if "." in raw else 0
                    sc = SCALE.get(unit, 1.0)
                    if any(round(v / sc, dp) == n or round(v, dp) == n
                           for v in vals):
                        continue
                    out.append((f"{short}:{i}", m.group(0),
                                line.strip()[:70]))
    return out


def main():
    # This tool READS UTF-8 prose and PRINTS the offending line back, so on a
    # cp1252 console any finding containing an em-dash or a >= sign killed the
    # run with a UnicodeEncodeError - the check crashing on the very text it
    # exists to inspect, and exiting non-zero for the wrong reason.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
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
    print("\nevery referenced line exists, and every numeric claim - bolded "
          "or not - traces to the model")
    return 0


if __name__ == "__main__":
    sys.exit(main())
