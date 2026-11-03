# Chinese font (Track B)

## Chosen approach

Reuse Emerald's existing two-byte text codes. `RenderText` and `GetStringWidth`
decode `F9 xx` to glyph id `0x100 | xx`. A full single-byte charmap does not mean
every extra-symbol slot is occupied.

Stock byte assignments stay where they are:

- arrows and UI symbols `F9 00..1A`
- emoji `F9 D0..FE`
- keypad icons `F8 00..0C`
- `。 = AD` and `？ = AC` (English period and question mark)
- `{JPN}` / `{ENG}` and the Japanese font graphics

Han and the fullwidth comma use the free suffixes on those same leads:

- `F9 20..CF` holds 176 glyphs. The original opening manifest stays at
  `F9 20..99` (122 glyphs: 121 Han plus `，`), so those codes do not move.
  The next 54 glyphs continue at `F9 9A..CF`.
- Further glyphs use `F8 20` upward. `F8` is already a two-byte lead for keypad
  icons. Suffixes `20..F6` are unused. They stop before `F7`, so a trail byte
  is not `CHAR_DYNAMIC`, a keypad lead, an extra-symbol lead, a prompt
  (`FA`/`FB`), an extended control (`FC`), a placeholder (`FD`), a newline
  (`FE`), or EOS (`FF`).

The opening set plus the fullname reskin is **253 glyphs**. That does not fit
in the 176 safe `F9` slots before emoji, which is why the keypad page is the
second bank. Safe capacity is 176 + 215 = 391 glyphs. Another encoding is only
needed past that.

`StringLength_Multibyte` and `StringCopyN_Multibyte` treat both `F8` and `F9`
as one character. The nine Latin font variants draw these glyph ids from one
shared 12×12 bitmap and report a width of 12. Narrow font selection does not
shrink Han; use explicit line breaks. Chinese text uses the default English
font mode. Do not wrap it in `{JPN}`.

Page-1 codes still fall through to the Japanese extra-symbol font when Japanese
mode is on, which is the previous opening-font behavior. Those slots were
unassigned, so existing Japanese strings do not use them. Page-2 codes have no
Japanese graphic. They still draw the Han bitmap in Japanese mode, instead of
indexing off the end of the Japanese font. Braille and the bold sprite renderer
are outside this path: braille skips an `F8` pair, and the bold renderer skips
both leads without drawing them.

Bitmap data is the existing four-tile, 2-bits-per-pixel format passed through
`DecompressGlyphTile`. 253 glyphs are 16,192 bytes, plus the dispatch code.
There is no extra persistent RAM buffer. No maps, events, battle, catch, or
save code changes.

## Coverage

Manifest order is the original opening string, then each added Han in Unicode
order. The fullname set required by PR #3 is these 147 Han, and all of them
are in the manifest (16 were already in the opening font, 131 are new):

东九云五人仙令依侠儿元入全分剑南古台吒吟咬善四国城增墟外多大天头如妖嫂子孙孩客寨尤山岩巨广庄应建开归御怪恋意戬持撼敖斧星有木机杉李杨杵极柱栖楚武毛水波泽流海涧港溪演灵炉炎焰照牛犼猪玄王珠琉璃目眼石破碧神祭程站符精红缘翁翅老虎虫蚩蛙蛟观诀赤逆通道邺野金锤镇镜长门闻阁陨隐雷雾青靖风馆马驿魂魔鹏鼓龙

The Dunk-approved 定稿 display names (places, NPCs, badges, HMs, items,
legendaries, starters) use no Han outside that list. The PR #3 string diff
adds exactly those 147 Han and no others. `东海龙王·敖广` uses the existing
middle dot (`U+00B7 = AF`), not a new glyph. `金吒&木吒` uses the stock
ampersand. Editorial notes and 建议 rows (for example 师长, 龟丞相, 傲来)
are not display strings and are not in this font.

`tests/chinese_font/dialogue.s` is the 34 opening lines.
`tests/chinese_font/coverage.s` is the 147 plus the 定稿 display names.
Neither object is linked into the ROM.

## Investigation and alternatives

