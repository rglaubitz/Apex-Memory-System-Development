# Docling Documentation

**Version:** 2.55.1
**Last Updated:** 2025-10-06
**Official Source:** https://docling-project.github.io/docling/

## Overview

Docling is an advanced document parsing toolkit developed by IBM Research and hosted as a project in the LF AI & Data Foundation. It simplifies document processing with advanced PDF understanding and seamless integration with the gen AI ecosystem.

## Key Features

- **Multi-format Support:** PDF, DOCX, PPTX, XLSX, HTML, WAV, MP3, VTT, images (PNG, TIFF, JPEG)
- **Advanced PDF Understanding:** Page layout, reading order, table structure, code/formula recognition
- **Extensive OCR:** Support for scanned PDFs and images
- **Unified Format:** DoclingDocument representation for all input types
- **Export Options:** Markdown, HTML, DocTags, lossless JSON
- **Local Execution:** Process sensitive documents locally
- **AI Integration:** LangChain, LlamaIndex support

## Installation

```bash
pip install docling==2.55.1
```

### With OCR Support

```bash
pip install docling[ocr]==2.55.1
```

### Development Installation

```bash
git clone https://github.com/docling-project/docling.git
cd docling
pip install -e .
```

## Core API

### Basic Document Conversion

```python
from docling.document_converter import DocumentConverter

# Initialize converter
converter = DocumentConverter()

# Convert document
result = converter.convert("document.pdf")

# Access content
print(result.document.export_to_markdown())
```

### Supported Formats

```python
# PDF
result = converter.convert("document.pdf")

# DOCX
result = converter.convert("document.docx")

# PPTX
result = converter.convert("presentation.pptx")

# Images with OCR
result = converter.convert("scanned_page.png")

# HTML
result = converter.convert("webpage.html")

# Audio (with ASR)
result = converter.convert("recording.mp3")
```

### Export Formats

#### Markdown Export

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("document.pdf")

# Export to Markdown
markdown_text = result.document.export_to_markdown()
print(markdown_text)

# Save to file
with open("output.md", "w") as f:
    f.write(markdown_text)
```

#### HTML Export

```python
# Export to HTML
html_content = result.document.export_to_html()

with open("output.html", "w") as f:
    f.write(html_content)
```

#### JSON Export (Lossless)

```python
# Export to JSON with full metadata
json_content = result.document.export_to_json()

import json
with open("output.json", "w") as f:
    json.dump(json_content, f, indent=2)
```

#### DocTags Export

```python
# Export to DocTags format
doctags = result.document.export_to_doctags()
```

## Advanced Features

### OCR Configuration

```python
from docling.datamodel.pipeline_options import PipelineOptions
from docling.document_converter import DocumentConverter

# Configure OCR
options = PipelineOptions(
    do_ocr=True,
    ocr_engine="tesseract"  # or "easyocr"
)

converter = DocumentConverter(
    pipeline_options=options
)

# Process scanned document
result = converter.convert("scanned.pdf")
```

### Table Extraction

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("tables.pdf")

# Access tables
for table in result.document.tables:
    print(f"Table: {table.data}")
    # Table data is structured and parsed
```

### Page Layout Analysis

```python
# Access page structure
for page in result.document.pages:
    print(f"Page {page.page_no}:")
    print(f"  Layout: {page.layout}")
    print(f"  Reading order: {page.reading_order}")
```

### Formula and Code Recognition

```python
# Extract formulas
for formula in result.document.formulas:
    print(f"Formula: {formula.content}")
    print(f"LaTeX: {formula.latex}")

# Extract code blocks
for code in result.document.code_blocks:
    print(f"Code: {code.content}")
    print(f"Language: {code.language}")
```

## Integration with RAG Systems

### LangChain Integration

```python
from langchain_community.document_loaders import DoclingLoader

# Initialize loader
loader = DoclingLoader(
    file_path="document.pdf",
    export_format="markdown"
)

# Load documents for LangChain
documents = loader.load()

# Use in RAG pipeline
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = splitter.split_documents(documents)
```

### Direct RAG Integration

