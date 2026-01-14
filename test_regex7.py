#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Líneas de ejemplo
test_lines = [
    "**[1.](/url)** Texto",
    "**[1.1](/url)** Texto",
    "**[1.2.3](/url)** Texto",
]

# Patrón correcto: capturar dígitos y puntos, pero el punto final es opcional
pattern = r'^\*\*\[(\d+(?:\.\d+)*)\.\]/\([^\)]+\)\*\*'

# Versión mejorada: el punto después de los números puede estar o no
pattern_better = r'^\*\*\[(\d+(?:\.\d+)*)\.?\]\([^\)]+\)\*\*'

print("Pattern mejorado:", pattern_better)
print()

for line in test_lines:
    match = re.match(pattern_better, line)
    if match:
        print(f"[OK] {line[:30]}")
        print(f"     Captured ID: {match.group(1)}")
    else:
        print(f"[FAIL] {line[:30]}")
    print()
