#!/usr/bin/env python3
"""Compile approved dialogue to ARM ELF, and check the former failure and byte stream."""
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
subprocess.run([sys.executable, str(ROOT / 'tools/chinese_font/generate.py'), '--check'], check=True)
subprocess.run(['make', '-C', str(ROOT / 'tools/preproc')], check=True)
fixture = ROOT / 'tests/chinese_font/dialogue.s'
charmap = ROOT / 'charmap.txt'
preproc = str(ROOT / 'tools/preproc/preproc')
text = charmap.read_text()
base = text.split('@ BEGIN GENERATED CHINESE FONT')[0]
chars = (ROOT / 'graphics/fonts/chinese/characters.txt').read_text().strip()
assert len(chars) == 122 and sum('\u4e00' <= c <= '\u9fff' for c in chars) == 121
# No original extra-symbol assignment may overlap our new glyph page.
assert not any(0x20 <= int(x, 16) < 0x20 + len(chars)
               for x in re.findall(r'= F9 ([0-9A-F]{2})(?:\s|$)', base))
strings = re.findall(r'\.string "(.*)"', fixture.read_text())
assert len(strings) == 34
mapping = {c: bytes((0xF9, 0x20+i)) for i, c in enumerate(chars)}
# Preserve the existing Japanese punctuation aliases (English ? and period glyphs).
mapping.update({'。': bytes((0xAD,)), '？': bytes((0xAC,)), '$': bytes((0xFF,))})
expected = b''.join(mapping[c] for line in strings for c in line)
with tempfile.TemporaryDirectory() as directory:
    tmp = Path(directory)
    old = tmp / 'old-charmap.txt'
    old.write_text(base)
    failed = subprocess.run([preproc, str(fixture), str(old)], capture_output=True)
    assert failed.returncode != 0 and b'U+96FE' in failed.stderr, failed.stderr.decode()
    result = subprocess.run([preproc, str(fixture), str(charmap)], check=True, capture_output=True)
    actual = bytes(int(x, 16) for line in result.stdout.decode().splitlines()
                   if line.strip().startswith('.byte ') for x in re.findall(r'0x([0-9A-F]{2})', line))
    assert actual == expected
    asm = tmp / 'dialogue.s'
    asm.write_bytes(result.stdout)
    obj = tmp / 'dialogue.o'
    if shutil.which('arm-none-eabi-as'):
        command = ['arm-none-eabi-as', '-mcpu=arm7tdmi', str(asm), '-o', str(obj)]
    elif shutil.which('clang'):
        command = ['clang', '--target=arm-none-eabi', '-mcpu=arm7tdmi', '-c', str(asm), '-o', str(obj)]
    else:
        sys.exit('Install arm-none-eabi-as or clang to complete the ARM assembly check.')
    subprocess.run(command, check=True)
    elf = obj.read_bytes()
    assert elf[:4] == b'\x7fELF' and int.from_bytes(elf[18:20], 'little') == 40
print(f'PASS: original charmap rejects 雾; all 34 approved lines assemble to ARM ELF ({len(actual)} bytes).')
