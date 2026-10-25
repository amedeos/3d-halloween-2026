"""The classic six-sided coffin outline, shared by the box and the lid."""

from math import acos, sin

from build123d import Face, Kind, Polyline, Vector, make_face, offset

from . import params as P


def outline_points() -> list[tuple[float, float]]:
    return [
        (0.0, -P.HEAD_W / 2),
        (P.SHOULDER_X, -P.SHOULDER_W / 2),
        (P.BOX_L, -P.FOOT_W / 2),
        (P.BOX_L, P.FOOT_W / 2),
        (P.SHOULDER_X, P.SHOULDER_W / 2),
        (0.0, P.HEAD_W / 2),
    ]


def outline_face(grow: float = 0.0) -> Face:
    """Outline in the XY plane, optionally grown (+) or shrunk (-) with sharp corners."""
    face = make_face(Polyline(*outline_points(), close=True))
    if grow:
        face = offset(face, grow, kind=Kind.INTERSECTION)
    return face


def max_miter(grow: float) -> float:
    """Largest corner displacement when the outline is grown by `grow` with sharp corners.

    A corner with interior angle a moves by grow / sin(a / 2), more than `grow` itself.
    """
    pts = [Vector(*p) for p in outline_points()]
    worst = 0.0
    for i, p in enumerate(pts):
        a, b = (pts[i - 1] - p).normalized(), (pts[(i + 1) % len(pts)] - p).normalized()
        half = acos(max(-1.0, min(1.0, a.dot(b)))) / 2
        worst = max(worst, grow / sin(half))
    return worst


def side_segments() -> list[tuple[Vector, Vector]]:
    """The four slanted side walls (start, end) on the +y and -y sides."""
    pts = [Vector(*p) for p in outline_points()]
    return [(pts[0], pts[1]), (pts[1], pts[2]), (pts[3], pts[4]), (pts[4], pts[5])]