```python
from docling.document_converter import DocumentConverter
from langchain.schema import Document

converter = DocumentConverter()
result = converter.convert("document.pdf")

# Convert to LangChain documents
langchain_docs = []
for page in result.document.pages:
    doc = Document(
        page_content=page.export_to_markdown(),
        metadata={
            "source": "document.pdf",
            "page": page.page_no,
            "layout": str(page.layout)
        }
    )
    langchain_docs.append(doc)
```

## DoclingDocument Model

### Document Structure

```python
# Access document structure
doc = result.document

# Metadata
print(doc.metadata)  # Author, title, creation date, etc.

# Pages
for page in doc.pages:
    print(f"Page {page.page_no}: {page.size}")

# Text content
full_text = doc.export_to_text()

# Images
for image in doc.images:
    print(f"Image: {image.uri}")
```

### Metadata Access

```python
# Document metadata
metadata = result.document.metadata
print(f"Title: {metadata.title}")
print(f"Author: {metadata.author}")
print(f"Created: {metadata.creation_date}")
print(f"Pages: {metadata.num_pages}")
```

## Batch Processing

```python
from docling.document_converter import DocumentConverter
from pathlib import Path

converter = DocumentConverter()

# Process directory
pdf_files = Path("documents/").glob("*.pdf")

results = []
for pdf_file in pdf_files:
    try:
        result = converter.convert(str(pdf_file))
        results.append({
            "file": pdf_file.name,
            "content": result.document.export_to_markdown(),
            "metadata": result.document.metadata
        })
    except Exception as e:
        print(f"Error processing {pdf_file}: {e}")

# Save results
import json
with open("batch_results.json", "w") as f:
    json.dump(results, f, indent=2)
```

## Configuration Options

### Pipeline Options

```python
from docling.datamodel.pipeline_options import (
    PipelineOptions,
    TableFormerMode
)

options = PipelineOptions(
    do_ocr=True,                          # Enable OCR
    do_table_structure=True,              # Extract table structure
    table_structure_mode=TableFormerMode.ACCURATE,
    images_scale=2.0,                     # Image scaling factor
    generate_page_images=True,            # Generate page images
    generate_picture_images=True          # Extract pictures
)

converter = DocumentConverter(pipeline_options=options)
```

### Conversion Options

```python
from docling.datamodel.conversion_options import ConversionOptions

conv_options = ConversionOptions(
    max_num_pages=100,        # Limit pages to process
    max_file_size=50_000_000  # 50MB limit
)

result = converter.convert(
    "large_document.pdf",
    options=conv_options
)
```

## Error Handling

```python
from docling.document_converter import DocumentConverter
from docling.exceptions import ConversionException

converter = DocumentConverter()

try:
    result = converter.convert("document.pdf")
    markdown = result.document.export_to_markdown()
except ConversionException as e:
    print(f"Conversion failed: {e}")
except FileNotFoundError:
    print("Document not found")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Performance Optimization

### Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor
from docling.document_converter import DocumentConverter

def process_document(file_path):
    converter = DocumentConverter()
    result = converter.convert(file_path)
    return result.document.export_to_markdown()

files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_document, files))
```

### Memory Management

```python
# Process large documents in chunks
from docling.datamodel.conversion_options import ConversionOptions

options = ConversionOptions(
    max_num_pages=50  # Process 50 pages at a time
)

# For very large documents, process in batches
for i in range(0, total_pages, 50):
    batch_options = ConversionOptions(
        page_range=(i, min(i+50, total_pages))
    )
    result = converter.convert("large.pdf", options=batch_options)
```

## Visual Language Model (VLM) Support

```python
from docling.datamodel.pipeline_options import PipelineOptions

# Enable VLM for enhanced understanding
options = PipelineOptions(
    use_vlm=True,  # Use visual language model
    vlm_model="microsoft/layoutlmv3-base"
)

converter = DocumentConverter(pipeline_options=options)
result = converter.convert("complex_layout.pdf")
```

## Automatic Speech Recognition (ASR)

```python
# Process audio files
result = converter.convert("meeting_recording.mp3")

# Access transcription
transcript = result.document.export_to_text()
print(transcript)

# Access with timestamps
for segment in result.document.segments:
    print(f"[{segment.start_time} - {segment.end_time}] {segment.text}")
```

