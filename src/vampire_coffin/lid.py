"""Sliding lid: dovetail slot underneath, nail holes, raised cross and lettering on top.

Printed top-up. Insert an M600 colour change at the first relief layer (see export.py).
"""

from functools import cache
from pathlib import Path

from build123d import (
    Axis,
    Circle,
    Part,
    Plane,
    Polygon,
    Pos,
    Rectangle,
    Sketch,
    Text,
    chamfer,
    extrude,
)

from . import params as P
from .box import rail_points, rail_profile
from .kinematics import LID_SLOT_U0, PIN_U
from .outline import outline_face
from .shapes import box_between

FONT = Path(__file__).resolve().parent / "fonts" / "PirataOne-Regular.ttf"
if not FONT.is_file():  # build123d would silently fall back to a system font
    raise FileNotFoundError(f"bundled font missing: {FONT}")
LID_TOP = P.BOX_H + P.LID_T
SLOT_U1 = P.BOX_L - P.WALL  # foot end of the slot = closed position stop
SLOT_TOP = P.RAIL_HEAD_Z1 + P.CLR_SLOT_TOP  # slot ceiling, on a layer boundary


def nail_hole_xy() -> tuple[float, float, float, float]:
    """(x0, x1, y0, y1) of the +y nail hole; the pin must pass through it."""
    hx = P.PIN_D / 2 + P.CLR_NAIL_HOLE
    return (PIN_U - hx, PIN_U + hx, P.PIN_Y0 - P.CLR_NAIL_HOLE,
            P.NAIL_Y0 + P.NAIL_SHANK + P.CLR_NAIL)


def _body() -> Part:
    body = Pos(0, 0, P.BOX_H) * extrude(outline_face(), P.LID_T)
    body = chamfer(body.edges().group_by(Axis.Z)[-1], P.LID_BEVEL)
    return chamfer(body.edges().group_by(Axis.Z)[0], 0.4)


def _slot() -> Part:
    lips = extrude(rail_profile(P.CLR_SLIDE, z_floor=P.BOX_H - 1, top=SLOT_TOP),
                   SLOT_U1 - LID_SLOT_U0)
    lips = Pos(LID_SLOT_U0, 0, 0) * lips
    hw = P.RAIL_HEAD_W / 2 + P.CLR_SLIDE
    free = box_between(P.LID_LIPS_U1, SLOT_U1, -hw, hw, P.BOX_H - 1, SLOT_TOP)
    # Lead-in ramp: cut the lips from the top, so that at their open end they are flush with
    # the underside of the lid and they reach full height LID_ENTRY_LEN further in. The rail
    # head then slides over the ramp and under the lips even if the lid is lifted a little.
    u0, u1 = P.LID_LIPS_U1 - P.LID_ENTRY_LEN, P.LID_LIPS_U1 + 0.01
    lip_top = rail_points(P.CLR_SLIDE)[3][1]  # top of the grown 45-degree flare
    ramp = Polygon((u0, lip_top), (u1, P.BOX_H), (u1, SLOT_TOP), (u0, SLOT_TOP), align=None)
    entry = extrude(Plane.XZ * ramp, hw, both=True)
    return lips + free + entry


def _nail_holes() -> Part:
    x0, x1, y0, y1 = nail_hole_xy()
    hole = box_between(x0, x1, y0, y1, P.BOX_H - P.LID_T, LID_TOP + P.LID_T)
    return hole + hole.mirror(Plane.XZ)


def nail_head_footprint(margin: float = 0.0) -> Sketch:
    hx, hy0, hy1 = P.NAIL_HEAD[0] / 2, P.NAIL_Y0 + P.NAIL_SHANK - P.NAIL_HEAD[1], (
        P.NAIL_Y0 + P.NAIL_SHANK)
    r = Pos(PIN_U, (hy0 + hy1) / 2) * Rectangle(2 * hx + 2 * margin, hy1 - hy0 + 2 * margin)
    return r + r.mirror(Plane.XZ)


def _cross() -> Sketch:
    top, bottom, bar_u, span, w, knob = 22.0, 88.0, 40.0, 14.0, 5.0, 3.4
    s = Pos((top + bottom) / 2, 0) * Rectangle(bottom - top, w)
    s += Pos(bar_u, 0) * Rectangle(w, 2 * span)
    for x, y in [(top, 0), (bottom, 0), (bar_u, span), (bar_u, -span)]:
        s += Pos(x, y) * Circle(knob)
    s -= Pos(bar_u, 0) * Circle(1.4)
    return s


def _lettering() -> Sketch:
    """Reads upright for someone at the foot end, i.e. whoever pulls the lid open."""
    return Pos(128.0, 0) * Text("R.I.P.", 15, font_path=str(FONT), rotation=90)


def _border() -> Sketch:
    outer = outline_face(-P.RELIEF_INSET)
    inner = outline_face(-P.RELIEF_INSET - P.BORDER_W)
    return Sketch() + outer - inner


def relief_sketch() -> Sketch:
    return (_cross() + _lettering() + _border()) - nail_head_footprint(0.8)


@cache
def lid_base() -> Part:
    """The lid without its relief: the part printed before the colour change."""
    return _body() - _slot() - _nail_holes()


@cache
def lid_relief() -> Part:
    """Cross, border and lettering: printed after the colour change."""
    return Pos(0, 0, LID_TOP) * extrude(relief_sketch(), P.RELIEF_H)


@cache
def make_lid() -> Part:
    lid = lid_base() + lid_relief()
    lid.label = "lid"
    return lid


if __name__ == "__main__":
    lid = make_lid()
    print(lid.is_valid, lid.volume, lid.bounding_box())
