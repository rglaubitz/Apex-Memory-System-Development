# Document Processing - Quick Reference Card

## 🎯 TL;DR - What to Use When

### Primary Choice: Docling
```bash
pip install docling
```
**Use for:** All PDFs, DOCX, PPTX, complex layouts, production RAG pipelines

### Fallback: Unstructured-IO
```bash
pip install unstructured
```
**Use for:** Non-PDF formats, email (EML/MSG), CSV/TSV, quick processing

### Research: RAG-Anything
```bash
pip install raganything
```
**Use for:** Multimodal inspiration, VLM patterns, knowledge graphs

---

## 📊 Quick Comparison

| Feature | Docling | Unstructured | RAG-Anything |
|---------|---------|--------------|--------------|
| Stars | 40k+ | 13k+ | 3.6k+ |
| PDF Quality | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Format Support | 10+ | 25+ | 10+ |
| Token-Aware Chunking | ✅ | ❌ | ✅ |
| Learning Curve | Medium | Easy | Hard |
| Production Ready | ✅ | ✅ | 🔬 Research |

---

## 💻 Code Templates

### Docling - Basic RAG Pipeline
```python
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker

# Convert
doc = DocumentConverter().convert("file.pdf").document

# Chunk with token awareness
chunker = HybridChunker(tokenizer="sentence-transformers/all-MiniLM-L6-v2")
chunks = list(chunker.chunk(dl_doc=doc))
```

### Unstructured - Multi-Format
```python
from unstructured.partition.auto import partition
from unstructured.chunking.title import chunk_by_title

# Auto-detect and partition
elements = partition("file.pdf", strategy="hi_res")

# Chunk by sections
chunks = chunk_by_title(elements, max_characters=1500)
```

### LangChain Integration
```python
from langchain_docling import DoclingLoader

loader = DoclingLoader(
    file_path="docs/",
    chunker=HybridChunker(tokenizer="...")
)
docs = loader.load()
```

---

## 🔑 Key Decisions

### Chunking Strategy
**Use HybridChunker (Docling)** - Token-aware, hierarchy-preserving

### Token Limit
**512 tokens max** - Matches embedding model (all-MiniLM-L6-v2)

### Overlap
**50-100 tokens** - Balance context and deduplication

### Vector DB
**Parallel write** - Qdrant + PostgreSQL + Neo4j (saga pattern)

---

## 📚 Essential Links

**Docling:**
- Repo: https://github.com/docling-project/docling
- Docs: https://docling-project.github.io/docling/
- RAG: https://docling-project.github.io/docling/examples/rag_langchain/

**Unstructured:**
- Repo: https://github.com/Unstructured-IO/unstructured
- Docs: https://docs.unstructured.io/
- Chunking: https://docs.unstructured.io/api-reference/api-services/chunking

**RAG-Anything:**
- Repo: https://github.com/HKUDS/RAG-Anything
- Base: https://github.com/HKUDS/LightRAG

---

## ⚡ Performance Tips

1. **Batch Processing**: Use `DocumentConverter` batch mode for multiple files
2. **Strategy Selection**:
   - `hi_res` for complex PDFs (slower, accurate)
   - `fast` for simple documents (faster)
3. **Parallel Pipelines**: RAG-Anything pattern for multimodal
4. **Caching**: Cache converted documents before chunking
5. **Memory**: Process large PDFs in streaming mode

---

## 🚨 Common Pitfalls

❌ **Token Mismatch**: Not matching chunker tokenizer to embedding model
✅ **Solution**: Use HybridChunker with same tokenizer

❌ **Lost Hierarchy**: Using basic chunking on structured docs
✅ **Solution**: Use Docling HybridChunker or by_title strategy

❌ **Format Errors**: Assuming all PDFs are processable
✅ **Solution**: Implement fallback to Unstructured ocr_only

❌ **Metadata Loss**: Not preserving document structure
✅ **Solution**: Extract headings, page numbers, element types

---

## 📈 Apex Memory Integration

```python
# Recommended Architecture
from apex_memory.ingestion import DocumentPipeline

pipeline = DocumentPipeline(
    primary_parser="docling",        # IBM Research quality
    fallback_parser="unstructured",  # Broad format support
    chunking_strategy="hybrid",      # Token-aware
    max_tokens=512,                  # Match embedding model
    vector_stores=["qdrant", "postgres"],
    graph_stores=["neo4j"]
)

result = pipeline.ingest("document.pdf")
```

---

## 🎓 Learning Path

1. **Week 1**: Install Docling, basic conversion, export to Markdown
2. **Week 2**: HybridChunker, token tuning, metadata extraction
3. **Week 3**: LangChain integration, vector DB writes
4. **Week 4**: Unstructured fallback, multi-format support
5. **Week 5**: Production pipeline, error handling, monitoring
6. **Week 6+**: RAG-Anything patterns, multimodal, VLM

---

## 🔍 Troubleshooting

**Issue:** "Chunk too large for embedding model"
**Fix:** Reduce `max_tokens` in HybridChunker

**Issue:** "Table structure lost"
**Fix:** Enable `pdf_infer_table_structure=True`

**Issue:** "Poor quality scanned PDF"
**Fix:** Use Unstructured `strategy="ocr_only"`

**Issue:** "Document hierarchy missing"
**Fix:** Use Docling, access `chunk.meta.headings`

---

**Quick Start:** Start with Docling + HybridChunker → LangChain → Qdrant

**Last Updated:** October 6, 2025
