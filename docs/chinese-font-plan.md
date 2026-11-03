# Chinese opening font unblock (Track B)

## Chosen approach

Reuse Emerald's existing two-byte extra-symbol page: `F9 xx` is decoded to
`0x100 | xx` by `RenderText` and `GetStringWidth`. A full single-byte charmap
does **not** mean that every extra-symbol slot is occupied. Reserve `F9 20` through
`F9 99` for the opening's 121 distinct Han characters plus `，` (122 glyphs).
The old arrows (`F9 00..1A`) and emoji (`F9 D0..FE`) remain intact. The two
existing punctuation aliases `。 = AD` and `？ = AC` remain intact, so in English
font mode they use the existing period and question-mark graphics.

The nine Latin font variants now dispatch these glyph IDs to a shared, fixed
12×12 Chinese bitmap font and report a width of 12 pixels. Glyph data uses the
existing four-tile, 2-bits-per-pixel format and `DecompressGlyphTile`, so text
colors, window printing, and control sequences use the normal renderer. Chinese
text uses the default English font mode; do not wrap it in `{JPN}`. The Japanese
font path remains unchanged. Braille and the special bold sprite renderer are
outside this opening-dialogue path. Narrow font selection does not shrink Han
glyphs; use explicit line breaks rather than relying on font fitting.

This adds 7,808 bytes of bitmap data (122 × 64), plus dispatch code, with no
extra persistent RAM buffer. No maps, events, battle, catch, or save code changes
are required. This is a finite opening font, not a general Unicode/GB2312 font.
There are 54 more slots before `F9 D0`; expanding past that needs a new page or
encoding design. Preserve the manifest order when extending the font so existing
encoded strings retain their glyph IDs. The current highest suffix is `99`, so
none of the suffix bytes can be mistaken for a text control or terminator by
byte-oriented string helpers. Re-audit those helpers before using suffixes at
or above `F7`, or before putting Chinese in fixed-size names/save fields.

## Investigation and alternatives

- [pret/pokeemerald text.c](https://github.com/pret/pokeemerald/blob/master/src/text.c)
  and [charmap.txt](https://github.com/pret/pokeemerald/blob/master/charmap.txt)
  show the Japanese font switch (`{JPN}` / `{ENG}`), separate Latin/Japanese
  graphics, and the `F9` extra-symbol page. The preprocessor already supports
  mapping a Unicode source character to multiple output bytes; no preprocessor
  modification is necessary. This checkout has the same useful extra-symbol
  mechanism, and its multibyte length/copy helpers already recognize `F9`.
- [rh-hideout-chinese/pokeemerald-expansion](https://github.com/rh-hideout-chinese/pokeemerald-expansion)
  has a larger GBA Chinese solution. Its
  [chinese_text.c](https://github.com/rh-hideout-chinese/pokeemerald-expansion/blob/master/src/chinese_text.c)
  recognizes lead bytes `01..1E` (excluding `06` and `1B`), trailing bytes
  through `F6`, and separate normal/small Chinese glyph banks. Its
  [text.c](https://github.com/rh-hideout-chinese/pokeemerald-expansion/blob/master/src/text.c)
  handles Chinese decoding in both rendering and width measurement. That is a
  useful model for full localization, but those lead bytes overlap this
  checkout's existing Latin characters. Importing that encoding would require
  broader text and string-helper migration; it is unnecessary for 121 Han.
- [francisagust198/pokeemerald-zh](https://github.com/francisagust198/pokeemerald-zh)
  describes an atlas/generated-header approach on a PC/SDL port. Its renderer
  and platform assumptions should not be transplanted into this GBA build.

The chosen approach keeps all existing byte mappings and text controls while
adding only the glyph coverage needed for this opening.

## Assets and regeneration

The font is a renamed subset, **Wushan Opening 12**, of
[Fusion Pixel Font 12px monospaced zh_hans, release 2026.10.25](https://github.com/TakWolf/fusion-pixel-font/releases/tag/2026.10.25).
The upstream archive is `fusion-pixel-font-12px-monospaced-bdf-v2026.10.25.zip`;
SHA-256: `d8788cf5ffd6a2dabec397c33c878261195fb9146cdb67d8afd418fe73db15bd`.
The source BDF subset and upstream OFL/copyright notices are checked in under
`graphics/fonts/chinese/`, including the bundled component notices. No font
installation, Python package, or network access is needed for regeneration.

From the repository root:

```sh
python3 tools/chinese_font/generate.py
python3 tools/chinese_font/check.py
```

`characters.txt` defines the stable glyph order. `opening-12.bdf` holds the
actual bitmaps, with ascent 10 and descent 2. The generator packs them into
`src/data/fonts/chinese.h` and updates only its marked block in `charmap.txt`.
Normal ROM builds consume these checked-in outputs automatically. For a bitmap
correction, edit the corresponding BDF glyph and regenerate. To add a character,
append it to the manifest, copy its `STARTCHAR..ENDCHAR` block from the upstream
zh_hans BDF into the subset, update the BDF `CHARS` count, and regenerate. Do not
silently substitute a blank/missing glyph. Keep OFL notices with redistributed
font assets. If the dialogue grows, update the compile fixture and its explicit
coverage counts in `check.py` as well.

`generate.py --check` detects stale generated files without rewriting them.
`check.py` builds the native project preprocessor, verifies that the original
charmap rejects `雾` (U+96FE), checks all 34 approved dialogue lines byte for byte,
checks allocation collisions, and assembles the fixture to an ARM ELF object.
It uses `arm-none-eabi-as`, or Clang's ARM assembler when GNU ARM tools are absent.
The fixture is `tests/chinese_font/dialogue.s`; it is not linked into gameplay.

## Swapping the English placeholders later

1. Merge this font branch and the independent English-placeholder map/event work.
2. Replace only the placeholder script text using the approved lines in
   `design/opening-dialogue-v1.md`. The compile fixture contains those same 34
   lines verbatim; it does not propose new dialogue. Use normal font mode, with
   `{ENG}` if the preceding script explicitly selected `{JPN}`.
3. Add explicit `\n`, `\l`, and `\p` breaks to fit the actual dialogue window.
   Budget 12 pixels per Han/comma and the existing punctuation widths; inspect
   the longest lines and scrolling in mGBA. Use `FONT_NORMAL` for opening text.
4. Translate choice labels, speaker labels, and map names only after adding any
   additional characters they need to the manifest. Coverage here is for the
   **spoken lines**, not all headings/names in the design document. Text buffers
   need two bytes per Han/comma plus controls and EOS; don't use character counts
   as byte capacities.
5. Run the font check, a full GNU ARM `make -j4`, and play through all three
   starter branches, repeat talks, and the gate. Review line wrapping, colors,
   cursor placement, and page/scroll behavior before removing placeholders.

## Validation on this branch

- Original charmap: fixture fails on U+96FE as expected.
- New charmap: all 34 lines assemble to ARM ELF, 549 encoded bytes including EOS.
- Generated files reproduce exactly; collision and 121-Han coverage checks pass.
- The actual C `DecompressGlyphTile` and Chinese dispatch helpers were compiled
  into a temporary host harness: all 122 decoded rasters matched the BDF pixels;
  range boundaries and Japanese-mode rejection passed.
- `src/text.c` compiled to an ARM7TDMI Thumb object with Clang after generating
  map/region constants and host preprocessing. This is a source/object check,
  not a full project GNU ARM build.
- Full ROM linking and mGBA visual/gameplay checks remain unverified on this
  machine, which has no GNU ARM toolchain installed. The stock build report in
  `docs/first-playable-build.md` predates this change and is not new validation.
