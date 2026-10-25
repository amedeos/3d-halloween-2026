from math import cos, radians, sin

import pytest
from build123d import Pos

from vampire_coffin import params as P
from vampire_coffin.assembly import collisions, parts, parts_at
from vampire_coffin.kinematics import S_DWELL, theta
from vampire_coffin.vampire import placed as placed_vampire

SAMPLES = [P.S_MAX * k / 24 for k in range(25)]


@pytest.mark.parametrize("s", SAMPLES)
def test_nothing_collides(s):
    bad = {k: v for k, v in collisions(s).items() if v > 0.01}
    assert not bad, f"s={s:.1f} theta={theta(s):.1f}: {bad}"


@pytest.mark.parametrize("s", [S_DWELL + 2, (S_DWELL + P.S_MAX) / 2, P.S_MAX])
def test_nails_drive_the_levers(s):
    placed = parts_at(s)
    assert placed["vampire"].distance_to(placed["nail_r"]) < 0.05
    assert placed["vampire"].distance_to(placed["nail_l"]) < 0.05


@pytest.mark.parametrize("s", [0, S_DWELL / 2, S_DWELL - 3])
def test_nails_are_free_during_the_dwell(s):
    placed = parts_at(s)
    assert placed["vampire"].distance_to(placed["nail_r"]) > 0.5
    assert placed["vampire"].distance_to(placed["nail_l"]) > 0.5


RISE = [S_DWELL + (P.S_MAX - S_DWELL) * k / 12 for k in range(13)]
MIN_LID_GAP = 2.0  # measured: 2.34 mm at s = 68 (lever tips vs lid underside)


def test_lid_clears_the_rising_vampire():
    gaps = []
    for s in RISE:
        placed = parts_at(s)
        gaps.append(placed["vampire"].distance_to(placed["lid"]))
    assert min(gaps) >= MIN_LID_GAP, f"closest approach {min(gaps):.2f} mm"


def _overlap_backed_out(theta_deg: float, depth: float, lateral: float = 0.0) -> float:
    """Overlap with the box when the vampire is pulled `depth` mm out along the slot and
    shifted `lateral` mm sideways, towards the foot-side wall."""
    tilt = radians(P.BEARING_TILT)
    out = (-sin(tilt) * depth + cos(tilt) * lateral, 0, cos(tilt) * depth + sin(tilt) * lateral)
    vampire = Pos(*out) * placed_vampire(parts()["vampire"], theta_deg)
    common = parts()["box"] & vampire
    return sum(s.volume for s in common.solids()) if common else 0.0


# The mouth is asymmetric: the foot-side wall is tangent to the hole (no overhanging lip),
# the head-side wall carries the retaining lip. Its centre line is shifted towards the foot.
FOOT = P.STUB_D / 2 + P.CLR_STUB
HEAD = P.STUB_D - P.SNAP - FOOT
MOUTH_CENTRE = (FOOT - HEAD) / 2


@pytest.mark.parametrize("depth", [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 9.0])
def test_hip_bayonet_insertion(depth):
    """At 45 degrees the flats of the stubs pass along the middle of the mouth. In the last
    millimetre the stubs slide sideways into the centre of the hole."""
    lateral = MOUTH_CENTRE * min(1.0, depth)
    assert _overlap_backed_out(45.0, depth, lateral) < 0.01


@pytest.mark.parametrize("theta_deg", [0.0, 15.0, 25.0])
@pytest.mark.parametrize("lateral", [0.0, MOUTH_CENTRE])
def test_hip_stays_in_the_bearing(theta_deg, lateral):
    """Lying down the stubs cannot leave the slot, whichever way they are pulled: SNAP > 0.

    From about 30 degrees on, the flats start to line up with the mouth (bayonet). There
    the nails push the stubs into the bottom of the slot, so they still stay in.
    """
    worst = max(_overlap_backed_out(theta_deg, d, lateral) for d in (0.5, 1.0, 1.5, 2.0, 3.0))
    assert worst > 0.05
