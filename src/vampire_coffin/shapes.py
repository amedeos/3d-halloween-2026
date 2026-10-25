"""Small geometry helpers shared by the part modules."""

from build123d import Box, Part, Pos


def box_between(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> Part:
    """Axis-aligned box from its min and max corners."""
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)
