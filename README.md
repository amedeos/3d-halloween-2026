# Nosferatu's Coffin 🧛

An entry for the Printables contest **[Halloween 2026: Make It Move](https://www.printables.com/contest/533-halloween-2026)**.

A classic six-sided coffin. **Pull the lid towards you (towards the feet)**. Halfway through the movement, the vampire skeleton sits up to 70° and stares at you over the lid. Push the lid back and he lies down again.

The vampire wears a black cape and a high collar, and he has fangs. He lies on a satin pillow on a quilted floor. There is a small candy stash at his feet.

The model is fully parametric. It is written in Python with [build123d](https://github.com/gumyr/build123d).

## How it works

- **Hip joint.** The vampire turns around his hips. Two stubs on the pelvis sit in a bearing block. The bearing slot is tilted 45° towards the head.
- **Levers.** Two levers stick up from the pelvis. The lid always covers them, so you never see them.
- **Coffin nails.** Two square nails go through the lid. Each nail has a pin at the bottom that pushes one lever.
  - For the first 54 mm, the pins touch nothing. The lid uncovers the head end, and the vampire stays lying down.
  - In the last 28 mm, the pins push the levers and the vampire sits up to 70°.
  - On the way back, gravity keeps the levers against the pins.
- **Dovetail rail.** The walls of a coffin are slanted, so they cannot guide a sliding lid. A straight rail in the middle of the foot end keeps the lid straight.
  - After 20 mm of travel, the rail also holds the lid down, so it cannot tip over when it is open.
  - There are hard stops at both ends.
  - When the lid is closed, you can lift it off. You need this to assemble the coffin and to reach the **candy stash** at the vampire's feet.

All the numbers (lever angles, lid travel, the 54 mm with no movement) come from `kinematics.py`. The tests check 25 lid positions: no parts collide, and the nails really push the levers.

## Requirements

- [uv](https://docs.astral.sh/uv/) and Python 3.14 (3.13 also works)
- `uv sync` installs build123d, trimesh and pillow

```sh
uv run pytest                              # kinematics, printable parts, collisions, 3MF files
uv run python -m vampire_coffin.kinematics # table: lid travel -> sit-up angle
uv run python -m vampire_coffin.export     # STL files (out/stl) and 3MF plates (out/3mf)
uv run python -m vampire_coffin.slicer     # optional, needs PrusaSlicer: times + projects
uv run python -m vampire_coffin.render     # listing images in out/render (no OpenGL needed)
uv run python -m vampire_coffin.render --gif  # ...plus the GIFs (sitting up, mechanism)
```

`export` exits with status 1 if a part has a problem. You can find every size and clearance in `src/vampire_coffin/params.py`.

## Printing

Prusa MK4 (Input Shaper firmware), **Prusament PETG** (PLA also works), 0.4 mm nozzle, **0.20mm STRUCTURAL** profile, **no supports**. PrusaSlicer confirms this: even with automatic supports turned on, it does not generate any. Use the textured or satin sheet: PETG sticks too much to the smooth PEI sheet.

There are three kinds of files. Use whichever you like:

- **`out/3mf/projects/*.3mf` — easiest.** PrusaSlicer projects with the MK4 + 0.20mm STRUCTURAL + Prusament PETG settings already loaded. The lid's colour change is already set.
- **`out/3mf/*.3mf`** — the same plates without print settings. They also include the colour change. Use them with any printer profile.
- **`out/stl/*.stl`** — one file per part, already in its print position.

| Plate (3MF) | Parts | Colour | Time* | Filament* |
|---|---|---|---|---|
| `plate_1_black_box_and_nails` | box + 2 nails | black | 3 h 08 min | 68 g |
| `plate_2_lid_black_then_orange` | lid | black, then orange at 5.20 mm | 1 h 01 min | 28 g |
| `plate_3_vampire_black_then_white` | vampire | black, then white at 1.80 mm | 40 min | 9 g |
| `coupon_all_pieces` | tolerance coupon | any, no colour change | 47 min | 12 g |
| `coupon_nail_gauge` | nail gauge (optional) | any | 14 min | 3 g |

\* PrusaSlicer 2.9.6 estimates (Prusament PETG, 0.20mm STRUCTURAL). The whole coffin takes about 4 h 50 min.

### Designed for 0.2 mm layers and 0.45 mm lines

The model follows the slicer grid, so nothing gets rounded away:

- **Layers.** In its print position, every flat horizontal face sits on a layer boundary (a multiple of 0.2 mm). Examples: the lid is 5.0 mm (25 layers), the relief 1.2 mm (6 layers), the floor 2.0 mm (10 layers), and the rail top is at 43.0 mm.
- **Colour changes.** The lid relief starts at 5.0 mm, so its first layer is printed from 5.0 to 5.2 mm, and the M600 goes before it (Z = 5.20 mm). The vampire's cape and collar are exactly 1.6 mm (8 layers) thick, so the bones start white at Z = 1.80 mm. PrusaSlicer's G-code confirms both.
- **Lines.** The walls are exactly 4 lines wide (1.67 mm): 2 perimeters on each side, with no gap fill. The rim band makes the top 6 lines wide.
- **Small details.** Gaps and grooves are at least one line wide, so they don't close up. The thinnest strokes of the lettering are wider than Arachne's minimum line, and the tips of the fangs are two lines wide.
- **No islands.** Every layer rests on the layer below. Nothing starts in mid-air, and all overhangs are 45° or steeper.

`tests/test_layers.py` checks all of this. If you change `LAYER` or `LINE_W` in `params.py`, the tests show which faces no longer fit the grid.

**Two parts need a colour change (M600).** The 3MF files already contain them. With the STL files, add them yourself: open the preview, move the vertical slider to the layer and click the **+**.

- **Lid:** at Z = 5.20 mm, from black to orange. The cross, the border and R.I.P. come out orange.
- **Vampire:** at Z = 1.80 mm, from black to white. The cape and the collar stay black.

`slicer.py` needs PrusaSlicer with the MK4 profiles installed. If `prusa-slicer` is not on your PATH, set `PRUSA_SLICER`, for example `PRUSA_SLICER="flatpak run com.prusa3d.PrusaSlicer"`.

### Print the tolerance coupon first (about 50 min)

Print `coupon_all_pieces.3mf` (or the `coupon_*.stl` files) in one colour. It has no colour change, so the print never pauses. The lid's colour change is tested on the real lid.

The `coupon_*.stl` files are pieces cut from the real parts. If they fit together, the coffin will fit together too.

1. **Hip joint** (`coupon_bearing` + `coupon_pelvis`)
   - It works like a bayonet. Tilt the pelvis to about 45°: the flat sides of the stubs now pass through the opening of the slot. Push them in along the slot; at the bottom they settle into the round hole.
   - Lay the pelvis down. It should stay locked, turn freely and fall back on its own.
   - Push a lever with your finger. The stubs must stay in the slot.
   - Too tight or too loose? Change `SNAP` or `CLR_STUB`. Keep `SNAP` above 0, or the vampire falls out when you tip the coffin (a test checks this).
2. **Rail** (`coupon_rail` + `coupon_lid_slide`)
   - Slide the lid piece onto the rail from the wide, open end. This is how the real lid moves.
   - It should slide smoothly, without wobbling, and it should not lift off.
   - Change `CLR_SLIDE` if needed.
3. **Nails** (`coupon_nail` + `coupon_lid_nails`)
   - Press the nail into the hole from the top. It should hold firmly, with the pin straight.
   - Too tight or too loose? Print `coupon_nail_gauge` (14 min): a strip with four holes, 0.05, 0.10, 0.15 and 0.20 mm wider per side, marked with 1 to 4 dots. Push a nail into each hole and set `CLR_NAIL` to the one that holds best. On our MK4 with Prusament PETG it was 0.10 mm (2 dots), the default. A drop of glue is also fine.

## Assembly

1. Hold the vampire half sitting up (about 45°). Push the hip stubs into the tilted slot (towards the feet and down). Then lay him on the pillow. The bayonet locks him in place.
2. Press the two nails into the holes at the head end of the lid. The pins must point inwards.
3. Put the lid on the coffin in the closed position. The rail goes into the slot under the lid.
4. Pull the lid towards the feet. After about 54 mm the vampire starts to rise. At the stop (82 mm) he sits at 70°.

If the lever faces come out rough (they are a 35° overhang), sand them lightly.

## License

- Model and code: **CC BY-SA 4.0** (see `LICENSE`).
- Font: *Pirata One*, SIL Open Font License (`src/vampire_coffin/fonts/PirataOne-OFL.txt`).
