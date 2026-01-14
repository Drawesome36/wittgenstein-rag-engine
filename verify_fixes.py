#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificación final de los Blocking Issues corregidos
"""
import json
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("=" * 80)
print("VERIFICACIÓN FINAL DE BLOCKING ISSUES")
print("=" * 80)
print()

# Leer corpus
chunks = []
with open('wittgenstein_corpus_clean.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        chunks.append(json.loads(line))

# ==================== FIX 1: TAXONOMÍA ====================
print("FIX #1: TAXONOMÍA DE PERÍODOS")
print("-" * 80)

# Verificar que "Bemerkungen über die Farben" esté clasificado como LATE
farben_chunks = [c for c in chunks if 'Bemerkungen über die Farben' in c['source_file']]

if farben_chunks:
    periods_found = set(c['period'] for c in farben_chunks)
    print(f"Archivo: [aleman] Bemerkungen über die Farben.md")
    print(f"  - Chunks totales: {len(farben_chunks)}")
    print(f"  - Períodos encontrados: {periods_found}")

    if periods_found == {'LATE'}:
        print(f"  ✅ CORRECTO: Todos los chunks clasificados como LATE")
    else:
        print(f"  ❌ ERROR: Encontrados períodos incorrectos: {periods_found}")
        sys.exit(1)

    # Mostrar muestra
    sample = farben_chunks[0]
    print(f"\n  Muestra (chunk 1):")
    print(f"    ID: {sample['id']}")
    print(f"    Period: {sample['period']}")
    print(f"    Proposition: {sample['proposition_id']}")
    print(f"    Content: {sample['content'][:100]}...")
else:
    print("  ⚠ WARNING: No se encontró el archivo 'Bemerkungen über die Farben'")

print()

# Verificar distribución general de períodos
print("Distribución de períodos en el corpus:")
periods_count = {}
for chunk in chunks:
    period = chunk['period']
    periods_count[period] = periods_count.get(period, 0) + 1

for period in ['EARLY', 'MIDDLE', 'LATE', 'GENERAL']:
    count = periods_count.get(period, 0)
    percentage = (count / len(chunks)) * 100
    print(f"  - {period:8s}: {count:,} chunks ({percentage:.1f}%)")

print()

# ==================== FIX 2: MEGA-CHUNKS ====================
print("FIX #2: MANEJO DE MEGA-CHUNKS")
print("-" * 80)

# Encontrar todos los chunks que fueron divididos (tienen chunk_part)
divided_chunks = [c for c in chunks if c.get('chunk_part') is not None]

print(f"Total de sub-chunks generados: {len(divided_chunks)}")
print()

if divided_chunks:
    # Agrupar por proposición original
    by_proposition = {}
    for chunk in divided_chunks:
        key = (chunk['source_file'], chunk['proposition_id'])
        if key not in by_proposition:
            by_proposition[key] = []
        by_proposition[key].append(chunk)

    print(f"Mega-chunks originales divididos: {len(by_proposition)}")
    print()

    print("Detalle de divisiones:")
    for i, ((source, prop_id), sub_chunks) in enumerate(by_proposition.items(), 1):
        total_chars = sum(len(c['content']) for c in sub_chunks)
        max_part = max(c['chunk_part'] for c in sub_chunks)
        print(f"\n{i}. {source[:50]}")
        print(f"   Proposición: {prop_id}")
        print(f"   Dividido en: {max_part} partes")
        print(f"   Tamaño total original: ~{total_chars:,} chars")
        print(f"   Tamaños de partes:")
        for part_chunk in sorted(sub_chunks, key=lambda x: x['chunk_part']):
            part_size = len(part_chunk['content'])
            print(f"     - Parte {part_chunk['chunk_part']}: {part_size:,} chars")

    print()

    # Verificar que ningún sub-chunk exceda el límite
    oversized = [c for c in divided_chunks if len(c['content']) > 30000]
    if oversized:
        print(f"  ❌ ERROR: {len(oversized)} sub-chunks aún exceden 30,000 chars")
        sys.exit(1)
    else:
        print(f"  ✅ CORRECTO: Todos los sub-chunks bajo el límite de 30,000 chars")

    # Mostrar el más grande
    largest_subchunk = max(divided_chunks, key=lambda x: len(x['content']))
    print(f"  ✅ Sub-chunk más grande: {len(largest_subchunk['content']):,} chars")
    print(f"     Archivo: {largest_subchunk['source_file'][:50]}")
    print(f"     Parte: {largest_subchunk['chunk_part']}")

else:
    print("  ⚠ INFO: No se generaron sub-chunks (ningún mega-chunk detectado)")

print()

# ==================== VERIFICACIÓN FINAL ====================
print("=" * 80)
print("RESUMEN DE VERIFICACIÓN")
print("=" * 80)

# Estadísticas finales
sizes = [len(c['content']) for c in chunks]
chunks_with_parts = len([c for c in chunks if c.get('chunk_part') is not None])

print(f"Total de chunks en corpus: {len(chunks):,}")
print(f"Chunks con subdivisión: {chunks_with_parts:,}")
print(f"Chunks sin subdivisión: {len(chunks) - chunks_with_parts:,}")
print()
print(f"Tamaño máximo de chunk: {max(sizes):,} chars")
print(f"Tamaño promedio: {sum(sizes) // len(sizes):,} chars")
print()

# Verificaciones críticas
critical_issues = []

# Check 1: Todos los chunks < 30,000
if max(sizes) >= 30000:
    critical_issues.append("Chunks > 30,000 chars detectados")

# Check 2: Bemerkungen über die Farben es LATE
if farben_chunks and not all(c['period'] == 'LATE' for c in farben_chunks):
    critical_issues.append("Bemerkungen über die Farben clasificado incorrectamente")

if critical_issues:
    print("❌ BLOCKING ISSUES PENDIENTES:")
    for issue in critical_issues:
        print(f"   - {issue}")
    print()
    sys.exit(1)
else:
    print("✅ TODOS LOS BLOCKING ISSUES RESUELTOS")
    print()
    print("Corpus listo para:")
    print("  • Indexación vectorial (Pinecone, ChromaDB, etc.)")
    print("  • Embeddings con OpenAI Ada-002, Cohere, etc.")
    print("  • RAG pipelines")
    print("  • Fine-tuning de LLMs")
    print()
    print("🎯 PRODUCCIÓN READY")
