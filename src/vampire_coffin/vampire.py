"""The vampire: a flat-backed skeleton relief that sits up around its hip axis.

Pivot frame: origin on the hip axis, x towards the coffin's foot (the head is at -x),
z up, back plane at z = -AXIS_E. Printed lying on its back.
"""

from functools import cache
from math import atan2, cos, degrees, hypot, radians, sin

from build123d import (
    Axis,
    Circle,
    Cylinder,
    Keep,
    Kind,
    Part,
    Plane,
    Polygon,
    Pos,
    Rectangle,
    RectangleRounded,
    Rot,
    Sketch,
    SlotCenterToCenter,
    extrude,
    fillet,
    offset,
)

from . import params as P
from .shapes import box_between, ellipsoid

BACK = -P.AXIS_E
UP = (0, 0, 1)  # always pass it: a sketch drawn clockwise would otherwise extrude downwards


SINK = 0.4  # domes are centred slightly below the back plane


def _ellipsoid(cx, cy, cz, a, b, c) -> Part:
    # poles along x, so they never sit on a visible top (they leave tiny STL holes there)
    if abs(cz - BACK) < 1e-6:  # keep the poles off the back plane (every part has a face there)
        cz, c = BACK - SINK, c + SINK
    return ellipsoid(cx, cy, cz, a, b, c)


def _side_xz(sketch: Sketch, y0: float, y1: float) -> Part:
    """Extrude an XZ-plane sketch between y0 and y1 (y0 < y1)."""
    return Pos(0, y0, 0) * extrude(Plane.XZ * sketch, y1 - y0, dir=(0, 1, 0))


# --- pelvis: wings, levers and hip stubs ---------------------------------------------

def _wing() -> Part:
    """+y pelvis wing incl. hub; the lever arm is added separately.

    The hub (around the axis) is part of the mechanism and keeps its shape; only the iliac
    blade towards the head is rounded off in top view, which removes material and never
    adds any.
    """
    hub = Circle(4.2)
    blade = Polygon((0.0, BACK), (-21.0, BACK), (-21.0, 1.5), (-12.0, 5.5), (-3.0, 4.6),
                    (0.0, 3.6), align=None)
    side = _side_xz(Sketch() + hub + blade, P.WING_Y0, P.ARM_Y1)
    w = P.ARM_Y1 - P.WING_Y0
    top = (Pos(-11.0, P.WING_Y0 + w / 2) * RectangleRounded(21.0, w, 3.0)
           + Pos(0.0, P.WING_Y0 + w / 2) * Rectangle(10.0, w + 0.02))
    return side & (Pos(0, 0, -10) * extrude(top, 40, dir=UP))


def _lever() -> Part:
    a = radians(P.ARM_REST)
    tip = (P.ARM_LEN - P.ARM_W / 2) * sin(a), (P.ARM_LEN - P.ARM_W / 2) * cos(a)
    arm = SlotCenterToCenter(hypot(*tip), P.ARM_W, rotation=degrees(atan2(tip[1], tip[0])))
    arm = Pos(tip[0] / 2, tip[1] / 2) * arm
    return _side_xz(Sketch() + arm, P.ARM_Y0, P.ARM_Y1)


def _stub() -> Part:
    """Hip stub with two flats. At 45 degrees the flats line up with the bearing mouth
    (bayonet); lying down, the full diameter keeps it in."""
    length = P.WING_Y0 - 0.6 + 1.0
    stub = Pos(0, 0.6 + length / 2, 0) * Rot(90, 0, 0) * Cylinder(P.STUB_D / 2, length)
    return stub & box_between(-5, 5, 0, 10, -P.AXIS_E, P.AXIS_E)


def _pelvis() -> Part:
    half = _wing() + _lever() + _stub()
    hw = P.WING_Y0 + 0.5
    outline = Polygon((-8.0, -hw), (-8.0, hw), (-22.0, hw - 1.6), (-22.0, -hw + 1.6), align=None)
    sacrum = Pos(0, 0, BACK) * extrude(Sketch() + outline, 3.0 - BACK, dir=UP)
    sacrum = fillet(sacrum.edges().group_by(Axis.Z)[-1], 1.0)
    return half + half.mirror(Plane.XZ) + sacrum


