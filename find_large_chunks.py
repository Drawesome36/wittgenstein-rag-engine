#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open('wittgenstein_corpus_clean.jsonl', 'r', encoding='utf-8') as f:
    chunks = [json.loads(line) for line in f]

# Encontrar los 10 chunks más grandes
chunks_sorted = sorted(chunks, key=lambda x: len(x['content']), reverse=True)

print("TOP 10 CHUNKS MÁS GRANDES:")
print("=" * 80)
for i, chunk in enumerate(chunks_sorted[:10], 1):
    size_kb = len(chunk['content']) / 1024
    print(f"{i}. {chunk['source_file']}")
    print(f"   Tamaño: {size_kb:.1f} KB ({len(chunk['content'])} chars)")
    print(f"   Proposición: {chunk['proposition_id']}")
    print(f"   Preview: {chunk['content'][:100]}...")
    print()
