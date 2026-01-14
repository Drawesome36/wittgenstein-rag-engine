#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificación crítica: Asegurar que NO existan chunks > 30,000 caracteres
"""
import json
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("=" * 80)
print("VERIFICACIÓN DE TAMAÑOS DE CHUNKS")
print("=" * 80)
print()

# Leer corpus
chunks = []
with open('wittgenstein_corpus_clean.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        chunks.append(json.loads(line))

print(f"Total de chunks: {len(chunks)}")
print()

# Analizar distribución de tamaños
sizes = [len(c['content']) for c in chunks]
sizes_sorted = sorted(sizes, reverse=True)

print("DISTRIBUCIÓN DE TAMAÑOS:")
print(f"  - Mínimo: {min(sizes):,} chars")
print(f"  - Promedio: {sum(sizes) // len(sizes):,} chars")
print(f"  - Mediana: {sizes_sorted[len(sizes_sorted)//2]:,} chars")
print(f"  - Máximo: {max(sizes):,} chars")
print()

# Verificar chunks que exceden límites críticos
CRITICAL_LIMIT = 30000  # Límite duro
WARNING_LIMIT = 25000   # Límite objetivo

critical_chunks = [c for c in chunks if len(c['content']) > CRITICAL_LIMIT]
warning_chunks = [c for c in chunks if WARNING_LIMIT < len(c['content']) <= CRITICAL_LIMIT]

print("VERIFICACIÓN DE LÍMITES:")
print(f"  ✓ Chunks < {WARNING_LIMIT:,} chars: {len([s for s in sizes if s <= WARNING_LIMIT]):,}")
print(f"  ⚠ Chunks entre {WARNING_LIMIT:,} y {CRITICAL_LIMIT:,} chars: {len(warning_chunks):,}")
print(f"  ✗ Chunks > {CRITICAL_LIMIT:,} chars (BLOCKER): {len(critical_chunks):,}")
print()

if critical_chunks:
    print("=" * 80)
    print("🚨 BLOCKING ISSUES DETECTADOS - CHUNKS > 30,000 CHARS")
    print("=" * 80)
    for i, chunk in enumerate(critical_chunks[:10], 1):
        size_kb = len(chunk['content']) / 1024
        print(f"\n{i}. {chunk['source_file']}")
        print(f"   Tamaño: {len(chunk['content']):,} chars ({size_kb:.1f} KB)")
        print(f"   Proposición: {chunk['proposition_id']}")
        print(f"   Chunk part: {chunk.get('chunk_part', 'N/A')}")
        print(f"   Preview: {chunk['content'][:80]}...")
    print()
    print(f"❌ FAILED: {len(critical_chunks)} chunks exceden el límite de embedding")
    sys.exit(1)
else:
    print("=" * 80)
    print("✅ PASSED: No hay chunks > 30,000 caracteres")
    print("=" * 80)
    print()

    # Mostrar top 10 chunks más grandes (que sí pasaron)
    print("TOP 10 CHUNKS MÁS GRANDES (todos dentro del límite):")
    print("-" * 80)

    chunks_sorted_by_size = sorted(chunks, key=lambda x: len(x['content']), reverse=True)
    for i, chunk in enumerate(chunks_sorted_by_size[:10], 1):
        size = len(chunk['content'])
        chunk_part = chunk.get('chunk_part', None)
        part_info = f" [parte {chunk_part}]" if chunk_part else ""
        print(f"{i}. {size:>6,} chars | {chunk['source_file'][:50]}{part_info}")
        print(f"           Prop: {chunk['proposition_id']} | Period: {chunk['period']}")

    print()
    print("🎯 Corpus listo para indexación vectorial")
    print(f"   - Total chunks: {len(chunks):,}")
    print(f"   - Todos bajo el límite de 8,192 tokens (~32,000 chars)")
    print(f"   - Máximo chunk: {max(sizes):,} chars")
