#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

# Línea de ejemplo del archivo
test_line = "**[1.](/w/index.php/Philosophische_Untersuchungen#1 \"Philosophische Untersuchungen\")** [San] Agustín, en las _Confesiones_ 1/8 [dice]:"

# Patrones a probar
pattern1 = r'^\*{0,2}\[(\d+(?:\.\d+)*)\]\([^\)]*\)\*{0,2}'
pattern2 = r'^\*{0,2}(\d+(?:\.\d+)*)\.*\*{0,2}\s+'

print("Línea de prueba:")
print(test_line)
print()

match1 = re.match(pattern1, test_line)
if match1:
    print(f"Pattern 1 matched: {match1.group(0)}")
    print(f"Captured proposition ID: {match1.group(1)}")
else:
    print("Pattern 1 did NOT match")

print()

match2 = re.match(pattern2, test_line)
if match2:
    print(f"Pattern 2 matched: {match2.group(0)}")
    print(f"Captured proposition ID: {match2.group(1)}")
else:
    print("Pattern 2 did NOT match")
