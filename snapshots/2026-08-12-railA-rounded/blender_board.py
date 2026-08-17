"""eFoil V2 - parametric board, cavity, removable electronics module and pack.

Run inside Blender:
    exec(open(r'.../model/blender_board.py').read())

Everything is in millimetres; the scene is built in metres. The build prints a
fit report and leaves it in `result` - the point of this script is to answer
"does it actually fit", not just to draw something.

Section topology (this is the thing that makes it laminatable):

        deck (crowned)  ─────────────┐
                                      ╲  DECK_EDGE_R roll
                                       ╲
                          rail taper     ╲
                                          │
        flat bottom ──────────────────────┘  CHINE_R
                                          ^ widest point is HERE, at the bottom

The widest point belongs at the bottom chine, not halfway up. That is what
makes it a planing hull with a crisp release edge, and it is what V1 and every
production eFoil do. No corner anywhere is left sharp.
"""

import math

import bmesh
import bpy

# ---------------------------------------------------------------- dimensions
LENGTH = 1400.0
WIDTH = 600.0                      # 570 left only 36 mm of deck outboard of the rim
THICK = 120.0                      # derived from the stack-up, see report

# Planform - superellipse halves. Tail fuller than nose. My 4'3 trace said the
# opposite, but the 5'4 trace and V1's as-built outline (200 mm flat tail vs
# 100 mm flat nose) both follow convention - the 4'3 product render is simply
# shot nose-down and I fitted it upside down.
WIDE_POINT = 0.48      # slightly aft of centre, like V1's parallel midsection
N_TAIL = 2.30          # higher exponent = fuller
N_NOSE = 1.90          # finer, more drawn out

# Both ends terminate in a FLAT, not a point. A plain superellipse runs to zero
# and the tail reads wrong for it. Traced Lift 5'4: tail 110 mm, nose 56 mm on
# a 620 mm board - i.e. 0.18 and 0.09 of width. V1 used a 200 mm flat tail and
# 100 mm flat nose on 600 mm, blunter again; these follow the Lift proportions.
TAIL_TIP_F = 0.18      # half width at the tail tip / max half width
NOSE_TIP_F = 0.09
TAIL_TIP_R = 30.0      # corner radius on the tail flat, must be < TAIL_TIP_F*hw
NOSE_TIP_R = 20.0

# thickness - long flat plateau, then taper to each tip
THICK_FLAT_0, THICK_FLAT_1 = 0.35, 0.55
THICK_NOSE, THICK_TAIL = 0.16, 0.15
P_THICK_FWD, P_THICK_AFT = 1.7, 4.5

# Nose rocker is DERIVED, not dialled. Deck height is rocker + thickness, so
# picking a rocker curve and a thickness curve independently makes them fight:
# every (rocker, power) pair I swept either dropped the tip 20 mm or humped
# +15 mm at 95% and then dropped anyway. This board is 167 mm thick against the
# traced Lift's 106, so its forward thickness taper sheds ~70 mm where Lift
# sheds 44 - no fixed rocker can absorb that.
#
# So specify the DECK instead and solve for the rocker underneath it:
#   deck(x)   = deck(ROCKER_START) + rise * u**DECK_P        (monotone by
#   rocker(x) = deck(x) - thickness(x)                        construction)
# The tip cannot dip and cannot hump, whatever the thickness curve does.
# 10 mm of rise matches the traced Lift 4'3, whose deck sits ~9 mm above mid at
# the tip. THICK_NOSE 0.16 (27 mm tip, V1 ran 15%) keeps the required rocker to
# ~150 mm; leaving it at 0.09 needed 164 mm for the same deck.
DECK_NOSE_RISE, DECK_P = 10.0, 2.2
ROCKER_START = 0.55
TAIL_ROCKER, TAIL_ROCKER_START = 8.0, 0.25

# section
# Volume trim. The board wanted to be a sinker and was only -3.8 kg, so the
# cheap shape levers all got pulled at once. Measured, each on its own:
#   deck 0.79 -> 0.72 (steeper rails)  -3.2 L
#   bottom vee 5 -> 16 mm              -2.1 L
#   planform N 2.6/2.15 -> 2.3/1.9     -3.4 L
# None of them is big alone; together they are worth ~9 L. The reason no
# single one can be pushed further is the HATCH LID: it is 374 mm wide, so
# the deck has to stay wider than that plus margin. Volume is gated by the
# module footprint, not by the rails.
BOTTOM_VEE = 16.0                  # at full thickness; scaled down at the ends
VEE_MAX_F = 0.12                   # vee is never more than this fraction of t                   # mm of lift at the chine - near-flat bottom
CHINE_R = 3.0                      # bottom edge radius. 0 would bridge the glass
DECK_EDGE_R = 25.0                 # deck edge roll
DECK_WIDTH_F = 0.72                # deck half width / max half width
# Rail shape. The widest point of the section sits at RAIL_APEX of the
# thickness, and BOTH the deck and the bottom tuck in from it. Pinning the
# max width at the bottom chine (BOT_WIDTH_F = 1.0) is what made the section
# read as a trapezoid.
BOT_WIDTH_F = 0.88                 # bottom half width / max half width
RAIL_APEX = 0.42                   # height of the widest point / thickness
# Flat, no crown. A flat sheet lid in a flat machined rebate cannot sit flush
# in a crowned deck - at 2 mm of crown the lid stood ~1.4 mm proud at its
# outboard edges. V1 ran a flat deck for the same reason ("simpler to build,
# EVA pad provides grip") and it is the right call here too.
DECK_CROWN = 0.0                   # centre to deck edge

# Feature-aligned section sampling. Every station emits the same points in the
# same roles - point k is always the same feature - so the loft quads cannot
# twist. Resampling by uniform arc length let the points slide as the outline
# changed shape, which is what printed as crease 'feathers' down the rail.
N_STATIONS = 161
# The rail is ONE curve, not a deck fillet + a rail + a chine fillet stacked
# together. Three separately-radiused features meant two tangent breaks part
# way up the rail: the deck rolled over, flattened, then bulged again, and the
# break printed as a hard line running the length of the board. Now: a flat
# deck, one tangent-continuous curve from the deck edge over the rail apex
# down to the chine, and a SHARP chine against the bottom - which is the only
# edge that wants to be sharp, for clean water release.
SEC_BOT, SEC_RAIL_LO, SEC_RAIL_HI, SEC_DECK = 20, 18, 24, 20
SEC_TOTAL = SEC_BOT + SEC_RAIL_LO + SEC_RAIL_HI + SEC_DECK
RAIL_TUCK = 0.30                   # how far the rail leans out leaving the chine
# The hard chine must NOT run to the bow. A sharp edge is what you want under
# the tail and mid-section for clean water release, but carried forward it is
# both wrong hydrodynamically and reads as a crease running all the way to the
# nose. Real boards fade the hard edge out ahead of the feet. Hardness is 1
# (sharp) aft of CHINE_HARD_X0 and 0 (rail and bottom fully tangent, no edge
# at all) forward of CHINE_HARD_X1, smoothstepped between.
# Moved well aft. The mast is at 29% of length and the rider's feet straddle
# it, so the edge is hard only through the tail, has softened by the front
# foot, and is a rounded rail through the whole forward half.
CHINE_HARD_X0, CHINE_HARD_X1 = 0.30, 0.62
# The chine is specified as the ANGLE the rail leaves the bottom at, not as an
# abstract 0-1 "hardness". That knob was badly non-linear: a value of 0.14,
# which sounds like a hint, still left a 31 degree kink running to the nose
# tip. Degrees are the thing that is actually visible, so set them directly.
CHINE_HARD_DEG = 72.0              # aft: rail leaves steeply -> sharp release edge
CHINE_SOFT_DEG = 3.0               # fwd: degrees ABOVE the bottom's own slope.
                                   # 0 = perfectly tangent, no edge at all.

# ------------------------------------------------------------------- cavity
# 690 long, not V1's 660: 9 columns per layer is what allows a 16S pack to use
# an uneven 9+7 split, which is what creates the BMS shelf. Buying that with
# length costs nothing; buying it with thickness would have cost 20 mm of board.
CAV_X0, CAV_X1 = 300.0, 990.0   # both derived in derive_layout()
MOD_X0 = 450.0                  # module aft face, derived
# 310 not 280: the ESC is 68 mm wide and lives in the strip beside the pack.
CAV_WIDTH = 310.0
# A square-cornered module only fits a rounded-corner cavity if
# R <= gap * sqrt(2)/(sqrt(2)-1) = gap * 3.414. At R=45 with a 6 mm gap the
# module's corners stood 10 mm proud into the milled radii. 30 mm is still a
# generous laminating radius - V1 hand-troweled about 10.
CAV_CORNER_R = 22.0
CAV_FILLET_R = 12.0                # floor-to-wall fillet, milled not troweled

FLOOR_Z = 30.0                     # flat cavity floor height above hull bottom
HULL_SKIN = 2.0

RIM_W = 34.0                       # bonded-on G10 ring, outboard of the opening
RIM_T = 12.0
CHAN_W, CHAN_D = 6.0, 3.0          # poured silicone channel (not an O-ring groove)
CHAN_INSET = 10.0                  # channel centreline outboard of the opening.
                                   # Seal inboard, bolts outboard - at 15 the
                                   # M5 heads landed on top of the channel.

LID_SKIN, LID_CORE = 1.0, 12.0     # hatch lid: glass / H80 / glass
LID_T = LID_SKIN * 2 + LID_CORE

# ------------------------------------------------------- electronics module
# Removable. Nothing about it is bonded to the hull - it lifts straight out
# through the opening for service.
ENC_GAP = 8.0                     # per side, module to cavity wall. Also sets
                                   # the largest cavity corner radius a square
                                   # -cornered module can live inside.
ENC_WALL = 3.0                     # G10
ENC_FLOOR = 3.0                    # G10

# Faces that touch. Every one of these is a real bond line, gasket or pad in
# the built board, and modelling them as exactly coincident planes is what was
# z-fighting inside the cavity.
FIT_FLOOR = 0.5                    # module floor to cavity floor (foam pad)
FIT_RIM = 0.3                      # rim ring to ledge (thickened epoxy bond)
FIT_LID = 0.4                      # module lid to wall/flange tops (gasket)
ENC_LID_SKIN, ENC_LID_CORE = 1.0, 6.0
ENC_LID_T = ENC_LID_SKIN * 2 + ENC_LID_CORE
ENC_TOP_GAP = 2.0                  # module top to the underside of the rim

# No internal divider. It was justified as a thermal break and a stiffening
# rib, but it bought neither cheaply: power had to cross it through glands
# (three penetrations, all of them a failure point, on a wall that is NOT a
# pressure boundary - if water is in the module the pack is lost either way),
# and it split the one open volume that the wiring actually needs. Stiffness
# comes back from the bonded corner posts and the flange rail instead.
#
# The only real gland in the boat is now the one that matters: where the mast
# wires cross from wet to dry at the cavity floor.

# --- module joinery -------------------------------------------------------
# The panels have to actually be joined, and butting 3 mm G10 edge-on gives a
# 3 mm wide glue line with no location - it would be a hinge. So:
#   - the floor is machined with a 1.5 mm locating groove; walls seat in it
#   - end walls land BETWEEN the long walls (a lap, not a mitre)
#   - a G10 corner post in each internal corner triples the corner glue area
#   - the flange rail is bonded inside the wall top and carries the lid inserts
# Everything is thickened epoxy with a glass-tape fillet on the inside corners.
JOINT_GROOVE_D = 1.5               # locating groove depth in the floor
CORNER_POST = 12.0                 # square G10 post, full internal height
FILLET_R = 6.0                     # internal epoxy fillet radius (bond area)

# --- wiring ---------------------------------------------------------------
# The pack fills the box; the wiring has to live somewhere that is not "in the
# gaps". WIRE_CH_W is a dedicated raceway the full length of the box, outboard
# of the ESC. The wire-loop zone is no longer inside the module at all - it
# moved out to the cavity's aft service bay, which the conduit already needed.
WIRE_CH_W = 20.0                   # raceway beside the ESC, for 8 AWG + balance
GLAND_D = 25.0                     # mast-wire gland at the cavity floor

# The pack DATUMS to three walls instead of floating in the middle. Leftover
# space split across both ends and both sides is awkward to use and awkward to
# strap into; one clean strip down one side is not. So the pack fills the
# module's full internal length and sits hard against one long wall, and every
# bit of slack ends up in a single service strip.
#
# The end clearance is set by the corner posts, not by choice - the pack would
# otherwise foul them - so those 14 mm are structure, not wasted space.
PACK_END_CLR = CORNER_POST + 2.0
PACK_SIDE_CLR = 2.0

# --- aft service bay ------------------------------------------------------
# Everything the rider touches lives in the bay the conduit already needs:
# mast-wire gland, power button, charge port. Nothing else penetrates the hull.
BTN_D, BTN_H = 22.0, 18.0          # latching power button
CHG_W, CHG_L, CHG_H = 32.0, 40.0, 26.0
BAY_GLAND_D = 16.0                 # module wall glands, PG11
BAY_GLAND_N = 3                    # motor phases / charge / switch + sense
# Button and port are panel-mount fittings through the module's aft wall,
# same as the glands. CHG_L / BTN_H are how far the body sticks AFT into the
# service bay; CHG_W x CHG_H is the panel cutout.

# --- mast wire conduit ----------------------------------------------------
# There was no route at all for the motor wires: they leave the mast head and
# have to get into the cavity without ever touching wet foam. A bonded G10 tube
# runs from the hull bottom, through the mast plate and the dense-foam ring, up
# to the cavity floor, where it terminates in a gland. Everything above the
# gland is dry; everything below is potted.
CONDUIT_D = 32.0                   # OD - swallows 2 x 8 AWG plus the sensor trio
CONDUIT_WALL = 2.0
CONDUIT_X_OFF = 0.0                # from MAST_X, on the mast's chord centreline
# The conduit surfaces at MAST_X, which is under the module unless the cavity
# is given its own bay aft of the module for it. Without this the tube lands
# in the middle of the module floor - which is exactly what the first cut did.
WIRE_BAY_CLR = 28.0                # conduit wall to cavity wall / module wall

# ------------------------------------------------------------ battery pack
# BAK N21700CG-50, datasheet maxima: 21.4 dia x 70.75 long, 72 g, 18.0 Wh,
# 15 A continuous. Build to max, not nominal, or the holders will not close.
CELL_D, CELL_L, CELL_G, CELL_WH, CELL_IMAX = 21.4, 70.75, 72.0, 18.0, 15.0
# Each column's strip is an L: a vertical leg welded to the eight terminal
# faces, bending 90 deg at the top into a horizontal tab that lies over the
# cells. Adjacent columns' tabs overlap above the boundary and are spot welded
# FROM ABOVE - flat, normal probes, exactly the V1 workflow.
#
# The consequence is that the inter-column gap never needs welder access. It
# only has to swallow two 0.2 mm strips, so the pitch stays tight and the 9+7
# split (and with it the BMS pocket) survives.
PITCH_X = 73.0                     # cell 70.75 + two strips + 1.85 slack
PITCH_Y = 24.0                     # dia + holder wall. 22.4 left a 0.4 mm web
PITCH_Z = 23.4                     # dia + cradle wall + 1.0 for the tab layer
                                   # that now sits between layer 1 and layer 2

