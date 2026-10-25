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
    Part,
    Plane,
    Polygon,
    Pos,
    Rot,
    Sketch,
    SlotCenterToCenter,
    Sphere,
    extrude,
    fillet,
    scale,
)

from . import params as P
from .shapes import box_between

BACK = -P.AXIS_E


SINK = 0.4  # domes are centred slightly below the back plane


def _ellipsoid(cx, cy, cz, a, b, c) -> Part:
    # poles along x, so they never sit on a visible top (they leave tiny STL holes there)
    if abs(cz - BACK) < 1e-6:  # keep the poles off the back plane (every part has a face there)
        cz, c = BACK - SINK, c + SINK
    return Pos(cx, cy, cz) * scale(Rot(0, 90, 0) * Sphere(1.0), (a, b, c))


def _side_xz(sketch: Sketch, y0: float, y1: float) -> Part:
    """Extrude an XZ-plane sketch between y0 and y1 (y0 < y1)."""
    return Pos(0, y0, 0) * extrude(Plane.XZ * sketch, y1 - y0, dir=(0, 1, 0))


# --- pelvis: wings, levers and hip stubs ---------------------------------------------

def _wing() -> Part:
    """+y pelvis wing incl. hub; the lever arm is added separately."""
    hub = Circle(4.2)
    blade = Polygon((0.0, BACK), (-21.0, BACK), (-21.0, 1.5), (-12.0, 5.5), (-3.0, 4.6),
                    (0.0, 3.6), align=None)
    return _side_xz(Sketch() + hub + blade, P.WING_Y0, P.ARM_Y1)


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
    sacrum = box_between(-22.0, -8.0, -P.WING_Y0 - 0.5, P.WING_Y0 + 0.5, BACK, 3.0)
    sacrum = fillet(sacrum.edges().group_by(Axis.Z)[-1], 1.2)
    return half + half.mirror(Plane.XZ) + sacrum


# --- spine, ribs, arms -----------------------------------------------------------------

def _spine() -> Part:
    core = box_between(-56.0, -14.0, -1.6, 1.6, BACK, 1.6)
    out = core
    for i in range(4):
        x = -16.5 - i * 3.6
        v = box_between(x - 1.4, x + 1.4, -3.4, 3.4, BACK, 3.4)
        out += fillet(v.edges().group_by(Axis.Z)[-1], 0.9)
    return out


RIB_X0, RIB_X1 = -53.0, -26.0
RIB_C, RIB_B = 10.0, P.FIG_HW


def _ribcage() -> Part:
    cx, a = (RIB_X0 + RIB_X1) / 2, (RIB_X1 - RIB_X0) / 2
    outer = _ellipsoid(cx, 0, BACK, a, RIB_B, RIB_C)
    core = _ellipsoid(cx, 0, BACK, a - 1.0, RIB_B - 2.2, RIB_C - 2.0)
    cutter = box_between(RIB_X0 + 2.0, RIB_X1 - 6.0, -1.7, 1.7, BACK, BACK + RIB_C + 1)  # sternum
    for i in range(6):
        x = RIB_X0 + 3.0 + i * 4.1
        cutter += box_between(x, x + 2.4, -RIB_B - 1, RIB_B + 1, BACK, BACK + RIB_C + 1)
    return core + (outer & cutter)


def _arms() -> Part:
    """Forearms crossed over the chest, bony hands on the opposite shoulders.

    Each arm is a flat outline extruded from the back plane and trimmed by an ellipsoid a
    little above the ribcage, so it hugs the chest and needs no support.
    """
    cx, a = (RIB_X0 + RIB_X1) / 2, (RIB_X1 - RIB_X0) / 2
    out = None
    for sgn, lift in ((1, 2.2), (-1, 3.0)):  # the -y arm lies on top
        elbow, hand = (-28.5, sgn * 10.8), (-47.0, -sgn * 7.0)
        ang = degrees(atan2(hand[1] - elbow[1], hand[0] - elbow[0]))
        length = hypot(hand[0] - elbow[0], hand[1] - elbow[1])
        sk = Pos((elbow[0] + hand[0]) / 2, (elbow[1] + hand[1]) / 2) * SlotCenterToCenter(
            length, 3.6, rotation=ang)
        sk += Pos(*elbow) * Circle(2.3)
        sk += Pos(hand[0] - 1.2, hand[1]) * Circle(2.6)
        for k in (-1, 0, 1):
            f0 = (hand[0] - 2.5, hand[1] + k * 1.7)
            f1 = (hand[0] - 7.0, hand[1] + k * 2.3)
            sk += Pos((f0[0] + f1[0]) / 2, (f0[1] + f1[1]) / 2) * SlotCenterToCenter(
                hypot(f1[0] - f0[0], f1[1] - f0[1]), 1.5,
                rotation=degrees(atan2(f1[1] - f0[1], f1[0] - f0[0])))
        prism = Pos(0, 0, BACK) * extrude(sk, RIB_C + 4)
        skin = _ellipsoid(cx, 0, BACK, a + 2.0, RIB_B + 1.0, RIB_C + lift)
        part = prism & skin
        out = part if out is None else out + part
    return out