## Output Quality Control

```python
from docling.datamodel.base_models import OutputFormat

# Validate output
result = converter.convert("document.pdf")

# Check quality metrics
if result.status == "success":
    print(f"Pages processed: {len(result.document.pages)}")
    print(f"Tables found: {len(result.document.tables)}")
    print(f"Images found: {len(result.document.images)}")

# Verify completeness
expected_pages = 10
actual_pages = len(result.document.pages)
if actual_pages != expected_pages:
    print(f"Warning: Expected {expected_pages}, got {actual_pages}")
```

## Best Practices

### 1. Document Preprocessing

```python
# Check file before processing
from pathlib import Path

def preprocess_document(file_path):
    path = Path(file_path)

    # Validate file
    if not path.exists():
        raise FileNotFoundError(f"{file_path} not found")

    # Check size
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > 100:
        print(f"Warning: Large file ({size_mb:.2f} MB)")

    # Check format
    if path.suffix.lower() not in ['.pdf', '.docx', '.pptx']:
        print(f"Warning: Unusual format {path.suffix}")

    return True

if preprocess_document("document.pdf"):
    result = converter.convert("document.pdf")
```

### 2. Chunking for RAG

```python
def chunk_document_for_rag(file_path, chunk_size=1000):
    converter = DocumentConverter()
    result = converter.convert(file_path)

    # Export to markdown
    markdown = result.document.export_to_markdown()

    # Split into chunks
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=200,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "]
    )

    chunks = splitter.split_text(markdown)

    # Add metadata
    chunks_with_metadata = [
        {
            "content": chunk,
            "metadata": {
                "source": file_path,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
        }
        for i, chunk in enumerate(chunks)
    ]

    return chunks_with_metadata
```

### 3. Caching Results

```python
import hashlib
import json
from pathlib import Path

def get_file_hash(file_path):
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def convert_with_cache(file_path, cache_dir="docling_cache"):
    cache_path = Path(cache_dir)
    cache_path.mkdir(exist_ok=True)

    file_hash = get_file_hash(file_path)
    cache_file = cache_path / f"{file_hash}.json"

    # Check cache
    if cache_file.exists():
        with open(cache_file) as f:
            cached_data = json.load(f)
        return cached_data["markdown"]

    # Convert and cache
    converter = DocumentConverter()
    result = converter.convert(file_path)
    markdown = result.document.export_to_markdown()

    with open(cache_file, "w") as f:
        json.dump({"markdown": markdown}, f)

    return markdown
```

## Upcoming Features

According to official documentation, upcoming capabilities include:

- **Metadata Extraction:** Enhanced document metadata
- **Chart Understanding:** Advanced chart parsing
- **Complex Chemistry:** Chemical structure recognition
- **Enhanced VLM:** Improved visual understanding

## Official Resources

- **Main Documentation:** https://docling-project.github.io/docling/
- **GitHub Repository:** https://github.com/docling-project/docling
- **PyPI:** https://pypi.org/project/docling/
- **LangChain Integration:** https://python.langchain.com/docs/integrations/document_loaders/docling/
- **IBM Research:** https://research.ibm.com/blog/docling-generative-AI
- **Official Website:** https://www.docling.ai/

## Version Notes

### Version 2.55.1

- Latest stable release
- Full OCR support
- VLM integration
- ASR capabilities
- Multiple export formats

## Troubleshooting

### Common Issues

```python
# Issue: OCR not working
# Solution: Install tesseract
# brew install tesseract (macOS)
# apt-get install tesseract-ocr (Ubuntu)

# Issue: Memory errors with large PDFs
# Solution: Process in batches
options = ConversionOptions(max_num_pages=50)

# Issue: Table extraction failures
# Solution: Enable accurate mode
options = PipelineOptions(
    do_table_structure=True,
    table_structure_mode=TableFormerMode.ACCURATE
)
```

---

**Quality Rating:** ⭐⭐⭐⭐⭐ Tier 1 - Official Documentation
**Source Type:** Official Project Documentation
**Verification Date:** 2025-10-06
