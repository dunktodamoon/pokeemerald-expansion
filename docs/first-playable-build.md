# First playable build

Stock `pokeemerald-expansion` ROM. The Wushan opening (雾杉驿站 / 雾杉外缘) is not in this binary. Map and event wiring is a follow-up; the blocker is recorded below.

## How to build

From the repository root, on Ubuntu, install the packages named in `docs/install/linux/UBUNTU.md`, then build:

```console
sudo apt install build-essential binutils-arm-none-eabi gcc-arm-none-eabi libnewlib-arm-none-eabi git libpng-dev python3
make -j$(nproc)
```

`make` with no extra target is the same ROM. This run used `make -j4`.

Observed toolchain: `arm-none-eabi-gcc (15:13.2.rel1-2) 13.2.1 20231009`. `DEVKITARM` was unset. The Makefile uses `arm-none-eabi-*` from `PATH` in that case. No separate devkitPro install and no agbcc step.

A commercial Emerald ROM is not an input. The graphics, tilemaps, and audio used by the build are already in this tree. Do not download a base ROM for this toolchain.

## Artifact

| | |
|---|---|
| Path | `pokeemerald.gba` at the repository root |
| Also copied on the build machine | `/opt/cursor/artifacts/pokeemerald.gba` |
| Size | 33554432 bytes (32 MiB, padded GBA image) |
| Header | `POKEMON EMER`, game code `BPEE`, maker `01`, revision 0 |
| SHA-256 | `7418499197377c7f8d90d092318d198324a189580099b98028a8f60de02f33b9` |

`*.gba` is gitignored (`.gitignore`), so the ROM is a build output and is not part of the commit.

Linker summary from this `make`:

```text
Memory region         Used Size  Region Size  %age Used
           EWRAM:      226420 B       256 KB     86.37%
           IWRAM:       28376 B        32 KB     86.60%
             ROM:    26751060 B        32 MB     79.72%
```

`tools/gbafix/gbafix` wrote the header. The complement byte is `0x72`. The 16-bit header checksum is `0x0000` because this project's gbafix leaves it at zero.

## Boot check

mGBA 0.10.2 (`/usr/games/mgba` from Ubuntu `mgba-sdl`), high-level BIOS, no Nintendo BIOS file:

- `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy` kept the process running for 8 seconds (killed by `timeout`, exit 124).
- A debugger `frame` loop of 60 frames advanced the cycle counter to about 16.6 million. The PC sat in the BIOS IRQ path (`0x188`), which is normal while the HLE BIOS services video interrupts.

That is a stock title-flow boot, not the Wushan opening.

## Why the opening is not in this ROM

Approved spoken lines are Chinese. `charmap.txt` already assigns all 256 byte values. Those lines use 121 distinct CJK characters, and this font has no free code point left. Putting the approved strings into a map script fails at assemble time. English stand-in lines were not added.

A follow-up has to add a CJK (or other multibyte) text path before those lines can appear. Battle, catch, Pokédex, and save code were left unchanged.

## Follow-up hooks

New game still starts in the moving truck. `WarpToTruck` in `src/new_game.c` calls `SetWarpDestination` for `MAP_INSIDE_OF_TRUCK`. The long Birch intro is `CB2_NewGameBirchSpeech_*` in `src/main_menu.c`, and it ends by entering `CB2_NewGame`.

Maps are registered in `data/maps/<Name>/map.json`, `data/layouts/layouts.json`, and `data/maps/map_groups.json`. Wild encounters live in `src/data/wild_encounters.json` (`land_mons` on an outdoor map). `givemon SPECIES_TREECKO` (and Torchic / Mudkip) is the existing give command; see `data/maps/LittlerootTown_ProfessorBirchsLab/scripts.inc`.

Planned maps, not created:

| Name | Role | Tilesets to reuse |
|---|---|---|
| 雾杉驿站 | Indoor start | `gTileset_Building` plus a house secondary such as `gTileset_BrendansMaysHouse` |
| 雾杉外缘 | North of the station, land encounters | `gTileset_General` plus a route/forest secondary such as `gTileset_Petalburg` (same pair as Route 101) |

Story flags from the approved dialogue table. They are not `#define`d yet. These unused permanent flags are free for them:

| Script name | Constant to claim | Value |
|---|---|---|
| `intro_seen` | `FLAG_UNUSED_0x020` | `0x20` |
| `talked_lan` | `FLAG_UNUSED_0x021` | `0x21` |
| `got_starter` | `FLAG_UNUSED_0x022` | `0x22` |

Temporary flags clear on every map load, so these three need permanent flags.

Overworld graphics, not placed. Palette tags are the ones already bound to each graphic in `src/data/object_events/object_event_graphics_info.h`.

| NPC | Graphic | Palette tag | Palette slot |
|---|---|---|---|
| 守林人·岚 | `OBJ_EVENT_GFX_SCIENTIST_1` | `OBJ_EVENT_PAL_TAG_NPC_3` (`0x1105`) | `PALSLOT_NPC_3` |
| 驿站记录员·柚 | `OBJ_EVENT_GFX_WOMAN_1` | `OBJ_EVENT_PAL_TAG_NPC_1` (`0x1103`) | `PALSLOT_NPC_1` |
| 豆豆 | `OBJ_EVENT_GFX_LITTLE_BOY` | `OBJ_EVENT_PAL_TAG_NPC_4` (`0x1106`) | `PALSLOT_NPC_4` |
| 门口守卫 | `OBJ_EVENT_GFX_BLACK_BELT` | `OBJ_EVENT_PAL_TAG_NPC_3` (`0x1105`) | `PALSLOT_NPC_3` |

岚 uses the adult male scientist sprite (lab coat, scholar). A ranger-leaning alternate already in the base set is `OBJ_EVENT_GFX_HIKER` with `OBJ_EVENT_PAL_TAG_NPC_1` (`0x1103`).

Starters stay base species: `SPECIES_TREECKO`, `SPECIES_TORCHIC`, `SPECIES_MUDKIP`.
