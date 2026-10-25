# Printables listing — Nosferatu's Coffin

Copy the parts below into the Printables form. Numbers come from PrusaSlicer 2.9.6
(Prusa MK4, 0.4 mm nozzle, 0.20mm STRUCTURAL, Prusament PETG).

---

## Title

Nosferatu's Coffin — slide the lid and the vampire sits up

## Summary (short text under the title)

Pull the lid towards you and the Count wakes up: he sits up and stares at you over the
lid. Five parts, no supports, colour changes already set.

## Tags

halloween, coffin, vampire, dracula, nosferatu, skeleton, mechanism, kinetic, moving parts,
candy box, toy, gift, parametric, build123d, petg, prusa, mk4, multicolor, colour change,
no supports

## Category

Toys & Games › Other (or Seasonal Designs › Halloween)

## License

Creative Commons — Attribution — Share Alike (CC BY-SA 4.0)

---

## Description

### The idea

A classic six-sided coffin with a sliding lid. The vampire inside is fast asleep.

Pull the lid towards you. For the first half of the way nothing happens: the lid only
uncovers his head. Then the vampire sits up, slowly and stiffly, like Count Orlok in
*Nosferatu* (1922). At the end he looks straight at you over the lid. Push the lid back and
he lies down again.

The black cape, the high collar and the fangs make it clear who he is. There is also a
small candy stash at his feet, under the lid.

### How it works

- **Hip joint.** The skeleton turns around his hips. Two stubs on the pelvis sit in a
  bearing block, with a bayonet fit: they only go in when he is half sitting up.
- **Levers.** Two levers stand up from the pelvis. The lid always covers them.
- **Coffin nails.** Two square nails go through the lid. Each nail has a pin underneath.
  When you pull the lid, the pins reach the levers after 54 mm and push them: the vampire
  sits up to 70°.
- **Gravity.** When you push the lid back, his own weight takes him back down.
- **Dovetail rail.** A straight rail at the foot end keeps the lid straight and holds it
  down, so it cannot tip over when it is open. There are hard stops at both ends.
- When the lid is closed, you can lift it off to reach the candy stash.

The pictures with a cut-away side show the nail pushing the lever.

### Features

- Five printed parts: coffin, lid, vampire and two nails. No glue is needed (a drop is
  fine for the nails).
- **No supports.** PrusaSlicer does not add any, even with automatic supports turned on.
- **Colour changes already set** in the 3MF files: the lid's cross and lettering turn
  orange, and the vampire has a black cape behind white bones. One extruder is enough.
- **Designed for 0.2 mm layers and 0.45 mm lines.** Every flat surface sits exactly on a
  layer, and the walls are a whole number of lines, so nothing gets rounded away.
- **Tolerance coupon** included: test the three fits in less than an hour before you print
  the real thing.
- **Fully parametric source code** (Python and build123d) with automatic tests for the
  mechanism, the print layers and the files.

---

## Print settings

| | |
|---|---|
| Printer | Prusa MK4 (Input Shaper firmware). Any printer with a 165 × 70 mm bed area works. |
| Nozzle | 0.4 mm |
| Profile | 0.20mm STRUCTURAL (0.2 mm layers) |
| Material | Prusament PETG (PLA also works) |
| Supports | none |
| Sheet | textured or satin (PETG sticks too much to smooth PEI) |

| File | Parts | Colours | Time | Filament |
|---|---|---|---|---|
| `plate_1_black_box_and_nails` | coffin + 2 nails | black | 3 h 08 min | 68 g |
| `plate_2_lid_black_then_orange` | lid | black, then orange at 5.20 mm | 1 h 01 min | 28 g |
| `plate_3_vampire_black_then_white` | vampire | black, then white at 1.80 mm | 40 min | 9 g |
| `coupon_all_pieces` | tolerance coupon (optional) | any, one colour | 47 min | 12 g |

The whole coffin takes about 4 h 50 min and 105 g of filament.

### Which files to use

- **PrusaSlicer projects (`projects/*.3mf`) — easiest.** The MK4 settings and the colour
  changes are already loaded. Open, slice, print.
- **3MF plates (`*.3mf`).** The same plates without print settings, but with the colour
  changes. Use them with your own printer profile.
- **STL files.** One file per part, already in its print position. Add the colour changes
  yourself (see below).

### Colour changes (only needed with the STL files)

In the PrusaSlicer preview, move the vertical slider to the layer and click the **+**:

- **Lid:** at **5.20 mm** (start black, then orange). The cross, the border and R.I.P.
  come out orange.
- **Vampire:** at **1.80 mm** (start black, then white). The cape and the collar stay
  black; the bones are white.

---

## Before you print: the tolerance coupon

Printers and materials are all a bit different. The coupon pieces are cut from the real
parts, so if they fit, the coffin fits.

1. **Hip joint.** Tilt the pelvis to about 45° and push the stubs into the slanted slot.
   Lay it down: it should stay in, turn freely and fall back on its own.
2. **Rail.** Slide the lid piece onto the rail from the wide end. It should slide smoothly
   and not lift off.
3. **Nail.** Press the nail into its hole. It should hold firmly.

If a fit is too tight or too loose, the source code lets you change the clearances in one
file (`params.py`).

## Assembly

1. Hold the vampire half sitting up (about 45°). Push the hip stubs into the slanted slot,
   towards the feet and down. Lay him on the pillow: the bayonet locks him in.
2. Press the two nails into the holes at the head end of the lid, pins pointing inwards.
3. Put the lid on the coffin in the closed position, with the rail in the slot underneath.
4. Pull the lid towards you. After about 54 mm the vampire starts to sit up.

Tips:

- The front faces of the two levers print as an overhang. If they are rough, sand them
  lightly so the nails slide well.
- If a nail is loose, a drop of glue is fine.
- Keep the coffin level when you open it: gravity brings the vampire back.

## Remix it

The model is written in Python with [build123d](https://github.com/gumyr/build123d). Every
size and clearance is in one file. The tests check that nothing collides at 25 positions of
the lid, that every layer rests on the one below, and that the colour changes are on the
right layers.

Source code: <GitHub link — add it after the repository is public>

## Credits

- Design and code: CC BY-SA 4.0.
- Lettering font: *Pirata One* by Rodrigo Fuenzalida and Nicolas Massi, SIL Open Font
  License.

---

## Upload checklist

- [ ] Cover photo: from the feet, the vampire sitting up (see `shot-list.md`)
- [ ] Other photos, then the renders: `exploded.png`, `mechanism_*.png`, `sit_up.gif`,
      `mechanism.gif`
- [ ] Files: `out/3mf/projects/*.3mf`, `out/3mf/*.3mf`, `out/stl/*.stl`,
      `out/3mf/assembly_preview.3mf`
- [ ] License: CC BY-SA 4.0
- [ ] Enter the contest: Halloween 2026: Make It Move
- [ ] Publish by 31 October (the contest closes on 1 November)
