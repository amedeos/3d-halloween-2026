"""Printability on a Prusa MK4: 0.4 mm nozzle, PrusaSlicer "0.20mm STRUCTURAL" profile."""

import pytest
from build123d import GeomType

from vampire_coffin import params as P
from vampire_coffin.coupon import coupon_parts, nail_gauge_parts
from vampire_coffin.export import M600_Z, VAMPIRE_M600_Z, printable_parts
from vampire_coffin.lid import FONT, _lettering, relief_sketch

PARTS = printable_parts() | coupon_parts() | nail_gauge_parts()


def on_grid(z: float) -> bool:
    return abs(z - round(z / P.LAYER) * P.LAYER) < 1e-3


def off_grid_faces(part) -> list[float]:
    """Heights of flat horizontal faces that do not sit on a layer boundary."""
    heights = []
    for face in part.faces():
        if face.geom_type == GeomType.PLANE and abs(abs(face.normal_at().Z) - 1) < 1e-6:
            z = face.center().Z
            if not on_grid(z):
                heights.append(round(z, 3))
    return sorted(set(heights))


@pytest.mark.parametrize("name", list(PARTS))
def test_flat_faces_sit_on_layer_boundaries(name):
    assert off_grid_faces(PARTS[name]) == []


def test_profile_assumptions():
    assert P.FIRST_LAYER == P.LAYER == 0.2
    assert P.LINE_W == 0.45 and P.NOZZLE == 0.4
    assert P.lines(1) == pytest.approx(P.LINE_W)
    assert P.lines(4) == pytest.approx(1.671, abs=1e-3)


def test_colour_change_layer():
    # the relief starts on a layer boundary, and the M600 comes before its first layer
    assert on_grid(P.LID_T) and on_grid(P.RELIEF_H)
    assert M600_Z == pytest.approx(P.LID_T + P.LAYER)
    assert P.layer_top(P.LID_T) == pytest.approx(5.2)
    # vampire: the black cape and collar are exactly CAPE_T thick, then white
    assert on_grid(P.CAPE_T) and VAMPIRE_M600_Z == pytest.approx(P.CAPE_T + P.LAYER)


def test_vampire_volume_is_sane():
    # a boolean that fails silently can drop half of a part without any error
    from vampire_coffin.vampire import make_vampire

    assert 8.0 < make_vampire().volume / 1000 < 13.5


def test_solid_shells():
    # walls are whole lines: 2 perimeters on each side, nothing in between
    assert P.WALL == pytest.approx(P.lines(2 * 2))
    # floor and lid are thicker than the profile's 4 bottom / 5 top solid layers
    assert P.FLOOR >= 4 * P.LAYER and P.LID_T >= (4 + 5) * P.LAYER


def _thin_fraction(sketch, min_width: float, px_per_mm: float = 20.0) -> float:
    """Share of the area in strokes thinner than `min_width` (morphological opening)."""
    import numpy as np
    from PIL import Image, ImageDraw
    from scipy import ndimage

    bb = sketch.bounding_box()
    w = int((bb.size.X + 2) * px_per_mm)
    h = int((bb.size.Y + 2) * px_per_mm)
    img = Image.new("1", (w, h), 0)
    draw = ImageDraw.Draw(img)
    for face in sketch.faces():
        verts, tris = face.tessellate(0.01)
        pts = [((v.X - bb.min.X + 1) * px_per_mm, (v.Y - bb.min.Y + 1) * px_per_mm) for v in verts]
        for a, b, c in tris:
            draw.polygon([pts[a], pts[b], pts[c]], fill=1)
    mask = np.array(img, dtype=bool)
    r = round(min_width / 2 * px_per_mm)
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    disk = xx**2 + yy**2 <= r * r
    opened = ndimage.binary_opening(mask, structure=disk)
    return 1 - opened.sum() / mask.sum()


@pytest.mark.parametrize("name", ["lettering", "relief"])
def test_relief_strokes_are_printable(name):
    # Arachne drops walls thinner than min_bead_width (85 % of a line). Corners always lose
    # a little in the opening, so allow 1.5 % of the area. The lettering is checked on its
    # own: averaged with the thick cross and border, thin strokes would hide.
    assert FONT.is_file()
    sketch = _lettering() if name == "lettering" else relief_sketch()
    assert _thin_fraction(sketch, 0.85 * P.LINE_W) < 0.015


def _layer_sections(part):
    """Cross-sections (shapely polygons) at the middle of every layer."""
    import numpy as np
    import trimesh

    verts, tris = part.tessellate(0.02, 0.2)
    mesh = trimesh.Trimesh([[v.X, v.Y, v.Z] for v in verts], tris)
    top = part.bounding_box().max.Z
    heights = np.arange(P.LAYER / 2, top, P.LAYER)
    paths = mesh.section_multiplane([0, 0, 0], [0, 0, 1], heights)
    return [list(p.polygons_full) if p is not None else [] for p in paths]


@pytest.mark.parametrize("name", list(PARTS))
def test_no_floating_islands(name):
    """Every island of every layer must rest on the layer below (nothing starts in mid-air)."""
    from shapely.ops import unary_union

    layers = _layer_sections(PARTS[name])
    for k in range(1, len(layers)):
        below = unary_union(layers[k - 1]) if layers[k - 1] else None
        for poly in layers[k]:
            if poly.area < 0.05:  # tessellation crumbs
                continue
            assert below is not None and poly.intersection(below).area > 0.01, (
                f"island of {poly.area:.2f} mm2 at z={(k + 0.5) * P.LAYER:.1f}")


def test_lid_lips_ramp_down_at_the_entry():
    """The lead-in lowers the lips from the top, so the rail head slides over them."""
    from build123d import Box, Pos

    from vampire_coffin.lid import SLOT_TOP, make_lid

    def lip_top(u: float) -> float:
        z0, z1 = P.BOX_H, SLOT_TOP - 0.05
        probe = make_lid() & (Pos(u, 3.6, (z0 + z1) / 2) * Box(0.05, 0.05, z1 - z0))
        return max((s.bounding_box().max.Z for s in probe.solids()), default=P.BOX_H)

    full, half, entry = lip_top(P.LID_LIPS_U1 - 10), lip_top(P.LID_LIPS_U1 - 2), lip_top(
        P.LID_LIPS_U1 - 0.1)
    assert full > half > entry
    assert entry < P.BOX_H + 0.3


@pytest.mark.parametrize("clr", [0.0, 0.05, 0.10, 0.15, 0.20])
def test_nail_gaps_follow_the_gauge(clr):
    """The real nail has the same total clearance as the gauge hole it was chosen from."""
    from vampire_coffin.lid import nail_y_gaps

    inner, outer = nail_y_gaps(clr)
    assert inner + outer == pytest.approx(2 * clr)
    assert on_grid(inner) and outer >= 0
