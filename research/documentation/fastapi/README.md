# FastAPI Documentation

**Version:** 0.118.0
**Last Updated:** 2025-10-06
**Official Source:** https://fastapi.tiangolo.com/

## Overview

FastAPI is a modern, fast (high-performance) web framework for building APIs with Python 3.9+ based on standard Python type hints. It's designed for production-ready applications with automatic API documentation.

## Key Features

- **Fast Performance:** Very high performance, on par with NodeJS and Go
- **Fast Development:** Increase development speed by 200-300%
- **Fewer Bugs:** Reduce human-induced errors by ~40%
- **Intuitive:** Great editor support with auto-completion everywhere
- **Easy:** Designed to be easy to use and learn
- **Standards-Based:** Based on OpenAPI and JSON Schema

## Installation

```bash
pip install fastapi==0.118.0
pip install uvicorn[standard]  # ASGI server
```

## Core API Reference

### FastAPI Class

The main application class.

```python
from fastapi import FastAPI

app = FastAPI(
    title="My API",
    description="API for Apex Memory System",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)
```

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `title` | str | API title for documentation |
| `description` | str | API description |
| `version` | str | API version |
| `openapi_url` | str | OpenAPI schema endpoint (default: `/openapi.json`) |
| `docs_url` | str | Swagger UI path (default: `/docs`) |
| `redoc_url` | str | ReDoc path (default: `/redoc`) |
| `dependencies` | List[Depends] | Global dependencies |
| `middleware` | List | Middleware stack |

### Path Operations

Define API endpoints using decorators.

```python
from fastapi import FastAPI, Path, Query, Body
from typing import Optional

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(
    item_id: int = Path(..., title="The ID of the item"),
    q: Optional[str] = Query(None, max_length=50)
):
    return {"item_id": item_id, "q": q}

@app.post("/items/")
async def create_item(item: dict = Body(...)):
    return item
```

### Request/Response Models with Pydantic

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class Document(BaseModel):
    id: Optional[int] = None
    content: str = Field(..., min_length=1)
    metadata: dict = {}
    embedding: Optional[List[float]] = None

class DocumentResponse(BaseModel):
    id: int
    content: str
    created_at: str

@app.post("/documents/", response_model=DocumentResponse)
async def create_document(document: Document):
    # Process document
    return DocumentResponse(
        id=1,
        content=document.content,
        created_at="2025-10-06T12:00:00"
    )
```

### Dependency Injection

Powerful dependency injection system for code reuse.

```python
from fastapi import Depends, HTTPException, status
from typing import Annotated

# Define dependency
def get_api_key(api_key: str = Header(...)):
    if api_key != "secret-key":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return api_key

# Use dependency
@app.get("/secure-data/")
async def get_secure_data(
    api_key: Annotated[str, Depends(get_api_key)]
):
    return {"data": "This is secure"}
```

#### Database Session Dependency

```python
from sqlalchemy.orm import Session
from database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/{user_id}")
async def read_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    user = db.query(User).filter(User.id == user_id).first()
    return user
```

### Error Handling

```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id not in items:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"X-Error": "Custom header"}
        )
    return items[item_id]
```

#### Custom Exception Handlers

```python
from fastapi import Request
from fastapi.responses import JSONResponse

class CustomException(Exception):
    def __init__(self, name: str):
        self.name = name

@app.exception_handler(CustomException)
async def custom_exception_handler(
    request: Request,
    exc: CustomException
):
    return JSONResponse(
        status_code=418,
        content={"message": f"Error: {exc.name}"}
    )
```

### Background Tasks

Run tasks after returning response.

```python
from fastapi import BackgroundTasks

def write_log(message: str):
    with open("log.txt", "a") as log:
        log.write(message)

@app.post("/send-notification/")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(write_log, f"Email sent to {email}")
    return {"message": "Notification sent"}
```

### Middleware

Add custom middleware for request/response processing.

```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import time

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# GZip Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### File Upload/Download

```python
from fastapi import File, UploadFile
from fastapi.responses import FileResponse

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents)
    }

@app.get("/download/{filename}")
async def download_file(filename: str):
    return FileResponse(
        path=f"files/{filename}",
        filename=filename,
        media_type="application/octet-stream"
    )
```

## RAG API Example

Complete example for a RAG system endpoint.

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import openai
from qdrant_client import QdrantClient

app = FastAPI(title="Apex Memory RAG API")

# Models
class QueryRequest(BaseModel):
    query: str
    k: int = 5

class DocumentChunk(BaseModel):
    content: str
    score: float
    metadata: dict

class QueryResponse(BaseModel):
    answer: str
    sources: List[DocumentChunk]

# Dependencies
def get_qdrant_client():
    return QdrantClient(url="http://localhost:6333")

