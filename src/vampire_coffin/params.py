"""Single source of truth for every dimension and clearance (millimetres, degrees).

Every horizontal face must sit on a layer boundary (multiples of LAYER when the part lies
in its print position), and thin walls are a whole number of extrusion lines: see
`lines()` and the tests in tests/test_layers.py.

Assembly frame: x runs from the head end (x=0) to the foot end (x=BOX_L), y is lateral
(symmetric), z is up with the box resting on z=0. The lid slides towards +x by `s`.
"""

from math import ceil, pi

# --- printer / process: Prusa MK4, 0.4 mm nozzle, PrusaSlicer "0.20mm STRUCTURAL" -----
NOZZLE = 0.4
LAYER = 0.2  # layer height
FIRST_LAYER = 0.2  # first layer height
LINE_W = 0.45  # extrusion width (perimeters and infill)
# centre distance of two touching lines, as PrusaSlicer computes it
LINE_SPACING = LINE_W - LAYER * (1 - pi / 4)


def lines(n: int) -> float:
    """Width of a wall made of n touching extrusion lines."""
    return (n - 1) * LINE_SPACING + LINE_W


def layer_top(z: float) -> float:
    """Top (print_z) of the first layer that starts at or above height z."""
    if z <= 1e-9:
        return FIRST_LAYER
    k = ceil((z - FIRST_LAYER) / LAYER - 1e-9) + 1
    return round(FIRST_LAYER + k * LAYER, 6)


def snap_up(z: float) -> float:
    """Smallest layer boundary at or above z (boundaries: 0, FIRST_LAYER, + n * LAYER)."""
    if z <= FIRST_LAYER:
        return 0.0 if z <= 1e-9 else FIRST_LAYER
    return round(FIRST_LAYER + ceil((z - FIRST_LAYER) / LAYER - 1e-9) * LAYER, 6)


# --- clearances (tune these after printing the coupon) ------------------------------
CLR_SLIDE = 0.30  # dovetail rail <-> lid slot, per side
CLR_STUB = 0.20  # hip stub <-> U bearing, radial
SNAP = 0.15  # bearing mouth is this much narrower than the stub; keep > 0 (retention)
CLR_NAIL = 0.0  # nail plug <-> lid hole, per side (holes print a bit small: press fit)
CLR_NAIL_HOLE = 0.2  # lid hole around the nail pin, so the pin passes through it

# --- coffin outline (outer, top view) ------------------------------------------------
BOX_L = 160.0
HEAD_W = 46.0  # width at x=0
SHOULDER_W = 66.0  # widest point
SHOULDER_X = 45.0
FOOT_W = 38.0  # width at x=BOX_L

WALL = lines(4)  # 2 perimeters on each side, no infill or gap fill
FLOOR = 2.0
BOX_H = 40.0  # rim height = underside of the lid

# --- lid ------------------------------------------------------------------------------
LID_T = 5.0
LID_BEVEL = 1.6
RELIEF_H = 1.2  # raised cross / text, printed after the M600 colour change
RELIEF_INSET = 4.0  # decorative border inset from the lid edge
BORDER_W = lines(3)  # raised border stroke
LID_ENTRY_LEN = 4.0  # lead-in ramp at the open end of the lid's lips
CLR_SLOT_TOP = 2 * LAYER  # lid slot ceiling above the rail top

# --- dovetail rail (box) and slot (lid) -------------------------------------------------
RAIL_X0 = 95.0  # head end of the rail; also the "fully open" stop
RAIL_STEM_W = 4.4
RAIL_HEAD_W = 7.6  # top width of the dovetail head
RAIL_HEAD_Z0 = BOX_H + 1.4  # where the dovetail starts to flare
RAIL_HEAD_Z1 = BOX_H + 3.0  # top of the rail
LID_LIPS_U1 = 75.0  # lips (that capture the rail) run from the slot start up to here

# --- hips: pivot axis and bearing block -----------------------------------------------
PILLOW_H = 2.6  # pillow under the skull, on top of the floor
BACK_Z = FLOOR + PILLOW_H  # back plane of the lying vampire
STUB_D = 5.0
STUB_FLAT = 0.3  # flats on both sides of the stubs (bed side and top): bayonet fit
AXIS_E = STUB_D / 2 - STUB_FLAT  # axis height above the vampire's back plane
PIVOT_X = 80.0
PIVOT_Z = BACK_Z + AXIS_E
BLOCK_HW = 4.0  # half width of the bearing block
BLOCK_HL = 4.5  # half length (x) of the bearing block
BLOCK_TOP = snap_up(PIVOT_Z + 3.2)
BEARING_TILT = 45.0  # bearing slot opens towards the head and up (deg from vertical)
STUB_GAP = 0.4  # lateral gap between the vampire and the bearing block

# --- lever arms (pelvis wings) and the nails that push them ---------------------------
ARM_REST = -35.0  # arm angle from vertical when lying (negative = towards the head)
ARM_LEN = 31.0  # from the axis to the tip of the rounded arm end
ARM_W = 5.0  # in-plane thickness of the arm
ARM_Y1 = 13.2  # arm occupies |y| in [ARM_Y0, ARM_Y1]
ARM_Y0 = ARM_Y1 - lines(8)
WING_Y0 = BLOCK_HW + STUB_GAP  # pelvis wings start next to the bearing block
PIN_H = 19.5  # nail pin height above the axis
PIN_D = 4.0
PIN_Y0 = 10.4  # pin spans |y| in [PIN_Y0, NAIL_Y0]
NAIL_SHANK = 3.2  # square shank
NAIL_Y0 = 14.0  # inner face of the shank
NAIL_HEAD = (7.0, 9.0, lines(4))  # x, y, z of the nail head; z is a wall when printed
THETA_MAX = 70.0  # how far the vampire sits up
S_MAX = 82.0  # lid travel from closed to fully open (hard stop)

# --- figure ---------------------------------------------------------------------------
SKULL_TOP = 76.0  # distance from the hip axis to the top of the skull
CAPE_T = 1.6  # cape and collar plates (8 layers): printed black, then M600 to white
FIG_HW = 12.8  # half width of the ribcage
COLLAR_HW = 17.4  # half width at the collar tips: the widest part of the figure
CAPE_HW = 15.0  # half width of the cape at the hem

# --- coffin handles (6 bar handles on the side walls) --------------------------------
HANDLE_Z = snap_up(BOX_H * 0.55)  # handle centre height
HANDLE_BAR = (lines(4), 1.8)  # bar: depth (outwards) and height (9 layers)
HANDLE_MOUNT = (lines(6), lines(6), 0.6)  # brackets: width, depth, extra height above/below
HANDLE_LEN = 18.0  # outside length of the handle along the wall

# --- candy stash at the feet ----------------------------------------------------------
STASH_WALL_X = 101.0
STASH_WALL_H = 28.0
