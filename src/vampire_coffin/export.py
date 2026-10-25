"""Export the printable parts: STL files (out/stl) and ready-made 3MF plates (out/3mf).

- One STL per part, already in its print orientation.
- One 3MF per print job ("plate"): parts arranged on the MK4 bed, with names and colours.
  The plates that need a colour change carry it as PrusaSlicer metadata, so the M600 is
  already set when you open the file in PrusaSlicer.
- assembly_preview.3mf: the assembled, coloured coffin, only for viewing.

Exits with status 1 if any part fails a check, so scripts and CI can rely on it.
"""

import sys
import tempfile
import zipfile
from pathlib import Path

import trimesh
from build123d import Color, Mesher, Part, Pos, export_stl

from . import params as P
from .assembly import parts_at
from .box import make_box
from .coupon import coupon_parts
from .lid import lid_base, lid_relief, make_lid
from .nail import make_nail
from .nail import print_pose as nail_pose
from .vampire import make_vampire
from .vampire import print_pose as vampire_pose

BED = (250.0, 210.0, 220.0)  # Prusa MK4
M600_Z = P.layer_top(P.LID_T)  # print_z of the first relief layer (lid on the bed)
STL_TOLERANCE = (0.01, 0.1)  # linear (mm), angular (rad)
COLOURS = {"black": "#1c1a1e", "orange": "#f07318", "white": "#ece8dc"}


def printable_parts() -> dict[str, Part]:
    """name -> part on the bed (z=0). Names carry colour and quantity."""
    return {
        "box_black": make_box(),
        "lid_black_M600_orange": Pos(0, 0, -P.BOX_H) * make_lid(),
        "vampire_white": vampire_pose(make_vampire()),
        "nail_black_x2": nail_pose(make_nail()),
    }


def check(part: Part) -> list[str]:
    """Problems with the CAD solid itself (empty list = fine)."""
    problems = []
    bb = part.bounding_box()
    if not part.is_valid:
        problems.append("invalid solid")
    if abs(bb.min.Z) > 1e-3:
        problems.append(f"not on the bed (zmin={bb.min.Z:.3f})")
    if bb.size.X > BED[0] or bb.size.Y > BED[1] or bb.size.Z > BED[2]:
        problems.append(f"larger than the bed {bb.size}")
    if len(part.solids()) != 1:
        problems.append(f"{len(part.solids())} separate bodies")
    return problems


def write_stl(part: Part, path: Path) -> list[str]:
    """Write the STL and check the mesh that a slicer will actually load."""
    export_stl(part, path, tolerance=STL_TOLERANCE[0], angular_tolerance=STL_TOLERANCE[1])
    mesh = trimesh.load(path)
    return [] if mesh.is_watertight else ["mesh not watertight"]


def mesh_problems(part: Part) -> list[str]:
    with tempfile.TemporaryDirectory() as tmp:
        return write_stl(part, Path(tmp) / "part.stl")


def _on_bed(part: Part, x_min: float, y_min: float) -> Part:
    """Move a part (already lying on z=0) so its footprint starts at (x_min, y_min)."""
    bb = part.bounding_box()
    return Pos(x_min - bb.min.X, y_min - bb.min.Y, 0) * part


def _row(parts: list[Part], gap: float = 8.0, y_centre: float = BED[1] / 2) -> list[Part]:
    """Lay parts out left to right, centred on the bed."""
    widths = [p.bounding_box().size.X for p in parts]
    x = (BED[0] - sum(widths) - gap * (len(parts) - 1)) / 2
    placed = []
    for part, w in zip(parts, widths):
        placed.append(_on_bed(part, x, y_centre - part.bounding_box().size.Y / 2))
        x += w + gap
    return placed


