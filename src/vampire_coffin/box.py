"""Coffin body: walls, pillow, hip bearing, dovetail rail and the candy stash.

Printed upright as modelled, no supports.
"""

from functools import cache
from math import cos, radians, sqrt

from build123d import (
    Axis,
    Circle,
    Location,
    Part,
    Plane,
    Polygon,
    Polyline,
    Pos,
    Rectangle,
    Rot,
    Sketch,
    Vector,
    chamfer,
    extrude,
    fillet,
    loft,
    make_face,
)

from . import params as P
from .outline import max_miter, outline_face, side_segments
from .shapes import box_between


def rail_points(grow: float = 0.0, z_floor: float = P.FLOOR,
                top: float | None = None) -> list[tuple[float, float]]:
    """(y, z) outline of the rail (stem + 45-degree dovetail head), grown by `grow`.

    Every edge moves outwards by exactly `grow`, measured at right angles, so `grow` is the
    real clearance on the stem, on the flare and on the top. `top` replaces the top height
    (the lid slot puts its ceiling on a layer boundary).
    """
    sw = P.RAIL_STEM_W / 2 + grow
    hw = P.RAIL_HEAD_W / 2 + grow
    flare = P.RAIL_HEAD_W / 2 - P.RAIL_STEM_W / 2  # 45 degrees: rise = run
    z0 = P.RAIL_HEAD_Z0 - grow * (sqrt(2) - 1)  # where the grown stem meets the grown flare
    z_flare_top = z0 + flare
    z1 = P.RAIL_HEAD_Z1 + grow if top is None else top
    right = [(sw, z0), (hw, z_flare_top)]
    if z1 - z_flare_top > 1e-6:  # a vertical step above the flare
        right.append((hw, z1))
    left = [(-y, z) for y, z in reversed(right)]
    return [(-sw, z_floor - grow), (sw, z_floor - grow), *right, *left]


def rail_profile(grow: float = 0.0, z_floor: float = P.FLOOR, top: float | None = None):
    """Rail cross-section as a face in the YZ plane (extrude it along +x)."""
    pts = rail_points(grow, z_floor, top)
    return make_face(Polyline(*[(0, y, z) for y, z in pts], close=True))


def _shell() -> Part:
    outer = extrude(outline_face(), P.BOX_H)
    cavity = Pos(0, 0, P.FLOOR) * extrude(outline_face(-P.WALL), P.BOX_H)
    body = outer - cavity

    plinth = extrude(outline_face(1.2), 2.6)
    plinth = chamfer(plinth.edges().group_by(Axis.Z)[-1], 1.1)
    band_w = P.lines(6) - P.WALL  # wall + band = 6 lines at the rim, where the lid slides
    z_band = P.BOX_H - 3.4
    # Loft from the wall outline up to the grown outline. The corners move further than the
    # edges (miter), so the rise follows the corners: every face and corner edge is at 45
    # degrees or steeper and prints without support.
    rise = max_miter(band_w)
    flare = loft([Pos(0, 0, z_band - rise) * outline_face(),
                  Pos(0, 0, z_band) * outline_face(band_w)])
    band = flare + Pos(0, 0, z_band) * extrude(outline_face(band_w), 3.4)
    return body + (plinth - cavity) + (band - cavity)


def _wall_relief(depth: float, z0: float, z1: float, length: float) -> Part:
    """A block on the wall (canonical frame) whose underside rises at 45 degrees from the
    wall, so it prints without support or bridging. Spans x in [-length/2, length/2]."""
    profile = Polygon((-0.5, z0 - depth), (0.0, z0 - depth), (depth, z0), (depth, z1),
                      (-0.5, z1), align=None)  # (y, z) in the YZ plane
    block = extrude(Plane.YZ * profile, length / 2, both=True)
    return chamfer(block.edges().group_by(Axis.Z)[-1].filter_by(Axis.X).group_by(Axis.Y)[-1],
                   0.5)


