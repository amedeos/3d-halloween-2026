"""Tolerance coupon (~25 min): the real hip joint, rail fit and nail fit, cut from the parts.

Because the pieces are cut from the real models, whatever fits here fits in the coffin.
Tune CLR_* / SNAP in params.py from what you see.
"""

from functools import cache

from build123d import Cylinder, Part, Pos

from . import params as P
from .box import make_box
from .lid import make_lid, nail_hole_xy
from .nail import make_nail
from .nail import print_pose as nail_pose
from .shapes import box_between
from .vampire import make_vampire
from .vampire import print_pose as vampire_pose


def bearing_piece() -> Part:
    """Floor patch with the hip bearing block, printed upright."""
    region = box_between(P.PIVOT_X - 9, P.PIVOT_X + 9, -7, 7, 0, P.BLOCK_TOP + 1)
    return Pos(-P.PIVOT_X, 0, 0) * (make_box() & region)


def pelvis_piece() -> Part:
    """Pelvis, levers and hip stubs of the vampire, printed on its back."""
    return vampire_pose(make_vampire() & box_between(-20, 6, -30, 30, -10, 40))


def rail_piece() -> Part:
    """30 mm of the real dovetail rail, cut from the box, on a plate at the rim plane."""
    x0, x1 = 120.0, 150.0
    rail = make_box() & box_between(x0, x1, -6, 6, P.BOX_H - 2, P.BOX_H + 10)
    plate = box_between(x0, x1, -12, 12, P.BOX_H - 2, P.BOX_H)
    return Pos(-x0, 0, 2 - P.BOX_H) * (plate + rail)


def lid_nail_piece() -> Part:
    """Head end of the lid with both nail holes."""
    region = box_between(2, 13, -19, 19, 0, 60)
    return Pos(-2, 0, -P.BOX_H) * (make_lid() & region)


def lid_slide_piece() -> Part:
    """Middle of the lid: lips, the flared entry and the open part of the slot.

    Slide it onto the rail from the wide (open) end, as the real lid does.
    """
    region = box_between(55, 85, -19, 19, 0, 60)
    return Pos(-55, 0, -P.BOX_H) * (make_lid() & region)


def nail_gauge_piece() -> Part:
    """A 5 mm strip of lid with four nail holes, NAIL_GAUGE mm wider per side than the
    nail's plug. Holes are marked with 1 to 4 dots. Push a nail printed with zero
    clearance (`make_nail(0.0)`) into each hole and keep the clearance that holds best."""
    pitch, margin, half_w = 12.0, 8.0, 8.0
    x0, x1, y0, y1 = nail_hole_xy(clr=0.0)  # nominal hole = plug of a zero-clearance nail
    hw, hd = (x1 - x0) / 2, (y1 - y0) / 2
    length = 2 * margin + pitch * (len(P.NAIL_GAUGE) - 1)
    strip = box_between(0, length, -half_w, half_w, 0, P.LID_T)
    for k, clr in enumerate(P.NAIL_GAUGE):
        cx = margin + k * pitch
        strip -= box_between(cx - hw - clr, cx + hw + clr, -hd - clr, hd + clr, -1, P.LID_T + 1)
        for d in range(k + 1):  # k + 1 dots next to the hole
            dx = (d - k / 2) * 1.8
            strip += Pos(cx + dx, half_w - 2.2, P.LID_T + 0.3) * Cylinder(0.6, 0.6)
    return strip


def nail_gauge_parts() -> dict[str, Part]:
    """The nail gauge and a zero-clearance nail to test it with."""
    return {"coupon_nail_gauge": nail_gauge_piece(),
            "coupon_nail_gauge_nail": nail_pose(make_nail(0.0))}


@cache
def _coupon_parts() -> dict[str, Part]:
    return {
        "coupon_bearing": bearing_piece(),
        "coupon_pelvis": pelvis_piece(),
        "coupon_rail": rail_piece(),
        "coupon_lid_nails": lid_nail_piece(),
        "coupon_lid_slide": lid_slide_piece(),
        "coupon_nail": nail_pose(make_nail()),
    }


def coupon_parts() -> dict[str, Part]:
    """Coupon pieces on the bed (cached; the dict is a fresh copy)."""
    return dict(_coupon_parts())


if __name__ == "__main__":
    for name, part in coupon_parts().items():
        bb = part.bounding_box()
        print(f"{name:16s} valid={part.is_valid} vol={part.volume:7.1f} "
              f"size=({bb.size.X:.1f}, {bb.size.Y:.1f}, {bb.size.Z:.1f}) zmin={bb.min.Z:.2f}")
