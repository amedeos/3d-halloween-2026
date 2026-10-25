from itertools import pairwise

import pytest

from vampire_coffin import params as P
from vampire_coffin.kinematics import (
    PIN_U,
    S_DWELL,
    contact_distance,
    pressure_angle,
    theta,
)

STEPS = [P.S_MAX * k / 100 for k in range(101)]


def test_rest_and_full_travel():
    assert theta(0) == 0
    assert theta(S_DWELL - 0.1) == 0
    assert theta(P.S_MAX) == pytest.approx(P.THETA_MAX, abs=0.05)


def test_monotonic():
    angles = [theta(s) for s in STEPS]
    assert all(b >= a for a, b in pairwise(angles))


def test_pressure_angle_stays_low():
    assert max(pressure_angle(s) for s in STEPS if theta(s) > 0) <= 35.5


def test_contact_stays_on_the_straight_face_of_the_lever():
    straight = P.ARM_LEN - P.ARM_W / 2
    for phi in (P.ARM_REST, P.ARM_REST + P.THETA_MAX):
        assert contact_distance(phi) + 1.0 <= straight


def test_nail_fits_on_the_lid():
    assert PIN_U - P.NAIL_HEAD[0] / 2 > P.LID_BEVEL + 1.0
    assert P.RAIL_X0 - P.S_MAX > 5  # slot head end stays inside the lid


def test_lever_tip_clears_the_lid_when_vertical():
    assert P.PIVOT_Z + P.ARM_LEN < P.BOX_H - 1.0
