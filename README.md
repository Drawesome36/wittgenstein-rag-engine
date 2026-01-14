# Wittgenstein RAG Pipeline

> Production-ready ETL and vectorization system for building RAG applications with Ludwig Wittgenstein's complete philosophical works.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-CC%20BY--SA%204.0-green)](https://creativecommons.org/licenses/by-sa/4.0/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)](https://github.com)

---

## 📖 Overview

This project provides a complete pipeline for processing Ludwig Wittgenstein's philosophical corpus into a structured, RAG-optimized dataset. The corpus includes **8,037 chunks** across **61 works** in three languages (German, English, Spanish), ready for:

- 🔍 **Semantic search** across philosophical texts
- 🤖 **RAG applications** (Retrieval-Augmented Generation)
- 🧠 **LLM fine-tuning** on structured propositions
- 🌐 **Cross-lingual analysis** of translations

---

## ✨ Features

- ✅ **Dual-strategy chunking**: Propositional (95.3%) + Prose (4.7%)
- ✅ **Rich metadata**: Language, period (EARLY/MIDDLE/LATE), proposition IDs
- ✅ **Mega-chunk splitting**: Automatic division of oversized content (<25K chars)
- ✅ **Clean output**: Wiki headers/footers removed, normalized spacing
- ✅ **Production-ready**: Compatible with OpenAI, Cohere, Sentence-BERT APIs
- ✅ **Extensive validation**: Automated tests for taxonomy and chunk sizes

---

## 📊 Corpus Statistics

| Metric | Value |
|--------|-------|
| **Total chunks** | 8,037 |
| **Total size** | 5.7 MB |
| **Languages** | German (3,669), English (1,255), Spanish (3,113) |
| **Periods** | EARLY (38.6%), MIDDLE (2.6%), LATE (57.5%) |
| **Avg chunk size** | 532 chars |
| **Max chunk size** | 24,995 chars (under embedding limits ✓) |

### Key Works Included

**EARLY (1914-1922):**
- Tractatus Logico-Philosophicus
- Notebooks 1914-1916
- Notes on Logic

**MIDDLE (1929-1936):**
- Blue Book
- Brown Book
- Remarks on Frazer's Golden Bough

**LATE (1936-1951):**
- Philosophical Investigations
- Zettel
- On Certainty
- Remarks on Colour

---

## 🚀 Installation and Usage

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/wittgenstein-rag.git
cd wittgenstein-rag
```

### Step 2: Install Dependencies

```bash
pip install requests beautifulsoup4 html2text
```

**Dependencies:**
- `requests`: HTTP library for downloading source files
- `beautifulsoup4`: HTML parsing for cleaning wiki content
- `html2text`: Converting HTML to Markdown

### Step 3: Prepare Source Data

**Option A: Use Your Own Markdown Files**

Place Wittgenstein's works in the `wittgenstein_obras/` directory with the following naming convention:

```
wittgenstein_obras/
├── [aleman] Tractatus Logico-Philosophicus.md
├── [ingles] Philosophical Investigations.md
├── [espanol] Sobre la certeza.md
└── ...
```

**Naming format:** `[language] Title.md`
- Languages: `[aleman]`, `[ingles]`, `[espanol]`
- The ETL will automatically filter by language prefix

**Option B: Download from Wittgenstein Project**

Run the included scraper to download all works:

```bash
python descargar_obras.py
```

This will download 61 works from [The Wittgenstein Project](https://www.wittgensteinproject.org/) and save them to `wittgenstein_obras/`.

### Step 4: Run the ETL Pipeline

```bash
python etl_wittgenstein.py
```

**Expected output:**
```
======================================================================
WITTGENSTEIN ETL PIPELINE
======================================================================
Directorio fuente: wittgenstein_obras
Archivos encontrados: 31

[PROCESSING] [aleman] Tractatus Logico-Philosophicus.md
  -> 653 chunks generados
[PROCESSING] [ingles] Philosophical Investigations.md
  -> 693 chunks generados
...

Total de chunks: 8,037
  - Proposicionales: 7,655
  - Prosa: 382
```

**Output file:** `wittgenstein_corpus_clean.jsonl` (5.7 MB)

### Step 5: Verify the Output

```bash
# Verify blocking issues are resolved
python verify_fixes.py

# Check chunk sizes
python verify_chunk_sizes.py

