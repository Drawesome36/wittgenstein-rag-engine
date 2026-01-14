#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Leer primeras 10 líneas
with open('wittgenstein_corpus_clean.jsonl', 'r', encoding='utf-8') as f:
    chunks = [json.loads(line) for i, line in enumerate(f) if i < 10]

print("=" * 80)
print("MUESTRAS DEL CORPUS FINAL")
print("=" * 80)
print()

# Mostrar diferentes tipos
for i, chunk in enumerate(chunks[:5], 1):
    print(f"MUESTRA {i}:")
    print(f"  Archivo: {chunk['source_file']}")
    print(f"  Idioma: {chunk['language']} | Período: {chunk['period']}")
    print(f"  Proposición: {chunk['proposition_id']}")
    content_preview = chunk['content'][:250] + "..." if len(chunk['content']) > 250 else chunk['content']
    print(f"  Contenido: {content_preview}")
    print()
