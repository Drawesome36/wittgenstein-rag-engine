# CLAUDE.MD - Project Context for AI Assistants & Developers

> This file provides context for Claude (or any AI assistant) and future developers working on this project.

---

## 🎯 Project Objective

**Wittgenstein RAG Pipeline**: A production-ready ETL and vectorization system for building Retrieval-Augmented Generation (RAG) applications focused on philosophical texts by Ludwig Wittgenstein.

**Use Cases:**
- Semantic search across Wittgenstein's complete works
- Question-answering systems for philosophy students/researchers
- Fine-tuning LLMs on structured philosophical propositions
- Cross-lingual analysis (German, English, Spanish)

---

## 📁 Project Structure

```
Wittgenstein/
├── wittgenstein_obras/          # Source corpus (Markdown files)
│   ├── [aleman] *.md           # German originals
│   ├── [ingles] *.md           # English translations
│   └── [espanol] *.md          # Spanish translations
│
├── etl_wittgenstein.py         # 🔧 MAIN ETL PIPELINE
│   └── Transforms raw Markdown → structured JSONL
│
├── wittgenstein_corpus_clean.jsonl  # 📊 OUTPUT: 8,037 chunks
│   └── Ready for embedding & indexing
│
├── descargar_obras.py          # Scraper for Wittgenstein Project
├── inspect_corpus.py           # Corpus analysis tool
├── verify_fixes.py             # Validation script
├── verify_chunk_sizes.py       # Size verification
│
├── README.MD                   # Project documentation
├── README_CORPUS.md            # Detailed corpus specs
├── RESUMEN_EJECUTIVO.md        # Executive summary (Spanish)
├── BLOCKING_ISSUES_RESOLVED.md # Technical fixes report
└── CLAUDE.MD                   # This file
```

---

## 🔧 Key Scripts

### 1. `etl_wittgenstein.py` (Main ETL Pipeline)

**Purpose:** Transform raw Markdown files into a structured, RAG-optimized JSONL corpus.

**What it does:**
1. **Filters** source files by language (German, English, Spanish)
2. **Cleans** wiki headers, footers, images
3. **Chunks** using dual strategy:
   - **Propositional**: Extracts numbered propositions (e.g., `1.2.3`)
   - **Prose**: Splits by paragraphs (~500 tokens)
4. **Splits** mega-chunks (>25K chars) to prevent token overflow
5. **Enriches** with metadata: language, period (EARLY/MIDDLE/LATE), proposition ID

**Input:** `wittgenstein_obras/*.md`
**Output:** `wittgenstein_corpus_clean.jsonl` (5.7 MB, 8,037 chunks)

**Run:**
```bash
python etl_wittgenstein.py
```

**Expected output:**
```
Total de chunks: 8,037
  - Proposicionales: 7,655
  - Prosa: 382
```

---

### 2. Vectorization Pipeline (Future)

**Status:** Not yet implemented (next phase)

**Planned approach:**
```python
# Pseudocode for future implementation
import openai
import chromadb

# Load corpus
chunks = load_jsonl('wittgenstein_corpus_clean.jsonl')

# Generate embeddings
for chunk in chunks:
    embedding = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=chunk['content']
    )
    chunk['embedding'] = embedding['data'][0]['embedding']

# Index in vector DB
client = chromadb.Client()
collection = client.create_collection("wittgenstein")
collection.add(
    embeddings=[c['embedding'] for c in chunks],
    metadatas=[c for c in chunks],
    ids=[c['id'] for c in chunks]
)
```

**Recommended Vector DBs:**
- **Pinecone**: Managed, scalable (namespace by period)
- **ChromaDB**: Local, SQLite-based (collection by language)
- **Qdrant**: High-performance, filters on metadata
- **Weaviate**: GraphQL interface, hybrid search

---

### 3. Verification Scripts

**`verify_fixes.py`**: Validates critical fixes (taxonomy, chunk sizes)
**`verify_chunk_sizes.py`**: Ensures no chunks exceed embedding limits
**`inspect_corpus.py`**: Detailed corpus analysis and statistics

---

## 📊 Corpus Specifications

**File:** `wittgenstein_corpus_clean.jsonl`

