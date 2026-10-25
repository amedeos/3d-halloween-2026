# AGENTS.md

Guidance for coding agents working in this repository.

## Project

"Nosferatu's Coffin" is an entry for the Printables contest
[Halloween 2026: Make It Move](https://www.printables.com/contest/533-halloween-2026)
(contest id 533). You pull the lid towards the feet, and a skeleton vampire sits up to 70°.

- **Deadline:** entries close on 1 Nov 2026. The contest text says 23:59 UTC, but the API
  says 21:59 UTC. Plan to publish by 31 Oct.
- **Judging:** creativity 25, Halloween spirit 20, aesthetics 20, functionality 20,
  printability 15. The judge (3DPrintingDoctor) prints the best entries, so every part
  must print reliably without supports.
- **Printer:** Prusa MK4 (Input Shaper firmware) with one extruder. Colours come from
  separate parts and from two M600 colour changes: the lid (cross and lettering orange)
  and the vampire (black cape and collar, white bones). Keep the total print time
  under about 6 hours (now about 4 h 50 min).
- **Slicer profile:** PrusaSlicer "Original Prusa MK4 Input Shaper 0.4 nozzle",
  "0.20mm STRUCTURAL @MK4IS 0.4", "Prusament PETG @PGIS". 0.2 mm layers (first layer too),
  0.45 mm lines, 2 perimeters (Arachne), 4 bottom / 5 top solid layers.
- **Material:** **Prusament PETG** by default (black, orange, white). PLA also works.
- **License:** CC BY-SA 4.0. The font (Pirata One) is under the SIL OFL.

## Language

- Write all repository text in **English at B2/C1 level**: README, listing, docstrings,
  comments. Use clear, short sentences and common words.
- The owner chats in Italian.

## Environment and commands

- Python 3.14 (3.13 also works), [uv](https://docs.astral.sh/uv/),
  [build123d](https://github.com/gumyr/build123d) 0.13.

```sh
uv sync
uv run pytest                              # ~25 s: kinematics, parts, collisions
uv run python -m vampire_coffin.kinematics # lid travel -> sit-up angle table
uv run python -m vampire_coffin.assembly   # collision report over the lid travel
uv run python -m vampire_coffin.export     # STLs -> out/stl, 3MF plates -> out/3mf (exit 1 on problems)
uv run python -m vampire_coffin.slicer     # optional, PrusaSlicer CLI: times, checks, projects
uv run python -m vampire_coffin.render     # PNG previews -> out/render (add --gif for the animation)
```

- OCP (used by build123d) loads `libGL.so.1` and some X11 libraries when you import it.
- On a headless machine without them, `import build123d` fails. You don't need root to fix
  this: unpack the distro packages (mesa-libGL, libglvnd, libX11, libXext, libxcb,
  libXau, libXxf86vm, libX11-xcb) into a folder and point `LD_LIBRARY_PATH` at it.

## Layout

| File | Role |
|---|---|
| `src/vampire_coffin/params.py` | **Single source of truth** for every size and clearance. Change numbers here, not in the part modules. |
| `kinematics.py` | Lid travel `s` → sit-up angle `theta(s)`; pin position, dwell, pressure angle |
| `outline.py` | Six-sided coffin outline shared by box and lid |
| `shapes.py` | Small shared helpers (`box_between`) |
| `box.py`, `lid.py`, `nail.py`, `vampire.py` | The printable parts |
| `assembly.py` | Places all parts for a given `s`; `collisions(s)` |
| `coupon.py` | Tolerance test pieces, cut from the real parts |
| `export.py` | STL export in print orientation, plus checks (valid, on the bed, fits the bed, watertight mesh). 3MF plates (one per print job, named and coloured, M600 as PrusaSlicer metadata) and a coloured assembly preview. |
| `slicer.py` | Optional. Slices the plates with the PrusaSlicer CLI (MK4 + 0.20mm STRUCTURAL + Prusament PETG). It checks the M600 (present exactly where needed, at the right Z), runs a second slice with automatic supports on (bridges excluded) that must create no support, and writes project 3MFs with the full config taken from the G-code. |
| `render.py` | numpy z-buffer renderer (no OpenGL), PNG and GIF. `listing()` makes every image for the Printables page: hero view from the feet (`FROM_FEET`), exploded view, cutaway of the mechanism, GIFs. |
| `fonts/` | The bundled font, shipped inside the package |
| `tests/` | pytest suite. Keep it green. |
| `listing/` | Printables page text (`printables.md`) and the photo/video plan (`shot-list.md`) |

## Frames

- **Assembly frame:** x runs from the head end (x=0) to the foot end (x=160), y is
  lateral, z is up, and the box stands on z=0. The lid moves by +s along x.
- **Vampire (pivot) frame:** the origin is on the hip axis, the head is at −x, and the
  back plane is at z = −`AXIS_E`. `vampire.placed(v, theta)` puts the vampire in the
  assembly frame.
- When he sits up, the vampire **faces the foot end**. Take the main photos and renders
  from the feet, looking over the lid.

## Look of the vampire

- The face is carved, not built up, so nothing overhangs: slanted eye sockets, a heart
  nose, a mouth pocket, teeth grooves and fangs that are two lines wide at the tip.
- The black cape and the high collar are plates on the back plane, exactly `CAPE_T` thick.
  They make the figure wider than the ribcage: `COLLAR_HW` (17.4 mm) is the real half width,
  `FIG_HW` (12.8 mm) is only the ribcage.
- Use `vampire.coloured(theta)` and `assembly.scene_parts(s)` when you need coloured parts;
  do not split the vampire or the lid again yourself.
- Judge every change on the hero view: sitting at 70°, seen from the feet
  (`render.FROM_FEET`). Do not change `_wing`'s hub, `_lever` or `_stub`: they are part of
  the mechanism.

## Mechanism (do not break it)

- Two nails through the lid carry pins at `PIN_H` above the hip axis. The pins push the
  head-side face of two pelvis levers.
- There is a dwell of about 54 mm, then the vampire rises over about 28 mm.
- Gravity brings the vampire back. The pressure angle must stay ≤ 35°.
- A dovetail rail at the foot end guides the lid and holds it down after 20 mm. It also
  gives hard stops at `s=0` and `s=S_MAX`.
- The hip stubs have two flats, so they work as a bayonet: they go into the 45° bearing
  slot only when the vampire is sitting at about 45°. Lying down, the mouth (`SNAP`
  narrower than the stubs) keeps them in. `SNAP` must stay > 0.

## Layers and lines (0.4 mm nozzle, 0.2 mm layers)

- In its print position, **every flat horizontal face must sit on a layer boundary**
  (k × `LAYER`). Use `P.snap_up()` for derived heights. `tests/test_layers.py` scans all
  the parts.
- Thin walls are a whole number of lines: use `P.lines(n)`. For example
  `WALL = lines(4)` gives 2 perimeters on each side, with no gap fill.
- Gaps and grooves must be at least `LINE_W` wide, and raised strokes at least 85 % of
  `LINE_W` (Arachne's minimum line width).
- Two plates have a colour change. Lid: `P.layer_top(LID_T)` = 5.20 mm, to orange.
  Vampire: `P.layer_top(CAPE_T)` = 1.80 mm, to white. The cape and the collar are exactly
  `CAPE_T` thick and print black. `slicer.py` reads the planned heights from each 3MF and
  checks the real G-code against `export.PLANNED_M600`, not against the 3MF it is checking.

## Checks after any geometry change

1. Run `uv run pytest`. It covers collisions at 25 lid positions, nail–lever contact, the
   lid gap (≥ 2 mm), bayonet insertion, hip retention, printability, watertight STLs, the
   layer grid, floating islands (every layer rests on the one below), the lid's lead-in
   ramp, the lettering stroke width and the 3MF plates.
2. Run `uv run python -m vampire_coffin.export`. Every part must print `OK`.
3. Render and look at the images: `render.render(scene(s), path, ...)`.
4. Compare the part volumes with the previous run. A boolean that fails **silently** can
   halve a part without any error.

## 3MF and PrusaSlicer notes

- PrusaSlicer reads `Metadata/Prusa_Slicer_custom_gcode_per_print_z.xml` even from a 3MF
  without print settings. That is how the M600 travels with the plates.
- The CLI crashes on `--export-3mf` without a display (it renders a thumbnail with
  OpenGL). So `slicer.py` slices to text G-code instead. It copies the
  `; prusaslicer_config` block into `Metadata/Slic3r_PE.config` and sets
  `binary_gcode = 1` again.
- The MK4 profile writes binary G-code. Use `--no-binary-gcode` when you need to read the
  G-code.
- Do not put the box and the lid on the same plate: the lid's M600 would turn the box
  walls orange.
- The MK4 profiles build supports only inside support enforcers, so a normal slice never
  shows a missing support. `slicer.py` slices once more with
  `--support-material --support-material-auto --dont-support-bridges`; the result must have
  no `;TYPE:Support` extrusions.
- Do not rely on PrusaSlicer recognising a bridge: a flat bar between two mounts got
  support towers on one side of the coffin. Prefer 45° undersides (see `box._wall_relief`).

## build123d gotchas we hit

- `Box(..., align=None)` puts the box's **corner** at the origin, not its centre.
- With sketches on `Plane.XZ`, the order of the points decides the extrude direction.
  Pass `dir=` to `extrude`.
- Ellipsoids centred on the vampire's back plane make other booleans fail (their poles
  touch other faces). Always use `vampire._ellipsoid()`: it turns the poles along x and
  sinks the centre by `SINK`.
- `split()` can return a list. `render` accepts lists.
- **Always pass `dir=UP` when you extrude a sketch in `vampire.py`.** A polygon drawn
  clockwise has a downward normal, so it extrudes downwards. A clockwise nose triangle once
  cut straight through the skull, and the fangs extruded into nothing.
- Make ellipsoids with `shapes.ellipsoid()` (poles on the x axis) and place the poles
  outside the final part.
- Never cut with a sphere or a cone where its pole or apex ends up on a visible surface
  (dimples, eye sockets). The STL gets degenerate triangles and non-manifold edges there.
  Keep poles outside the part (see the eye sockets), or leave the detail out.
- Cut overlapping 2D shapes one at a time. One cutting tool made of overlapping pieces left
  doubled edges on the floor of the nose cut.
- Text must use the bundled font (`src/vampire_coffin/fonts/PirataOne-Regular.ttf`). If
  the file is missing, `Text` silently uses a system font, so `lid.py` raises an error at
  import instead.
- `make_box`, `make_lid`, `make_nail` and `make_vampire` are cached (`functools.cache`).
  Never change a returned part in place. Transform it (`Pos(...) * part`) or combine it
  (`part & region`); both give you a new object.
- Grown profiles (clearances) must move every edge by the clearance at right angles. See
  `box.rail_points`: on a 45° flare, a naive vertical shift gives √2 times the gap.
- A sharp-corner offset (`Kind.INTERSECTION`) moves corners further than edges (miter).
  A 45° chamfer or loft must rise by `outline.max_miter()`, not by the offset, or the
  corners overhang.
- A retaining lip over a horizontal hole is a ceiling, so it needs support. The hip bearing
  keeps its only lip on the side that faces up (head side). The foot-side wall is tangent
  to the hole at 45°.

## Git

Do not commit or push unless the owner asks.