# --- spine, ribs, arms -----------------------------------------------------------------

def _spine() -> Part:
    """Neck and lumbar vertebrae on a thin core; the ribcage covers the middle."""
    out = box_between(-53.0, -14.0, -1.4, 1.4, BACK, 1.2)
    for x0, x1, hw, h in [(-16.6, -14.4, 3.2, 3.4), (-20.4, -18.2, 3.4, 3.6),
                          (-24.2, -22.0, 3.6, 3.8), (-52.6, -51.0, 2.4, 4.0),
                          (-50.4, -48.8, 2.6, 4.0)]:
        v = box_between(x0, x1, -hw, hw, BACK, BACK + h)
        out += fillet(v.edges().group_by(Axis.Z)[-1], 0.7)
    return out


RIB_X0, RIB_X1 = -49.5, -24.5
RIB_C, RIB_B = 9.6, P.FIG_HW
RIB_SLANT = 16.0  # ribs run from the breastbone towards the hips


def _ribcage() -> Part:
    cx, a = (RIB_X0 + RIB_X1) / 2, (RIB_X1 - RIB_X0) / 2
    outer = _ellipsoid(cx, 0, BACK, a, RIB_B, RIB_C)
    core = _ellipsoid(cx, 0, BACK, a - 1.0, RIB_B - 2.2, RIB_C - 2.0)
    cutter = box_between(RIB_X0 + 3.5, RIB_X1 - 6.0, -1.6, 1.6, BACK, BACK + RIB_C + 1)
    h = RIB_C + 2
    for i in range(5):
        x = RIB_X0 + 3.4 + i * 4.3
        for s in (1, -1):  # each rib is two slanted bands that meet at the breastbone
            band = box_between(-1.2, 1.2, 0, RIB_B + 2, BACK, BACK + h)
            cutter += Pos(x, 0, 0) * Rot(0, 0, s * -RIB_SLANT) * (
                band if s > 0 else band.mirror(Plane.XZ))
    return core + (outer & cutter)


