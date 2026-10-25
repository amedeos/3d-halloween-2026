"""Lid travel -> sit-up angle.

A pin (on each coffin nail) moves horizontally with the lid at height PIN_H above the hip
axis and pushes the head-side face of a lever arm that sticks up from the pelvis. The arm
angle phi is measured from vertical, positive towards the foot; the vampire's sit-up
angle is theta = phi - ARM_REST. Gravity keeps the arm against the pin on the way back.

Contact condition (pin centre at horizontal offset `a` from the axis):
    PIN_H * sin(phi) - a * cos(phi) = ARM_W / 2 + PIN_D / 2
"""

from math import asin, atan2, cos, degrees, hypot, radians, sin

from . import params as P

CONTACT = P.ARM_W / 2 + P.PIN_D / 2


def offset_for_phi(phi_deg: float) -> float:
    """Horizontal pin offset from the axis that puts the arm at `phi_deg`."""
    phi = radians(phi_deg)
    return (P.PIN_H * sin(phi) - CONTACT) / cos(phi)


def phi_for_offset(a: float) -> float:
    """Arm angle (deg) when the pin centre is `a` mm from the axis (towards the foot)."""
    return degrees(atan2(a, P.PIN_H) + asin(CONTACT / hypot(P.PIN_H, a)))


def contact_distance(phi_deg: float) -> float:
    """Distance along the arm from the axis to the contact point."""
    phi = radians(phi_deg)
    return (P.PIN_H - CONTACT * sin(phi)) / cos(phi)


PIN_X_START = P.PIVOT_X + offset_for_phi(P.ARM_REST)  # first touch
PIN_X_END = P.PIVOT_X + offset_for_phi(P.ARM_REST + P.THETA_MAX)
PIN_U = PIN_X_END - P.S_MAX  # pin position in lid coordinates
S_DWELL = PIN_X_START - PIN_U  # lid travel before the vampire starts to move
LID_SLOT_U0 = P.RAIL_X0 - P.S_MAX  # closed end of the dovetail slot (open stop)
PIN_Z = P.PIVOT_Z + P.PIN_H


def theta(s: float) -> float:
    """Sit-up angle in degrees for lid travel `s`."""
    x = PIN_U + s
    if x <= PIN_X_START:
        return 0.0
    return min(max(phi_for_offset(x - P.PIVOT_X) - P.ARM_REST, 0.0), P.THETA_MAX)


def pressure_angle(s: float) -> float:
    """Angle between the push force and the pin's travel direction (deg)."""
    return abs(P.ARM_REST + theta(s))


if __name__ == "__main__":
    print(f"pin u={PIN_U:.2f} z={PIN_Z:.2f}  dwell={S_DWELL:.1f}  s_max={P.S_MAX}")
    print(f"contact along arm: rest {contact_distance(P.ARM_REST):.1f}  "
          f"end {contact_distance(P.ARM_REST + P.THETA_MAX):.1f}  arm {P.ARM_LEN}")
    for s in range(0, int(P.S_MAX) + 1, 4):
        print(f"s={s:3d}  theta={theta(s):5.1f}  pressure={pressure_angle(s):4.1f}")
