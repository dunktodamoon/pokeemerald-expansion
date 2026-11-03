#!/usr/bin/env python3
"""Assemble the opening lines and the fullname Han set, and check encoding."""
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
subprocess.run([sys.executable, str(ROOT / 'tools/chinese_font/generate.py'), '--check'], check=True)
subprocess.run(['make', '-C', str(ROOT / 'tools/preproc')], check=True)

OPENING_PREFIX = '一三上不个也乱了从伙伴住你儿先再出别到前力动北厚去可吗吧回图在外大好子存它守完宫就岚差己带影往很得急性想慢我手打找拿挑撑收散时是更有木杉来档楚段比气水沉没清火点的看眼着硬稚稳空站累缘耐能脚自行要见记走足跃跑路过还这进选道都里重鉴门雾靠面驿鱼鸡，'
# Han that PR #3 adds. Sixteen of these are already in the opening prefix.
REQUIRED_HAN = '东九云五人仙令依侠儿元入全分剑南古台吒吟咬善四国城增墟外多大天头如妖嫂子孙孩客寨尤山岩巨广庄应建开归御怪恋意戬持撼敖斧星有木机杉李杨杵极柱栖楚武毛水波泽流海涧港溪演灵炉炎焰照牛犼猪玄王珠琉璃目眼石破碧神祭程站符精红缘翁翅老虎虫蚩蛙蛟观诀赤逆通道邺野金锤镇镜长门闻阁陨隐雷雾青靖风馆马驿魂魔鹏鼓龙'

charmap_path = ROOT / 'charmap.txt'
preproc = str(ROOT / 'tools/preproc/preproc')
text = charmap_path.read_text()
base, generated = text.split('@ BEGIN GENERATED CHINESE FONT')
generated = generated.split('@ END GENERATED CHINESE FONT')[0]
chars = (ROOT / 'graphics/fonts/chinese/characters.txt').read_text().strip()
assert chars.startswith(OPENING_PREFIX) and len(OPENING_PREFIX) == 122
assert len(chars) == len(set(chars))
assert set(REQUIRED_HAN) <= set(chars) and len(REQUIRED_HAN) == len(set(REQUIRED_HAN)) == 147
han_count = sum('\u4e00' <= c <= '\u9fff' for c in chars)
assert han_count == len(chars) - 1  # the opening fullwidth comma is the only non-Han glyph

assignments = re.findall(r"^'(.)' = (F[89]) ([0-9A-F]{2})$", generated, re.M)
assert [c for c, _, _ in assignments] == list(chars)
for index, (char, lead, suffix_text) in enumerate(assignments):
    suffix = int(suffix_text, 16)
    if index < 0xD0 - 0x20:
        assert lead == 'F9' and suffix == 0x20 + index, char
    else:
        assert lead == 'F8' and suffix == 0x20 + (index - (0xD0 - 0x20)), char
    assert suffix < 0xF7, char

# Stock arrows, emoji, and keypad icons stay clear of the generated suffixes.
base_f9 = {int(x, 16) for x in re.findall(r'= F9 ([0-9A-F]{2})(?:\s|$)', base)}
base_f8 = {int(x, 16) for x in re.findall(r'= F8 ([0-9A-F]{2})(?:\s|$)', base)}
used_f9 = {int(suffix, 16) for _, lead, suffix in assignments if lead == 'F9'}
used_f8 = {int(suffix, 16) for _, lead, suffix in assignments if lead == 'F8'}
assert not (used_f9 & base_f9) and not (used_f8 & base_f8)
assert used_f9 and max(used_f9) < 0xD0 and min(used_f9) >= 0x20
assert not used_f8 or (max(used_f8) < 0xF7 and min(used_f8) >= 0x20)

mapping = {c: bytes((0xF9 if i < 0xB0 else 0xF8, 0x20 + (i if i < 0xB0 else i - 0xB0)))
           for i, c in enumerate(chars)}
# 0xB0 is 176, the F9 20..CF capacity.
assert all(mapping[c] == bytes((int(lead, 16), int(suffix, 16)))
           for c, lead, suffix in ((a[0], a[1], a[2]) for a in assignments))
singles = {}
for line in base.splitlines():
    match = re.match(r"^'(.)'\s+=\s+([0-9A-F]{2})\s*$", line.split('@')[0].rstrip())
    if match:
        singles[match.group(1)] = bytes((int(match.group(2), 16),))
mapping.update(singles)
mapping['$'] = bytes((0xFF,))


def encoded(path):
    strings = re.findall(r'\.string "(.*)"', path.read_text())
    assert strings, path
    for line in strings:
        unknown = [c for c in line if c not in mapping]
        assert not unknown, f'{path.name} unmapped: {unknown}'
    return strings, b''.join(mapping[c] for line in strings for c in line)


def assemble(fixture, old_charmap_rejects):
    strings, expected = encoded(fixture)
    with tempfile.TemporaryDirectory() as directory:
        tmp = Path(directory)
        if old_charmap_rejects:
            old = tmp / 'old-charmap.txt'
            old.write_text(base)
            failed = subprocess.run([preproc, str(fixture), str(old)], capture_output=True)
            assert failed.returncode != 0 and old_charmap_rejects in failed.stderr, failed.stderr.decode()
        result = subprocess.run([preproc, str(fixture), str(charmap_path)], check=True, capture_output=True)
        actual = bytes(int(x, 16) for line in result.stdout.decode().splitlines()
                       if line.strip().startswith('.byte ') for x in re.findall(r'0x([0-9A-F]{2})', line))
        assert actual == expected, fixture.name
        asm = tmp / 'fixture.s'
        asm.write_bytes(result.stdout)
        obj = tmp / 'fixture.o'
        if shutil.which('arm-none-eabi-as'):
            command = ['arm-none-eabi-as', '-mcpu=arm7tdmi', str(asm), '-o', str(obj)]
        elif shutil.which('clang'):
            command = ['clang', '--target=arm-none-eabi', '-mcpu=arm7tdmi', '-c', str(asm), '-o', str(obj)]
        else:
            sys.exit('Install arm-none-eabi-as or clang to complete the ARM assembly check.')
        subprocess.run(command, check=True)
        elf = obj.read_bytes()
        assert elf[:4] == b'\x7fELF' and int.from_bytes(elf[18:20], 'little') == 40
    return len(strings), len(actual)


opening_n, opening_bytes = assemble(ROOT / 'tests/chinese_font/dialogue.s', b'U+96FE')
assert opening_n == 34
coverage_n, coverage_bytes = assemble(ROOT / 'tests/chinese_font/coverage.s', b'U+4E1C')
coverage_han = {c for line in re.findall(r'\.string "(.*)"', (ROOT / 'tests/chinese_font/coverage.s').read_text())
                for c in line if '\u4e00' <= c <= '\u9fff'}
assert coverage_han == set(REQUIRED_HAN)
page2 = sum(1 for _, lead, _ in assignments if lead == 'F8')
print(f'PASS: {len(chars)} glyphs ({han_count} Han, {page2} on F8); '
      f'opening {opening_n} lines/{opening_bytes} bytes; '
      f'fullname coverage {coverage_n} strings/{coverage_bytes} bytes; both assemble to ARM ELF.')
