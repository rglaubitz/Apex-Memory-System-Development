# LangChain Documentation

**Version:** 0.3.27
**Last Updated:** 2025-10-06
**Official Source:** https://python.langchain.com/

## Overview

LangChain is a framework for developing applications powered by large language models (LLMs). Version 0.3.27 provides a comprehensive suite of tools for building RAG systems, agents, and complex AI workflows.

## Core Architecture

LangChain 0.3 is built on modular packages:

- **langchain-core (0.3.76):** Base abstractions and universal invocation protocol (Runnables)
- **langchain (0.3.27):** Main orchestration package
- **langchain-community (0.3.30):** Community integrations
- **langchain-openai (0.3.33):** OpenAI-specific integrations

## Key Modules for RAG Systems

### 1. Embeddings

LangChain provides a unified interface for embedding models.

#### OpenAI Embeddings Integration

```python
from langchain_openai import OpenAIEmbeddings

# Initialize embeddings
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key="YOUR_API_KEY"
)

# Embed documents
doc_vectors = embeddings.embed_documents([
    "First document",
    "Second document"
])

# Embed query
query_vector = embeddings.embed_query("Search query")
```

#### Embedding Configuration

```python
from langchain.embeddings import init_embeddings

# Initialize with caching
embeddings = init_embeddings(
    model_name="text-embedding-3-small",
    cache=True  # Enable embedding cache
)
```

### 2. Document Loaders

LangChain supports multiple document formats for RAG pipelines.

```python
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    DirectoryLoader
)

# PDF loading
pdf_loader = PyPDFLoader("document.pdf")
documents = pdf_loader.load()

# Directory loading with filtering
loader = DirectoryLoader(
    "docs/",
    glob="**/*.md",
    loader_cls=TextLoader
)
docs = loader.load()
```

#### Docling Integration

```python
from langchain_community.document_loaders import DoclingLoader

# Use Docling for advanced PDF parsing
loader = DoclingLoader(
    file_path="complex_document.pdf",
    export_format="markdown"
)
documents = loader.load()
```

### 3. Text Splitters

Split documents into chunks for embedding and retrieval.

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)

chunks = text_splitter.split_documents(documents)
```

#### Token-Based Splitting

```python
from langchain.text_splitter import TokenTextSplitter

splitter = TokenTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
```

### 4. Vector Stores

LangChain integrates with multiple vector databases.

#### Qdrant Integration

```python
from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings
import qdrant_client

client = qdrant_client.QdrantClient(url="http://localhost:6333")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Create vector store
vectorstore = Qdrant(
    client=client,
    collection_name="documents",
    embeddings=embeddings
)

# Add documents
vectorstore.add_documents(documents)

# Similarity search
results = vectorstore.similarity_search(
    "query text",
    k=5
)
```

#### PostgreSQL with pgvector

```python
from langchain_community.vectorstores import PGVector

connection_string = "postgresql://user:password@localhost:5432/vectordb"

vectorstore = PGVector(
    connection_string=connection_string,
    embedding_function=embeddings,
    collection_name="my_collection"
)
```

### 5. Retrievers

Advanced retrieval strategies for RAG systems.

#### Basic Retriever

```python
# Convert vector store to retriever
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)

# Retrieve documents
docs = retriever.get_relevant_documents("query")
```

#### Contextual Compression Retriever

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_openai import OpenAI

llm = OpenAI(temperature=0)
compressor = LLMChainExtractor.from_llm(llm)

compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=retriever
)

# Get compressed, relevant documents
compressed_docs = compression_retriever.get_relevant_documents(
    "What is the main topic?"
)
```

#### Multi-Query Retriever

```python
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(temperature=0)

multi_query_retriever = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(),
    llm=llm
)

# Automatically generates multiple query variations
docs = multi_query_retriever.get_relevant_documents(
    "original query"
)
```

#### Parent Document Retriever

```python
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore

# Store for parent documents
store = InMemoryStore()

parent_retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter
)
```

### 6. Chains

Build RAG pipelines using chains.

#### Retrieval QA Chain

```python
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4", temperature=0)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)

# Query the chain
result = qa_chain({"query": "What is the main topic?"})
print(result["result"])
print(result["source_documents"])
```

#### Conversational Retrieval Chain

```python
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

conversation_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory
)

# Maintain conversation context
response = conversation_chain({"question": "What is RAG?"})
```

### 7. Runnables (LCEL)

LangChain Expression Language for composable chains.

```python
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# Define RAG chain with LCEL
template = """Answer the question based only on the following context:
{context}

Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Invoke chain
answer = rag_chain.invoke("What is the main topic?")
```

