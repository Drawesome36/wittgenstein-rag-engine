#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Línea de ejemplo del archivo
test_line = "**[1.](/w/index.php/Philosophische_Untersuchungen#1 \"Philosophische Untersuchungen\")** [San] Agustín, en las _Confesiones_ 1/8 [dice]:"

print("Primeros caracteres:")
for i, char in enumerate(test_line[:5]):
    print(f"  [{i}] = {repr(char)} (ord: {ord(char)})")
print()

# Probar patrones muy simples
patterns = [
    r'^\*',  # Un solo asterisco al inicio
    r'^\*\*',  # Dos asteriscos al inicio
    r'^\*\*\[',  # ** seguido de [
    r'^\*\*\[(\d+)',  # ** seguido de [ y dígitos
    r'^\*\*\[(\d+)\.',  # Con punto
]

for pattern in patterns:
    match = re.match(pattern, test_line)
    result = "[OK]" if match else "[FAIL]"
    print(f"{result} {pattern}")
    if match:
        print(f"      Matched: {repr(match.group(0))}")