def plates() -> dict[str, tuple[list[tuple[str, Part, str]], float | None]]:
    """plate name -> ([(object name, part on the bed, colour)], M600 height or None)."""
    pp, cp = printable_parts(), coupon_parts()
    nail = pp["nail_black_x2"]
    box, n1, n2 = _row([pp["box_black"], nail, nail], gap=10)
    coupon_names = list(cp)
    coupon_colour = {"coupon_pelvis": "white"}
    return {
        "plate_1_black_box_and_nails": (
            [("box", box, "black"), ("nail", n1, "black"), ("nail", n2, "black")], None),
        "plate_2_lid_black_then_orange": (
            [("lid", _row([pp["lid_black_M600_orange"]])[0], "black")], M600_Z),
        "plate_3_white_vampire": ([("vampire", _row([pp["vampire_white"]])[0], "white")], None),
        "coupon_all_pieces": (
            [(n, p, coupon_colour.get(n, "black"))
             for n, p in zip(coupon_names, _row([cp[n] for n in coupon_names]))], None),
    }


def _named(part: Part, name: str, colour: str) -> Part:
    part = part.moved(Pos())  # a copy: the cached parts must not be changed
    part.label = name
    part.color = Color(COLOURS[colour])
    return part


def m600_metadata(print_z: float) -> str:
    """PrusaSlicer's colour-change list, as stored inside its 3MF files."""
    return ('<?xml version="1.0" encoding="utf-8"?>\n<custom_gcodes_per_print_z>\n'
            f'<code print_z="{print_z:.2f}" type="0" extruder="1" color="{COLOURS["orange"]}" '
            'extra="" gcode="M600"/>\n<mode value="SingleExtruder"/>\n'
            '</custom_gcodes_per_print_z>\n')


def write_3mf(path: Path, objects: list[tuple[str, Part, str]], m600_z: float | None = None):
    mesher = Mesher()
    for name, part, colour in objects:
        mesher.add_shape(_named(part, name, colour), linear_deflection=STL_TOLERANCE[0],
                         angular_deflection=STL_TOLERANCE[1])
    mesher.write(str(path))
    if m600_z is not None:
        with zipfile.ZipFile(path, "a", zipfile.ZIP_DEFLATED) as z:
            z.writestr("Metadata/Prusa_Slicer_custom_gcode_per_print_z.xml",
                       m600_metadata(m600_z))


def assembly_preview() -> list[tuple[str, Part, str]]:
    """The coffin fully open, vampire sitting up, lid relief in orange (view only)."""
    placed = parts_at(P.S_MAX)
    moved = Pos(P.S_MAX, 0, 0)
    return [("box", placed["box"], "black"), ("lid", moved * lid_base(), "black"),
            ("lid relief", moved * lid_relief(), "orange"),
            ("nail", placed["nail_r"], "black"), ("nail", placed["nail_l"], "black"),
            ("vampire", placed["vampire"], "white")]


def export_all(out: Path, coupon: bool = True) -> dict[str, list[str]]:
    """Write every STL into out/stl and the 3MF plates into out/3mf; return the problems."""
    stl_dir, mf_dir = out / "stl", out / "3mf"
    stl_dir.mkdir(parents=True, exist_ok=True)
    mf_dir.mkdir(parents=True, exist_ok=True)
    parts = printable_parts() | (coupon_parts() if coupon else {})
    report = {}
    for name, part in parts.items():
        problems = check(part) + write_stl(part, stl_dir / f"{name}.stl")
        report[name] = problems
        status = "OK" if not problems else "; ".join(problems)
        print(f"{name:30s} {part.volume / 1000:6.1f} cm3  {status}")
    for name, (objects, m600_z) in plates().items():
        write_3mf(mf_dir / f"{name}.3mf", objects, m600_z)
        note = f"  (M600 at Z = {m600_z:.2f} mm)" if m600_z else ""
        print(f"{name + '.3mf':30s} {len(objects)} object(s){note}")
    write_3mf(mf_dir / "assembly_preview.3mf", assembly_preview())
    print(f"{'assembly_preview.3mf':30s} view only")
    print(f"\nLid: the colour change (M600) goes at layer Z = {M600_Z:.2f} mm (0.2 mm layers). "
          "It is already set in the 3MF plates.")
    return report


if __name__ == "__main__":
    result = export_all(Path(sys.argv[1] if len(sys.argv) > 1 else "out"))
    sys.exit(1 if any(result.values()) else 0)
