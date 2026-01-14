#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETL Pipeline for Wittgenstein Corpus
Transforms raw Markdown files into structured JSONL for RAG applications
Senior Data Engineer: NLP Pipeline Specialist
"""

import os
import re
import json
import uuid
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import sys

# Configurar salida UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


# ==================== CONFIGURACIÓN ====================

# Idiomas permitidos (prefijos de archivos)
ALLOWED_LANGUAGES = ['aleman', 'ingles', 'espanol']

# Mapeo de idioma a código ISO
LANG_MAP = {
    'aleman': 'de',
    'ingles': 'en',
    'espanol': 'es'
}

# Taxonomía temporal de obras (EARLY, MIDDLE, LATE)
# CRITICAL: El orden importa - los patrones más específicos deben ir primero
# para evitar matches incorrectos con substrings genéricos
PERIOD_TAXONOMY = {
    'EARLY': [
        'Tractatus', 'Logisch-philosophische Abhandlung', 'Tratado lógico-filosófico',
        'Tagebücher', 'Notebooks', 'Cuadernos',
        'Notes on Logic', 'Notas sobre lógica'
    ],
    'LATE': [
        # Primero los patrones específicos de "Bemerkungen" para evitar match con MIDDLE
        'Bemerkungen über die Farben', 'Remarks on Colour', 'Observaciones sobre los colores',
        'Über Gewißheit', 'On Certainty', 'Sobre la certeza',
        'Philosophische Untersuchungen', 'Philosophical Investigations', 'Investigaciones filosóficas',
        'Zettel',
        'Vermischte Bemerkungen'  # Remarks escritas a lo largo de su vida, publicadas póstumas
    ],
    'MIDDLE': [
        'Blue Book', 'Libro Azul',
        'Brown Book', 'Libro Marrón',
        'Philosophical Remarks',
        'Bemerkungen über Frazers'  # Solo Frazer's Golden Bough es MIDDLE, no confundir con Farben
    ]
}

# Obras con estructura proposicional (numeración)
PROPOSITIONAL_WORKS = [
    'Tractatus', 'Logisch-philosophische Abhandlung', 'Tratado lógico-filosófico',
    'Tractatus Logico-Philosophicus',  # Versión inglesa
    'Philosophische Untersuchungen', 'Philosophical Investigations', 'Investigaciones filosóficas',
    'Zettel',
    'Über Gewißheit', 'On Certainty', 'Sobre la certeza',
    'Bemerkungen', 'Remarks', 'Observaciones'
]

# Patrones de limpieza
HEADER_PATTERNS = [
    r'.*?Change language.*?\n',
    r'.*?Navigation.*?\n',
    r'.*?Jump to:.*?\n',
    r'.*?Tools.*?\n',
    r'\[\s*edit\s*\]',
    r'##\s*Contents\s*\n.*?(?=\n##|\n#|$)',
]

FOOTER_PATTERNS = [
    r'Retrieved from.*',
    r'Categories:.*',
    r'Navigation menu.*',
    r'Personal tools.*',
    r'Namespaces.*',
    r'This page was last edited.*',
]


# ==================== MODELOS DE DATOS ====================

@dataclass
class Chunk:
    """Modelo de datos para cada chunk procesado"""
    id: str
    source_file: str
    language: str
    proposition_id: Optional[str]
    period: str
    content: str
    chunk_part: Optional[int] = None  # Para mega-chunks divididos (ej: parte 1 de 3)

    def to_dict(self) -> Dict:
        result = asdict(self)
        # Omitir chunk_part si es None para mantener compatibilidad con chunks no divididos
        if result['chunk_part'] is None:
            del result['chunk_part']
        return result


# ==================== FUNCIONES DE FILTRADO ====================

def should_process_file(filename: str) -> bool:
    """
    Verifica si un archivo debe ser procesado basándose en el prefijo de idioma
    """
    for lang in ALLOWED_LANGUAGES:
        if filename.startswith(f'[{lang}]'):
            return True
    return False


def extract_language_from_filename(filename: str) -> Optional[str]:
    """
    Extrae el código de idioma ISO del nombre del archivo
    """
    for lang, code in LANG_MAP.items():
        if filename.startswith(f'[{lang}]'):
            return code
    return None


# ==================== FUNCIONES DE LIMPIEZA ====================

def clean_markdown_images(text: str) -> str:
    """
    Elimina todas las imágenes Markdown ![](...)
    """
    return re.sub(r'!\[.*?\]\(.*?\)', '', text)


def remove_wiki_header(text: str) -> str:
    """
    Elimina el header de wiki hasta encontrar el primer encabezado real
    """
    # Buscar el primer encabezado Markdown real (# Título)
    match = re.search(r'^#\s+[^\n]+\n', text, re.MULTILINE)
    if match:
        return text[match.start():]

    # Si no hay encabezado, buscar "Change language" y similares
    for pattern in HEADER_PATTERNS:
        text = re.sub(pattern, '', text, flags=re.DOTALL | re.MULTILINE)

    return text


def remove_wiki_footer(text: str) -> str:
    """
    Elimina el footer de wiki (Retrieved from, Categories, etc.)
    """
    for pattern in FOOTER_PATTERNS:
        # Buscar el patrón y eliminar todo después de él
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            text = text[:match.start()]

    return text


def clean_text(text: str) -> str:
    """
    Pipeline completo de limpieza
    """
    text = remove_wiki_header(text)
    text = remove_wiki_footer(text)
    text = clean_markdown_images(text)

    # Normalizar espacios en blanco
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Máximo dos saltos de línea
    text = re.sub(r'[ \t]+', ' ', text)  # Espacios múltiples a uno solo
    text = text.strip()

    return text


# ==================== FUNCIONES DE CHUNKING ====================

def is_propositional_work(filename: str) -> bool:
    """
    Determina si una obra tiene estructura proposicional (numerada)
    """
    for work in PROPOSITIONAL_WORKS:
        if work.lower() in filename.lower():
            return True
    return False


def extract_propositional_chunks(text: str) -> List[Tuple[Optional[str], str]]:
    """
    Estrategia A: Extrae chunks basados en numeración proposicional

    Patrones soportados:
    - **1.** Texto
    - **1.1** Texto
    - **1.2.3** Texto
    - 1. Texto
    - 1.1 Texto
    - **[1.1](/url)** Texto (formato wiki con links)

    Returns:
        Lista de tuplas (proposition_id, content)
    """
    chunks = []

    # Patrón para detectar proposiciones numeradas (dos variantes)
    # Variante 1: **[1.1](/url)** Texto o **[1.](/url)** (con punto trailing opcional)
    # Variante 2: **1.1** Texto o 1.1 Texto (formato simple)
    pattern1 = r'^\*\*\[(\d+(?:\.\d+)*)\.?\]\([^\)]+\)\*\*'
    pattern2 = r'^\*{0,2}(\d+(?:\.\d+)*)\.*\*{0,2}\s+'

    lines = text.split('\n')
    current_prop_id = None
    current_content = []

    for line in lines:
        # Intentar ambos patrones
        match1 = re.match(pattern1, line, re.MULTILINE)
        match2 = re.match(pattern2, line, re.MULTILINE)

        match = match1 or match2
        pattern_to_remove = pattern1 if match1 else pattern2

        if match:
            # Guardar el chunk anterior si existe
            if current_prop_id is not None and current_content:
                content = '\n'.join(current_content).strip()
                if content:  # Solo agregar si hay contenido
                    chunks.append((current_prop_id, content))

            # Iniciar nuevo chunk
            current_prop_id = match.group(1)
            # Eliminar el número del contenido
            line_content = re.sub(pattern_to_remove, '', line, count=1)
            current_content = [line_content] if line_content.strip() else []
        else:
            # Continuar con el chunk actual
            if line.strip():
                current_content.append(line)

    # Agregar el último chunk
    if current_prop_id is not None and current_content:
        content = '\n'.join(current_content).strip()
        if content:
            chunks.append((current_prop_id, content))

    # Si no se encontraron proposiciones numeradas, tratar como prosa
    if not chunks:
        return [(None, text)]

    return chunks


def count_tokens_approximate(text: str) -> int:
    """
    Aproximación simple de tokens (palabras + puntuación)
    """
    # Aproximación: split por espacios y contar
    return len(text.split())


def split_large_paragraph(para: str, max_tokens: int = 500) -> List[str]:
    """
    Divide un párrafo muy grande en chunks más pequeños respetando oraciones
    """
    # Si el párrafo es pequeño, retornarlo como está
    if count_tokens_approximate(para) <= max_tokens:
        return [para]

    # Dividir por oraciones (aproximado)
    sentences = re.split(r'([.!?]+\s+)', para)
    chunks = []
    current = []
    current_tokens = 0

    for i in range(0, len(sentences), 2):
        sentence = sentences[i]
        punctuation = sentences[i+1] if i+1 < len(sentences) else ''
        full_sentence = sentence + punctuation

        sent_tokens = count_tokens_approximate(full_sentence)

        if current_tokens + sent_tokens > max_tokens and current:
            chunks.append(''.join(current))
            current = [full_sentence]
            current_tokens = sent_tokens
        else:
            current.append(full_sentence)
            current_tokens += sent_tokens

    if current:
        chunks.append(''.join(current))

    return chunks


def extract_prose_chunks(text: str, max_tokens: int = 500) -> List[str]:
    """
    Estrategia B: Divide texto de prosa en chunks de ~max_tokens
    respetando fronteras de párrafos y oraciones
    Con límite máximo absoluto de 3000 tokens por chunk
    """
    chunks = []
    MAX_ABSOLUTE_TOKENS = 3000  # Límite duro

    # Dividir por párrafos (doble salto de línea)
    paragraphs = re.split(r'\n\s*\n', text)

    current_chunk = []
    current_tokens = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        para_tokens = count_tokens_approximate(para)

        # Si un solo párrafo excede el límite absoluto, dividirlo
        if para_tokens > MAX_ABSOLUTE_TOKENS:
            # Guardar chunk actual si existe
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_tokens = 0

            # Dividir el párrafo grande
            sub_chunks = split_large_paragraph(para, max_tokens)
            chunks.extend(sub_chunks)
            continue

        # Si agregar este párrafo excede el límite y ya hay contenido
        if current_tokens + para_tokens > max_tokens and current_chunk:
            # Guardar chunk actual
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [para]
            current_tokens = para_tokens
        else:
            # Agregar al chunk actual
            current_chunk.append(para)
            current_tokens += para_tokens

    # Agregar el último chunk
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))

    return chunks


# ==================== MANEJO DE MEGA-CHUNKS ====================

def split_oversized_chunk(text: str, max_chars: int = 25000) -> List[str]:
    """
    Divide chunks excesivamente grandes que exceden límites de modelos de embedding.

    CRITICAL FIX: Proposiciones como "693" de Investigaciones Filosóficas (~120KB)
    exceden el límite de 8192 tokens de modelos como OpenAI Ada-002.

    Args:
        text: Contenido del chunk a dividir
        max_chars: Límite máximo de caracteres (default: 25,000 ≈ 6,250 tokens)

    Returns:
        Lista de sub-chunks divididos por párrafos

    Strategy:
        1. Si texto <= max_chars: retornar como está
        2. Si texto > max_chars: dividir por dobles saltos de línea
        3. Agrupar párrafos hasta max_chars respetando fronteras
        4. Recursión si un párrafo individual > max_chars
    """
    # Caso base: chunk dentro del límite
    if len(text) <= max_chars:
        return [text]

    sub_chunks = []
    paragraphs = re.split(r'\n\s*\n', text)

    current_sub = []
    current_length = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        para_length = len(para)

        # Si un solo párrafo excede el límite, dividirlo por oraciones
        if para_length > max_chars:
            # Guardar sub-chunk actual si existe
            if current_sub:
                sub_chunks.append('\n\n'.join(current_sub))
                current_sub = []
                current_length = 0

            # Dividir párrafo grande por oraciones
            sentences = re.split(r'([.!?]+\s+)', para)
            sentence_chunk = []
            sentence_length = 0

            for i in range(0, len(sentences), 2):
                sentence = sentences[i]
                punctuation = sentences[i+1] if i+1 < len(sentences) else ''
                full_sentence = sentence + punctuation
                sent_len = len(full_sentence)

                if sentence_length + sent_len > max_chars and sentence_chunk:
                    sub_chunks.append(''.join(sentence_chunk))
                    sentence_chunk = [full_sentence]
                    sentence_length = sent_len
                else:
                    sentence_chunk.append(full_sentence)
                    sentence_length += sent_len

            if sentence_chunk:
                sub_chunks.append(''.join(sentence_chunk))

            continue

        # Si agregar este párrafo excede el límite
        if current_length + para_length > max_chars and current_sub:
            sub_chunks.append('\n\n'.join(current_sub))
            current_sub = [para]
            current_length = para_length
        else:
            current_sub.append(para)
            current_length += para_length + 2  # +2 por \n\n

    # Agregar último sub-chunk
    if current_sub:
        sub_chunks.append('\n\n'.join(current_sub))

    return sub_chunks if sub_chunks else [text]


# ==================== FUNCIONES DE METADATOS ====================

def determine_period(filename: str) -> str:
    """
    Determina el período temporal de la obra (EARLY, MIDDLE, LATE)

    CRITICAL FIX: Procesa períodos en orden LATE -> MIDDLE -> EARLY
    para asegurar que patrones más específicos (ej: "Bemerkungen über die Farben")
    se matcheen antes que patrones genéricos (ej: "Bemerkungen")
    """
    filename_lower = filename.lower()

    # Orden específico: LATE primero (más específico), luego MIDDLE, luego EARLY
    for period in ['LATE', 'MIDDLE', 'EARLY']:
        if period in PERIOD_TAXONOMY:
            for work in PERIOD_TAXONOMY[period]:
                if work.lower() in filename_lower:
                    return period

    return 'GENERAL'


def extract_title_from_filename(filename: str) -> str:
    """
    Extrae el título limpio del nombre del archivo
    """
    # Remover prefijo de idioma [idioma]
    title = re.sub(r'^\[.*?\]\s*', '', filename)
    # Remover extensión .md
    title = re.sub(r'\.md$', '', title)
    return title


# ==================== PIPELINE PRINCIPAL ====================

def create_chunk_with_split(
    chunk_content: str,
    source_file: str,
    language: str,
    proposition_id: Optional[str],
    period: str,
    max_chars: int = 25000
) -> List[Chunk]:
    """
    Crea uno o más chunks, dividiendo automáticamente si excede max_chars

    CRITICAL FIX: Token overflow prevention para modelos de embedding
    que tienen límite de 8192 tokens (≈32,000 chars)

    Returns:
        Lista de chunks (1 si no necesita división, N si fue dividido)
    """
    # Caso normal: chunk dentro del límite
    if len(chunk_content) <= max_chars:
        return [Chunk(
            id=str(uuid.uuid4()),
            source_file=source_file,
            language=language,
            proposition_id=proposition_id,
            period=period,
            content=chunk_content,
            chunk_part=None
        )]

    # Caso crítico: mega-chunk que excede límite
    print(f"  [WARNING] Mega-chunk detected: {len(chunk_content)} chars (prop: {proposition_id})")
    print(f"           Splitting into sub-chunks...")

    sub_contents = split_oversized_chunk(chunk_content, max_chars)
    chunks = []

    for part_num, sub_content in enumerate(sub_contents, start=1):
        chunk = Chunk(
            id=str(uuid.uuid4()),
            source_file=source_file,
            language=language,
            proposition_id=proposition_id,
            period=period,
            content=sub_content,
            chunk_part=part_num if len(sub_contents) > 1 else None
        )
        chunks.append(chunk)

    print(f"           Split into {len(chunks)} parts")
    return chunks


def process_file(filepath: Path) -> List[Chunk]:
    """
    Procesa un archivo completo y retorna una lista de chunks

    Incluye manejo automático de mega-chunks que exceden límites de embedding
    """
    filename = filepath.name

    # Leer archivo
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"[ERROR] No se pudo leer {filename}: {e}")
        return []

    # Extraer metadatos
    language = extract_language_from_filename(filename)
    period = determine_period(filename)
    source_file = filename

    # Limpiar contenido
    content = clean_text(content)

    # Determinar estrategia de chunking
    chunks_data = []

    if is_propositional_work(filename):
        # Estrategia A: Proposicional
        prop_chunks = extract_propositional_chunks(content)
        for prop_id, chunk_content in prop_chunks:
            # Verificar y dividir si es mega-chunk
            created_chunks = create_chunk_with_split(
                chunk_content=chunk_content,
                source_file=source_file,
                language=language,
                proposition_id=prop_id,
                period=period,
                max_chars=25000
            )
            chunks_data.extend(created_chunks)
    else:
        # Estrategia B: Prosa
        prose_chunks = extract_prose_chunks(content, max_tokens=500)
        for chunk_content in prose_chunks:
            # Verificar y dividir si es mega-chunk
            created_chunks = create_chunk_with_split(
                chunk_content=chunk_content,
                source_file=source_file,
                language=language,
                proposition_id=None,
                period=period,
                max_chars=25000
            )
            chunks_data.extend(created_chunks)

    return chunks_data


def run_etl_pipeline(input_dir: str = 'wittgenstein_obras',
                     output_file: str = 'wittgenstein_corpus_clean.jsonl') -> Dict:
    """
    Ejecuta el pipeline ETL completo
    """
    input_path = Path(input_dir)

    if not input_path.exists():
        raise FileNotFoundError(f"El directorio {input_dir} no existe")

    # Estadísticas
    stats = {
        'files_processed': 0,
        'files_skipped': 0,
        'total_chunks': 0,
        'propositional_chunks': 0,
        'prose_chunks': 0,
        'by_language': {'de': 0, 'en': 0, 'es': 0},
        'by_period': {'EARLY': 0, 'MIDDLE': 0, 'LATE': 0, 'GENERAL': 0}
    }

    all_chunks = []

    # Procesar archivos
    md_files = sorted(input_path.glob('*.md'))

    print("=" * 70)
    print("WITTGENSTEIN ETL PIPELINE")
    print("=" * 70)
    print(f"Directorio fuente: {input_dir}")
    print(f"Archivos encontrados: {len(md_files)}")
    print()

    for filepath in md_files:
        filename = filepath.name

        # Filtrar por idioma
        if not should_process_file(filename):
            stats['files_skipped'] += 1
            print(f"[SKIP] {filename} (idioma no permitido)")
            continue

        print(f"[PROCESSING] {filename}")

        # Procesar archivo
        chunks = process_file(filepath)

        if chunks:
            stats['files_processed'] += 1
            stats['total_chunks'] += len(chunks)

            # Actualizar estadísticas
            for chunk in chunks:
                all_chunks.append(chunk)

                if chunk.proposition_id:
                    stats['propositional_chunks'] += 1
                else:
                    stats['prose_chunks'] += 1

                stats['by_language'][chunk.language] += 1
                stats['by_period'][chunk.period] += 1

        print(f"  -> {len(chunks)} chunks generados")

    # Escribir JSONL
    print()
    print("=" * 70)
    print(f"Escribiendo {len(all_chunks)} chunks a {output_file}...")

    with open(output_file, 'w', encoding='utf-8') as f:
        for chunk in all_chunks:
            json_line = json.dumps(chunk.to_dict(), ensure_ascii=False)
            f.write(json_line + '\n')

    print(f"[OK] Archivo generado: {output_file}")
    print()

    # Mostrar estadísticas
    print("=" * 70)
    print("ESTADÍSTICAS DEL ETL")
    print("=" * 70)
    print(f"Archivos procesados: {stats['files_processed']}")
    print(f"Archivos omitidos: {stats['files_skipped']}")
    print(f"Total de chunks: {stats['total_chunks']}")
    print(f"  - Proposicionales: {stats['propositional_chunks']}")
    print(f"  - Prosa: {stats['prose_chunks']}")
    print()
    print("Por idioma:")
    for lang, count in stats['by_language'].items():
        print(f"  - {lang}: {count} chunks")
    print()
    print("Por período:")
    for period, count in stats['by_period'].items():
        print(f"  - {period}: {count} chunks")
    print("=" * 70)

    return stats, all_chunks


# ==================== MAIN ====================

if __name__ == "__main__":
    try:
        stats, all_chunks = run_etl_pipeline()

        # Mostrar muestras
        print()
        print("=" * 70)
        print("MUESTRAS DE CHUNKS PROCESADOS")
        print("=" * 70)

        # Encontrar un chunk proposicional
        prop_chunk = None
        for chunk in all_chunks:
            if chunk.proposition_id:
                prop_chunk = chunk
                break

        if prop_chunk:
            print()
            print("MUESTRA 1: Chunk Proposicional")
            print("-" * 70)
            print(json.dumps(prop_chunk.to_dict(), ensure_ascii=False, indent=2))

        # Encontrar un chunk de prosa
        prose_chunk = None
        for chunk in all_chunks:
            if not chunk.proposition_id:
                prose_chunk = chunk
                break

        if prose_chunk:
            print()
            print("MUESTRA 2: Chunk de Prosa")
            print("-" * 70)
            # Limitar contenido para visualización
            sample = prose_chunk.to_dict()
            if len(sample['content']) > 300:
                sample['content'] = sample['content'][:300] + "..."
            print(json.dumps(sample, ensure_ascii=False, indent=2))

        print()
        print("=" * 70)
        print("[SUCCESS] ETL Pipeline completado exitosamente")
        print("=" * 70)

    except Exception as e:
        print(f"[ERROR FATAL] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