def _handle() -> Part:
    """One coffin handle in a canonical frame: wall along X, outward +Y, centre at z=0.

    A bar between two brackets, modelled as relief on the wall: no gap behind the bar, so
    there is nothing to bridge. All flat faces sit on the layer grid when z=0 is HANDLE_Z.
    """
    depth, height = P.HANDLE_BAR
    mount_w, mount_d, extra = P.HANDLE_MOUNT
    z_bar, z_top = -height / 2 + 0.1, height / 2 + 0.1  # 21.2 .. 23.0 with HANDLE_Z = 22
    bar = _wall_relief(depth, z_bar, z_top, P.HANDLE_LEN - mount_w)
    mount = _wall_relief(mount_d, z_bar - extra, z_top + extra, mount_w)
    x_mount = (P.HANDLE_LEN - mount_w) / 2
    return bar + Pos(-x_mount, 0, 0) * mount + Pos(x_mount, 0, 0) * mount


def _handles() -> Part:
    handle = _handle()
    out = []
    for (a, b), fracs in zip(side_segments(), [(0.5,), (0.3, 0.7), (0.3, 0.7), (0.5,)]):
        d = (b - a).normalized()
        for f in fracs:
            origin = a + (b - a) * f + Vector(0, 0, P.HANDLE_Z)
            loc = Location(Plane(origin=origin, x_dir=-d, z_dir=(0, 0, 1)))
            out.append(loc * handle)
    result = out[0]
    for h in out[1:]:
        result += h
    return result


def _pillow() -> Part:
    """Satin pillow under the skull; its top is the rest position of the vampire's back."""
    pillow = box_between(P.WALL, P.WALL + 25.0, -12.0, 12.0, P.FLOOR - 0.5, P.FLOOR + P.PILLOW_H)
    return fillet(pillow.edges().group_by(Axis.Z)[-1], 1.2)


def _bearing() -> Part:
    """Block with a slot for the hip stubs, tilted towards the head.

    The push of the nails loads the stubs towards the foot and down, into the bottom of
    the slot. The mouth is SNAP narrower than the stubs: lying down, the vampire stays in;
    at about 45 degrees the two flats of each stub line up with the mouth (bayonet).
    Everything prints without support: the only lip is on the head side and faces up.
    """
    block = box_between(P.PIVOT_X - P.BLOCK_HL, P.PIVOT_X + P.BLOCK_HL, -P.BLOCK_HW, P.BLOCK_HW,
                        P.FLOOR - 0.01, P.BLOCK_TOP)
    r = P.STUB_D / 2 + P.CLR_STUB
    # Sketch frame: +y along the slot (out of the block), +x towards the foot side.
    # Foot side: the wall is tangent to the hole, i.e. a plain 45-degree wall after the
    # tilt (a lip there would overhang the hole). Head side: the retaining lip, a ledge
    # that faces up. The opening is SNAP narrower than the stubs.
    head = P.STUB_D - P.SNAP - r  # head-side half opening
    slot = Sketch() + Circle(r) + Pos((r - head) / 2, 6) * Rectangle(r + head, 12)
    # Lead-in: past the lip, the head-side wall opens at 45 degrees. After the tilt that
    # wall is horizontal, so start it on a layer boundary.
    c = cos(radians(P.BEARING_TILT))
    lip_end = head + (P.snap_up(P.PIVOT_Z + c * (r + 0.2 - head)) - P.PIVOT_Z) / c
    slot += Polygon((-head, lip_end), (0, lip_end), (0, lip_end + 8),
                    (-head - 8, lip_end + 8), align=None)
    # Plane.XZ maps sketch y to +z; the rotation turns the slot towards -x (the head)
    cut = Pos(P.PIVOT_X, 0, P.PIVOT_Z) * Rot(0, -P.BEARING_TILT, 0) * extrude(
        Plane.XZ * slot, 2 * P.BLOCK_HW + 1, both=True)
    return block - cut


def _rail() -> Part:
    length = P.BOX_L - P.WALL - P.RAIL_X0  # ends flush with the foot wall: closed stop
    return Pos(P.RAIL_X0, 0, 0) * extrude(rail_profile(), length)


def _stash_wall() -> Part:
    t = P.lines(4)
    wall = box_between(P.STASH_WALL_X, P.STASH_WALL_X + t, -P.SHOULDER_W / 2, P.SHOULDER_W / 2,
                       P.FLOOR - 0.01, P.FLOOR + P.STASH_WALL_H)
    return wall & extrude(outline_face(-P.WALL + 0.01), P.BOX_H)


@cache
def make_box() -> Part:
    box = _shell() + _handles() + _pillow() + _bearing() + _rail() + _stash_wall()
    box.label = "box"
    return box


if __name__ == "__main__":
    b = make_box()
    print(b.is_valid, b.volume, b.bounding_box())