def get_openai_client():
    return openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# RAG Endpoint
@app.post("/query", response_model=QueryResponse)
async def query_rag(
    request: QueryRequest,
    qdrant: QdrantClient = Depends(get_qdrant_client),
    openai_client: openai.OpenAI = Depends(get_openai_client)
):
    try:
        # 1. Embed query
        embedding_response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=request.query
        )
        query_vector = embedding_response.data[0].embedding

        # 2. Search vector store
        search_results = qdrant.search(
            collection_name="documents",
            query_vector=query_vector,
            limit=request.k
        )

        # 3. Extract context
        context = "\n\n".join([
            result.payload["content"]
            for result in search_results
        ])

        # 4. Generate answer
        completion = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Answer based on context."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuery: {request.query}"}
            ]
        )

        answer = completion.choices[0].message.content

        # 5. Format response
        sources = [
            DocumentChunk(
                content=r.payload["content"],
                score=r.score,
                metadata=r.payload.get("metadata", {})
            )
            for r in search_results
        ]

        return QueryResponse(answer=answer, sources=sources)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Document ingestion endpoint
class DocumentCreate(BaseModel):
    content: str
    metadata: Optional[dict] = {}

@app.post("/documents/")
async def add_document(
    doc: DocumentCreate,
    qdrant: QdrantClient = Depends(get_qdrant_client),
    openai_client: openai.OpenAI = Depends(get_openai_client)
):
    # Generate embedding
    embedding_response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=doc.content
    )
    vector = embedding_response.data[0].embedding

    # Store in vector database
    point_id = hash(doc.content) % (10 ** 8)
    qdrant.upsert(
        collection_name="documents",
        points=[{
            "id": point_id,
            "vector": vector,
            "payload": {
                "content": doc.content,
                "metadata": doc.metadata
            }
        }]
    )

    return {"id": point_id, "status": "created"}
```

## Authentication & Security

### API Key Authentication

```python
from fastapi.security import APIKeyHeader
from fastapi import Security

api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

@app.get("/protected/")
async def protected_route(api_key: str = Depends(verify_api_key)):
    return {"message": "Access granted"}
```

### OAuth2 with JWT

```python
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Verify credentials
    if form_data.username != "admin" or form_data.password != "secret":
        raise HTTPException(status_code=400, detail="Incorrect credentials")

    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}
```

## Testing

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_create_item():
    response = client.post(
        "/items/",
        json={"name": "Test Item", "price": 10.5}
    )
    assert response.status_code == 200
```

## Running the Application

### Development

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### With Gunicorn

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Version 0.118.0 Notes

### Key Changes in 0.118.0

1. **Dependencies with Yield:** Exit code now runs after response is sent (reverted behavior)
2. **Performance improvements** in request handling
3. **Enhanced OpenAPI schema** generation

### Breaking Changes

- Dependencies with `yield` behavior changed - ensure compatibility if using cleanup code

## Best Practices

### 1. Project Structure

```
app/
├── main.py           # FastAPI app initialization
├── api/
│   ├── routes/       # Endpoint definitions
│   ├── dependencies/ # Reusable dependencies
│   └── models/       # Pydantic models
├── core/
│   ├── config.py     # Configuration
│   └── security.py   # Auth logic
└── services/         # Business logic
```

### 2. Configuration Management

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Apex Memory API"
    openai_api_key: str
    qdrant_url: str = "http://localhost:6333"

    class Config:
        env_file = ".env"

settings = Settings()
```

### 3. Async vs Sync

```python
# Use async for I/O-bound operations
@app.get("/async-data/")
async def get_async_data():
    data = await fetch_from_db()
    return data

# Use sync for CPU-bound or blocking operations
@app.get("/sync-data/")
def get_sync_data():
    data = process_heavy_computation()
    return data
```

## Official Resources

- **Main Documentation:** https://fastapi.tiangolo.com/
- **API Reference:** https://fastapi.tiangolo.com/reference/
- **Tutorial:** https://fastapi.tiangolo.com/tutorial/
- **GitHub:** https://github.com/fastapi/fastapi
- **PyPI:** https://pypi.org/project/fastapi/
- **Release Notes:** https://github.com/fastapi/fastapi/releases

## OpenAPI & Documentation

FastAPI automatically generates:

- **OpenAPI schema:** Available at `/openapi.json`
- **Swagger UI:** Interactive docs at `/docs`
- **ReDoc:** Alternative docs at `/redoc`

### Custom OpenAPI Schema

```python
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Custom API",
        version="1.0.0",
        description="Custom OpenAPI schema",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

---

**Quality Rating:** ⭐⭐⭐⭐⭐ Tier 1 - Official Documentation
**Source Type:** Official API Documentation
**Verification Date:** 2025-10-06
