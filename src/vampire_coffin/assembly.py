"""Place every part for a given lid travel and check that nothing collides."""

from build123d import Part, Plane, Pos

from . import params as P
from .box import make_box
from .kinematics import theta
from .lid import lid_base, lid_relief, make_lid
from .nail import make_nail
from .vampire import make_vampire, placed

COLOR = {"box": "black", "lid": "black", "nail": (0.3, 0.3, 0.32), "vampire": "white"}


def parts() -> dict[str, Part]:
    """The parts in assembly coordinates (lid closed). The builders are cached."""
    nail = make_nail()
    return {
        "box": make_box(),
        "lid": make_lid(),
        "nail_r": nail,
        "nail_l": nail.mirror(Plane.XZ),
        "vampire": make_vampire(),
    }


def parts_at(s: float | None) -> dict[str, Part]:
    """All parts in assembly coordinates with the lid slid open by s (None = fully open)."""
    s = P.S_MAX if s is None else s
    p = parts()
    moved = Pos(s, 0, 0)
    return {
        "box": p["box"],
        "lid": moved * p["lid"],
        "nail_r": moved * p["nail_r"],
        "nail_l": moved * p["nail_l"],
        "vampire": placed(p["vampire"], theta(s)),
    }


def scene(s: float | None, lid: bool = True):
    """Coloured parts for rendering; the lid relief shows in orange (the M600 colour)."""
    out = []
    for name, shape in parts_at(s).items():
        if name == "lid":
            if lid:
                moved = Pos(P.S_MAX if s is None else s, 0, 0)
                out.append((moved * lid_base(), COLOR["lid"]))
                out.append((moved * lid_relief(), "orange"))
            continue
        out.append((shape, COLOR[name.split("_")[0]]))
    return out


PAIRS = [
    ("vampire", "box"),
    ("vampire", "lid"),
    ("vampire", "nail_r"),
    ("vampire", "nail_l"),
    ("nail_r", "box"),
    ("nail_l", "box"),
    ("lid", "box"),
]


def collisions(s: float | None) -> dict[tuple[str, str], float]:
    """Intersection volume (mm^3) of every pair that must never overlap."""
    placed_parts = parts_at(s)
    out = {}
    for a, b in PAIRS:
        common = placed_parts[a] & placed_parts[b]
        out[(a, b)] = sum(sol.volume for sol in common.solids()) if common else 0.0
    return out


if __name__ == "__main__":
    import sys

    steps = [0, 20, 40, 52, 56, 60, 64, 68, 72, 76, 80, P.S_MAX]
    if len(sys.argv) > 1:
        steps = [float(a) for a in sys.argv[1:]]
    for s in steps:
        c = collisions(s)
        bad = {f"{a}/{b}": round(v, 3) for (a, b), v in c.items() if v > 0.01}
        print(f"s={s:5.1f} theta={theta(s):5.1f}  {'OK' if not bad else bad}")
