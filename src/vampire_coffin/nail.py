"""Square coffin nails: pressed through the lid, their pins push the vampire's pelvis levers.

Modelled for the +y side in lid coordinates (lid closed); mirror for the -y side.
Printed lying on the outer face, so the pin points straight up.
"""

from functools import cache

from build123d import Axis, Cylinder, Part, Pos, Rot, chamfer

from . import params as P
from .kinematics import PIN_U, PIN_Z
from .lid import LID_TOP, nail_hole_xy
from .shapes import box_between

Y_OUT = P.NAIL_Y0 + P.NAIL_SHANK  # outer face, flat on the bed when printing


@cache
def make_nail(clr: float = P.CLR_NAIL) -> Part:
    """The nail for a lid hole with `clr` mm of clearance on each side of the plug."""
    hx, hy, hz = P.NAIL_HEAD
    head = box_between(PIN_U - hx / 2, PIN_U + hx / 2, Y_OUT - hy, Y_OUT, LID_TOP, LID_TOP + hz)
    head = chamfer(head.edges().group_by(Axis.Z)[-1], 0.5)

    x0, x1, y0, _ = nail_hole_xy()
    # Printed lying down, the inner face of the plug is a flat top face: keep it on a layer
    # boundary. So across y the clearance is 0 or one layer, across x it is exactly clr.
    y_in = Y_OUT - P.snap_down(Y_OUT - (y0 + clr))
    plug = box_between(x0 + clr, x1 - clr, y_in, Y_OUT, P.BOX_H, LID_TOP + 0.01)
    # lead-in: a small chamfer around the bottom of the plug centres it in the hole
    plug = chamfer(plug.edges().group_by(Axis.Z)[0], 0.4)

    sx = P.PIN_D / 2 + P.CLR_NAIL_HOLE / 2  # a bit wider than the pin, narrower than the hole
    z_low = PIN_Z - P.PIN_D / 2 - 0.6
    shank = box_between(PIN_U - sx, PIN_U + sx, P.NAIL_Y0, Y_OUT, z_low, P.BOX_H + 0.01)
    shank = chamfer(shank.edges().group_by(Axis.Z)[0].filter_by(Axis.Y), 0.6)

    pin_len = P.NAIL_Y0 - P.PIN_Y0 + 0.5
    pin = Pos(PIN_U, P.PIN_Y0 + pin_len / 2, PIN_Z) * Rot(90, 0, 0) * Cylinder(P.PIN_D / 2, pin_len)
    pin = chamfer(pin.edges().group_by(Axis.Y)[0], 0.4)

    nail = head + plug + shank + pin
    nail.label = "nail"
    return nail


def print_pose(nail: Part) -> Part:
    """Outer face down on the bed, pin pointing up."""
    return Pos(0, 0, Y_OUT) * Rot(-90, 0, 0) * nail


if __name__ == "__main__":
    n = make_nail()
    print(n.is_valid, n.volume, n.bounding_box())
    print(print_pose(n).bounding_box())