- [pret/pokeemerald text.c](https://github.com/pret/pokeemerald/blob/master/src/text.c)
  and [charmap.txt](https://github.com/pret/pokeemerald/blob/master/charmap.txt)
  show the Japanese font switch, separate Latin/Japanese graphics, and the
  `F9` extra-symbol page. The preprocessor already maps one Unicode character
  to several output bytes. Multibyte length/copy helpers already recognized
  `F9`; they now recognize `F8` the same way.
- [rh-hideout-chinese/pokeemerald-expansion](https://github.com/rh-hideout-chinese/pokeemerald-expansion)
  uses lead bytes `01..1E` for a full localization. Those bytes are already
  Latin and kana here. Importing that encoding would move stock assignments.
  It is not required for this finite set.
- [francisagust198/pokeemerald-zh](https://github.com/francisagust198/pokeemerald-zh)
  targets a PC/SDL port. Its renderer is not used here.

Every single-byte value in this charmap is already assigned, aside from the
two-byte leads `F8`, `F9`, and `FC`. A new lead byte would have to steal a
stock character. Extending the two leads that the text walker already consumes
as a pair keeps punctuation, arrows, emoji, keypad icons, and Japanese mode
on their current bytes.

## Assets and regeneration

The font is **Wushan Han 12**, a renamed subset of
[Fusion Pixel Font 12px monospaced zh_hans, release 2026.10.25](https://github.com/TakWolf/fusion-pixel-font/releases/tag/2026.10.25).
The upstream archive is `fusion-pixel-font-12px-monospaced-bdf-v2026.10.25.zip`,
SHA-256 `d8788cf5ffd6a2dabec397c33c878261195fb9146cdb67d8afd418fe73db15bd`.
The source BDF subset and the Fusion Pixel / Galmuri / Ark Pixel / Cubic 11
notices are under `graphics/fonts/chinese/`. Regeneration does not need a font
package or network access.

From the repository root:

```sh
python3 tools/chinese_font/generate.py
python3 tools/chinese_font/check.py
```

`characters.txt` is the stable glyph order. `opening-12.bdf` holds the bitmaps
(ascent 10, descent 2). The generator writes `src/data/fonts/chinese.h` and
replaces only the marked block in `charmap.txt`. Normal ROM builds consume
those checked-in outputs. To add a character, append it to the manifest, copy
its `STARTCHAR..ENDCHAR` block from the upstream zh_hans BDF, update `CHARS`,
and regenerate. Do not substitute a blank glyph. Keep the OFL notices with the
font files. If the dialogue grows, add the line to a compile fixture and
extend `check.py`.

`generate.py --check` fails when a generated file is stale. `check.py` builds
the project preprocessor, checks that the original charmap still rejects `雾`
and `犼`, checks that the opening prefix and all 147 Han are assigned without
colliding with stock `F8`/`F9` suffixes, and assembles both fixtures to ARM ELF
with `arm-none-eabi-as` (or Clang's ARM assembler).

## Later string integration

1. Merge this font branch. The English Wushan opening on `master` does not
   depend on these glyphs.
2. A fullname reskin can then use the 定稿 display strings. It still needs its
   own line breaks. Budget 12 pixels per Han or fullwidth comma, and the
   existing widths for `·`, `&`, `。`, and `？`.
3. Text buffers need two bytes per Han or comma, plus controls and EOS. Do not
   treat a character count as a byte capacity.
4. Spoken lines that introduce Han outside this manifest still need those
   glyphs added here before they will assemble.

## Validation

`python3 tools/chinese_font/check.py` covers the generated files, the opening
lines (34 strings, 549 bytes), and the 147 Han plus the 定稿 display names.
On this branch that check reports 253 glyphs, 252 of them Han, 77 of them on
the `F8` page, and both fixtures assemble to ARM ELF.

`make -j4` with `arm-none-eabi-gcc 13.2.1 20231009` linked `pokeemerald.gba`
(32 MiB). SHA-256 `80bad0fe29195f53651a2fc98493a048f4c0dc901445d448ff366b0e939f0c6e`.
ROM usage was 26,764,768 bytes. mGBA 0.10.2, high-level BIOS, no Nintendo BIOS:
the expansion intro ran, New Game entered the Wushan Station interior, the
intro box appeared, and the process was still running afterward.
