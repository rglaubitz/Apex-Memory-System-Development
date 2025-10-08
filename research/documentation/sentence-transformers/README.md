# Sentence-Transformers Documentation

**Version:** 5.1.1
**Last Updated:** 2025-10-06
**Official Source:** https://sbert.net/

## Overview

Sentence-Transformers (SBERT) is a Python framework for state-of-the-art sentence, text, and image embeddings. It provides an easy method to compute dense vector representations for sentences, paragraphs, and images. The framework is based on PyTorch and Transformers and offers a large collection of pre-trained models.

## Key Features

- **15,000+ Pre-trained Models:** Available on Hugging Face Hub
- **Fast & Efficient:** Optimized for production use
- **Multi-task Support:** Semantic search, clustering, classification
- **Flexible Precision:** float32, int8, binary quantization
- **Multi-GPU Support:** Parallel processing capabilities
- **Task-specific Prompts:** Optimized for different use cases

## Installation

```bash
pip install sentence-transformers==5.1.1
```

### System Requirements

- Python 3.9+
- PyTorch 1.11.0+
- Transformers 4.34.0+

## Core API

### SentenceTransformer Class

The main class for encoding text to embeddings.

#### Initialization

```python
from sentence_transformers import SentenceTransformer

# Load pre-trained model
model = SentenceTransformer('all-mpnet-base-v2')

# With specific device
model = SentenceTransformer(
    'all-MiniLM-L6-v2',
    device='cuda'  # or 'cpu', 'mps'
)

# From local path
model = SentenceTransformer('/path/to/model')
```

#### Key Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `model_name_or_path` | str | Model name or path |
| `device` | str | Device: 'cuda', 'cpu', 'mps' |
| `prompts` | dict | Task-specific prompts |
| `similarity_fn_name` | str | Similarity function: cosine, dot, euclidean, manhattan |
| `cache_folder` | str | Model cache directory |
| `trust_remote_code` | bool | Execute remote code (default: False) |

### Encoding Methods

#### encode() - General Purpose

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-mpnet-base-v2')

# Single sentence
sentence = "This is a test sentence"
embedding = model.encode(sentence)
print(f"Embedding shape: {embedding.shape}")  # (768,)

# Multiple sentences
sentences = [
    "The weather is lovely today",
    "It's so sunny outside",
    "He drove to the stadium"
]
embeddings = model.encode(sentences)
print(f"Embeddings shape: {embeddings.shape}")  # (3, 768)
```

#### encode_query() - Optimized for Queries

```python
# For search queries (asymmetric search)
query = "What is the capital of France?"
query_embedding = model.encode_query(query)
```

#### encode_document() - Optimized for Documents

```python
# For document/passage embeddings
documents = [
    "Paris is the capital of France",
    "Berlin is the capital of Germany",
    "Madrid is the capital of Spain"
]
doc_embeddings = model.encode_document(documents)
```

### Advanced Encoding Options

#### Batch Processing

```python
# Process large datasets efficiently
model = SentenceTransformer('all-mpnet-base-v2')

# With batch size
embeddings = model.encode(
    sentences,
    batch_size=32,
    show_progress_bar=True
)
```

#### Normalization

```python
# Normalize embeddings for cosine similarity
embeddings = model.encode(
    sentences,
    normalize_embeddings=True
)
```

#### Precision Control

```python
# Different precisions for performance/storage tradeoff
embeddings_fp32 = model.encode(sentences, precision='float32')
embeddings_int8 = model.encode(sentences, precision='int8')
embeddings_binary = model.encode(sentences, precision='binary')
```

#### Multi-process Encoding

```python
# Use multiple processes for CPU encoding
pool = model.start_multi_process_pool()

embeddings = model.encode_multi_process(
    sentences,
    pool,
    batch_size=32
)

model.stop_multi_process_pool(pool)
```

## Similarity Computation

### Cosine Similarity

```python
from sentence_transformers import util

# Compute cosine similarity
embeddings1 = model.encode(["sentence 1", "sentence 2"])
embeddings2 = model.encode(["sentence 3", "sentence 4"])

cosine_scores = util.cos_sim(embeddings1, embeddings2)
print(cosine_scores)
```

### Pairwise Similarity

```python
# Compute similarity matrix
sentences = ["sent1", "sent2", "sent3"]
embeddings = model.encode(sentences)

similarity_matrix = util.cos_sim(embeddings, embeddings)
print(similarity_matrix)
```

### Semantic Search

```python
from sentence_transformers import util

# Query and corpus
query = "What is Python?"
corpus = [
    "Python is a programming language",
    "Java is also a programming language",
    "The sky is blue"
]

