import pytest

from vampire_coffin.coupon import coupon_parts, nail_gauge_parts
from vampire_coffin.export import check, mesh_problems, printable_parts

PRINTABLE = printable_parts()
PARTS = PRINTABLE | coupon_parts() | nail_gauge_parts()


@pytest.mark.parametrize("name", list(PARTS))
def test_part_is_printable(name):
    assert check(PARTS[name]) == []


@pytest.mark.parametrize("name", list(PARTS))
def test_stl_mesh_is_watertight(name):
    assert mesh_problems(PARTS[name]) == []


def test_print_time_budget():
    # ~5 h on an MK4 for about 120 cm3 of solid model (infill makes it lighter)
    total = sum(part.volume for part in PRINTABLE.values()) + PRINTABLE["nail_black_x2"].volume
    assert total / 1000 < 125