def _bone(p0: tuple[float, float], p1: tuple[float, float], width: float) -> Sketch:
    """A straight bone between two points, with round ends, in the XY plane."""
    length = hypot(p1[0] - p0[0], p1[1] - p0[1])
    ang = degrees(atan2(p1[1] - p0[1], p1[0] - p0[0]))
    return Pos((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2) * SlotCenterToCenter(
        length, width, rotation=ang)


def _arms() -> Part:
    """Forearms crossed over the chest (two bones each), bony hands on the shoulders.

    Each arm is a flat outline extruded from the back plane and trimmed by an ellipsoid a
    little above the ribcage, so it hugs the chest and needs no support. All bones are at
    least two lines wide and the gaps between them at least one line.
    """
    cx, a = (RIB_X1 + RIB_X0) / 2, (RIB_X1 - RIB_X0) / 2
    bone_w, gap = P.lines(2) + 0.3, P.LINE_W + 0.25
    out = None
    for s, lift in ((1, 2.0), (-1, 3.0)):  # the -y arm lies on top
        elbow, wrist = (-26.5, s * 10.6), (-43.0, -s * 6.0)
        d = (wrist[0] - elbow[0], wrist[1] - elbow[1])
        n = hypot(*d)
        off = ((-d[1] / n) * (bone_w + gap) / 2, (d[0] / n) * (bone_w + gap) / 2)
        sk = Sketch()
        for k in (1, -1):  # radius and ulna
            sk += _bone((elbow[0] + k * off[0], elbow[1] + k * off[1]),
                        (wrist[0] + k * off[0], wrist[1] + k * off[1]), bone_w)
        sk += Pos(*elbow) * Circle(2.0)
        # hand: palm and three bony fingers reaching over the shoulder (away from the
        # middle of the chest, towards the head a little)
        palm = (wrist[0] - 2.0, wrist[1] - s * 0.8)
        sk += Pos(*palm) * Circle(1.9)
        ang = atan2(-s * 1.0, -0.25)
        d, n = (cos(ang), sin(ang)), (-sin(ang), cos(ang))
        finger_w = bone_w - 0.1
        pitch = finger_w + P.LINE_W + 0.15  # a gap of more than one line between fingers
        for k in (-1, 0, 1):
            base = (palm[0] + n[0] * k * pitch, palm[1] + n[1] * k * pitch)
            fan = 0.25 * k  # the tips spread a little
            tip = (base[0] + 5.5 * d[0] + n[0] * fan, base[1] + 5.5 * d[1] + n[1] * fan)
            sk += _bone(base, tip, finger_w)
        prism = Pos(0, 0, BACK) * extrude(sk, RIB_C + 4, dir=UP)
        skin = _ellipsoid(cx, 0, BACK, a + 2.5, RIB_B + 1.5, RIB_C + lift)
        part = prism & skin
        out = part if out is None else out + part
    return out


def _cape() -> Part:
    """The cape behind the shoulders and the back, with a bat-wing hem at the waist."""
    w = P.CAPE_HW
    hem = [(-21.0, 0.0), (-24.0, 0.3 * w), (-21.5, 0.57 * w), (-24.5, 0.8 * w), (-22.0, w)]
    pts = [*hem, (-36.0, w), (-48.0, w - 1.4), (-48.0, 0.0)]
    half = Sketch() + Polygon(*pts, align=None)
    return Pos(0, 0, BACK) * extrude(half + half.mirror(Plane.XZ), P.CAPE_T, dir=UP)


# --- head ----------------------------------------------------------------------------
# The face is carved rather than built up: carved details never overhang when the figure
# is printed on its back. Flat floors of cuts sit on the layer grid (print z = z + AXIS_E).

SKULL_TOP = -P.SKULL_TOP  # x of the top of the cranium


def _fang_outline(y: float) -> Sketch:
    """A fang hanging from the upper teeth; the tip stays two lines wide (printable)."""
    base, tip = SKULL_TOP + 18.4, SKULL_TOP + 20.9
    half_base, half_tip = 1.0, P.lines(2) / 2
    return Sketch() + Polygon((base, y - half_base), (base, y + half_base),
                              (tip, y + half_tip), (tip, y - half_tip), align=None) + Pos(
        tip, y) * Circle(half_tip)


def _skull() -> Part:
    t = SKULL_TOP
    cranium = _ellipsoid(t + 9.5, 0, BACK, 9.5, 9.0, 10.8)
    cheekbones = _ellipsoid(t + 15.0, 0, BACK, 4.4, 7.0, 8.6)  # cheekbones and upper jaw
    maxilla = _ellipsoid(t + 18.4, 0, BACK, 3.4, 5.4, 7.8)
    mandible = _ellipsoid(t + 21.2, 0, BACK, 2.6, 4.4, 6.4)
    skull = cranium + cheekbones + maxilla + mandible

    # eye sockets, slanted so the inner corners sit lower: a mean look
    for s in (1, -1):
        # poles along x, centre above the bone: the poles stay outside the skull, so they
        # never end up on the visible socket wall (they leave holes in the STL there)
        socket = Rot(0, 0, s * 26) * ellipsoid(0, 0, 0, 2.4, 3.5, 3.6)
        skull -= Pos(t + 11.4, s * 3.9, BACK + 10.6) * socket

    # nasal cavity: an upside-down heart, cut piece by piece (overlapping cutting tools
    # leave doubled edges on the floor of the cut)
    floor = BACK + 5.6  # clearly below the bone
    for piece in (Pos(t + 15.4, 0.75) * Circle(0.9), Pos(t + 15.4, -0.75) * Circle(0.9),
                  Polygon((t + 15.2, -1.6), (t + 15.2, 1.6), (t + 17.1, 0.0), align=None)):
        skull -= Pos(0, 0, floor) * extrude(Sketch() + piece, 8.0, dir=UP)

    # dark mouth between the teeth rows, with the upper teeth carved in
    mouth = Pos(t + 20.4, 0) * SlotCenterToCenter(5.0, 3.0, rotation=90)
    skull -= Pos(0, 0, BACK + 3.8) * extrude(mouth, 8.0, dir=UP)
    gap = P.LINE_W + 0.05  # narrower grooves close up when printed
    for y in (-1.3, 0.0, 1.3):
        skull -= box_between(t + 17.4, t + 19.2, y - gap / 2, y + gap / 2, BACK + 5.8, BACK + 12)

    # fangs over the mouth and the chin, a little proud of the jaw
    fang_skin = _ellipsoid(t + 18.6, 0, BACK, 3.8, 5.8, 8.6)  # fangs stand a bit proud
    for s in (1, -1):
        skull += (Pos(0, 0, BACK) * extrude(_fang_outline(s * 2.4), 9.0, dir=UP)) & fang_skin
    return skull


def _collar() -> Part:
    """Dracula's high collar: narrow at the neck, flaring out to sharp points beside the
    top of the skull."""
    t = SKULL_TOP + 0.5

    def flare(u: float) -> tuple[float, float]:  # concave curve from the neck to the tip
        x = -48.0 + (-73.5 + 48.0) * u
        return x, 9.6 + (P.COLLAR_HW - 9.6) * u**1.8

    side = [flare(k / 8) for k in range(9)]
    pts = [(-48.0, 0.0), *side, (-71.6, 12.6), (t, 10.2), (t, 0.0)]
    half = Sketch() + Polygon(*pts, align=None)
    plate = half + half.mirror(Plane.XZ)
    collar = Pos(0, 0, BACK) * extrude(plate, P.CAPE_T, dir=UP)
    # an engraved line along the free edges gives the black collar some depth; not along
    # the neck edge (x = -48), where the collar joins the cape
    inner = offset(plate, -P.lines(2), kind=Kind.ARC)
    groove = inner - offset(plate, -P.lines(2) - 0.6, kind=Kind.ARC)
    groove = groove & (Pos(-50.5 - 15, 0) * Rectangle(30, 2 * P.COLLAR_HW + 2))
    return collar - Pos(0, 0, BACK + P.CAPE_T - 0.6) * extrude(groove, 1.0, dir=UP)


@cache
def make_vampire() -> Part:
    body = _pelvis() + _spine() + _cape() + _ribcage() + _arms() + _collar() + _skull()
    body = body & box_between(-90, 20, -30, 30, BACK, 40)  # flat back for printing
    body.label = "vampire"
    return body


@cache
def colour_parts() -> tuple[Part, Part]:
    """(black, white): everything up to CAPE_T above the back is printed black."""
    cut = Plane.XY.offset(BACK + P.CAPE_T)
    v = make_vampire()
    return _one_part(v.split(cut, keep=Keep.BOTTOM)), _one_part(v.split(cut, keep=Keep.TOP))


def _one_part(result) -> Part:
    """split() returns a Part, a list of Parts or None; always give back one Part."""
    if result is None:
        raise ValueError("colour split left nothing on one side")
    if isinstance(result, list):
        fused = result[0]
        for piece in result[1:]:
            fused += piece
        return fused
    return result


def coloured(theta_deg: float) -> list[tuple[Part, str]]:
    """The vampire in assembly coordinates, split into its print colours."""
    black, white = colour_parts()
    return [(placed(black, theta_deg), "black"), (placed(white, theta_deg), "white")]


def placed(vampire: Part, theta_deg: float) -> Part:
    """Vampire in assembly coordinates, sat up by theta degrees."""
    return Pos(P.PIVOT_X, 0, P.PIVOT_Z) * Rot(0, theta_deg, 0) * vampire


def print_pose(vampire: Part) -> Part:
    return Pos(0, 0, P.AXIS_E) * vampire


if __name__ == "__main__":
    v = make_vampire()
    print(v.is_valid, v.volume, v.bounding_box())
