#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Línea de ejemplo del archivo
test_line = "**[1.](/w/index.php/Philosophische_Untersuchungen#1 \"Philosophische Untersuchungen\")** [San] Agustín, en las _Confesiones_ 1/8 [dice]:"

print("Línea de prueba:")
print(repr(test_line))
print()

# Probar diferentes patrones - el ** puede tener espacios después
patterns = [
    r'^\*\*\[(\d+(?:\.\d+)*)\]\([^\)]*\)\*\*\s*',  # ** con espacios opcionales después
    r'^\*{2}\[(\d+(?:\.\d+)*?)\]',  # Simplificar: solo capturar el número dentro de []
]

for i, pattern in enumerate(patterns, 1):
    print(f"Pattern {i}: {pattern}")
    match = re.match(pattern, test_line)
    if match:
        print(f"  [OK] MATCHED: {repr(match.group(0))}")
        print(f"  Captured ID: {match.group(1)}")
    else:
        print(f"  [FAIL] did NOT match")
    print()
