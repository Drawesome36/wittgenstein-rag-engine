#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para inspeccionar muestras del corpus procesado
"""
import json
import sys

# Configurar salida UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def inspect_corpus(filepath='wittgenstein_corpus_clean.jsonl'):
    """Lee el corpus y muestra muestras representativas"""

    chunks = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            chunks.append(json.loads(line))

    print("=" * 80)
    print(f"INSPECCIÓN DEL CORPUS PROCESADO")
    print("=" * 80)
    print(f"Total de chunks: {len(chunks)}")
    print()

    # Encontrar muestras representativas
    propositional_samples = []
    prose_samples = []

    for chunk in chunks:
        if chunk['proposition_id'] and len(propositional_samples) < 3:
            # Solo agregar si el contenido es razonable (>50 chars)
            if len(chunk['content']) > 50:
                propositional_samples.append(chunk)

        if not chunk['proposition_id'] and len(prose_samples) < 3:
            # Solo agregar si el contenido es razonable y no tiene ruido wiki
            if len(chunk['content']) > 100 and '[Home]' not in chunk['content']:
                prose_samples.append(chunk)

    # Mostrar muestras proposicionales
    print("=" * 80)
    print("MUESTRAS DE CHUNKS PROPOSICIONALES")
    print("=" * 80)

    for i, chunk in enumerate(propositional_samples, 1):
        print(f"\nMUESTRA PROPOSICIONAL {i}:")
        print("-" * 80)
        print(f"ID: {chunk['id']}")
        print(f"Archivo: {chunk['source_file']}")
        print(f"Idioma: {chunk['language']}")
        print(f"Proposición: {chunk['proposition_id']}")
        print(f"Período: {chunk['period']}")
        print(f"Contenido ({len(chunk['content'])} chars):")
        content_preview = chunk['content'][:400] + "..." if len(chunk['content']) > 400 else chunk['content']
        print(f"{content_preview}")

    # Mostrar muestras de prosa
    print()
    print("=" * 80)
    print("MUESTRAS DE CHUNKS DE PROSA")
    print("=" * 80)

    for i, chunk in enumerate(prose_samples, 1):
        print(f"\nMUESTRA PROSA {i}:")
        print("-" * 80)
        print(f"ID: {chunk['id']}")
        print(f"Archivo: {chunk['source_file']}")
        print(f"Idioma: {chunk['language']}")
        print(f"Proposición: {chunk['proposition_id']}")
        print(f"Período: {chunk['period']}")
        print(f"Contenido ({len(chunk['content'])} chars):")
        content_preview = chunk['content'][:500] + "..." if len(chunk['content']) > 500 else chunk['content']
        print(f"{content_preview}")

    # Estadísticas adicionales
    print()
    print("=" * 80)
    print("ESTADÍSTICAS DETALLADAS")
    print("=" * 80)

    # Distribución de longitudes
    prop_lengths = [len(c['content']) for c in chunks if c['proposition_id']]
    prose_lengths = [len(c['content']) for c in chunks if not c['proposition_id']]

    if prop_lengths:
        print(f"\nChunks proposicionales:")
        print(f"  - Cantidad: {len(prop_lengths)}")
        print(f"  - Longitud promedio: {sum(prop_lengths) / len(prop_lengths):.0f} chars")
        print(f"  - Longitud mínima: {min(prop_lengths)} chars")
        print(f"  - Longitud máxima: {max(prop_lengths)} chars")

    if prose_lengths:
        print(f"\nChunks de prosa:")
        print(f"  - Cantidad: {len(prose_lengths)}")
        print(f"  - Longitud promedio: {sum(prose_lengths) / len(prose_lengths):.0f} chars")
        print(f"  - Longitud mínima: {min(prose_lengths)} chars")
        print(f"  - Longitud máxima: {max(prose_lengths)} chars")

    # Ejemplos por idioma
    print()
    print("Distribución por idioma y tipo:")
    for lang in ['de', 'en', 'es']:
        prop_count = sum(1 for c in chunks if c['language'] == lang and c['proposition_id'])
        prose_count = sum(1 for c in chunks if c['language'] == lang and not c['proposition_id'])
        print(f"  {lang}: {prop_count} proposicionales, {prose_count} prosa")

    print()
    print("=" * 80)

if __name__ == "__main__":
    inspect_corpus()