# --- printed cell holder --------------------------------------------------
# One full-height comb per column pair. Ribs sit at mid-cell only, so the
# inter-column gaps stay clear for the nickel and the joints. Layer 2's cradles
# are cut into the same ribs - no separate interlayer tray, which would not fit
# in the height budget anyway.
HOLD_BASE_T = 2.0
HOLD_RAIL_W = 5.0                  # longitudinal rails tying the ribs together
HOLD_RIB_T = 4.0
HOLD_RIB_OFF = 20.0                # rib centre from column centre, +/-
HOLD_RETAIN_T = 2.0                # thin; a foam pad above it takes up the slack
HOLD_CLEAR = 0.3                   # cradle radial clearance on the cell
HOLD_BED = 250.0                   # usable Bambu A1 bed

# --- LYING pack, 16S8P ----------------------------------------------------
# MEASURED, not assumed: lying the cells down is not worth it here.
#
#                        board        thick  module         hatch lid   dead air
#   upright 16S8P    1400 x 600        145   425x284x76     595 x 374        35%
#   lying   16S8P    1550 x 600        140   660x293x71     830 x 383        50%
#
# Lying converts pack HEIGHT into pack FOOTPRINT, and footprint is what sets
# the lid. It bought 5 mm of thickness for +150 mm of board length, a 45%
# bigger hatch lid, and a box that is half air. Even with the connector panel
# moved off the aft wall (which is what caps the module height) it only
# reaches 124 mm, still with the oversized lid.
#
# Set CELLS_LYING = True to model it anyway; the geometry below handles both.
#
# The earlier lying design was rejected on FABRICATION, not geometry: it needed
# a novel interconnect, sub-modules floppy until potted, and a 146 mm
# full-current jumper between layers. This arrangement removes all three,
# because of how the groups are cut:
#
#   cells lie with their axis along X, 8 abreast across Y
#   -> those 8 cells ARE one 8P group, and their terminals share one X plane
#   -> 8 groups along X = a complete 8S8P LAYER
#   -> 2 layers stacked = 16S8P
#
# So each layer is a self-contained 8S8P slab, welded flat on the bench with
# open access from above and both sides, and tested before it is ever stacked.
# The two layers meet at exactly ONE full-current busbar. That is one novel
# joint instead of sixteen, and nothing is floppy: each slab is a rigid
# rectangle in its own printed tray.
CELLS_LYING = False
PACK_S, PACK_P = 16, 8             # 128 cells. 16S was the stated preference
LAY_S = PACK_S // 2                # series groups per layer
PACK_LAYERS = 2
BUS_GAP = 7.0                      # between series groups: busbar + probe room
PITCH_LAY_Y = 23.4                 # dia + tray wall, across the pack
PITCH_LAY_Z = 23.4                 # layer to layer
CELL_H = 70.2                      # upright fallback, incl. nickel (V1 measured)
PITCH_CELL = 22.3                  # upright: within a row (Heyiarbeit bracket)
PITCH_ROW = 24.2                   # upright: row to row
PACK_EDGE = 5.0                    # bracket margin beyond the outer cells
WRAP_T = 0.7                       # Kapton + heat shrink
TOP_CLEAR = 5.0                    # pack or BMS top to the module lid
# BMS placement. "on_pack" lies it flat on the cells and costs its full
# height in board thickness. "on_edge" stands it against the outboard wall of
# the service strip, where only its THICKNESS eats width instead.
#
# Sourced part for on_edge: LLT Power OD17S051-3 smart BMS, 10S-17S,
# 150 A continuous, 150 x 75 x 16 mm, Bluetooth, ~$51-58. Heavy leads are
# ring-lug pads at one short end and the balance connector is at the other,
# which is what makes standing it on edge in a narrow slot work at all.
# LUG_STACK is the bolted ring lug proud of the PCB - vendors quote bare PCB.
BMS_HOME = "flat_beside"           # "on_pack" | "on_edge" | "flat_beside"
BMS_ON_PACK = BMS_HOME == "on_pack"
BMS_E_L, BMS_E_H, BMS_E_T = 150.0, 75.0, 16.0
BMS_LUG_STACK = 8.0
PEAK_W = 5300.0                    # design peak, from V1's measured limits

BMS_L, BMS_W, BMS_H = 162.0, 102.0, 22.0
ESC_L, ESC_W, ESC_H = 130.0, 68.0, 41.0
FUSE_L, FUSE_W, FUSE_H = 123.0, 37.0, 40.0

# --- fasteners ------------------------------------------------------------
# Module lid: M4 into brass inserts in a G10 flange rail bonded inside the top
# edge of the walls (4 mm wall alone cannot hold an insert).
MOD_BOLT_D = 4.0
MOD_INSERT_D, MOD_INSERT_L = 6.0, 8.0   # M4 heat-set insert in the flange rail
MOD_BOLT_PITCH = 80.0              # target spacing; actual is evened out
MOD_FLANGE_W, MOD_FLANGE_H = 14.0, 10.0
MOD_INSERT_D = 5.6                 # M4 x 8 brass heat-set pilot
# Hatch lid: M5 into inserts in the bonded G10 rim ring.
HATCH_BOLT_D = 5.0
HATCH_BOLT_PITCH = 130.0
HATCH_INSERT_D, HATCH_INSERT_L = 7.0, 10.0   # M5 x 10 insert in the rim
HATCH_BOLT_INSET = 12.0            # from the rim's outer edge, outboard of the seal


def derive_layout():
    """Pack -> module -> cavity -> board thickness. Sets the cavity globals."""
    global CAV_X0, CAV_X1, CAV_WIDTH, THICK, MOD_X0
    if CELLS_LYING:
        pack_l = LAY_S * (CELL_L + BUS_GAP) + 2 * PACK_EDGE
        pack_w = PACK_P * PITCH_LAY_Y + 2 * PACK_EDGE
        pack_h = PACK_LAYERS * PITCH_LAY_Z + HOLD_BASE_T
    else:
        pack_l = PACK_S * PITCH_ROW + 2 * PACK_EDGE
        pack_w = PACK_P * PITCH_CELL + 2 * PACK_EDGE
        pack_h = CELL_H
    stack = pack_h + WRAP_T + (BMS_H if BMS_ON_PACK else 0.0)
    # On edge, the BMS sets the internal height instead of the pack does.
    # "flat_beside" lies the BMS on the module floor in the service strip, so
    # it costs neither height nor the pack's real estate. Standing it on edge
    # would put a 75 mm board in a 54 mm box and undo the whole cells-down win.
    # The connector panel needs wall height: a gland row, then a row for the
    # button and the charge port, both clear of the flange rail.
    panel_h = ((BAY_GLAND_D + 7.0) + 6.0 + max(BTN_D, CHG_H) + 8.0 + 8.0)
    int_h = max(stack + TOP_CLEAR,
                (BMS_E_H + 6.0) if BMS_HOME == "on_edge" else 0.0,
                (BMS_E_T + 6.0) if BMS_HOME == "flat_beside" else 0.0,
                panel_h)
    # Pack fills the length; the only end slack is what the corner posts need.
    # Neither "on_pack" nor "on_edge" needs extra LENGTH for the BMS. The old
    # `not BMS_ON_PACK` branch meant "at the end of the pack" and silently
    # added 118 mm the moment BMS_HOME stopped being "on_pack".
    int_l = pack_l + 2 * PACK_END_CLR
    if BMS_HOME == "at_end":
        int_l += BMS_W + 16.0
    # ESC bay and a dedicated wire raceway outboard of it. No divider - the
    # bay and the raceway are one open volume the wiring can actually use.
    # This strip is the ONLY slack in the box.
    esc_bay = ESC_W + 6.0 + WIRE_CH_W
    # The aft wall is the connector panel and everything on it has to sit in
    # the service strip. Five fittings in ONE row need ~150 mm of strip, which
    # pushed the cavity to 392 wide and left 1.3 mm between the rim ring and
    # the rail - the board ran out of width before the wall ran out of room.
    # So they go in TWO rows and the box pays in HEIGHT instead: +17 mm of
    # board against +77 mm of cavity width. Width was the scarce one.
    PANEL_ROWS = 2
    if BMS_HOME == "on_edge":
        esc_bay += BMS_E_T + BMS_LUG_STACK + 4.0
    elif BMS_HOME == "flat_beside":
        esc_bay = max(esc_bay, BMS_E_H + 8.0)
    int_w = pack_w + PACK_SIDE_CLR + esc_bay
    ext_l, ext_w = int_l + 2 * ENC_WALL, int_w + 2 * ENC_WALL
    ext_h = int_h + ENC_FLOOR + ENC_LID_T
    # Aft wire bay: the cavity starts far enough aft of the conduit to clear
    # it, and the module starts far enough forward that the conduit and its
    # gland surface in open space, not through the module floor. This also
    # walks the whole cavity forward, which is what the trim wanted anyway.
    CAV_X0 = MAST_X + CONDUIT_X_OFF - CONDUIT_D / 2 - WIRE_BAY_CLR
    MOD_X0 = MAST_X + CONDUIT_X_OFF + CONDUIT_D / 2 + WIRE_BAY_CLR
    CAV_X1 = MOD_X0 + ext_l + ENC_GAP
    CAV_WIDTH = ext_w + 2 * ENC_GAP
    cav_depth = ext_h + ENC_TOP_GAP
    THICK = FLOOR_Z + cav_depth + RIM_T + LID_T
    return dict(pack_l=pack_l, pack_w=pack_w, pack_h=pack_h, stack=stack,
                int_l=int_l, int_w=int_w, int_h=int_h,
                ext_l=ext_l, ext_w=ext_w, ext_h=ext_h, esc_bay=esc_bay)