# Inspect corpus statistics
python inspect_corpus.py
```

---

## 📁 Project Structure

```
wittgenstein-rag/
├── wittgenstein_obras/          # Source Markdown files (input)
│   ├── [aleman] *.md
│   ├── [ingles] *.md
│   └── [espanol] *.md
│
├── etl_wittgenstein.py         # 🔧 Main ETL pipeline
├── descargar_obras.py          # Web scraper for source data
├── inspect_corpus.py           # Corpus analysis tool
├── verify_fixes.py             # Validation script
├── verify_chunk_sizes.py       # Size verification
│
├── wittgenstein_corpus_clean.jsonl  # 📊 Output corpus
│
├── README.md                   # This file
├── README_CORPUS.md            # Detailed corpus documentation
├── CLAUDE.MD                   # AI assistant context
├── RESUMEN_EJECUTIVO.md        # Executive summary (ES)
├── BLOCKING_ISSUES_RESOLVED.md # Technical fixes report
│
└── .gitignore                  # Git ignore rules
```

---

## 📄 Output Format

Each line in `wittgenstein_corpus_clean.jsonl` is a JSON object:

```json
{
  "id": "943b88d9-cf48-44ba-841e-1f251f5bbd2d",
  "source_file": "[aleman] Tractatus Logico-Philosophicus.md",
  "language": "de",
  "proposition_id": "1.1",
  "period": "EARLY",
  "content": "Die Welt ist die Gesamtheit der Tatsachen, nicht der Dinge.",
  "chunk_part": null
}
```

**Fields:**
- `id`: UUID v4 unique identifier
- `source_file`: Original Markdown filename
- `language`: ISO 639-1 code (`de`, `en`, `es`)
- `proposition_id`: Logical number (e.g., `"1.2.3"`) or `null` for prose
- `period`: Philosophical period (`EARLY`, `MIDDLE`, `LATE`, `GENERAL`)
- `content`: Clean text content
- `chunk_part`: Part number if split from mega-chunk (e.g., `1`, `2`, `3...`)

---

## 🔬 How It Works

### Chunking Strategies

**Strategy A: Propositional (95.3%)**
- For works with logical structure (Tractatus, Investigations, Zettel)
- Detects numbered propositions: `**[1.2.3](/url)**`, `**1.2.3**`, `1.2.3`
- Preserves semantic hierarchy
- Average: 418 chars per chunk

**Strategy B: Prose (4.7%)**
- For narrative works (Blue Book, Brown Book, Notebooks)
- Splits by paragraphs, groups to ~500 tokens
- Respects sentence boundaries
- Average: 2,861 chars per chunk

### Mega-Chunk Splitting

Chunks exceeding 25,000 characters (e.g., Philosophical Investigations §693 = 120KB) are automatically split:

```python
# Example: Proposition 693 split into 5 parts
{
  "proposition_id": "693",
  "chunk_part": 1,
  "content": "First 24,960 chars..."
}
{
  "proposition_id": "693",
  "chunk_part": 2,
  "content": "Next 24,688 chars..."
}
# ... parts 3, 4, 5
```

This ensures compatibility with embedding APIs (OpenAI Ada-002: 8,192 tokens limit).

---

## 💡 Use Cases

### 1. RAG Application

```python
import json
import openai

# Load corpus
with open('wittgenstein_corpus_clean.jsonl', 'r', encoding='utf-8') as f:
    chunks = [json.loads(line) for line in f]

# Generate embeddings
for chunk in chunks:
    embedding = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=chunk['content']
    )
    chunk['embedding'] = embedding['data'][0]['embedding']

# Query example: "What does Wittgenstein say about language?"
query_embedding = openai.Embedding.create(...)
results = search_similar(query_embedding, chunks, top_k=5)
```

### 2. Semantic Search by Period

```python
# Filter by philosophical period
early_works = [c for c in chunks if c['period'] == 'EARLY']
late_works = [c for c in chunks if c['period'] == 'LATE']

# Compare concepts across periods
query = "What is a proposition?"
early_results = search(query, early_works)
late_results = search(query, late_works)
```

### 3. Cross-lingual Analysis

```python
# Same work in multiple languages
tractatus_de = [c for c in chunks if 'Logisch-philosophische' in c['source_file']]
tractatus_en = [c for c in chunks if 'Tractatus Logico' in c['source_file']]
tractatus_es = [c for c in chunks if 'Tratado lógico' in c['source_file']]