## API Reference

### Core Classes

| Class | Module | Description |
|-------|--------|-------------|
| `Embeddings` | langchain.embeddings | Base embeddings interface |
| `BaseRetriever` | langchain.retrievers | Base retriever interface |
| `VectorStore` | langchain.vectorstores | Base vector store interface |
| `BaseChain` | langchain.chains | Base chain interface |
| `BaseLLM` | langchain.llms | Base LLM interface |
| `ChatModel` | langchain.chat_models | Chat model interface |

### Document Models

```python
from langchain.schema import Document

# Document structure
doc = Document(
    page_content="The actual text content",
    metadata={
        "source": "document.pdf",
        "page": 1,
        "chunk_id": "abc123"
    }
)
```

## Configuration & Best Practices

### 1. Environment Setup

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Set API keys
os.environ["OPENAI_API_KEY"] = "your-api-key"
```

### 2. Caching

```python
from langchain.cache import InMemoryCache
from langchain.globals import set_llm_cache

# Enable LLM caching
set_llm_cache(InMemoryCache())
```

### 3. Callbacks

```python
from langchain.callbacks import StdOutCallbackHandler

# Add debugging callbacks
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    callbacks=[StdOutCallbackHandler()]
)
```

### 4. Error Handling

```python
from langchain.schema import OutputParserException

try:
    result = chain.run("query")
except OutputParserException as e:
    print(f"Parsing error: {e}")
except Exception as e:
    print(f"Chain error: {e}")
```

## Pydantic 2 Support

LangChain 0.3 fully supports Pydantic 2.x:

```python
from pydantic import BaseModel, Field
from typing import List

class RAGConfig(BaseModel):
    collection_name: str = Field(..., description="Vector store collection")
    chunk_size: int = Field(1000, ge=100, le=2000)
    k: int = Field(5, description="Number of documents to retrieve")

config = RAGConfig(
    collection_name="documents",
    chunk_size=1000,
    k=5
)
```

## Migration from 0.2.x to 0.3.x

### Breaking Changes

1. **Pydantic 2 Migration:** All packages now use Pydantic 2 internally
2. **Import Paths:** Some imports moved to more specific packages

```python
# Old (0.2.x)
from langchain.embeddings import OpenAIEmbeddings

# New (0.3.x)
from langchain_openai import OpenAIEmbeddings
```

### Compatibility

- **Pydantic:** v2.x required (no bridge needed)
- **Python:** 3.9+ required
- **Deprecation:** v0.3 docs deprecated with v1.0 release (October 2025)

## Official Resources

- **Main Documentation:** https://python.langchain.com/
- **API Reference:** https://python.langchain.com/api_reference/
- **v0.3 Docs:** https://python.langchain.com/docs/versions/v0_3/
- **GitHub:** https://github.com/langchain-ai/langchain
- **Release Announcement:** https://blog.langchain.com/announcing-langchain-v0-3/
- **Community:** https://github.com/langchain-ai/langchain/discussions

## Package Versions

```bash
pip install langchain==0.3.27
pip install langchain-core==0.3.76
pip install langchain-openai==0.3.33
pip install langchain-community==0.3.30
```

## Advanced RAG Patterns

### Hybrid Search

```python
from langchain.retrievers import EnsembleRetriever

# Combine multiple retrievers
ensemble_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.5, 0.5]
)
```

### Re-ranking

```python
from langchain.retrievers.document_compressors import CohereRerank

reranker = CohereRerank(
    model="rerank-english-v2.0",
    top_n=3
)

compression_retriever = ContextualCompressionRetriever(
    base_compressor=reranker,
    base_retriever=retriever
)
```

### Time-Weighted Retrieval

```python
from langchain.retrievers import TimeWeightedVectorStoreRetriever

time_retriever = TimeWeightedVectorStoreRetriever(
    vectorstore=vectorstore,
    decay_rate=0.01,
    k=5
)
```

## Memory Management

```python
from langchain.memory import (
    ConversationBufferMemory,
    ConversationBufferWindowMemory,
    VectorStoreBackedMemory
)

# Token-based memory
memory = ConversationBufferWindowMemory(
    k=5,  # Keep last 5 interactions
    return_messages=True
)

# Vector-backed memory
vector_memory = VectorStoreBackedMemory(
    vectorstore=vectorstore,
    k=3
)
```

---

**Quality Rating:** ⭐⭐⭐⭐⭐ Tier 1 - Official Documentation
**Source Type:** Official API Documentation
**Verification Date:** 2025-10-06