# --- head ----------------------------------------------------------------------------

SKULL_CX = -P.SKULL_TOP + 10.0


def _collar() -> Part:
    tip = -P.SKULL_TOP + 0.5
    pts = [(-46.0, 12.6), (-57.0, 15.8), (-65.0, 16.6), (-71.5, 15.4), (tip, 11.6),
           (-71.0, 9.4), (-67.0, 10.6), (-62.0, 10.0)]
    half = Polygon(*pts, align=None)
    plate = Sketch() + half + half.mirror(Plane.XZ) + Pos(-60.0, 0) * Polygon(
        (14.0, 10.6), (-6.0, 11.2), (-6.0, -11.2), (14.0, -10.6), align=None)
    return Pos(0, 0, BACK) * extrude(plate, 2.4)


def _skull() -> Part:
    cx = SKULL_CX
    cranium = _ellipsoid(cx, 0, BACK, 10.2, 9.0, 11.5)
    cheeks = _ellipsoid(cx + 6.0, 0, BACK, 5.5, 7.4, 8.6)
    jaw = _ellipsoid(cx + 9.5, 0, BACK, 3.6, 5.2, 6.4)
    skull = cranium + cheeks + jaw
    top = BACK + 11.5
    for sgn in (1, -1):
        skull -= _ellipsoid(cx + 1.0, sgn * 3.9, top - 1.4, 3.1, 2.7, 2.6)
    nose = Polygon((cx + 4.6, 0.0), (cx + 7.8, -1.5), (cx + 7.8, 1.5), align=None)
    skull -= Pos(0, 0, BACK + 7.0) * extrude(Sketch() + nose, 6.0)
    # mouth line and teeth
    skull -= box_between(cx + 10.2, cx + 10.8, -4.2, 4.2, BACK + 4.6, BACK + 12)
    gap = P.LINE_W + 0.05  # narrower grooves close up when printed
    for k in range(-2, 3):
        y = k * 1.6
        skull -= box_between(cx + 9.0, cx + 12.4, y - gap / 2, y + gap / 2, BACK + 5.6, BACK + 12)
    for sgn in (1, -1):
        fang = Polygon((cx + 10.0, sgn * 2.0 - 0.9), (cx + 10.0, sgn * 2.0 + 0.9),
                       (cx + 13.2, sgn * 2.0), align=None)
        skull += Pos(0, 0, BACK) * extrude(Sketch() + fang, 6.2)
    return skull


@cache
def make_vampire() -> Part:
    body = _pelvis() + _spine() + _ribcage() + _arms() + _collar() + _skull()
    neck = box_between(-58.0, -50.0, -2.6, 2.6, BACK, 3.2)
    body += fillet(neck.edges().group_by(Axis.Z)[-1], 1.0)
    body = body & box_between(-90, 20, -30, 30, BACK, 40)  # flat back for printing
    body.label = "vampire"
    return body


def placed(vampire: Part, theta_deg: float) -> Part:
    """Vampire in assembly coordinates, sat up by theta degrees."""
    return Pos(P.PIVOT_X, 0, P.PIVOT_Z) * Rot(0, theta_deg, 0) * vampire


def print_pose(vampire: Part) -> Part:
    return Pos(0, 0, P.AXIS_E) * vampire


if __name__ == "__main__":
    v = make_vampire()
    print(v.is_valid, v.volume, v.bounding_box())