# Compare translations of proposition 1.1
prop_1_1_de = [c for c in tractatus_de if c['proposition_id'] == '1.1'][0]
prop_1_1_en = [c for c in tractatus_en if c['proposition_id'] == '1.1'][0]
```

---

## 🧪 Testing & Validation

### Run All Tests

```bash
# Full test suite
python verify_fixes.py && python verify_chunk_sizes.py && python inspect_corpus.py
```

### Expected Results

```
✅ PASSED: No hay chunks > 30,000 caracteres
✅ CORRECTO: Todos los chunks clasificados como LATE
✅ PASSED: 8,037 chunks procesados correctamente
```

---

## 📚 Documentation

| File | Description |
|------|-------------|
| `README.md` | Project overview (this file) |
| `CLAUDE.MD` | Context for AI assistants and developers |
| `README_CORPUS.md` | Detailed corpus specifications |
| `RESUMEN_EJECUTIVO.md` | Executive summary in Spanish |
| `BLOCKING_ISSUES_RESOLVED.md` | Technical report on critical fixes |

---

## 🔧 Configuration

### Add New Languages

Edit `etl_wittgenstein.py`:

```python
# Line 27-34
ALLOWED_LANGUAGES = ['aleman', 'ingles', 'espanol', 'frances']  # Add 'frances'

LANG_MAP = {
    'aleman': 'de',
    'ingles': 'en',
    'espanol': 'es',
    'frances': 'fr'  # Add mapping
}
```

### Adjust Chunk Size Limits

```python
# Line 25000 default
max_chars = 20000  # Reduce for stricter limits
```

### Modify Period Taxonomy

```python
# Lines 37-58 - Edit PERIOD_TAXONOMY dictionary
PERIOD_TAXONOMY = {
    'EARLY': ['Tractatus', ...],
    'MIDDLE': ['Blue Book', ...],
    'LATE': ['Philosophical Investigations', ...]
}
```

---

## 🐛 Troubleshooting

### Issue: "No module named 'requests'"
```bash
pip install requests beautifulsoup4 html2text
```

### Issue: "wittgenstein_obras/ directory not found"
```bash
mkdir wittgenstein_obras
# Then add your Markdown files or run descargar_obras.py
```

### Issue: "UnicodeEncodeError on Windows"
Already handled! The pipeline includes Windows cp1252 compatibility.

### Issue: Chunks > 30,000 chars detected
```bash
# Verify split logic is working
python verify_chunk_sizes.py
# Should show: ✅ PASSED: No hay chunks > 30,000 caracteres
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Development workflow:**
```bash
# Make changes to etl_wittgenstein.py
python etl_wittgenstein.py

# Verify changes
python verify_fixes.py
python verify_chunk_sizes.py

# Commit if tests pass
git add .
git commit -m "Description of changes"
```

---

## 📜 License

**Source Data:**
- German originals: Public Domain (70+ years since author's death)
- Translations: [Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/)

**Pipeline Code:**
- MIT License (or specify your preferred license)

**Attribution:**
This corpus includes texts from [The Wittgenstein Project](https://www.wittgensteinproject.org/), licensed under CC BY-SA 4.0.

---

## 🙏 Acknowledgments

- **The Wittgenstein Project** for providing high-quality digital editions
- **Ludwig Wittgenstein** (1889-1951) for his groundbreaking philosophical work
- **Open-source community** for the excellent Python libraries used

---

## 📧 Contact

For questions, issues, or suggestions:
- Open an issue on GitHub
- Check `CLAUDE.MD` for AI assistant context
- Review `README_CORPUS.md` for detailed specifications

---

## 🗺️ Roadmap

**v1.1 (Current):**
- ✅ ETL pipeline with dual-strategy chunking
- ✅ Mega-chunk splitting (<25K chars)
- ✅ Rich metadata (period, language, proposition IDs)
- ✅ Automated validation scripts

**v1.2 (Next):**
- [ ] Vectorization pipeline (OpenAI Ada-002)
- [ ] ChromaDB/Pinecone indexing
- [ ] Simple RAG query interface
- [ ] CLI tool for corpus exploration

**v2.0 (Future):**
- [ ] Add French, Italian, Portuguese support
- [ ] Cross-reference resolution between propositions
- [ ] Graph-based navigation of logical structure
- [ ] LLM fine-tuning scripts

---

## 📊 Quick Stats

```
Pipeline Version: v1.1
Corpus Size: 5.7 MB (8,037 chunks)
Languages: 3 (German, English, Spanish)
Works: 61 philosophical texts
Propositions: 7,655 (numbered logical statements)
Prose chunks: 382 (narrative sections)
Status: ✅ Production Ready
```

---

**Built with ❤️ for philosophy and AI**

*"The limits of my language mean the limits of my world." - Ludwig Wittgenstein, Tractatus 5.6*