**Schema:**
```json
{
  "id": "uuid-v4",
  "source_file": "[idioma] Título.md",
  "language": "de|en|es",
  "proposition_id": "1.2.3",
  "period": "EARLY|MIDDLE|LATE|GENERAL",
  "content": "Chunk text...",
  "chunk_part": 1  // Optional, only for split mega-chunks
}
```

**Statistics:**
- Total chunks: 8,037
- Languages: German (3,669), English (1,255), Spanish (3,113)
- Periods: EARLY (3,104), MIDDLE (205), LATE (4,620), GENERAL (108)
- Avg size: 532 chars
- Max size: 24,995 chars (under 30K limit ✓)

**Key Works Included:**
- **EARLY**: Tractatus Logico-Philosophicus, Notebooks 1914-1916
- **MIDDLE**: Blue Book, Brown Book, Remarks on Frazer
- **LATE**: Philosophical Investigations, Zettel, On Certainty, Remarks on Colour

---

## 🚀 How to Replicate This Project

### Step 1: Get Source Data

**Option A: Use included data** (if `wittgenstein_obras/` exists)
```bash
# Data already downloaded, skip to Step 2
```

**Option B: Download fresh data**
```bash
python descargar_obras.py
# Downloads 61 works from wittgensteinproject.org
# Saves to wittgenstein_obras/
```

### Step 2: Run ETL Pipeline

```bash
pip install requests beautifulsoup4 html2text
python etl_wittgenstein.py
```

**Output:** `wittgenstein_corpus_clean.jsonl` (8,037 chunks)

### Step 3: Verify Output

```bash
python verify_fixes.py
python verify_chunk_sizes.py
```

### Step 4: (Future) Generate Embeddings & Index

```bash
# Not implemented yet - see "Vectorization Pipeline" section above
```

---

## 🔍 Important Implementation Details

### Blocking Issues Fixed (v1.1)

1. **Taxonomy Error**: "Bemerkungen über die Farben" was classified as MIDDLE instead of LATE
   - **Fix**: Reordered PERIOD_TAXONOMY to check LATE patterns first
   - **Impact**: LATE chunks increased from 2,135 to 4,620

2. **Token Overflow**: 5 chunks exceeded 120KB (>30K tokens)
   - **Fix**: Implemented `split_oversized_chunk()` with 25K char limit
   - **Impact**: Split into 19 sub-chunks, all under embedding limits

### Chunking Strategies

**Strategy A: Propositional** (95.3% of chunks)
- For works with logical structure (Tractatus, Investigations, Zettel)
- Detects patterns: `**[1.2.3](/url)**`, `**1.2.3**`, `1.2.3`
- Preserves semantic hierarchy
- Avg: 418 chars/chunk

**Strategy B: Prose** (4.7% of chunks)
- For narrative works (Blue Book, Brown Book, Notebooks)
- Splits by paragraphs, groups to ~500 tokens
- Respects sentence boundaries
- Avg: 2,861 chars/chunk

### Edge Cases Handled

- **Mega-chunks**: Propositions like "693" (Investigations Part II) = 120KB
  - Split into 5 parts maintaining metadata
- **Multilingual**: Same work in 3 languages with consistent structure
- **Special characters**: UTF-8 encoding with Windows cp1252 compatibility
- **Wiki noise**: Headers, footers, navigation removed heuristically

---

## 💡 Tips for AI Assistants

### When Working on This Project:

1. **Always read the corpus structure first:**
   ```bash
   python inspect_corpus.py
   ```

2. **Before modifying ETL:**
   - Test on a small subset first
   - Run verification scripts after
   - Check chunk_part field for split chunks

3. **Common tasks:**
   - **Add new language**: Update `ALLOWED_LANGUAGES` and `LANG_MAP`
   - **Fix taxonomy**: Modify `PERIOD_TAXONOMY` (most specific first!)
   - **Adjust chunk size**: Change `max_chars` in `split_oversized_chunk()`
   - **Add new metadata**: Update `Chunk` dataclass

4. **Red flags:**
   - Chunks > 30K chars → Token overflow in embeddings
   - MIDDLE period > 10% → Likely taxonomy error
   - Chunks < 50 chars → Overly aggressive splitting

### Debugging Checklist:

```python
# Quick corpus health check
import json
chunks = [json.loads(line) for line in open('wittgenstein_corpus_clean.jsonl')]

# Check 1: Size distribution
sizes = [len(c['content']) for c in chunks]
print(f"Max: {max(sizes)}, Avg: {sum(sizes)//len(sizes)}")

# Check 2: Period distribution
from collections import Counter
print(Counter(c['period'] for c in chunks))

# Check 3: Split chunks
split_chunks = [c for c in chunks if c.get('chunk_part')]
print(f"Split chunks: {len(split_chunks)}")
```

---

## 📚 Academic Context

### Wittgenstein's Periods

**EARLY (1914-1922):**
- Focus: Logic, language, metaphysics
- Style: Aphoristic, numbered propositions
- Key work: Tractatus Logico-Philosophicus
- Famous line: "Whereof one cannot speak, thereof one must be silent"

**MIDDLE (1929-1936):**
- Transition period, returned to philosophy
- Focus: Language games, philosophy of mathematics
- Style: Conversational, exploratory
- Key works: Blue and Brown Books (lecture notes)

**LATE (1936-1951):**
- Focus: Ordinary language, forms of life
- Style: Investigations, remarks, observations
- Key work: Philosophical Investigations (published posthumously)
- Revolutionary shift from early logical atomism

### Propositional Structure

Works like the Tractatus use hierarchical numbering:
```
1. The world is everything that is the case
  1.1 The world is the totality of facts, not of things
    1.11 The world is determined by the facts...
    1.12 For the totality of facts determines...
  1.2 The world divides into facts
    1.21 Any one can either be the case or not be the case...
```

This structure is **preserved** in the corpus via `proposition_id`.

---

## 🔐 Data Licensing

**Source:** [The Wittgenstein Project](https://www.wittgensteinproject.org/)

**Licenses:**
- German originals: Public Domain (70+ years since author's death)
- Translations: Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0)

**Attribution:**
This corpus includes translations from The Wittgenstein Project, licensed under CC BY-SA 4.0. Original German texts are in the public domain.

---

## 🚧 Known Limitations

1. **Languages limited to 3**: German, English, Spanish
   - French, Italian, Portuguese available but not processed
   - Easy to add: Update `ALLOWED_LANGUAGES`

2. **Header cleaning heuristic**: May occasionally miss wiki elements
   - Low impact: ~0.1% of chunks may have minor artifacts

3. **Chunk size variability**:
   - Propositional chunks: 19 - 24,995 chars
   - Some very small (single line propositions)
   - Acceptable for RAG, but consider filtering <50 chars for training

4. **Cross-references not resolved**:
   - Propositions reference each other (e.g., "see 1.2.3")
   - These are kept as-is, not hyperlinked in corpus

---

## 🎯 Future Enhancements

### Short-term (Next Sprint):
- [ ] Implement vectorization pipeline (OpenAI Ada-002)
- [ ] Build ChromaDB index with metadata filters
- [ ] Create simple RAG query interface
- [ ] Add CLI tool for corpus exploration

### Medium-term:
- [ ] Add French, Italian, Portuguese support
- [ ] Implement cross-reference resolution
- [ ] Build graph of propositional dependencies
- [ ] Add sentence-level embeddings for granular search

### Long-term:
- [ ] Fine-tune LLM on corpus (GPT-3.5, Llama)
- [ ] Build interactive philosophy tutor chatbot
- [ ] Multilingual semantic search across translations
- [ ] Integration with philosophical concept ontologies

---

## 🤝 Contributing

**For AI Assistants:**
- Always run verification scripts after changes
- Preserve backwards compatibility in JSONL schema
- Document breaking changes in commit messages

**For Humans:**
- Follow PEP 8 for Python code
- Add docstrings to new functions
- Update this file when adding major features

---

## 📞 Contact & Support

**Project Context:**
- Built as RAG pipeline for philosophical research
- Optimized for production embedding APIs
- Designed for extensibility and maintenance

**Key Files to Review:**
1. This file (CLAUDE.MD) - Project overview
2. README_CORPUS.md - Detailed corpus documentation
3. BLOCKING_ISSUES_RESOLVED.md - Technical fixes
4. etl_wittgenstein.py - Implementation

**Quick Start Command:**
```bash
# Full pipeline from scratch
python descargar_obras.py && python etl_wittgenstein.py && python verify_fixes.py
```

---

**Last Updated:** January 14, 2026
**Pipeline Version:** v1.1 (Post-Fix)
**Corpus Size:** 8,037 chunks (5.7 MB)
**Status:** ✅ Production Ready
