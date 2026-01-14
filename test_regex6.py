#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Línea de ejemplo del archivo
test_line = "**[1.](/w/index.php/Philosophische_Untersuchungen#1 \"Philosophische Untersuchungen\")** [San] Agustín, en las _Confesiones_ 1/8 [dice]:"

# Construir el patrón paso a paso
patterns = [
    r'^\*\*\[(\d+)\.',  # ** [ dígito .
    r'^\*\*\[(\d+\.)\]',  # Añadir ]
    r'^\*\*\[(\d+\.)\]\(',  # Añadir (
    r'^\*\*\[(\d+\.)\]\([^\)]+\)',  # Todo hasta ) (no vacío)
    r'^\*\*\[(\d+\.)\]\([^\)]+\)\*\*',  # Añadir ** al final
    r'^\*\*\[(\d+(?:\.\d+)*)\]\([^\)]+\)\*\*',  # Patrón completo con captura de decimales
]

for pattern in patterns:
    match = re.match(pattern, test_line)
    result = "[OK]" if match else "[FAIL]"
    print(f"{result} {pattern}")
    if match:
        print(f"      Matched: {repr(match.group(0)[:50])}")
        print(f"      Captured: {match.group(1)}")
    print()
