# First playable build

English placeholder opening for Wushan Station and the Wushan Outskirts. Approved Chinese display names are in the string sources (雾杉驿站, 南极仙翁, 野猪 / 海毛虫 / 巨蛙). `charmap.txt` is unchanged, so those glyphs do not assemble until the separate Chinese-font track lands.

## How to build

From the repository root, on Ubuntu:

```console
sudo apt install build-essential binutils-arm-none-eabi gcc-arm-none-eabi libnewlib-arm-none-eabi git libpng-dev python3
make -j$(nproc)
```

This run used `make -j4` with `arm-none-eabi-gcc (15:13.2.rel1-2) 13.2.1 20231009`. `DEVKITARM` was unset. The Makefile uses `arm-none-eabi-*` from `PATH`.

A commercial Emerald ROM is not an input. Do not download one.

## Artifact

| | |
|---|---|
| Path | `pokeemerald.gba` at the repository root |
| Copy on the build machine | `/opt/cursor/artifacts/pokeemerald-wushan.gba` |
| Size | 33554432 bytes |
| Header | `POKEMON EMER`, game code `BPEE`, maker `01`, revision 0 |
| SHA-256 | `f151fd69ed9ee2c9cae0d791947a33cf06a978026b83f0b583fdc0fcb59f06dc` |

`*.gba` is gitignored. Linker usage for this ROM:

```text
Memory region         Used Size  Region Size  %age Used
           EWRAM:      226416 B       256 KB     86.37%
           IWRAM:       28372 B        32 KB     86.58%
             ROM:    26747800 B        32 MB     79.71%
```

mGBA 0.10.2 with its high-level BIOS kept this ROM running for 6 seconds (`timeout` exit 124). No Nintendo BIOS file was used.

## How to test in mGBA

1. `make -j$(nproc)`
2. Open `pokeemerald.gba` in mGBA. Do not supply a Nintendo BIOS.
3. Title screen, choose **New Game**. The Birch speech and the truck ride are skipped. The player is male, named `GUEST`, and fades in inside Wushan Station.
4. The narration plays once (`intro_seen`). Talk to the scientist (Lan) and pick Treecko, Torchic, or Mudkip. That sets `talked_lan` and `got_starter` and gives five Poké Balls.
5. Walk up to the north door before that gift. The guard stops you. After the gift, the same tiles let you through. Talk to the guard for the pass lines.
6. The woman (You) and the little boy (Doudou) repeat their lines any time.
7. The north door warps to the south edge of the Wushan Outskirts. Tall grass uses the framework land encounters (Wurmple, Poochyena, Zigzagoon, levels 2–3). Battle, catch, and save are the stock systems. Walk back onto the south tiles to return to the station. A white-out returns to the station as well.

SELECT on the title screen is the stock quickstart and also enters this warp, because new games no longer run the truck cutscene.

## Maps

| English name | Map constant | Group | Layout | Tilesets |
|---|---|---|---|---|
| Wushan Station (雾杉驿站) | `MAP_WUSHAN_STATION` | `gMapGroup_Wushan` (group 75, map 0) | `LAYOUT_WUSHAN_STATION` | `gTileset_Building` + `gTileset_GenericBuilding` |
| Wushan Outskirts (雾杉外缘) | `MAP_WUSHAN_OUTSKIRTS` | `gMapGroup_Wushan` (group 75, map 1) | `LAYOUT_WUSHAN_OUTSKIRTS` | `gTileset_General` + `gTileset_Petalburg` (Route 101 block data) |

Map section names: `MAPSEC_WUSHAN_STATION` (`WUSHAN STATION`), `MAPSEC_WUSHAN_OUTSKIRTS` (`WUSHAN OUTSKIRTS`).

Player spawn and white-out point: Wushan Station (7, 8). `HEAL_LOCATION_WUSHAN_STATION`.

## Flags

| Script name | Constant | Value |
|---|---|---|
| `intro_seen` | `FLAG_INTRO_SEEN` (`FLAG_UNUSED_0x020`) | `0x20` |
| `talked_lan` | `FLAG_TALKED_LAN` (`FLAG_UNUSED_0x021`) | `0x21` |
| `got_starter` | `FLAG_GOT_STARTER` (`FLAG_UNUSED_0x022`) | `0x22` |

`intro_seen` is set when the narration finishes. `talked_lan` and `got_starter` are set together when Lan's gift succeeds.

## NPCs

Palette tags are the ones already bound to each graphic.

| NPC | Graphic | Palette tag | Palette slot |
|---|---|---|---|
| 南极仙翁 (speaker was Lan) | `OBJ_EVENT_GFX_SCIENTIST_1` | `OBJ_EVENT_PAL_TAG_NPC_3` (`0x1105`) | `PALSLOT_NPC_3` |
| You (驿站记录员·柚) | `OBJ_EVENT_GFX_WOMAN_1` | `OBJ_EVENT_PAL_TAG_NPC_1` (`0x1103`) | `PALSLOT_NPC_1` |
| Doudou (豆豆) | `OBJ_EVENT_GFX_LITTLE_BOY` | `OBJ_EVENT_PAL_TAG_NPC_4` (`0x1106`) | `PALSLOT_NPC_4` |
| Guard (门口守卫) | `OBJ_EVENT_GFX_BLACK_BELT` | `OBJ_EVENT_PAL_TAG_NPC_3` (`0x1105`) | `PALSLOT_NPC_3` |

Starters are `SPECIES_TREECKO`, `SPECIES_TORCHIC`, and `SPECIES_MUDKIP` at level 5. Battle, catch, Pokédex, and save code are unchanged.