# Encode
query_embedding = model.encode(query)
corpus_embeddings = model.encode(corpus)

# Find most similar
hits = util.semantic_search(
    query_embedding,
    corpus_embeddings,
    top_k=2
)

for hit in hits[0]:
    print(f"{corpus[hit['corpus_id']]} (Score: {hit['score']:.4f})")
```

## Popular Pre-trained Models

### Recommended Models

```python
# General purpose - Best performance
model = SentenceTransformer('all-mpnet-base-v2')
# Dimensions: 768, Max Seq Length: 384

# Fast & efficient - Smaller model
model = SentenceTransformer('all-MiniLM-L6-v2')
# Dimensions: 384, Max Seq Length: 256

# Multilingual support
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
# Dimensions: 768, 50+ languages

# Large model - Highest quality
model = SentenceTransformer('all-mpnet-base-v2')
# Dimensions: 768
```

### Model Selection Guide

| Use Case | Recommended Model | Dimensions |
|----------|------------------|------------|
| General embedding | all-mpnet-base-v2 | 768 |
| Speed-optimized | all-MiniLM-L6-v2 | 384 |
| Multilingual | paraphrase-multilingual-mpnet-base-v2 | 768 |
| Code search | code-search-net | 768 |
| Question answering | multi-qa-mpnet-base-dot-v1 | 768 |

## Integration with RAG Systems

### Basic RAG Integration

```python
from sentence_transformers import SentenceTransformer, util

# Initialize model
model = SentenceTransformer('all-mpnet-base-v2')

# Documents
documents = [
    "RAG stands for Retrieval Augmented Generation",
    "Vector databases store embeddings",
    "Semantic search finds similar documents"
]

# Create embeddings
doc_embeddings = model.encode(documents, normalize_embeddings=True)

# Query
query = "What is RAG?"
query_embedding = model.encode(query, normalize_embeddings=True)

# Retrieve
hits = util.semantic_search(query_embedding, doc_embeddings, top_k=2)

# Get relevant documents
for hit in hits[0]:
    print(f"Document: {documents[hit['corpus_id']]}")
    print(f"Score: {hit['score']:.4f}\n")
```

### Vector Database Integration

#### With Qdrant

```python
from sentence_transformers import SentenceTransformer
import qdrant_client
from qdrant_client.models import Distance, VectorParams, PointStruct

model = SentenceTransformer('all-mpnet-base-v2')
client = qdrant_client.QdrantClient(url="http://localhost:6333")

# Create collection
client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(
        size=768,  # all-mpnet-base-v2 dimension
        distance=Distance.COSINE
    )
)

# Index documents
documents = ["doc1", "doc2", "doc3"]
embeddings = model.encode(documents)

points = [
    PointStruct(
        id=i,
        vector=embedding.tolist(),
        payload={"text": doc}
    )
    for i, (doc, embedding) in enumerate(zip(documents, embeddings))
]

client.upsert(collection_name="documents", points=points)

# Search
query = "search query"
query_vector = model.encode(query)

results = client.search(
    collection_name="documents",
    query_vector=query_vector.tolist(),
    limit=5
)
```

#### With FAISS

```python
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer('all-mpnet-base-v2')

# Create embeddings
documents = ["doc1", "doc2", "doc3"]
embeddings = model.encode(documents)

# Create FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# Search
query_embedding = model.encode(["query"])
distances, indices = index.search(query_embedding, k=2)

print(f"Top results: {[documents[i] for i in indices[0]]}")
```

### LangChain Integration

```python
from langchain_community.embeddings import HuggingFaceEmbeddings