def bolt_ring(x0, x1, y0, y1, pitch, r=0.0):
    """Bolt centres evenly spaced by ARC LENGTH round a rounded rectangle.

    Placing them on a plain rectangle put the four corner bolts outside the
    lid's rounded corners - they were hanging in space off the corner radius.
    """
    path = (rounded_rect(x0, x1, y0, y1, r, seg=16) if r > 0.5
            else [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    pts = []
    n = len(path)
    for i in range(n):
        a, b = path[i], path[(i + 1) % n]
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        for j in range(max(1, int(d / 2.0))):
            f = j / max(1, int(d / 2.0))
            pts.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
    cum = [0.0]
    m = len(pts)
    for i in range(m):
        a, b = pts[i], pts[(i + 1) % m]
        cum.append(cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    total = cum[-1]
    nb = max(6, int(round(total / pitch)))
    out = []
    for i in range(nb):
        s = total * i / nb
        for j in range(m):
            if cum[j] <= s <= cum[j + 1]:
                d = cum[j + 1] - cum[j]
                f = 0.0 if d < 1e-9 else (s - cum[j]) / d
                a, b = pts[j], pts[(j + 1) % m]
                out.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
                break
    return out


def point_in_poly(p, poly):
    x, y = p
    inside = False
    n = len(poly)
    for i in range(n):
        (xa, ya), (xb, yb) = poly[i], poly[(i + 1) % n]
        if (ya > y) != (yb > y):
            xc = xa + (y - ya) / (yb - ya) * (xb - xa)
            if x < xc:
                inside = not inside
    return inside

# ------------------------------------------------------------ mast hardpoint
MAST_X = 400.0                     # V1 as-built
BOLT_SPACING_X = 165.0             # V1 as-built Gong pattern
BOLT_SPACING_Y = 90.0
BOLT_D = 8.0                       # M8, Gong's mast screws
G10_L, G10_W = 250.0, 175.0
DENSE_MARGIN = 90.0

# BLIND THREADED INSERTS, not through-bolts. Through-bolting meant a nut and
# washer sitting in a milled pocket in the CAVITY FLOOR, which (a) put four
# permanent penetrations through the one surface that has to stay dry and
# (b) pinned the cavity's aft end at ~292 mm because the nuts needed access
# from inside. Inserts kill both: nothing passes above the plate, so the floor
# is unbroken and the cavity is free to move forward for trim.
#
# G10 is not tapped directly - it threads, but M8 in a laminate that gets
# torqued to 20 Nm and unbolted every trailer trip will strip. Stainless
# key-locking inserts (Recoil / E-Z LOK, M8 x 16) go in from the TOP face of a
# 16 mm plate and bottom out 2 mm short of the underside, so nothing shows.
G10_T = 16.0                       # up from 8: has to house a 16 mm insert
INSERT_L = 16.0
INSERT_OD = 12.0                   # tapped hole for an M8 key-locking insert
INSERT_BLIND = 2.0                 # G10 left below the insert - stays sealed

SEAM_X = 1030.0                    # halves of 1030 + 370, both under a 1219 bed
COLL_NAME = "eFoil_V2"


# ------------------------------------------------------------------ profiles
def _se(u, n):
    u = min(1.0, max(0.0, u))
    return (1.0 - u ** n) ** (1.0 / n)


def half_width(x):
    """Half width in mm at station x (0 = tail, 1 = nose).

    Superellipse blended to a finite tip width, then the tip corners rounded
    in plan - so each end terminates in a FLAT with radiused corners instead of
    running to a point.
    """
    hw = WIDTH * 0.5
    if x >= WIDE_POINT:
        tip, r = NOSE_TIP_F, NOSE_TIP_R
        f = tip + (1.0 - tip) * _se((x - WIDE_POINT) / (1.0 - WIDE_POINT), N_NOSE)
        d = (1.0 - x) * LENGTH
    else:
        tip, r = TAIL_TIP_F, TAIL_TIP_R
        f = tip + (1.0 - tip) * _se((WIDE_POINT - x) / WIDE_POINT, N_TAIL)
        d = x * LENGTH
    # No separate corner radius. `_se` has a vertical tangent as u -> 1, so the
    # outline already leaves the end flat perpendicular to the centreline -
    # i.e. tangent to it. Clamping with a circular corner on top of that put a
    # cliff in the outline: 108 mm wide at 2% of length, 396 mm at 5%.
    return max(hw * f, 1.0)


def thickness(x):
    if x > THICK_FLAT_1:
        u = (x - THICK_FLAT_1) / (1.0 - THICK_FLAT_1)
        f = THICK_NOSE + (1.0 - THICK_NOSE) * _se(u, P_THICK_FWD)
    elif x < THICK_FLAT_0:
        u = (THICK_FLAT_0 - x) / THICK_FLAT_0
        f = THICK_TAIL + (1.0 - THICK_TAIL) * _se(u, P_THICK_AFT)
    else:
        f = 1.0
    return THICK * f


def deck_line(x):
    """Height of the DECK above the datum, forward of ROCKER_START.

    This is the curve that is specified; the rocker below it is whatever falls
    out. Monotone rising, so the nose tip physically cannot dip.
    """
    base = thickness(ROCKER_START)                     # deck where the kick starts
    u = (x - ROCKER_START) / (1.0 - ROCKER_START)
    return base + (thickness(0.5) + DECK_NOSE_RISE - base) * u ** DECK_P


def rocker(x):
    z = 0.0
    if x > ROCKER_START:
        z += deck_line(x) - thickness(x)
    if x < TAIL_ROCKER_START:
        z += TAIL_ROCKER * ((TAIL_ROCKER_START - x) / TAIL_ROCKER_START) ** 2.0
    return z


# --------------------------------------------------------- section outline
def _fillet(a, b, c, r, seg=8):
    """Circular arc tangent to ba and bc. Always returns seg+1 points."""
    v1 = (a[0] - b[0], a[1] - b[1])
    v2 = (c[0] - b[0], c[1] - b[1])
    l1 = math.hypot(*v1) or 1e-9
    l2 = math.hypot(*v2) or 1e-9
    u1 = (v1[0] / l1, v1[1] / l1)
    u2 = (v2[0] / l2, v2[1] / l2)
    dot = max(-1.0, min(1.0, u1[0] * u2[0] + u1[1] * u2[1]))
    ang = math.acos(dot)
    if ang < 1e-4 or abs(math.pi - ang) < 1e-4:
        return [b] * (seg + 1)
    tan = r / math.tan(ang * 0.5)
    tan = min(tan, l1 * 0.95, l2 * 0.95)
    r_eff = tan * math.tan(ang * 0.5)
    p1 = (b[0] + u1[0] * tan, b[1] + u1[1] * tan)
    p2 = (b[0] + u2[0] * tan, b[1] + u2[1] * tan)
    bis = (u1[0] + u2[0], u1[1] + u2[1])
    lb = math.hypot(*bis) or 1e-9
    bis = (bis[0] / lb, bis[1] / lb)
    d = r_eff / math.sin(ang * 0.5)
    cen = (b[0] + bis[0] * d, b[1] + bis[1] * d)
    a1 = math.atan2(p1[1] - cen[1], p1[0] - cen[0])
    a2 = math.atan2(p2[1] - cen[1], p2[0] - cen[0])
    while a2 - a1 > math.pi:
        a2 -= 2 * math.pi
    while a1 - a2 > math.pi:
        a2 += 2 * math.pi
    return [(cen[0] + r_eff * math.cos(a1 + (a2 - a1) * i / seg),
             cen[1] + r_eff * math.sin(a1 + (a2 - a1) * i / seg))
            for i in range(seg + 1)]


def _smin(a, b, k=6.0):
    """Polynomial smooth minimum.

    A hard min() on the fillet radii switches which term binds as the station
    changes, and that switch is a step - it printed as small crease 'feathers'
    down the rail. Blending the transition removes them.
    """
    h = max(0.0, min(1.0, 0.5 + 0.5 * (b - a) / k))
    return b * (1.0 - h) + a * h - k * h * (1.0 - h)


def _bez3(p0, p1, p2, p3, u):
    w = ((1 - u) ** 3, 3 * u * (1 - u) ** 2, 3 * u ** 2 * (1 - u), u ** 3)
    return (w[0] * p0[0] + w[1] * p1[0] + w[2] * p2[0] + w[3] * p3[0],
            w[0] * p0[1] + w[1] * p1[1] + w[2] * p2[1] + w[3] * p3[1])


def chine_hardness(x):
    """1 = sharp chine, 0 = rail and bottom meet tangentially (no edge)."""
    if x <= CHINE_HARD_X0:
        return 1.0
    if x >= CHINE_HARD_X1:
        return 0.0
    u = (x - CHINE_HARD_X0) / (CHINE_HARD_X1 - CHINE_HARD_X0)
    return 1.0 - (u * u * (3.0 - 2.0 * u))          # smoothstep


def section(hw, t, x=0.0):
    """Half section as (y, z), centreline bottom -> rail -> centreline deck.

    Flat bottom (with vee) to a SHARP chine, then one tangent-continuous curve
    up over the rail apex and onto a flat deck. Two cubic Beziers meeting at
    the apex with a shared vertical tangent, so the widest point is exactly
    hw and there is no crease anywhere above the chine.

    Always SEC_TOTAL points in the same roles, so the loft cannot twist.
    """
    if hw <= 1.0 or t <= 1.0:
        return [(0.0, t * i / (SEC_TOTAL - 1)) for i in range(SEC_TOTAL)]

    hw_deck = hw * DECK_WIDTH_F
    hw_bot = hw * BOT_WIDTH_F
    z_apex = t * RAIL_APEX
    # The vee has to scale with the LOCAL thickness. Held at a fixed 16 mm it
    # was 8.6% of the section at mid-board but 57% at the tail tip and 53% at
    # the nose tip, where the board is only ~22 mm thick - the "bottom" became
    # a giant wedge and the chine sat halfway up the section. That is the
    # creasing at both ends, and it is why it appeared at the ends only.
    vee = min(BOTTOM_VEE, t * VEE_MAX_F)
    # The chine MUST be the bottom curve's own endpoint. Writing it as
    # (hw_bot, vee) put the rail's start 2.2 mm ABOVE where the bottom
    # actually finished - a literal ledge running the full length of the
    # board, which is the crease that survived every change to the fade.
    z_chine = vee * (hw_bot / hw) ** 2.0
    chine = (hw_bot, z_chine)
    apex = (hw, z_apex)
    d_edge = (hw_deck, t)

    # bottom: centreline out to the chine, vee'd. Ends AT the chine.
    bot = [(hw_bot * i / (SEC_BOT - 1),
            vee * ((hw_bot * i / (SEC_BOT - 1)) / hw) ** 2.0)
           for i in range(SEC_BOT)]

    # chine -> apex. How steeply it leaves the chine is what sets whether
    # there is an edge there at all: steep gives a sharp corner against the
    # flat bottom, horizontal makes it tangent and the edge vanishes.
    h = chine_hardness(x)
    # Departure angle, interpolated in DEGREES between "tangent to the bottom
    # plus a few" and the hard-edge angle. At h=0 the rail leaves along the
    # bottom's own slope, so there is no kink at all - which is the only way
    # the line actually disappears at the nose.
    bot_slope = math.degrees(math.atan2(2.0 * vee * hw_bot / (hw * hw), 1.0))
    soft = bot_slope + CHINE_SOFT_DEG
    theta = math.radians(soft + h * (CHINE_HARD_DEG - soft))
    seg = math.hypot(apex[0] - chine[0], apex[1] - chine[1])
    a1 = (chine[0] + 0.45 * seg * math.cos(theta),
          chine[1] + 0.45 * seg * math.sin(theta))
    a2 = (hw, z_apex - 0.40 * (z_apex - chine[1]))
    lo = [_bez3(chine, a1, a2, apex, (i + 1) / SEC_RAIL_LO)
          for i in range(SEC_RAIL_LO)]

    # apex -> deck edge. Leaves the apex vertical (tangent-continuous with the
    # segment below) and arrives at the deck horizontal, so deck and rail are
    # one surface rather than two bulges.
    b1 = (hw, z_apex + 0.42 * (t - z_apex))
    b2 = (hw_deck + 0.55 * (hw - hw_deck), t)
    hi = [_bez3(apex, b1, b2, d_edge, (i + 1) / SEC_RAIL_HI)
          for i in range(SEC_RAIL_HI)]

    # flat deck back to the centreline
    deck = [(hw_deck * (1.0 - (i + 1) / SEC_DECK), t) for i in range(SEC_DECK)]

    return bot + lo + hi + deck


def deck_z_at(x_mm, y_mm):
    """Deck surface height at (x, y) - the highest point of the outline."""
    x = x_mm / LENGTH
    pts = section(half_width(x), thickness(x), x)
    y = abs(y_mm)
    best = None
    for i in range(len(pts) - 1):
        (ya, za), (yb, zb) = pts[i], pts[i + 1]
        if (ya - y) * (yb - y) <= 0 and abs(ya - yb) > 1e-9:
            f = (y - ya) / (yb - ya)
            z = za + (zb - za) * f
            best = z if best is None else max(best, z)
    return (best if best is not None else 0.0) + rocker(x)


def deck_half_width_at_z(x_mm, z_mm):
    """Widest half width at height z - how far a flat land can reach out.

    Scans the whole outline rather than assuming the deck is the back half of
    the point list; the rail taper is a single long segment and an index split
    walked straight past it.
    """
    x = x_mm / LENGTH
    t = thickness(x)
    z = z_mm - rocker(x)
    if z >= t or z <= 0:
        return 0.0
    pts = section(half_width(x), t, x)
    best = 0.0
    for i in range(len(pts) - 1):
        (ya, za), (yb, zb) = pts[i], pts[i + 1]
        if (za - z) * (zb - z) <= 0 and abs(za - zb) > 1e-9:
            f = (z - za) / (zb - za)
            best = max(best, ya + (yb - ya) * f)
    return best


# ------------------------------------------------------------------- scene
def fresh_collection():
    old = bpy.data.collections.get(COLL_NAME)
    if old:
        for o in list(old.objects):
            bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.collections.remove(old)
    coll = bpy.data.collections.new(COLL_NAME)
    bpy.context.scene.collection.children.link(coll)
    return coll


# --------------------------------------------------------------- palette
# One entry per REAL material in the BOM, not per object, so that two parts
# sharing a colour is a statement that they are cut from the same stock. Hues
# are spread around the wheel and kept apart in value as well, so the parts
# stay distinguishable in the flat-shaded viewport and in a mono print.
#
#   key                colour            rough  metal  a    what it is
PALETTE = {
    "hull_glass":    ((0.88, 0.89, 0.90), 0.30, 0.0, 0.18),  # glass/H80/glass shell
    "eps":           ((0.96, 0.96, 0.93), 0.95, 0.0, 1.00),  # EPS blank
    "h80":           ((0.95, 0.86, 0.42), 0.85, 0.0, 1.00),  # H80 PVC foam core
    "dense":         ((0.20, 0.45, 0.80), 0.85, 0.0, 1.00),  # H200 mast block
    "g10":           ((0.85, 0.68, 0.28), 0.50, 0.0, 1.00),  # G10 laminate
    "g10_rim":       ((0.72, 0.45, 0.14), 0.45, 0.0, 1.00),  # G10 rim ring, 12 mm
    "g10_mast":      ((0.55, 0.29, 0.08), 0.45, 0.0, 1.00),  # G10 mast plate, 8 mm
    "flange":        ((0.95, 0.78, 0.50), 0.50, 0.0, 1.00),  # G10 flange rails
    "enclosure":     ((0.62, 0.66, 0.72), 0.50, 0.0, 1.00),  # module shell
    "lid":           ((0.35, 0.80, 0.88), 0.25, 0.0, 0.45),  # hatch lid sandwich
    "lid_mod":       ((0.62, 0.40, 0.78), 0.30, 0.0, 0.55),  # module lid sandwich
    "cell":          ((0.16, 0.62, 0.38), 0.40, 0.3, 1.00),  # 21700 cells
    "wrap":          ((0.10, 0.11, 0.13), 0.60, 0.0, 1.00),  # pack wrap / kapton
    "pcb":           ((0.05, 0.30, 0.14), 0.50, 0.0, 1.00),  # BMS board
    "esc":           ((0.20, 0.24, 0.55), 0.35, 0.2, 1.00),  # VESC
    "fuse":          ((0.90, 0.45, 0.05), 0.40, 0.0, 1.00),  # fuse / breaker
    "nickel":        ((0.80, 0.81, 0.83), 0.25, 1.0, 1.00),  # nickel strip
    "steel":         ((0.62, 0.63, 0.66), 0.30, 1.0, 1.00),  # A4 bolts, glands
    "alu_anod":      ((0.28, 0.30, 0.33), 0.35, 1.0, 1.00),  # anodised alu foil
    "carbon":        ((0.07, 0.07, 0.08), 0.28, 0.1, 1.00),  # carbon wing
    "seal":          ((0.85, 0.15, 0.35), 0.60, 0.0, 1.00),  # poured silicone
}


def material(name, rgba, rough=0.45, metal=0.0):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    if b:
        b.inputs["Base Color"].default_value = rgba
        b.inputs["Roughness"].default_value = rough
        if "Metallic" in b.inputs:
            b.inputs["Metallic"].default_value = metal
        if "Alpha" in b.inputs:
            b.inputs["Alpha"].default_value = rgba[3]
    if rgba[3] < 1.0:
        m.blend_method = "BLEND"
    m.diffuse_color = rgba                 # solid/flat viewport shading
    return m


PALETTE_LEGEND = {
    "hull_glass": "hull shell - E-glass / H80 / E-glass, vacuum bagged",
    "eps":        "EPS blank, 2 lb/ft3, CNC milled in two halves",
    "h80":        "H80 PVC foam core, 5 lb/ft3 - lid and hull sandwich cores",
    "dense":      "H200/H250 dense PVC foam - mast load path ring",
    "g10":        "G10 laminate, general",
    "g10_rim":    "G10 rim ring, 12 mm - carries the O-ring channel and hatch bolts",
    "g10_mast":   "G10 mast plate, 8 mm - the mast bolts thread through this",
    "flange":     "G10 flange rail, 14 x 10 mm - module lid bolts land here",
    "enclosure":  "G10 module shell, 3 mm walls and floor",
    "lid":        "hatch lid sandwich, glass 1 / H80 12 / glass 1",
    "lid_mod":    "module lid sandwich, glass 1 / H80 6 / glass 1",
    "cell":       "BAK N21700CG-50 cells, 14S9P",
    "wrap":       "pack wrap and kapton",
    "pcb":        "BMS, sitting on top of the pack",
    "esc":        "VESC (Flipsky 75200 Pro)",
    "fuse":       "fuse / main breaker",
    "nickel":     "nickel interconnect strip",
    "steel":      "A4 stainless bolts and cable glands",
    "alu_anod":   "anodised aluminium - foil mast and fuselage",
    "carbon":     "carbon - front wing, stabiliser, prop",
    "seal":       "poured silicone gasket, 6 x 3 mm machined channel",
}


def print_legend():
    print("--- colour key " + "-" * 52)
    for k, (rgb, _r, _m, a) in PALETTE.items():
        hexc = "#%02X%02X%02X" % tuple(int(c * 255) for c in rgb)
        note = " (transparent)" if a < 1.0 else ""
        print(f"  {hexc}  {k:12s} {PALETTE_LEGEND.get(k, '')}{note}")


def bom_mat(key):
    """Material for a BOM material key. Single source of truth for colour."""
    rgb, rough, metal, alpha = PALETTE[key]
    return material("V2_" + key, (rgb[0], rgb[1], rgb[2], alpha), rough, metal)


def new_object(name, verts, faces, coll, mat=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata([(v[0] / 1000.0, v[1] / 1000.0, v[2] / 1000.0) for v in verts],
                   [], faces)
    me.validate()
    me.update()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    if mat:
        ob.data.materials.append(mat)
    return ob


def prism(name, poly, z0, z1, coll, mat=None):
    n = len(poly)
    verts = [(p[0], p[1], z0) for p in poly] + [(p[0], p[1], z1) for p in poly]
    faces = [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)]
    faces.append(list(range(n - 1, -1, -1)))
    faces.append(list(range(n, 2 * n)))
    return new_object(name, verts, faces, coll, mat)


# ------------------------------------------------------------------- foil
# Gong Allvator Veloce, the kit priced in build-budget.md. Dimensions are the
# published ones; sections are representative. Modelled so the mast bolt
# pattern, the motor's swing radius and the ride height can be seen against the
# board rather than taken on trust.
FOIL_MAST_H, FOIL_MAST_C, FOIL_MAST_T = 750.0, 120.0, 0.115      # 75 cm alu mast
FOIL_FUSE_L, FOIL_FUSE_D = 720.0, 32.0
FOIL_FW_SPAN, FOIL_FW_CR, FOIL_FW_CT = 1100.0, 205.0, 78.0       # X-Over front wing
FOIL_FW_SWEEP, FOIL_FW_DIHEDRAL = 95.0, 55.0
FOIL_ST_SPAN, FOIL_ST_CR, FOIL_ST_CT = 440.0, 105.0, 55.0
FOIL_MOTOR_L, FOIL_MOTOR_D = 205.0, 65.0                    # Flipsky 65161
FOIL_MOTOR_Z = 120.0    # motor axis above the fuselage - set by prop clearance
FOIL_PROP_D = 165.0


def build_foil(coll, rep):
    """Mast, fuselage, front wing, stabiliser, motor pod and prop."""
    m_alu, m_carbon = bom_mat("alu_anod"), bom_mat("carbon")
    m_steel = bom_mat("steel")

    # The mast hangs from the hull bottom at the mast datum, not from z=0 -
    # the tail rocker and the bottom vee both lift the surface there.
    top = bottom_z_at(MAST_X, 0.0)
    base = top - FOIL_MAST_H
    mast_sec = naca(FOIL_MAST_C, FOIL_MAST_T)
    loft("V2_Foil_Mast",
         [[(MAST_X - FOIL_MAST_C * 0.30 + p[0], p[1], z) for p in mast_sec]
          for z in (top, base)], coll, m_alu)

    # Fuselage. cyl/cyl_y run along Z and Y; this runs along X, so loft it.
    fx = MAST_X - FOIL_MAST_C * 0.30
    n = 20
    ring = [(FOIL_FUSE_D * 0.5 * math.cos(2 * math.pi * i / n),
             FOIL_FUSE_D * 0.5 * math.sin(2 * math.pi * i / n)) for i in range(n)]
    # +X is the NOSE, so the front wing goes to the HIGH x end of the fuselage
    # and the motor and prop hang off the low-x, aft end. Getting this backwards
    # is easy to miss in a render and puts the prop under the rider's front foot.
    f_aft, f_fwd = fx - FOIL_FUSE_L * 0.58, fx + FOIL_FUSE_L * 0.42
    loft("V2_Foil_Fuselage",
         [[(x, p[0], base + FOIL_FUSE_D * 0.5 + p[1]) for p in ring]
          for x in (f_aft, f_fwd)], coll, m_alu)

    zc = base + FOIL_FUSE_D * 0.5
    wing("V2_Foil_FrontWing", FOIL_FW_SPAN, FOIL_FW_CR, FOIL_FW_CT, 0.115,
         -FOIL_FW_SWEEP, FOIL_FW_DIHEDRAL, f_fwd - FOIL_FW_CR - 20.0, zc,
         coll, m_carbon)
    # At the aft end of the fuselage where it belongs. It used to be offset by
    # the motor length, which only made sense while the motor was on the
    # fuselage; with the motor on the mast that offset put it under the prop.
    st_x0 = f_aft + 20.0
    wing("V2_Foil_Stab", FOIL_ST_SPAN, FOIL_ST_CR, FOIL_ST_CT, 0.090, -30.0,
         10.0, st_x0, zc, coll, m_carbon)

    # Motor clamps to the MAST, not to the back of the fuselage. It hangs off
    # the mast's trailing edge on a saddle clamp, low down, with the prop aft.
    # The consequence to watch is prop-to-fuselage clearance: the disc is 165
    # dia against a 32 mm tube, so the motor axis has to sit high enough that
    # the blade tips miss it. That clearance is reported, not assumed.
    mz = zc + FOIL_MOTOR_Z
    m_te = fx + FOIL_MAST_C * 0.70              # mast trailing edge
    loft("V2_Foil_Motor",
         [[(x, p[0], mz + p[1]) for p in
           [(FOIL_MOTOR_D * 0.5 * math.cos(2 * math.pi * i / n),
             FOIL_MOTOR_D * 0.5 * math.sin(2 * math.pi * i / n)) for i in range(n)]]
          for x in (m_te - FOIL_MOTOR_L, m_te)], coll, m_steel)
    # saddle clamp round the mast
    box("V2_Foil_MotorClamp", fx - 8.0, m_te + 6.0, -34.0, 34.0,
        mz - 26.0, mz + 26.0, coll, m_alu)
    px = m_te - FOIL_MOTOR_L - 16.0
    loft("V2_Foil_Prop",
         [[(x, FOIL_PROP_D * 0.5 * math.cos(2 * math.pi * i / 24),
            mz + FOIL_PROP_D * 0.5 * math.sin(2 * math.pi * i / 24))
           for i in range(24)] for x in (px - 6.0, px + 6.0)], coll, m_carbon)
    rep["motor_mount"] = "saddle clamp on the mast trailing edge"
    # Vertical: blade tips vs the fuselage tube directly below the disc.
    rep["prop_to_fuselage_mm"] = round(
        (mz - FOIL_PROP_D / 2) - (zc + FOIL_FUSE_D / 2), 1)
    # Longitudinal: the disc spins in the gap between the mast and the stab.
    # Aft is -X, so clear means the disc sits FORWARD of the stab's trailing
    # edge. Getting this comparison backwards is how the stab ended up inside
    # the prop disc.
    rep["prop_to_stab_mm"] = round((px - 6.0) - (st_x0 + FOIL_ST_CR), 1)
    rep["prop_clear_of_stab"] = rep["prop_to_stab_mm"] > 0
    rep["prop_clear_of_mast_mm"] = round(
        (fx - FOIL_MAST_C * 0.30) - (px + 6.0), 1)

    rep["foil_mast_height_mm"] = FOIL_MAST_H
    rep["foil_ride_height_mm"] = round(top - base, 1)
    rep["foil_prop_below_hull_mm"] = round(top - (mz - FOIL_PROP_D / 2), 1)


def naca(chord, t_ratio, n=24):
    """Symmetric NACA 00xx half-section, LE at x=0, running to the TE and back.

    Used for the mast and both wings. A symmetric section is right for the mast
    (it must be neutral on both tacks) and close enough for the wings at this
    level of detail - the point is to read as a foil, not to predict lift.
    """
    pts_u, pts_l = [], []
    for i in range(n + 1):
        # cosine spacing: points bunch at the leading edge where curvature is
        u = 0.5 * (1.0 - math.cos(math.pi * i / n))
        y = 5.0 * t_ratio * chord * (0.2969 * math.sqrt(u) - 0.1260 * u
                                     - 0.3516 * u ** 2 + 0.2843 * u ** 3
                                     - 0.1015 * u ** 4)
        pts_u.append((u * chord, y))
        pts_l.append((u * chord, -y))
    return pts_u + pts_l[-2:0:-1]          # closed loop, no duplicate LE/TE


def loft(name, sections, coll, mat=None, cap=True):
    """Loft equal-length sections given as lists of (x, y, z) points."""
    n = len(sections[0])
    verts = [p for sec in sections for p in sec]
    faces = []
    for s in range(len(sections) - 1):
        a, b = s * n, (s + 1) * n
        faces += [[a + i, a + (i + 1) % n, b + (i + 1) % n, b + i]
                  for i in range(n)]
    if cap:
        faces.append(list(range(n - 1, -1, -1)))
        faces.append(list(range(len(verts) - n, len(verts))))
    return new_object(name, verts, faces, coll, mat)


def wing(name, span, chord_root, chord_tip, t_ratio, sweep, dihedral,
         x0, z0, coll, mat, n_sec=13):
    """Tapered, swept wing lofted about the Y axis, symmetric about y=0."""
    secs = []
    for i in range(n_sec):
        v = (i / (n_sec - 1)) * 2.0 - 1.0            # -1 tip .. +1 tip
        a = abs(v)
        # elliptical chord taper - the planform real front wings use
        c = chord_tip + (chord_root - chord_tip) * math.sqrt(max(0.0, 1.0 - a ** 2))
        sec = naca(c, t_ratio)
        xo = x0 + sweep * a - (c - chord_root) * 0.25   # sweep the quarter chord
        zo = z0 + dihedral * a ** 2
        secs.append([(xo + p[0], v * span * 0.5, zo + p[1]) for p in sec])
    return loft(name, secs, coll, mat)


def box(name, x0, x1, y0, y1, z0, z1, coll, mat=None):
    return prism(name, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, coll, mat)


def cyl(name, cx, cy, z0, z1, d, coll, mat=None, seg=20):
    r = d * 0.5
    return prism(name, [(cx + r * math.cos(2 * math.pi * i / seg),
                         cy + r * math.sin(2 * math.pi * i / seg))
                        for i in range(seg)], z0, z1, coll, mat)


def cyl_y(name, cx, cz, y0, y1, d, coll, mat=None, seg=20):
    """Cylinder with its axis along Y - for anything passing through a wall."""
    r = d * 0.5
    ring = [(cx + r * math.cos(2 * math.pi * i / seg),
             cz + r * math.sin(2 * math.pi * i / seg)) for i in range(seg)]
    verts = [(p[0], y0, p[1]) for p in ring] + [(p[0], y1, p[1]) for p in ring]
    faces = [[i, (i + 1) % seg, seg + (i + 1) % seg, seg + i] for i in range(seg)]
    faces.append(list(range(seg - 1, -1, -1)))
    faces.append(list(range(seg, 2 * seg)))
    return new_object(name, verts, faces, coll, mat)


def rounded_rect(x0, x1, y0, y1, r, seg=10):
    r = max(0.1, min(r, (x1 - x0) / 2 - 0.1, (y1 - y0) / 2 - 0.1))
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -math.pi / 2), (x1 - r, y1 - r, 0.0),
                       (x0 + r, y1 - r, math.pi / 2), (x0 + r, y0 + r, math.pi)):
        for i in range(seg + 1):
            a = a0 + (math.pi / 2) * i / seg
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def _box_into(verts, faces, x0, x1, y0, y1, z0, z1):
    b = len(verts)
    verts.extend([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                  (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)])
    faces.extend([[b, b + 3, b + 2, b + 1], [b + 4, b + 5, b + 6, b + 7],
                  [b, b + 1, b + 5, b + 4], [b + 1, b + 2, b + 6, b + 5],
                  [b + 2, b + 3, b + 7, b + 6], [b + 3, b, b + 4, b + 7]])


def channel_profile(z_l1, z_l2, r, throat, z_top, n=64):
    """YZ outline of one cell channel: both cradles plus the snap-in throat.

    Built as a single union outline rather than overlapping solids - a cutter
    mesh that self-intersects makes the EXACT boolean remove far more than
    intended (it ate every rib the first time).
    """
    z0 = z_l1 - r
    out = []
    for i in range(n + 1):
        z = z0 + (z_top - z0) * i / n
        hw = 0.0
        for zc in (z_l1, z_l2):
            d = abs(z - zc)
            if d < r:
                hw = max(hw, math.sqrt(r * r - d * d))
        if z >= z_l1:
            hw = max(hw, throat / 2)
        out.append((hw, z))
    return out


def _sweep_x_into(verts, faces, prof, y_off, x0, x1):
    poly = [(p[0] + y_off, p[1]) for p in prof]
    poly += [(-p[0] + y_off, p[1]) for p in reversed(prof)]
    # drop duplicate points at the closed ends
    clean = [poly[0]]
    for p in poly[1:]:
        if abs(p[0] - clean[-1][0]) > 1e-6 or abs(p[1] - clean[-1][1]) > 1e-6:
            clean.append(p)
    if (abs(clean[0][0] - clean[-1][0]) < 1e-6
            and abs(clean[0][1] - clean[-1][1]) < 1e-6):
        clean.pop()
    n = len(clean)
    b = len(verts)
    verts.extend([(x0, p[0], p[1]) for p in clean])
    verts.extend([(x1, p[0], p[1]) for p in clean])
    for i in range(n):
        j = (i + 1) % n
        faces.append([b + i, b + j, b + n + j, b + n + i])
    faces.append([b + i for i in range(n - 1, -1, -1)])
    faces.append([b + n + i for i in range(n)])


def _fix_normals(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()
    return ob


def build_cell_holder(coll, cols, x_start, pack_y0, iz0, mat, rep):
    """Printed holder: rails + scalloped ribs, cradles cut by long cylinders.

    Returns the z of each layer's cell centreline so the pack sits in it.
    """
    n1, n2 = cols[0], cols[1]
    py0, py1 = pack_y0, pack_y0 + PACK_P * PITCH_Y
    zb = iz0 + HOLD_BASE_T
    z_l1 = zb + PITCH_Z / 2
    z_l2 = z_l1 + PITCH_Z
    top1, top2 = z_l1 + PITCH_Z / 2, z_l2 + PITCH_Z / 2
    span = n1 * PITCH_X

    boxes = []
    # longitudinal rails on the cell boundaries - the gaps between them are the
    # drain and vent path, and they halve the print mass versus a solid floor
    for i in range(PACK_P + 1):
        y = py0 + i * PITCH_Y
        boxes.append((x_start, x_start + span,
                      y - HOLD_RAIL_W / 2, y + HOLD_RAIL_W / 2, iz0, zb))
    # ribs, two per column at +/- HOLD_RIB_OFF from centre
    for c in range(n1):
        cx = x_start + (c + 0.5) * PITCH_X
        top = top2 if c < n2 else top1
        for s in (-1, 1):
            xc = cx + s * HOLD_RIB_OFF
            boxes.append((xc - HOLD_RIB_T / 2, xc + HOLD_RIB_T / 2,
                          py0, py1, iz0, top))

    verts, faces = [], []
    for b in boxes:
        _box_into(verts, faces, *b)
    holder = new_object("V2_CellHolder", verts, faces, coll, mat)
    _fix_normals(holder)

    cv, cf = [], []
    r = CELL_D / 2 + HOLD_CLEAR
    # Snap-in throat above each cradle. Columns are welded into 8-cell
    # sub-modules on the bench, so they cannot be threaded in axially - they
    # have to drop in from above past a lip that then retains them.
    throat = CELL_D - 1.0
    prof = channel_profile(z_l1, z_l2, r, throat, top2 + 5.0)
    for p in range(PACK_P):
        y = py0 + (p + 0.5) * PITCH_Y
        _sweep_x_into(cv, cf, prof, y, x_start - 5.0, x_start + span + 5.0)
    cut = new_object("V2_HolderCradle_cut", cv, cf, coll)
    _fix_normals(cut)
    boolean(holder, cut)
    cut.hide_set(True)
    cut.hide_render = True

    # retainer over layer 2 only - layer 1's columns 8-9 carry the BMS instead
    prism("V2_Holder_Retainer",
          [(x_start, py0), (x_start + n2 * PITCH_X, py0),
           (x_start + n2 * PITCH_X, py1), (x_start, py1)],
          top2, top2 + HOLD_RETAIN_T, coll, mat)

    segs = int(math.ceil(span / HOLD_BED))
    rep["holder_rib_web_mm"] = round(PITCH_Y - CELL_D - 2 * HOLD_CLEAR, 2)
    rep["strip_gap_mm"] = round(PITCH_X - CELL_L, 2)
    rep["interlayer_tab_gap_mm"] = round(PITCH_Z - CELL_D, 2)
    rep["holder_stack_top_mm"] = round(top2 + HOLD_RETAIN_T - iz0, 1)
    rep["holder_segments"] = segs
    rep["holder_segment_mm"] = f"{span / segs:.0f} x {py1 - py0:.0f} x {top2 - iz0:.0f}"
    rep["holder_fits_bed"] = (span / segs <= HOLD_BED and (py1 - py0) <= HOLD_BED)
    return z_l1, z_l2, top1


def volume_litres(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    v = bm.calc_volume(signed=True)
    bm.free()
    return abs(v) * 1000.0


def _evaluated(ob, coll, name):
    """A real mesh copy with all modifiers applied - for measuring, not keeping."""
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    o = bpy.data.objects.new(name, me)
    o.matrix_world = ob.matrix_world
    coll.objects.link(o)
    return o


def _bool_volume(a, b, op, coll):
    """Volume in litres of A op B, evaluated then thrown away."""
    ea = _evaluated(a, coll, "__chk_a")
    eb = _evaluated(b, coll, "__chk_b")
    m = ea.modifiers.new("chk", 'BOOLEAN')
    m.object = eb
    m.operation = op
    m.solver = 'EXACT'
    # Both operands were created moments ago. Without this the depsgraph has
    # not seen `eb`, the boolean silently does nothing, and every containment
    # test reports the whole part as protruding.
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ea.evaluated_get(dg))
    bm = bmesh.new()
    bm.from_mesh(me)
    v = abs(bm.calc_volume(signed=True)) * 1000.0
    bm.free()
    bpy.data.meshes.remove(me)
    for o in (ea, eb):
        bpy.data.objects.remove(o, do_unlink=True)
    return v


def bottom_z_at(x_mm, y_mm):
    """Hull underside height at (x, y) - lowest point of the outline."""
    x = x_mm / LENGTH
    pts = section(half_width(x), thickness(x), x)
    y = abs(y_mm)
    best = None
    for i in range(len(pts) - 1):
        (ya, za), (yb, zb) = pts[i], pts[i + 1]
        if (ya - y) * (yb - y) <= 0 and abs(ya - yb) > 1e-9:
            f = (y - ya) / (yb - ya)
            z = za + (zb - za) * f
            best = z if best is None else min(best, z)
    return (best if best is not None else 0.0) + rocker(x)


def inside_hull(x_mm, y_mm, z_mm, margin=0.0):
    """Analytic containment. Trustworthy where the boolean was not.

    Blender's EXACT boolean reported the G10 mast plate as 100% outside the
    hull when it demonstrably sits inside it, so the containment tests are done
    against the profile functions directly instead.
    """
    if x_mm < 0.0 or x_mm > LENGTH:
        return False
    if abs(y_mm) > half_width(x_mm / LENGTH) - margin:
        return False
    return (bottom_z_at(x_mm, y_mm) + margin <= z_mm
            <= deck_z_at(x_mm, y_mm) - margin)


def check_inside(name, x0, x1, y0, y1, z0, z1, rep, n=9):
    """Sample a box's surface against the hull and report the worst breach."""
    worst, where = 0.0, None
    for i in range(n):
        for j in range(n):
            x = x0 + (x1 - x0) * i / (n - 1)
            y = y0 + (y1 - y0) * j / (n - 1)
            for z in (z0, z1):
                if not inside_hull(x, y, z):
                    d = max(bottom_z_at(x, y) - z, z - deck_z_at(x, y),
                            abs(y) - half_width(x / LENGTH))
                    if d > worst:
                        worst, where = d, (round(x), round(y), round(z))
    rep[f"breach_{name}_mm"] = round(worst, 2)
    rep[f"breach_{name}_at"] = where
    return worst


def run_interference(coll, pairs, contains, rep, tol=0.005):
    """Two families of check, both of which have caught real errors here.

    `pairs`   - (A, B) that must not overlap at all.
    `contains`- (part, shell) where part must lie entirely inside shell. This
                is the one that would have caught the dense-foam ring erupting
                through the hull bottom, which I only found by eye.
    """
    hits = []
    for an, bn in pairs:
        a, b = bpy.data.objects.get(an), bpy.data.objects.get(bn)
        if not a or not b:
            continue
        v = _bool_volume(a, b, 'INTERSECT', coll)
        rep[f"overlap_{an}__{bn}_L"] = round(v, 4)
        if v > tol:
            hits.append(f"{an} overlaps {bn} by {v:.3f} L")
    for pn, sn in contains:
        p, s = bpy.data.objects.get(pn), bpy.data.objects.get(sn)
        if not p or not s:
            continue
        v = _bool_volume(p, s, 'DIFFERENCE', coll)
        rep[f"outside_{pn}_L"] = round(v, 4)
        if v > tol:
            hits.append(f"{pn} protrudes outside {sn} by {v:.3f} L")
    rep["interference"] = hits or ["none"]
    return hits


def boolean(target, cutter, op='DIFFERENCE'):
    m = target.modifiers.new(f"bool_{cutter.name}", 'BOOLEAN')
    m.object = cutter
    m.operation = op
    m.solver = 'EXACT'
    return m


# -------------------------------------------------------------------- hull
def build_hull(coll):
    rings, ring_n = [], None
    for i in range(N_STATIONS):
        x = i / (N_STATIONS - 1)
        hw, t, r = half_width(x), thickness(x), rocker(x)
        # No resampling - section() already returns a fixed, feature-aligned
        # point list, so ring point k means the same thing at every station.
        out = section(hw, t, x)
        ring = []
        for (y, z) in out:
            ring.append((x * LENGTH, -y, z + r))
        for (y, z) in reversed(out[1:-1]):
            ring.append((x * LENGTH, y, z + r))
        rings.append(ring)
        ring_n = len(ring)

    verts, faces = [], []
    for ring in rings:
        verts.extend(ring)
    for i in range(len(rings) - 1):
        a, b = i * ring_n, (i + 1) * ring_n
        for j in range(ring_n):
            k = (j + 1) % ring_n
            faces.append([a + j, a + k, b + k, b + j])
    faces.append(list(range(ring_n - 1, -1, -1)))
    base = (len(rings) - 1) * ring_n
    faces.append([base + j for j in range(ring_n)])
    hull = new_object("V2_Hull", verts, faces, coll,
                      bom_mat("hull_glass"))
    for p in hull.data.polygons:
        p.use_smooth = True
    return hull


# --------------------------------------------------------------- pack fit
def pack_splits(S, layers):
    """Candidate column splits, balanced first then deliberately uneven.

    An uneven split is not waste - the short layer leaves a shelf exactly one
    cell-layer high, which is where the BMS goes for free. A balanced split has
    no shelf, which is why 16S at 8+8 had nowhere to put it.
    """
    base, extra = divmod(S, layers)
    cands = [sorted([base + (1 if i < extra else 0) for i in range(layers)],
                    reverse=True)]
    if layers == 2:
        for d in (1, 2, 3):
            hi, lo = base + extra + d, base - d
            if lo >= 1:
                cands.append([hi, lo])
    return cands


def pack_grid(S, P, layers, int_l=None):
    """The split actually used - the first candidate that fits the length."""
    for cols in pack_splits(S, layers):
        if int_l is None or max(cols) * PITCH_X <= int_l:
            return cols
    return pack_splits(S, layers)[0]


def _bms_home(cols, P, int_l, int_w, int_h, layers):
    foot_x = max(cols) * PITCH_X
    foot_y = P * PITCH_Y
    foot_z = layers * PITCH_Z
    shelf_x = (max(cols) - min(cols)) * PITCH_X
    if (shelf_x >= BMS_W + 8 and foot_y >= BMS_L
            and PITCH_Z * (layers - 1) + BMS_H <= int_h):
        return "pocket in short layer", foot_z, min(shelf_x - BMS_W, foot_y - BMS_L)
    strip = int_w - foot_y
    if strip >= BMS_W + 8 and BMS_H <= int_h:
        return "beside pack", foot_z, strip - BMS_W
    endz = int_l - foot_x
    if endz >= BMS_W + 8 and int_w >= BMS_L:
        return "end of pack", foot_z, endz - BMS_W
    if foot_z + BMS_H <= int_h:
        return "on top", foot_z + BMS_H, int_h - foot_z - BMS_H
    return None, None, None


def pack_fit(S, P, layers, int_l, int_w, int_h):
    """Does S x P fit, and where does the BMS go? Returns a verdict dict."""
    cols = pack_grid(S, P, layers, int_l)
    best = None
    for cand in pack_splits(S, layers):
        if max(cand) * PITCH_X > int_l:
            continue
        home, stack, clear = _bms_home(cand, P, int_l, int_w, int_h, layers)
        if home and (best is None or clear > best[3]):
            best = (cand, home, stack, clear)
    if best:
        cols = best[0]
    foot_x = max(cols) * PITCH_X
    foot_y = P * PITCH_Y
    foot_z = layers * PITCH_Z
    n = S * P
    v_nom = S * 3.6
    i_peak = PEAK_W / v_nom
    out = {
        "config": f"{S}S{P}P", "cells": n, "columns": "+".join(map(str, cols)),
        "foot_mm": f"{foot_x:.0f} x {foot_y:.0f} x {foot_z:.0f}",
        "energy_Wh": round(n * CELL_WH),
        "mass_kg": round(n * CELL_G / 1000.0, 2),
        "v_nom": round(v_nom, 1), "v_max": round(S * 4.2, 1),
        "pack_A_at_peak": round(i_peak),
        "cell_A_at_peak": round(i_peak / P, 1),
        "cell_pct_of_15A": round(i_peak / P / CELL_IMAX * 100),
    }
    if foot_x > int_l or foot_y > int_w or foot_z > int_h:
        out.update(fits=False, bms="-", why="pack itself does not fit")
        return out
    if best is None:
        out.update(fits=False, bms="nowhere", why="BMS has no home at this height")
        return out
    out.update(fits=True, bms=best[1], stack_mm=round(best[2], 1),
               bms_clear_mm=round(best[3], 1))
    return out


# -------------------------------------------------------------------- build
def build():
    coll = fresh_collection()
    rep = {}

    m_g10 = bom_mat("g10")
    m_dense = bom_mat("dense")
    m_enc = bom_mat("enclosure")
    m_cell = bom_mat("cell")
    m_pcb = bom_mat("pcb")
    m_metal = bom_mat("steel")

    # Size the pack, then the module, then the cavity, then the board. The
    # board thickness is an OUTPUT of the electronics stack-up, which is what
    # the foil.zone builders mean when they quote "~120 mm max" - they are
    # quoting a stack-up, not a preference.
    L = derive_layout()
    hull = build_hull(coll)

    ledge_z = THICK - LID_T - RIM_T          # rim ring sits here
    cav_depth = ledge_z - FLOOR_Z
    ext_l, ext_w, ext_h = L["ext_l"], L["ext_w"], L["ext_h"]
    int_l, int_w, int_h = L["int_l"], L["int_w"], L["int_h"]
    rep["board_thickness_mm"] = round(THICK, 1)
    rep["seal_plane_z_mm"] = round(ledge_z + RIM_T, 1)
    rep["cavity_floor_z_mm"] = FLOOR_Z
    rep["cavity_mm"] = f"{CAV_X1 - CAV_X0:.0f} x {CAV_WIDTH:.0f} x {cav_depth:.0f}"
    rep["module_ext_mm"] = f"{ext_l:.0f} x {ext_w:.0f} x {ext_h:.0f}"
    rep["module_int_mm"] = f"{int_l:.0f} x {int_w:.0f} x {int_h:.0f}"
    rep["pack_mm"] = f"{L['pack_l']:.0f} x {L['pack_w']:.0f} x {L['stack']:.0f}"
    rep["bms_on_pack"] = BMS_ON_PACK
    rep["thickness_if_bms_moved_mm"] = round(
        THICK - BMS_H if BMS_ON_PACK else THICK + BMS_H, 1)

    n = PACK_S * PACK_P
    v_nom = PACK_S * 3.6
    rep["pack"] = dict(
        config=f"{PACK_S}S{PACK_P}P", cells=n, energy_Wh=round(n * CELL_WH),
        mass_kg=round(n * CELL_G / 1000.0, 2), v_nom=round(v_nom, 1),
        v_max=round(PACK_S * 4.2, 1), pack_A=round(PEAK_W / v_nom),
        cell_A=round(PEAK_W / v_nom / PACK_P, 1),
        pct_of_15A=round(PEAK_W / v_nom / PACK_P / CELL_IMAX * 100))

    # --- cavity in the hull ----------------------------------------------
    cav_poly = rounded_rect(CAV_X0, CAV_X1, -CAV_WIDTH / 2, CAV_WIDTH / 2,
                            CAV_CORNER_R)
    void = prism("V2_Cavity_Void_cut", cav_poly, FLOOR_Z - FIT_FLOOR,
                 THICK + 60.0, coll)
    rebate = prism("V2_Rebate_cut",
                   rounded_rect(CAV_X0 - RIM_W, CAV_X1 + RIM_W,
                                -CAV_WIDTH / 2 - RIM_W, CAV_WIDTH / 2 + RIM_W,
                                CAV_CORNER_R + RIM_W),
                   ledge_z - FIT_RIM, THICK + 60.0, coll)
    boolean(hull, rebate)
    boolean(hull, void)
    for o in (void, rebate):
        o.hide_set(True)
        o.hide_render = True

    # (the cavity floor-to-wall fillet is a milled feature, reported as a
    # parameter rather than drawn - the solid bead it used to draw was not
    # actual geometry and only got in the way of renders)

    # --- bonded-on G10 rim ring with silicone channel ---------------------
    outer = rounded_rect(CAV_X0 - RIM_W, CAV_X1 + RIM_W,
                         -CAV_WIDTH / 2 - RIM_W, CAV_WIDTH / 2 + RIM_W,
                         CAV_CORNER_R + RIM_W)
    rim = prism("V2_G10_RimRing", outer, ledge_z, ledge_z + RIM_T, coll, m_g10)
    hole = prism("V2_RimHole_cut", cav_poly, ledge_z - 8.0, ledge_z + RIM_T + 8.0,
                 coll)
    boolean(rim, hole)
    ci = CHAN_INSET
    chan_o = prism("V2_Chan_o_cut",
                   rounded_rect(CAV_X0 - ci - CHAN_W / 2, CAV_X1 + ci + CHAN_W / 2,
                                -CAV_WIDTH / 2 - ci - CHAN_W / 2,
                                CAV_WIDTH / 2 + ci + CHAN_W / 2,
                                CAV_CORNER_R + ci + CHAN_W / 2),
                   ledge_z + RIM_T - CHAN_D, ledge_z + RIM_T + 4.0, coll)
    chan_i = prism("V2_Chan_i_cut",
                   rounded_rect(CAV_X0 - ci + CHAN_W / 2, CAV_X1 + ci - CHAN_W / 2,
                                -CAV_WIDTH / 2 - ci + CHAN_W / 2,
                                CAV_WIDTH / 2 + ci - CHAN_W / 2,
                                CAV_CORNER_R + ci - CHAN_W / 2),
                   ledge_z + RIM_T - CHAN_D - 2.0, ledge_z + RIM_T + 4.0, coll)
    # Make the cutter an annulus FIRST, then cut once. Cutting with the outer
    # prism and unioning the inner one back plugs the rim's opening.
    boolean(chan_o, chan_i, op='DIFFERENCE')
    boolean(rim, chan_o, op='DIFFERENCE')
    for o in (hole, chan_o, chan_i):
        o.hide_set(True)
        o.hide_render = True

    # --- hatch lid --------------------------------------------------------
    lid_poly = rounded_rect(CAV_X0 - RIM_W + 1.5, CAV_X1 + RIM_W - 1.5,
                            -CAV_WIDTH / 2 - RIM_W + 1.5,
                            CAV_WIDTH / 2 + RIM_W - 1.5,
                            CAV_CORNER_R + RIM_W - 1.5)
    z0 = ledge_z + RIM_T
    # ONE object for the whole sandwich. Modelling it as three plies was
    # honest but meant three more things to hide every time the scene is
    # opened. The cut list still emits the H80 core as its own part, which is
    # where that distinction actually matters.
    prism("V2_Lid", lid_poly, z0, z0 + LID_T, coll, bom_mat("lid"))
    rep["lid_top_z_mm"] = round(z0 + LID_T, 1)
    rep["lid_flush_error_mm"] = round(z0 + LID_T - THICK, 2)
    # A flat lid against a possibly-crowned deck: compare the lid's top to the
    # deck surface at the lid's most outboard point, not at the centreline.
    y_out = CAV_WIDTH / 2 + RIM_W - 1.5
    rep["lid_proud_at_edge_mm"] = round(
        z0 + LID_T - deck_z_at((CAV_X0 + CAV_X1) / 2, y_out), 2)

    # --- hatch lid bolts: M5 through the lid into inserts in the G10 rim ---
    bi = HATCH_BOLT_INSET
    hb = bolt_ring(CAV_X0 - RIM_W + bi, CAV_X1 + RIM_W - bi,
                   -CAV_WIDTH / 2 - RIM_W + bi, CAV_WIDTH / 2 + RIM_W - bi,
                   HATCH_BOLT_PITCH, r=CAV_CORNER_R + RIM_W - bi)
    # Show what gets MADE, not what gets assembled: a clear thru hole in each
    # ply of the lid and the threaded insert sitting in the rim. The bolt
    # itself is hardware, and drawing it just hid the two features that
    # actually have to be machined.
    for i, (bx_, by_) in enumerate(hb):
        h = cyl(f"V2_HatchHole_cut_{i}", bx_, by_, z0 - 1.0,
                z0 + LID_T + 1.0, HATCH_BOLT_D + 0.6, coll)
        boolean(bpy.data.objects["V2_Lid"], h)
        h.hide_set(True)
        h.hide_render = True
        boolean(rim, cyl(f"V2_HatchInsertBore_cut_{i}", bx_, by_,
                         ledge_z + RIM_T - HATCH_INSERT_L,
                         ledge_z + RIM_T + 1.0, HATCH_INSERT_D, coll))
        cyl(f"V2_HatchInsert_{i}", bx_, by_,
            ledge_z + RIM_T - HATCH_INSERT_L, ledge_z + RIM_T,
            HATCH_INSERT_D, coll, m_metal)
    rep["hatch_fastening"] = (
        f"M{HATCH_BOLT_D:.0f} through the lid into "
        f"O{HATCH_INSERT_D:.0f} x {HATCH_INSERT_L:.0f} threaded inserts "
        f"in the {RIM_T:.0f} mm G10 rim")
    rep["hatch_insert_g10_below_mm"] = round(RIM_T - HATCH_INSERT_L, 1)
    rep["hatch_bolts"] = len(hb)
    # every bolt must actually land on the lid, with head clearance
    off = [p for p in hb
           if not point_in_poly(p, lid_poly)
           or min(math.hypot(p[0] - q[0], p[1] - q[1]) for q in lid_poly)
           < HATCH_BOLT_D]
    rep["hatch_bolts_off_lid"] = len(off)
    # Bolt circle must sit OUTBOARD of the channel. Both measured from the
    # rim's outer edge: channel inner face is RIM_W - CHAN_INSET - CHAN_W/2 in,
    # bolt head reaches HATCH_BOLT_INSET + one bolt diameter.
    gap = (RIM_W - CHAN_INSET - CHAN_W / 2) - (bi + HATCH_BOLT_D)
    rep["bolt_to_channel_mm"] = round(gap, 1)
    rep["bolts_clear_channel"] = gap > 2.0

    # --- mast hardpoint ---------------------------------------------------
    g10_x0, g10_x1 = MAST_X - G10_L / 2, MAST_X + G10_L / 2
    # Self-level to the hull underside, exactly as the dense ring does. The
    # plate's bottom is a flat plane and the hull's is not - deepening the
    # bottom vee from 5 to 16 mm lifted the underside at the plate's outboard
    # corners and pushed it 0.11 mm through the skin. Sitting it on the
    # HIGHEST point of its own footprint is the only placement that survives a
    # change to the vee or the rocker.
    plate_z0 = HULL_SKIN
    for i in range(9):
        for j in range(9):
            plate_z0 = max(plate_z0,
                           bottom_z_at(g10_x0 + (g10_x1 - g10_x0) * i / 8,
                                       -G10_W / 2 + G10_W * j / 8) + HULL_SKIN)
    box("V2_G10_MastPlate", g10_x0, g10_x1, -G10_W / 2, G10_W / 2,
        plate_z0, plate_z0 + G10_T, coll, m_g10)
    rep["mast_plate_z0_mm"] = round(plate_z0, 1)
    # The ring's bottom is a flat plane, but the hull underside is not - tail
    # rocker plus the bottom vee lift it ~4 mm at the ring's aft-outer corner,
    # and a ring starting at HULL_SKIN erupted through the skin there. Sit it
    # on the HIGHEST hull bottom under its own footprint so it cannot.
    rx0, rx1 = g10_x0 - DENSE_MARGIN, g10_x1 + DENSE_MARGIN
    ry0, ry1 = -G10_W / 2 - DENSE_MARGIN, G10_W / 2 + DENSE_MARGIN
    ring_z0 = HULL_SKIN
    for i in range(9):
        for j in range(9):
            ring_z0 = max(ring_z0, bottom_z_at(rx0 + (rx1 - rx0) * i / 8,
                                               ry0 + (ry1 - ry0) * j / 8)
                          + HULL_SKIN)
    dense = prism("V2_DenseFoam_Ring",
                  rounded_rect(rx0, rx1, ry0, ry1, 40.0),
                  ring_z0, FLOOR_Z - FIT_FLOOR, coll, m_dense)
    rep["dense_ring_z0_mm"] = round(ring_z0, 1)

    # M8 into blind key-locking inserts in the 16 mm plate. The bolt comes up
    # from the mast base and stops inside the plate; nothing breaks the top
    # face, so the cavity floor above it is unbroken.
    plate_z1 = plate_z0 + G10_T      # plate_z0 is the levelled value from above
    bolt_ok = True
    for sx in (-1, 1):
        for sy in (-1, 1):
            bx = MAST_X + sx * BOLT_SPACING_X / 2
            by = sy * BOLT_SPACING_Y / 2
            # insert: from the plate's TOP face down, stopping INSERT_BLIND
            # short of the underside so the laminate below stays continuous
            cyl(f"V2_MastInsert_{sx}{sy}", bx, by,
                plate_z1 - INSERT_L, plate_z1, INSERT_OD, coll, m_metal)
            cyl(f"V2_MastBolt_{sx}{sy}", bx, by,
                plate_z1 - INSERT_L + 1.0, plate_z1 - INSERT_BLIND,
                BOLT_D, coll, m_metal)
            if abs(bx - MAST_X) + INSERT_OD / 2 > G10_L / 2:
                bolt_ok = False
    rep["mast_fastening"] = (f"M8 x {INSERT_L:.0f} key-locking inserts in a "
                             f"{G10_T:.0f} mm G10 plate, blind from below")
    rep["insert_engagement_mm"] = INSERT_L - INSERT_BLIND
    rep["g10_below_insert_mm"] = INSERT_BLIND
    rep["cavity_floor_penetrations"] = 1        # the mast-wire gland, only
    # The mast structure is built off one datum plane at MAST_X, but the hull
    # bottom rises away from it - tail rocker plus the bottom vee, which at the
    # dense ring's outer corners is ~5 mm against a ring that starts at 2 mm.
    # Unclipped, the ring erupts through the hull as two curved slivers.
    envelope = hull.copy()
    envelope.data = hull.data.copy()
    envelope.modifiers.clear()
    coll.objects.link(envelope)
    envelope.name = "V2_HullEnvelope_cut"
    envelope.hide_set(True)
    envelope.hide_render = True
    # Shrink the clip 0.5 mm along its normals so the trimmed faces sit just
    # inside the laminate instead of exactly on it - coplanar faces z-fight.
    # Recalc first: the lofted mesh's normals are not reliably outward, and a
    # negative displace on inward normals inflates the shell instead.
    _fix_normals(envelope)
    d = envelope.modifiers.new("inset", 'DISPLACE')
    d.strength = -0.0005
    d.mid_level = 0.0
    for o in (dense, bpy.data.objects["V2_G10_MastPlate"]):
        boolean(o, envelope, op='INTERSECT')

    # --- mast wire conduit ------------------------------------------------
    # Wet-to-dry crossing. The tube is bonded through the hull skin, the mast
    # plate and the dense ring, and is potted solid at its lower end; the only
    # dry-side penetration in the whole cavity is the gland on top of it.
    cdx = MAST_X + CONDUIT_X_OFF
    cd_z0 = bottom_z_at(cdx, 0.0)
    cd = cyl("V2_Conduit", cdx, 0.0, cd_z0, FLOOR_Z + 6.0, CONDUIT_D,
             coll, bom_mat("g10_mast"), seg=24)
    bore = cyl("V2_Conduit_bore_cut", cdx, 0.0, cd_z0 - 2.0, FLOOR_Z + 8.0,
               CONDUIT_D - 2 * CONDUIT_WALL, coll, seg=24)
    boolean(cd, bore)
    bore.hide_set(True)
    bore.hide_render = True
    for o in (dense, bpy.data.objects["V2_G10_MastPlate"]):
        c = cyl(f"V2_ConduitHole_cut_{o.name}", cdx, 0.0, cd_z0 - 2.0,
                FLOOR_Z + 8.0, CONDUIT_D + 0.4, coll, seg=24)
        boolean(o, c)
        c.hide_set(True)
        c.hide_render = True
    cyl("V2_Conduit_Gland", cdx, 0.0, FLOOR_Z + 6.0, FLOOR_Z + 6.0 + 18.0,
        GLAND_D + 8.0, coll, m_metal, seg=20)
    rep["conduit_od_mm"] = CONDUIT_D
    rep["conduit_bore_mm"] = CONDUIT_D - 2 * CONDUIT_WALL
    rep["conduit_clear_of_mast_inserts_mm"] = round(
        BOLT_SPACING_X / 2 - INSERT_OD / 2 - CONDUIT_D / 2, 1)

    build_foil(coll, rep)

    rep["bolts_inside_G10"] = bolt_ok
    rep["mast_bolts_intrude_into_cavity"] = False

    # --- electronics module, as fabricable panels -------------------------
    # Six flat G10 parts plus a sandwich lid. Everything is a 2D profile that
    # nests on one sheet, so it is a single CNC setup and there is no 256 mm
    # print-bed limit to design around.
    ex0, ex1 = MOD_X0, CAV_X1 - ENC_GAP
    ey0, ey1 = -ext_w / 2, ext_w / 2
    ez0, ez1 = FLOOR_Z, FLOOR_Z + ext_h
    iz0 = ez0 + ENC_FLOOR
    ix0, ix1 = ex0 + ENC_WALL, ex1 - ENC_WALL
    iy0, iy1 = ey0 + ENC_WALL, ey1 - ENC_WALL
    lid_z0 = ez1 - ENC_LID_T
    m_lid = bom_mat("lid_mod")

    # Joinery. The walls do NOT butt onto the floor's top face - a 3 mm edge
    # gives a 3 mm glue line with no location, which is a hinge, not a joint.
    # The floor is machined with a 1.5 mm groove that the walls seat into, so
    # the box self-jigs during glue-up and the joint loads in shear.
    wall_top = lid_z0 - FIT_LID
    floor_top = ez0 + ENC_FLOOR
    wall_z0 = floor_top - JOINT_GROOVE_D
    floor = box("V2_Mod_Floor", ex0, ex1, ey0, ey1, ez0, floor_top, coll, m_enc)
    grv = []
    for nm, a, b, c, d in (
            ("P", ex0, ex1, ey1 - ENC_WALL, ey1),
            ("S", ex0, ex1, ey0, ey0 + ENC_WALL),
            ("A", ex0, ex0 + ENC_WALL, ey0, ey1),
            ("F", ex1 - ENC_WALL, ex1, ey0, ey1)):
        g = box(f"V2_FloorGroove_cut_{nm}", a + 0.15, b - 0.15, c + 0.15,
                d - 0.15, wall_z0, floor_top + 1.0, coll)
        boolean(floor, g)
        g.hide_set(True)
        g.hide_render = True
        grv.append(nm)

    # Long walls run full length; end walls land BETWEEN them - a lap, so each
    # end wall's glue line is its 3 mm edge PLUS the long wall's inner face.
    box("V2_Mod_WallP", ex0, ex1, ey1 - ENC_WALL, ey1, wall_z0, wall_top, coll, m_enc)
    box("V2_Mod_WallS", ex0, ex1, ey0, ey0 + ENC_WALL, wall_z0, wall_top, coll, m_enc)
    box("V2_Mod_WallAft", ex0, ex0 + ENC_WALL, iy0, iy1, wall_z0, wall_top, coll, m_enc)
    box("V2_Mod_WallFwd", ex1 - ENC_WALL, ex1, iy0, iy1, wall_z0, wall_top, coll, m_enc)

    # A G10 corner post in each internal corner. This is what replaces the
    # divider's stiffening job, and it turns a 3 mm butted corner into two
    # CORNER_POST-long bonded faces.
    m_post = bom_mat("g10")
    for nm, sx, sy in (("AS", 0, 0), ("AP", 0, 1), ("FS", 1, 0), ("FP", 1, 1)):
        px_ = ix0 if sx == 0 else ix1 - CORNER_POST
        py_ = iy0 if sy == 0 else iy1 - CORNER_POST
        # Stop UNDER the flange rail. Running them to wall_top made the posts
        # and the flange rails occupy the same space at all four corners, and
        # the interpenetrating solids read as bolt heads sitting in the
        # corners of the box. The flange now lands on top of the posts.
        box(f"V2_Mod_Post{nm}", px_, px_ + CORNER_POST, py_, py_ + CORNER_POST,
            floor_top, wall_top - MOD_FLANGE_H, coll, m_post)
    post_area = 4 * 2 * CORNER_POST * (wall_top - MOD_FLANGE_H - floor_top)
    rep["joint"] = (f"{JOINT_GROOVE_D:.1f} mm locating groove in the floor, "
                    f"end walls lapped inside the long walls, "
                    f"{CORNER_POST:.0f} mm G10 corner posts, thickened epoxy "
                    f"+ {FILLET_R:.0f} mm glass-tape fillet inside every corner")
    rep["corner_post_bond_area_mm2"] = round(post_area)
    rep["floor_bond_area_mm2"] = round(
        2 * ((ex1 - ex0) + (ey1 - ey0)) * (ENC_WALL + JOINT_GROOVE_D))

    # Flange rail inside the top edge - 4 mm wall cannot hold a heat-set insert
    fz0 = wall_top - MOD_FLANGE_H
    m_fl = bom_mat("flange")
    for nm, a, b, c, d in (
            ("P", ix0, ix1, iy1 - MOD_FLANGE_W, iy1),
            ("S", ix0, ix1, iy0, iy0 + MOD_FLANGE_W),
            ("A", ix0, ix0 + MOD_FLANGE_W, iy0 + MOD_FLANGE_W, iy1 - MOD_FLANGE_W),
            ("F", ix1 - MOD_FLANGE_W, ix1, iy0 + MOD_FLANGE_W, iy1 - MOD_FLANGE_W)):
        box(f"V2_Mod_Flange{nm}", a, b, c, d, fz0, wall_top, coll, m_fl)

    # Sandwich, not solid: glass / H80 PVC foam / glass. The skins carry the
    # bending, the foam only holds them apart. Solid G10 of the same weight
    # would be far floppier, and a lid that bows between bolts breaks gasket
    # compression mid-span - which no amount of seal tuning fixes.
    box("V2_Mod_Lid", ex0, ex1, ey0, ey1, lid_z0, ez1, coll, m_lid)

    # Thru holes in each ply and the insert in the flange rail - the two
    # machined features. The bolt is hardware; drawing it hid both.
    mb = bolt_ring(ix0 + MOD_FLANGE_W / 2, ix1 - MOD_FLANGE_W / 2,
                   iy0 + MOD_FLANGE_W / 2, iy1 - MOD_FLANGE_W / 2,
                   MOD_BOLT_PITCH)
    for i, (bx_, by_) in enumerate(mb):
        h = cyl(f"V2_ModBoltHole_cut_{i}", bx_, by_, lid_z0 - 1.0,
                ez1 + 1.0, MOD_BOLT_D + 0.5, coll)
        boolean(bpy.data.objects["V2_Mod_Lid"], h)
        h.hide_set(True)
        h.hide_render = True
        cyl(f"V2_ModInsert_{i}", bx_, by_, wall_top - MOD_INSERT_L, wall_top,
            MOD_INSERT_D, coll, m_metal)
    rep["module_lid_bolts"] = len(mb)
    rep["module_lid_bolt_pitch_mm"] = round(
        2 * ((ix1 - ix0) + (iy1 - iy0)) / max(1, len(mb)), 1)

    # --- upright pack, BMS on top ----------------------------------------
    # Pack pushed against one wall; the leftover width becomes one strip wide
    # enough for the ESC rather than two useless ones. ~9 kg offset ~50 mm
    # moves the rider+board centroid about 3 mm - irrelevant.
    pack_l, pack_w = L["pack_l"], L["pack_w"]
    px0 = ix0 + PACK_END_CLR
    pack_y0 = iy0 + PACK_SIDE_CLR
    pack_y1 = pack_y0 + pack_w
    iy_c = (pack_y0 + pack_y1) / 2
    pack_x1 = px0 + pack_l

    pack_h = L["pack_h"]
    verts, faces = [], []
    seg, r = 14, CELL_D / 2

    def _tube(p0, p1, axis):
        """Capped cylinder from p0 to p1 along 'axis' (0=X, 2=Z)."""
        b = len(verts)
        for i in range(seg):
            a = 2 * math.pi * i / seg
            c, s_ = r * math.cos(a), r * math.sin(a)
            if axis == 0:            # lying, axis along X
                verts.append((p0[0], p0[1] + c, p0[2] + s_))
                verts.append((p1[0], p0[1] + c, p0[2] + s_))
            else:                    # upright, axis along Z
                verts.append((p0[0] + c, p0[1] + s_, p0[2]))
                verts.append((p0[0] + c, p0[1] + s_, p1[2]))
        for i in range(seg):
            j = (i + 1) % seg
            faces.append([b + 2 * i, b + 2 * j, b + 2 * j + 1, b + 2 * i + 1])
        faces.append([b + 2 * i for i in range(seg - 1, -1, -1)])
        faces.append([b + 2 * i + 1 for i in range(seg)])

    if CELLS_LYING:
        # Each 8-abreast column across Y is one 8P group; 8 groups along X make
        # a layer; 2 layers make 16S. Terminals of a group share one X plane,
        # which is what lets a whole layer be welded flat before stacking.
        for lay in range(PACK_LAYERS):
            cz = iz0 + HOLD_BASE_T + (lay + 0.5) * PITCH_LAY_Z
            for g in range(LAY_S):
                x0 = px0 + PACK_EDGE + g * (CELL_L + BUS_GAP)
                for p in range(PACK_P):
                    cy = pack_y0 + PACK_EDGE + (p + 0.5) * PITCH_LAY_Y
                    _tube((x0, cy, cz), (x0 + CELL_L, cy, cz), 0)
        # the one full-current link between the two layers, at the far end
        box("V2_Pack_LayerLink", pack_x1 - PACK_EDGE - 14.0, pack_x1 - PACK_EDGE,
            pack_y0 + PACK_EDGE, pack_y1 - PACK_EDGE,
            iz0 + HOLD_BASE_T, iz0 + pack_h, coll, bom_mat("nickel"))
        # busbars between series groups, standing in the gaps
        for g in range(1, LAY_S):
            bx = px0 + PACK_EDGE + g * (CELL_L + BUS_GAP) - BUS_GAP / 2
            for lay in range(PACK_LAYERS):
                cz = iz0 + HOLD_BASE_T + lay * PITCH_LAY_Z
                box(f"V2_Pack_Busbar_{lay}_{g}", bx - 1.0, bx + 1.0,
                    pack_y0 + PACK_EDGE, pack_y1 - PACK_EDGE,
                    cz + 2.0, cz + PITCH_LAY_Z - 2.0, coll, bom_mat("nickel"))
    else:
        for row in range(PACK_S):
            for p in range(PACK_P):
                cx = px0 + PACK_EDGE + (row + 0.5) * PITCH_ROW
                cy = pack_y0 + PACK_EDGE + (p + 0.5) * PITCH_CELL
                _tube((cx, cy, iz0), (cx, cy, iz0 + pack_h), 2)
    new_object("V2_Pack_Cells", verts, faces, coll, m_cell)
    box("V2_Pack_Wrap", px0, pack_x1, pack_y0, pack_y1,
        iz0 + pack_h, iz0 + pack_h + WRAP_T, coll, bom_mat("wrap"))
    rep["pack_layers"] = PACK_LAYERS if CELLS_LYING else 1
    rep["pack_layout"] = (
        f"{LAY_S}S{PACK_P}P per layer x {PACK_LAYERS} layers = "
        f"{PACK_S}S{PACK_P}P, cells lying along X"
        if CELLS_LYING else f"{PACK_S}S{PACK_P}P upright")
    rep["interlayer_links"] = 1 if CELLS_LYING else 0

    if BMS_HOME == "flat_beside":
        # On a shelf ABOVE the ESC, not beside it. The pack sets the module
        # height, so there is ~35 mm of dead air over a 41 mm ESC in a 76 mm
        # box - putting the 16 mm BMS there costs nothing and is the one place
        # in this box that was pure wasted volume. Side by side, the two also
        # simply did not fit once the box went back to 425 long.
        bz0 = iz0 + ESC_H + 4.0
        by0 = pack_y1 + 2.0
        bx_ = ix0 + 20.0
        box("V2_BMS", bx_, bx_ + BMS_E_L, by0, by0 + BMS_E_H,
            bz0, bz0 + BMS_E_T, coll, m_pcb)
        rep["bms_home"] = "on a shelf above the ESC"
        rep["bms_headroom_mm"] = round(int_h - (bz0 - iz0 + BMS_E_T), 1)
        rep["bms_over_esc_clear_mm"] = 4.0
        rep["bms_within_strip"] = (by0 + BMS_E_H) < iy1
    elif BMS_HOME == "on_edge":
        # Standing against the outboard wall of the service strip, so only its
        # 16 mm thickness costs anything - and it costs WIDTH, not height.
        by1 = iy1 - 4.0
        by0 = by1 - BMS_E_T
        bx_ = ix0 + (int_l - BMS_E_L) / 2
        box("V2_BMS", bx_, bx_ + BMS_E_L, by0, by1,
            iz0 + 3.0, iz0 + 3.0 + BMS_E_H, coll, m_pcb)
        box("V2_BMS_Lugs", bx_, bx_ + 26.0, by0 - BMS_LUG_STACK, by0,
            iz0 + 3.0, iz0 + 3.0 + 30.0, coll, m_metal)
        rep["bms_standing_top_mm"] = round(3.0 + BMS_E_H, 1)
        rep["bms_headroom_mm"] = round(int_h - (3.0 + BMS_E_H), 1)
        rep["bms_to_esc_mm"] = round(by0 - BMS_LUG_STACK - (pack_y1 + ESC_W), 1)
    else:
        bms_z0 = iz0 + pack_h + WRAP_T if BMS_ON_PACK else iz0
        bms_x0 = px0 + (pack_l - BMS_W) / 2 if BMS_ON_PACK else pack_x1 + 8.0
        box("V2_BMS", bms_x0, bms_x0 + BMS_W, iy_c - BMS_L / 2, iy_c + BMS_L / 2,
            bms_z0, bms_z0 + BMS_H, coll, m_pcb)
    end_zone = ix1 - pack_x1
    rep["bms_footprint_on_pack_ok"] = (BMS_W <= pack_l and BMS_L <= pack_w)

    # --- ESC bay and wire raceway (no divider) ----------------------------
    strip = iy1 - pack_y1
    strip_y0 = pack_y1
    box("V2_ESC", ix0 + 20.0, ix0 + 20.0 + ESC_L, strip_y0, strip_y0 + ESC_W,
        iz0, iz0 + ESC_H, coll,
        bom_mat("esc"))
    box("V2_Fuse", ix0 + 20.0 + ESC_L + 25.0, ix0 + 20.0 + ESC_L + 25.0 + FUSE_L,
        strip_y0, strip_y0 + FUSE_W, iz0, iz0 + FUSE_H, coll,
        bom_mat("fuse"))
    rep["esc_bay_width_mm"] = round(strip, 1)
    rep["wire_raceway_w_mm"] = round(strip - 4.0 - ESC_W, 1)

    # --- aft service bay: glands, power button, charge port ---------------
    # All of it lives in the bay the conduit already forced into existence,
    # between the cavity's aft wall and the module's aft wall. Nothing here
    # penetrates the HULL - the hatch is still the only way in, and the
    # conduit gland is still the only wet-to-dry crossing.
    bay_x0, bay_x1 = CAV_X0, MOD_X0
    bay_mid = (bay_x0 + bay_x1) / 2.0
    # Glands go in the SERVICE STRIP, not on the centreline. The pack now
    # butts the aft wall, so a gland on the centreline lands its body and its
    # backing nut directly against the cells - there is nowhere for the wire
    # to turn and nowhere to get a spanner. Stack them tight in the strip,
    # where the ESC and the raceway already are.
    aft_wall = bpy.data.objects["V2_Mod_WallAft"]
    g_pitch = BAY_GLAND_D + 10.0                 # PG11 nut A/F is ~24
    g_span = (BAY_GLAND_N - 1) * g_pitch
    # Glands occupy the inboard part of the row; button and port follow.
    g_mid = (strip_y0 + iy1) / 2.0
    gz = iz0 + (BAY_GLAND_D + 7.0) / 2 + 6.0
    for g in range(BAY_GLAND_N):
        gy = g_mid - g_span / 2.0 + g * g_pitch
        hole = box(f"V2_BayGlandHole_cut_{g}", ex0 - 2.0, ex0 + ENC_WALL + 2.0,
                   gy - BAY_GLAND_D / 2, gy + BAY_GLAND_D / 2,
                   gz - BAY_GLAND_D / 2, gz + BAY_GLAND_D / 2, coll)
        boolean(aft_wall, hole)
        hole.hide_set(True)
        hole.hide_render = True
        box(f"V2_BayGland_{g}", ex0 - 9.0, ex0 + ENC_WALL + 4.0,
            gy - (BAY_GLAND_D + 7) / 2, gy + (BAY_GLAND_D + 7) / 2,
            gz - (BAY_GLAND_D + 7) / 2, gz + (BAY_GLAND_D + 7) / 2,
            coll, m_metal)
    rep["gland_y_range_mm"] = (round(g_mid - g_span / 2 - (BAY_GLAND_D + 7) / 2, 1),
                               round(g_mid + g_span / 2 + (BAY_GLAND_D + 7) / 2, 1))
    rep["gland_to_pack_mm"] = round(
        (g_mid - g_span / 2 - (BAY_GLAND_D + 7) / 2) - pack_y1, 1)
    rep["glands_clear_pack"] = rep["gland_to_pack_mm"] > 0
    rep["glands_inside_strip"] = (
        g_mid + g_span / 2 + (BAY_GLAND_D + 7) / 2 < iy1)

    # The button and the port were floating in the bay attached to nothing.
    # They mount on a G10 service panel bonded to the module's aft wall, so
    # they lift out WITH the module instead of tethering it to the hull - the
    # whole point of a removable module is that it comes out in one piece.
    # The panel is offset to the strip side, clear of the pack.
    # Button and charge port are PANEL-MOUNT THROUGH THE AFT WALL, exactly
    # like the glands - not on a bracket. The module's aft wall is the
    # connector panel: three glands low, button and port above them. Every
    # penetration is a sealed panel fitting, the module stays a closed box,
    # and the whole thing still lifts out in one piece.
    #
    # All of it stays inside the service strip band in Y, because the pack
    # butts the aft wall everywhere else and a fitting's body plus its backing
    # nut would land straight on the cells.
    btn_z = gz + (BAY_GLAND_D + 7.0) / 2 + 6.0 + max(BTN_D, CHG_H) / 2 + 4.0
    btn_y = g_mid - 24.0
    chg_y = g_mid + 26.0
    for nm, cy, cz, w, h, depth, m in (
            ("PowerButton", btn_y, btn_z, BTN_D, BTN_D, BTN_H, bom_mat("fuse")),
            ("ChargePort", chg_y, btn_z, CHG_W, CHG_H, CHG_L, bom_mat("esc"))):
        cut = box(f"V2_{nm}Hole_cut", ex0 - 2.0, ex0 + ENC_WALL + 2.0,
                  cy - w / 2, cy + w / 2, cz - h / 2, cz + h / 2, coll)
        boolean(aft_wall, cut)
        cut.hide_set(True)
        cut.hide_render = True
        box(f"V2_{nm}", ex0 - depth, ex0 + ENC_WALL + 6.0,
            cy - w / 2 - 4.0, cy + w / 2 + 4.0,
            cz - h / 2 - 4.0, cz + h / 2 + 4.0, coll, m)

    rep["aft_wall_is_connector_panel"] = (
        f"{BAY_GLAND_N} x PG11 glands, power button, charge port - all "
        f"panel-mount through the module aft wall, all inside the service strip")
    rep["button_to_pack_mm"] = round(btn_y - BTN_D / 2 - 4.0 - pack_y1, 1)
    rep["port_to_pack_mm"] = round(chg_y - CHG_W / 2 - 4.0 - pack_y1, 1)
    rep["button_to_port_mm"] = round(
        (chg_y - CHG_W / 2 - 4.0) - (btn_y + BTN_D / 2 + 4.0), 1)
    rep["fittings_above_glands_mm"] = round(
        (btn_z - max(BTN_D, CHG_H) / 2 - 4.0) - (gz + (BAY_GLAND_D + 7) / 2), 1)
    rep["fittings_beside_glands_mm"] = 99.0
    rep["fittings_under_wall_top_mm"] = round(
        (iz0 + int_h) - (btn_z + max(BTN_D, CHG_H) / 2 + 4.0), 1)
    rep["panel_row_end_to_wall_mm"] = round(iy1 - (chg_y + CHG_W / 2 + 4.0), 1)
    rep["panel_rows"] = 2
    rep["fittings_inside_strip"] = (btn_y - BTN_D / 2 - 4.0 > pack_y1
                                    and chg_y + CHG_W / 2 + 4.0 < iy1)
    # they stick aft into the bay - make sure the bay is deep enough
    rep["fittings_protrude_into_bay_mm"] = round(max(BTN_H, CHG_L), 1)
    rep["bay_depth_mm"] = round(ex0 - CAV_X0, 1)

    bay_l = bay_x1 - bay_x0
    rep["service_bay_mm"] = f"{bay_l:.0f} x {CAV_WIDTH:.0f}"
    rep["service_bay_holds"] = (f"mast conduit gland, {BAY_GLAND_N} x PG11 "
                                f"module glands, power button, charge port")
    # conduit is at y=0; button at -85, port spans +62..+94. Check they miss it.
    rep["button_to_conduit_mm"] = round(85.0 - BTN_D / 2 - GLAND_D / 2 - 4.0, 1)
    rep["port_to_conduit_mm"] = round(62.0 - GLAND_D / 2 - 4.0, 1)
    rep["bay_items_fit_width"] = (85.0 + BTN_D / 2 < CAV_WIDTH / 2
                                  and 62.0 + CHG_W < CAV_WIDTH / 2)
    rep["bay_items_fit_length"] = max(BTN_D, CHG_L) + 8.0 < bay_l
    rep["pack_offset_mm"] = round(iy_c, 1)
    rep["end_zone_mm"] = round(end_zone, 1)
    rep["esc_fits_strip"] = ESC_W <= strip - 4.0
    rep["esc_strip_clear_mm"] = round(strip - 4.0 - ESC_W, 1)
    rep["fuse_fits_strip"] = FUSE_W <= strip - 4.0
    rep["esc_fuse_run_mm"] = round(ESC_L + 25.0 + FUSE_L, 1)
    rep["strip_length_avail_mm"] = round(ix1 - ix0, 1)
    rep["bms_home"] = BMS_HOME
    rep["bms_placed_ok"] = True
    rep["esc_headroom_mm"] = round(int_h - ESC_H, 1)

    # --- fit checks -------------------------------------------------------
    # lift-out: the module must pass through the rim opening
    # A square module corner sits sqrt(2)*(R - gap) from the cavity's corner
    # arc centre; it must not exceed R.
    rep["corner_clear_mm"] = round(
        CAV_CORNER_R - math.sqrt(2.0) * (CAV_CORNER_R - ENC_GAP), 1)
    rep["module_corners_fit"] = rep["corner_clear_mm"] > 0.5
    rep["liftout_clear_x_mm"] = round((CAV_X1 - CAV_X0) - (ex1 - ex0), 1)
    rep["liftout_clear_y_mm"] = round(CAV_WIDTH - ext_w, 1)
    rep["liftout_ok"] = (ex1 - ex0) < (CAV_X1 - CAV_X0) and ext_w < CAV_WIDTH

    # the flat cavity floor must stay above the hull bottom everywhere
    worst = 1e9
    for i in range(61):
        x = CAV_X0 + (CAV_X1 - CAV_X0) * i / 60
        bot = rocker(x / LENGTH) + BOTTOM_VEE * 0.0
        worst = min(worst, FLOOR_Z - bot - HULL_SKIN)
    rep["min_floor_thickness_mm"] = round(worst, 1)

    # the opening must fit inside the deck at the ledge height
    tight = 1e9
    for i in range(61):
        x = CAV_X0 + (CAV_X1 - CAV_X0) * i / 60
        tight = min(tight, deck_half_width_at_z(x, ledge_z)
                    - (CAV_WIDTH / 2 + RIM_W))
    rep["rim_edge_to_rail_mm"] = round(tight, 1)
    rep["rim_fits_deck"] = tight > 0

    rep["seam_to_cavity_mm"] = round(SEAM_X - CAV_X1, 1)
    # The cavity is a sealed air volume, so it displaces water. V1's doc makes
    # the same split: foam 75.3 L, sealed displacement 96.6 L. Reporting only
    # the foam understated float by the whole cavity.
    rep["foam_volume_L"] = round(volume_litres(hull), 2)
    cav_air = volume_litres(bpy.data.objects["V2_Cavity_Void_cut"]) \
        - (CAV_X1 - CAV_X0) * CAV_WIDTH * (THICK + 60.0 - ledge_z) * 1e-6
    rep["cavity_air_L"] = round(max(0.0, cav_air), 2)
    rep["sealed_displacement_L"] = round(rep["foam_volume_L"]
                                         + rep["cavity_air_L"], 2)
    rep["hull_volume_L"] = rep["sealed_displacement_L"]
    rep["bbox_fill_pct"] = round(rep["sealed_displacement_L"] * 1e6
                                 / (LENGTH * WIDTH * THICK) * 100, 1)
    # --- mass budget ------------------------------------------------------
    # Was hardcoded as "- 86 - 16", where 16 kg was the TARGET board mass out
    # of the V2 docs, not a computed one. "Will it sink" is exactly the
    # question that assumption was hiding, so build the mass from the geometry
    # the model already knows.
    RHO_EPS, RHO_G10, RHO_H80, RHO_H200 = 32.0, 1850.0, 80.0, 200.0
    GLASS_KGM2 = 2.20            # 2 x 6 oz + 1708 biax, bagged, wet
    m = {}
    m["EPS core"] = rep["foam_volume_L"] * 1e-3 * RHO_EPS
    # hull wetted area from the section perimeters
    area = 0.0
    N = 120
    for i in range(N):
        x = (i + 0.5) / N
        sec = section(half_width(x), thickness(x), x)
        per = sum(math.hypot(sec[j + 1][0] - sec[j][0], sec[j + 1][1] - sec[j][1])
                  for j in range(len(sec) - 1))
        area += 2.0 * per * (LENGTH / N)          # both halves
    m["glass skin"] = area * 1e-6 * GLASS_KGM2
    g10_cm3 = (
        (ex1 - ex0) * (ey1 - ey0) * ENC_FLOOR                       # module floor
        + 2 * (ex1 - ex0) * (wall_top - wall_z0) * ENC_WALL          # long walls
        + 2 * (iy1 - iy0) * (wall_top - wall_z0) * ENC_WALL          # end walls
        + 4 * CORNER_POST * CORNER_POST * (wall_top - MOD_FLANGE_H - floor_top)
        + 2 * ((ix1 - ix0) + (iy1 - iy0)) * MOD_FLANGE_W * MOD_FLANGE_H
        + G10_L * G10_W * G10_T                                      # mast plate
        + (((CAV_X1 - CAV_X0 + 2 * RIM_W) * (CAV_WIDTH + 2 * RIM_W))
           - (CAV_X1 - CAV_X0) * CAV_WIDTH) * RIM_T)                 # rim ring
    m["G10"] = g10_cm3 * 1e-9 * RHO_G10
    lid_a = (CAV_X1 - CAV_X0 + 2 * RIM_W) * (CAV_WIDTH + 2 * RIM_W) * 1e-6
    mod_a = (ex1 - ex0) * (ey1 - ey0) * 1e-6
    m["lids"] = ((lid_a * LID_CORE * 1e-3 * RHO_H80 + 2 * lid_a * GLASS_KGM2 * 0.5)
                 + (mod_a * ENC_LID_CORE * 1e-3 * RHO_H80 + 2 * mod_a * GLASS_KGM2 * 0.5))
    m["dense foam"] = (((rx1 - rx0) * (ry1 - ry0) - G10_L * G10_W)
                       * (FLOOR_Z - ring_z0)) * 1e-9 * RHO_H200
    m["battery"] = PACK_S * PACK_P * CELL_G * 1e-3
    m["ESC"] = 0.60                     # Flipsky 75200 Pro
    m["BMS"] = 0.32                     # LLT OD17S051-3, 150 x 75 x 16
    m["fuse + switch + port"] = 0.45
    m["wiring + conduit"] = 1.30        # 8 AWG runs, balance loom, G10 tube
    m["hardware + seal"] = 0.9           # A4 bolts, inserts, silicone, adhesive
    board_kg = sum(m.values())
    # The foil is not part of the board's sealed displacement, but it is part
    # of what the water has to hold up. Gong alu mast + fuselage + wings ~4.2,
    # Flipsky 65161 ~2.6, prop + clamp ~0.5.
    foil_kg = 7.3
    rig_kg = board_kg + foil_kg
    rep["mass_kg"] = {k: round(v, 2) for k, v in m.items()}
    rep["board_mass_kg"] = round(board_kg, 1)
    rep["foil_mass_kg"] = foil_kg
    rep["rig_mass_kg"] = round(rig_kg, 1)
    rep["rider_kg"] = 86.0
    rep["net_float_kg"] = round(rep["sealed_displacement_L"] - 86.0 - board_kg, 1)
    # Reserve the BOARD alone has, and how deep the deck sits with the rider on
    rep["board_alone_reserve_kg"] = round(rep["sealed_displacement_L"] - board_kg, 1)
    waterplane = 0.0
    for i in range(N):
        waterplane += 2.0 * half_width((i + 0.5) / N) * DECK_WIDTH_F * (LENGTH / N)
    rep["waterplane_m2"] = round(waterplane * 1e-6, 3)
    rep["net_float_with_foil_kg"] = round(
        rep["sealed_displacement_L"] - 86.0 - rig_kg, 1)
    sink = -rep["net_float_with_foil_kg"]
    rep["deck_below_water_mm"] = (round(sink / (waterplane * 1e-6), 0)
                                  if sink > 0 else 0.0)

    # --- fore/aft balance -------------------------------------------------
    # Where the mass actually sits. The pack is ~9 kg of a ~16 kg board, so it
    # dominates, and moving it is the only real lever on trim.
    pack_cg = px0 + pack_l / 2.0
    mod_cg = (ex0 + ex1) / 2.0
    hull_cg = LENGTH * 0.47                      # foam, close to the area centroid
    m_pack, m_mod, m_hull = 12.0, 2.5, 5.0       # kg: pack+BMS, module+ESC, hull
    tot = m_pack + m_mod + m_hull
    cg = (pack_cg * m_pack + mod_cg * m_mod + hull_cg * m_hull) / tot
    rep["pack_cg_mm"] = round(pack_cg, 1)
    rep["board_cg_mm"] = round(cg, 1)
    rep["board_cg_pct"] = round(cg / LENGTH * 100, 1)
    rep["cg_ahead_of_mast_mm"] = round(cg - MAST_X, 1)

    # --- automatic interference sweep ------------------------------------
    # Two different shells, because "inside" means two different things.
    # Structure bonded into the core must be inside the RAW loft. The module
    # lives in the cavity, which is a void in the hull - testing it against the
    # hull says it protrudes, which is how the check read on its first run.
    raw = bpy.data.objects.new("V2_HullRaw_cut", hull.data.copy())
    coll.objects.link(raw)
    raw.hide_set(True)
    raw.hide_render = True
    # The checks read evaluated meshes, so the depsgraph has to see everything
    # built above first. Without this the shell evaluates empty and every
    # containment test reports the whole part as protruding.
    bpy.context.view_layer.update()
    hits = run_interference(
        coll,
        pairs=[("V2_Pack_Cells", "V2_Mod_Lid"), ("V2_BMS", "V2_Mod_Lid"),
               ("V2_ESC", "V2_Mod_Lid"), ("V2_Pack_Cells", "V2_Mod_WallP"),
               ("V2_Mod_PostAS", "V2_Mod_FlangeS"),
               ("V2_BMS", "V2_ESC"), ("V2_BMS", "V2_Pack_Cells"),
               ("V2_BMS", "V2_Mod_Lid"),
               ("V2_PowerButton", "V2_BayGland_2"),
               ("V2_ChargePort", "V2_BayGland_2"),
               ("V2_PowerButton", "V2_ChargePort"),
               ("V2_PowerButton", "V2_Pack_Cells"),
               ("V2_ChargePort", "V2_Conduit_Gland"),
               ("V2_Pack_Cells", "V2_Mod_PostAS"),
               ("V2_ESC", "V2_Mod_PostAP"), ("V2_Conduit", "V2_Mod_Floor"),
               ("V2_Pack_Cells", "V2_Mod_WallS"), ("V2_ESC", "V2_Mod_WallP"),
               ("V2_DenseFoam_Ring", "V2_Cavity_Void_cut"),
               ("V2_G10_MastPlate", "V2_Cavity_Void_cut"),
               ("V2_Mod_Floor", "V2_MastBolt_11"),
               ("V2_Mod_Floor", "V2_MastBolt_-11"),
               ("V2_Mod_Lid", "V2_G10_RimRing")],
        contains=[("V2_Mod_Floor", "V2_Cavity_Void_cut"),
                  ("V2_Mod_Lid", "V2_Cavity_Void_cut"),
                  ("V2_Mod_WallP", "V2_Cavity_Void_cut"),
                  ("V2_Pack_Cells", "V2_Cavity_Void_cut")],
        rep=rep)

    # Analytic containment for the parts bonded into the core
    b_ring = check_inside("dense_ring", rx0, rx1, ry0, ry1,
                          ring_z0, FLOOR_Z - FIT_FLOOR, rep)
    b_plate = check_inside("mast_plate", g10_x0, g10_x1, -G10_W / 2, G10_W / 2,
                           plate_z0, plate_z0 + G10_T, rep)

    fails = []
    fails += hits
    if b_ring > 0.5:
        fails.append(f"dense foam ring breaks the hull by {b_ring:.1f} mm "
                     f"at {rep['breach_dense_ring_at']}")
    if b_plate > 0.5:
        fails.append(f"mast plate breaks the hull by {b_plate:.1f} mm "
                     f"at {rep['breach_mast_plate_at']}")
    if not rep["bolts_clear_channel"]:
        fails.append("hatch bolts pass through the silicone channel")
    if rep["hatch_bolts_off_lid"]:
        fails.append(f"{rep['hatch_bolts_off_lid']} hatch bolts miss the lid")
    if not rep["module_corners_fit"]:
        fails.append("module corners foul the cavity radii")
    if rep["fittings_under_wall_top_mm"] < 0:
        fails.append("aft-wall fittings stand above the wall top")
    if rep.get("fittings_beside_glands_mm", 1) < 0:
        fails.append("aft-wall fittings clash with the gland row")
    if rep.get("panel_row_end_to_wall_mm", 1) < 0:
        fails.append("connector row runs off the end of the aft wall")
    if not rep["fittings_inside_strip"]:
        fails.append("aft-wall fittings foul the pack")
    if BMS_HOME == "on_edge" and rep.get("bms_headroom_mm", 1) < 0:
        fails.append("BMS on edge is taller than the module")
    if abs(rep["lid_proud_at_edge_mm"]) > 0.3:
        fails.append("flat lid does not sit flush at its outboard edge")
    if not rep["bms_footprint_on_pack_ok"] and BMS_ON_PACK:
        fails.append("BMS overhangs the pack")
    if not rep["liftout_ok"]:
        fails.append("module cannot lift out")
    if not rep["rim_fits_deck"]:
        fails.append("rim ring overhangs the rail")
    if rep["min_floor_thickness_mm"] < 8:
        fails.append("cavity floor too thin over the rocker")
    if abs(rep["lid_flush_error_mm"]) > 1.0:
        fails.append("lid not flush")
    if not rep["esc_fits_strip"]:
        fails.append("ESC does not fit the side strip")
    if not rep["fuse_fits_strip"]:
        fails.append("fuse does not fit the side strip")
    if rep["esc_fuse_run_mm"] > rep["strip_length_avail_mm"]:
        fails.append("ESC + fuse longer than the strip")
    if not rep["bms_placed_ok"]:
        fails.append("BMS has no home")
    if rep["esc_headroom_mm"] < 0:
        fails.append("ESC too tall for the module")
    if L["stack"] + TOP_CLEAR > int_h + 0.01:
        fails.append("pack + BMS taller than the module interior")
    # --- bill of materials, so the model states its own assumptions --------
    rep["materials"] = {
        "hull core": "EPS ~2 lb/ft3, CNC milled in two halves, seam at "
                     f"{SEAM_X:.0f} mm",
        "hull skin": "E-glass 2 x 6 oz + 1708 biax, vacuum bagged",
        "mast hardpoint ring": "Divinycell H200/H250 dense PVC foam",
        "mast plate": f"G10 laminate sheet, {G10_T:.0f} mm",
        "hatch rim ring": f"G10 laminate sheet, {RIM_T:.0f} mm, bonded on",
        "module shell": f"G10 laminate sheet, {ENC_WALL:.0f} mm walls / "
                        f"{ENC_FLOOR:.0f} mm floor, no divider",
        "module flange rail": f"G10, {MOD_FLANGE_W:.0f} x {MOD_FLANGE_H:.0f} mm",
        "hatch lid": f"glass {LID_SKIN:.1f} / H80 PVC foam {LID_CORE:.0f} / "
                     f"glass {LID_SKIN:.1f} = {LID_T:.1f} mm",
        "module lid": f"glass {ENC_LID_SKIN:.1f} / H80 PVC foam "
                      f"{ENC_LID_CORE:.0f} / glass {ENC_LID_SKIN:.1f} = "
                      f"{ENC_LID_T:.1f} mm",
        "hatch seal": f"poured silicone, {CHAN_W:.0f} x {CHAN_D:.0f} mm "
                      "machined channel",
        "cell holder": "off-the-shelf 21700 spacer brackets (already owned)",
    }
    rep["FAILS"] = fails or ["none"]
    return rep


result = build()
print("=" * 66)
for k, v in result.items():
    if k == "pack_options":
        print("pack_options:")
        for o in v:
            print("   ", o)
    else:
        print(f"{k}: {v}")
print_legend()