# Use with LangChain
embeddings = HuggingFaceEmbeddings(
    model_name="all-mpnet-base-v2",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

# Use in LangChain pipeline
from langchain_community.vectorstores import Qdrant
from langchain.schema import Document

docs = [
    Document(page_content="text1"),
    Document(page_content="text2")
]

vectorstore = Qdrant.from_documents(
    docs,
    embeddings,
    url="http://localhost:6333",
    collection_name="langchain_docs"
)
```

## Task-Specific Prompts

```python
# Initialize with prompts
model = SentenceTransformer(
    'all-mpnet-base-v2',
    prompts={
        "query": "Query: ",
        "passage": "Passage: "
    }
)

# Use prompts
query_emb = model.encode("search text", prompt_name="query")
doc_emb = model.encode("document text", prompt_name="passage")
```

## Clustering

```python
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import numpy as np

model = SentenceTransformer('all-mpnet-base-v2')

# Encode sentences
sentences = ["sent1", "sent2", "sent3", "sent4", "sent5"]
embeddings = model.encode(sentences)

# Cluster
num_clusters = 2
clustering_model = KMeans(n_clusters=num_clusters)
clustering_model.fit(embeddings)

# Get cluster assignments
cluster_assignment = clustering_model.labels_

for i, sentence in enumerate(sentences):
    print(f"Sentence: {sentence}")
    print(f"Cluster: {cluster_assignment[i]}\n")
```

## Performance Optimization

### GPU Acceleration

```python
# Use GPU if available
model = SentenceTransformer('all-mpnet-base-v2', device='cuda')

# Check device
print(f"Model device: {model.device}")
```

### Batch Size Tuning

```python
# Optimize batch size for your hardware
embeddings = model.encode(
    large_dataset,
    batch_size=64,  # Adjust based on GPU memory
    show_progress_bar=True
)
```

### Model Quantization

```python
# Use quantized models for faster inference
model = SentenceTransformer('all-MiniLM-L6-v2')

# Binary embeddings for storage efficiency
binary_embeddings = model.encode(
    sentences,
    precision='binary'
)
# 32x storage reduction!
```

## Fine-tuning Custom Models

```python
from sentence_transformers import SentenceTransformer, losses
from sentence_transformers import InputExample
from torch.utils.data import DataLoader

# Load base model
model = SentenceTransformer('all-mpnet-base-v2')

# Prepare training data
train_examples = [
    InputExample(texts=['sentence1', 'sentence2'], label=0.8),
    InputExample(texts=['sentence3', 'sentence4'], label=0.3)
]

train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)

# Define loss
train_loss = losses.CosineSimilarityLoss(model)

# Train
model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=1,
    warmup_steps=100
)

# Save
model.save('custom-model')
```

## Best Practices

### 1. Model Selection

```python
# Choose based on requirements
if speed_critical:
    model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast
elif quality_critical:
    model = SentenceTransformer('all-mpnet-base-v2')  # Best
elif multilingual_needed:
    model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
```

### 2. Normalization for Cosine Similarity

```python
# Always normalize for cosine similarity
embeddings = model.encode(
    sentences,
    normalize_embeddings=True
)
```

### 3. Caching Embeddings

```python
import pickle

# Save embeddings
embeddings = model.encode(documents)
with open('embeddings.pkl', 'wb') as f:
    pickle.dump(embeddings, f)

# Load embeddings
with open('embeddings.pkl', 'rb') as f:
    cached_embeddings = pickle.load(f)
```

### 4. Batch Processing Large Datasets

```python
# Process in chunks for memory efficiency
def encode_large_dataset(texts, batch_size=1000):
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        embeddings = model.encode(batch)
        all_embeddings.append(embeddings)
    return np.vstack(all_embeddings)
```

## Evaluation

```python
from sentence_transformers import evaluation

# Evaluate on test set
evaluator = evaluation.EmbeddingSimilarityEvaluator(
    sentences1=test_sentences1,
    sentences2=test_sentences2,
    scores=test_scores
)

score = evaluator(model)
print(f"Evaluation score: {score}")
```

## Official Resources

- **Main Documentation:** https://sbert.net/
- **API Reference:** https://sbert.net/docs/package_reference/sentence_transformer/SentenceTransformer.html
- **Hugging Face Hub:** https://huggingface.co/sentence-transformers
- **GitHub:** https://github.com/UKPLab/sentence-transformers
- **PyPI:** https://pypi.org/project/sentence-transformers/
- **Pre-trained Models:** https://www.sbert.net/docs/pretrained_models.html

## Version 5.1.1 Notes

### Key Features

- Enhanced multi-GPU support
- Improved quantization (binary embeddings)
- Task-specific prompt routing
- Better Hugging Face Hub integration
- Performance optimizations

### System Requirements

- Python 3.9+
- PyTorch 1.11.0+
- transformers 4.34.0+

## Troubleshooting

### Common Issues

```python
# Issue: CUDA out of memory
# Solution: Reduce batch size
embeddings = model.encode(sentences, batch_size=16)

# Issue: Slow encoding on CPU
# Solution: Use multi-process pool
pool = model.start_multi_process_pool()
embeddings = model.encode_multi_process(sentences, pool)
model.stop_multi_process_pool(pool)

# Issue: Model not found
# Solution: Check model name or download manually
from huggingface_hub import snapshot_download
snapshot_download(repo_id="sentence-transformers/all-mpnet-base-v2")
```

---

**Quality Rating:** ⭐⭐⭐⭐⭐ Tier 1 - Official Documentation
**Source Type:** Official Library Documentation
**Verification Date:** 2025-10-06
