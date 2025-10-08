# Pydantic Documentation

**Version:** 2.11.10
**Last Updated:** 2025-10-06
**Official Source:** https://docs.pydantic.dev/

## Overview

Pydantic is the most widely used data validation library for Python. Version 2.x features a core validation logic written in Rust, making it among the fastest data validation libraries available. Used by major companies including all FAANG organizations.

## Key Features

- **Fast Performance:** Core validation written in Rust
- **Type Hints Integration:** Leverages Python 3.9+ type annotations
- **Automatic Validation:** Validates data on model instantiation
- **JSON Schema Generation:** Auto-generates schemas for API docs
- **IDE Support:** Full autocomplete and type checking
- **Customizable:** Extensive validation and serialization options

## Installation

```bash
pip install pydantic==2.11.10
```

### With Email Validation

```bash
pip install pydantic[email]==2.11.10
```

## Core Concepts

### BaseModel

The foundation of Pydantic data validation.

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    is_active: bool = True
    metadata: Optional[dict] = None

# Automatic validation
user = User(
    id=1,
    name="John Doe",
    email="john@example.com",
    created_at="2025-10-06T12:00:00"
)

print(user.id)  # 1
print(user.created_at)  # datetime object
```

### Field Validation

Use `Field` for advanced validation and metadata.

```python
from pydantic import BaseModel, Field
from typing import List

class Document(BaseModel):
    id: int = Field(..., ge=1, description="Unique document ID")
    content: str = Field(..., min_length=1, max_length=10000)
    tags: List[str] = Field(default_factory=list, max_length=10)
    score: float = Field(0.0, ge=0.0, le=1.0)
    embedding: List[float] = Field(..., min_length=384, max_length=1536)

doc = Document(
    id=1,
    content="Sample document",
    embedding=[0.1] * 768
)
```

### Type Coercion

Pydantic automatically converts compatible types.

```python
from pydantic import BaseModel

class Item(BaseModel):
    id: int
    price: float
    quantity: int

# String to int/float conversion
item = Item(id="123", price="99.99", quantity="5")

print(item.id)       # 123 (int)
print(item.price)    # 99.99 (float)
print(item.quantity) # 5 (int)
```

## Validation Modes

### Lax Mode (Default)

Attempts type coercion.

```python
from pydantic import BaseModel

class Model(BaseModel):
    value: int

# Lax mode: converts string to int
m = Model(value="123")  # ✓ Works
```

### Strict Mode

No type coercion, exact types required.

```python
from pydantic import BaseModel, ConfigDict

class StrictModel(BaseModel):
    model_config = ConfigDict(strict=True)
    value: int

# Strict mode: requires exact type
m = StrictModel(value=123)     # ✓ Works
# m = StrictModel(value="123")  # ✗ Fails
```

## Custom Validators

### Field Validators

```python
from pydantic import BaseModel, field_validator
from typing import List

class DocumentModel(BaseModel):
    content: str
    tags: List[str]

    @field_validator('content')
    @classmethod
    def content_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Content cannot be empty')
        return v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        if len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        return [tag.lower() for tag in v]
```

### Model Validators

```python
from pydantic import BaseModel, model_validator

class SearchQuery(BaseModel):
    query: str
    limit: int
    offset: int

    @model_validator(mode='after')
    def check_pagination(self) -> 'SearchQuery':
        if self.offset > 10000:
            raise ValueError('Offset too large')
        if self.limit > 100:
            raise ValueError('Limit too large')
        return self
```

## RAG System Models

### Document Models

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class DocumentMetadata(BaseModel):
    source: str
    page: Optional[int] = None
    chunk_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    custom_fields: Dict[str, str] = Field(default_factory=dict)

class DocumentChunk(BaseModel):
    id: str = Field(..., description="Unique chunk identifier")
    content: str = Field(..., min_length=1, max_length=5000)
    embedding: List[float] = Field(..., min_length=384)
    metadata: DocumentMetadata
    score: Optional[float] = Field(None, ge=0.0, le=1.0)

    @field_validator('embedding')
    @classmethod
    def validate_embedding_dimension(cls, v: List[float]) -> List[float]:
        allowed_dims = [384, 768, 1536]  # Common dimensions
        if len(v) not in allowed_dims:
            raise ValueError(f'Embedding dimension must be one of {allowed_dims}')
        return v
```

### Query Models

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class SearchType(str, Enum):
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    KEYWORD = "keyword"

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    k: int = Field(5, ge=1, le=100, description="Number of results")
    search_type: SearchType = SearchType.SEMANTIC
    filters: Optional[Dict[str, str]] = None
    min_score: float = Field(0.0, ge=0.0, le=1.0)

class QueryResponse(BaseModel):
    answer: str
    sources: List[DocumentChunk]
    total_results: int
    processing_time_ms: float
```

### OpenAI API Models

```python
from pydantic import BaseModel, Field
from typing import List, Literal

class EmbeddingRequest(BaseModel):
    model: Literal["text-embedding-3-small", "text-embedding-3-large"]
    input: str | List[str]
    encoding_format: Literal["float", "base64"] = "float"
    dimensions: Optional[int] = None

    @field_validator('dimensions')
    @classmethod
    def validate_dimensions(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError('Dimensions must be positive')
        return v

class EmbeddingResponse(BaseModel):
    object: str
    data: List[dict]
    model: str
    usage: dict
```

## Configuration

### Model Config

```python
from pydantic import BaseModel, ConfigDict

class ConfiguredModel(BaseModel):
    model_config = ConfigDict(
        strict=False,              # Allow type coercion
        validate_assignment=True,  # Validate on attribute assignment
        validate_default=True,     # Validate default values
        frozen=False,              # Allow mutations
        extra='forbid',            # Forbid extra fields
        str_strip_whitespace=True, # Strip whitespace from strings
        str_max_length=1000        # Global string length limit
    )

    name: str
    value: int
```

### Common Config Options

| Option | Type | Description |
|--------|------|-------------|
| `strict` | bool | Strict type validation |
| `validate_assignment` | bool | Validate on assignment |
| `extra` | str | 'forbid', 'allow', 'ignore' extra fields |
| `frozen` | bool | Make model immutable |
| `populate_by_name` | bool | Allow field population by name |
| `json_schema_extra` | dict | Extra JSON schema metadata |

## Serialization

### Model Dump

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str
    password: str

user = User(id=1, name="John", email="john@example.com", password="secret")

# To dict
user_dict = user.model_dump()

# Exclude fields
user_dict = user.model_dump(exclude={'password'})

# Include only specific fields
user_dict = user.model_dump(include={'id', 'name'})
```

### JSON Serialization

```python
# To JSON string
user_json = user.model_dump_json()

# With exclusions
user_json = user.model_dump_json(exclude={'password'})

# From JSON
user = User.model_validate_json(user_json)
```

### Custom Serialization

```python
from pydantic import BaseModel, field_serializer

class Document(BaseModel):
    content: str
    embedding: List[float]

    @field_serializer('embedding')
    def serialize_embedding(self, embedding: List[float]) -> List[float]:
        # Round to 4 decimal places for storage
        return [round(x, 4) for x in embedding]
```

## Error Handling

### Validation Errors

```python
from pydantic import BaseModel, ValidationError

class Item(BaseModel):
    id: int
    price: float

try:
    item = Item(id="invalid", price="not_a_number")
except ValidationError as e:
    print(e.json())
    # Detailed error information
    for error in e.errors():
        print(f"Field: {error['loc']}")
        print(f"Error: {error['msg']}")
        print(f"Type: {error['type']}")
```

### Custom Error Messages

```python
from pydantic import BaseModel, Field, field_validator

class Document(BaseModel):
    content: str = Field(..., description="Document content")

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        if len(v) < 10:
            raise ValueError('Content must be at least 10 characters')
        if len(v) > 10000:
            raise ValueError('Content exceeds maximum length of 10000 characters')
        return v
```

## Integration Examples

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List

app = FastAPI()

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    k: int = Field(5, ge=1, le=100)

class QueryResponse(BaseModel):
    results: List[str]
    count: int

@app.post("/search", response_model=QueryResponse)
async def search(request: QueryRequest):
    # Pydantic automatically validates request
    # FastAPI automatically serializes response
    return QueryResponse(
        results=["result1", "result2"],
        count=2
    )
```

### LangChain Integration

```python
from pydantic import BaseModel, Field
from typing import List
from langchain.schema import Document

class DocumentModel(BaseModel):
    page_content: str
    metadata: dict = Field(default_factory=dict)

    def to_langchain_doc(self) -> Document:
        return Document(
            page_content=self.page_content,
            metadata=self.metadata
        )

    @classmethod
    def from_langchain_doc(cls, doc: Document) -> 'DocumentModel':
        return cls(
            page_content=doc.page_content,
            metadata=doc.metadata
        )
```

### Vector Database Models

```python
from pydantic import BaseModel, Field
from typing import List, Dict
import uuid

class VectorPoint(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    vector: List[float] = Field(..., min_length=384)
    payload: Dict[str, any] = Field(default_factory=dict)

    @field_validator('vector')
    @classmethod
    def validate_vector_values(cls, v: List[float]) -> List[float]:
        # Ensure all values are finite
        if not all(isinstance(x, (int, float)) and abs(x) < float('inf') for x in v):
            raise ValueError('Vector must contain finite numbers')
        return v

class CollectionConfig(BaseModel):
    name: str = Field(..., pattern=r'^[a-zA-Z0-9_-]+$')
    dimension: int = Field(..., ge=1)
    distance: str = Field("cosine", pattern=r'^(cosine|dot|euclidean)$')
```

## Advanced Patterns

### Nested Models

```python
from pydantic import BaseModel
from typing import List

class Address(BaseModel):
    street: str
    city: str
    country: str

class Company(BaseModel):
    name: str
    address: Address

class Employee(BaseModel):
    name: str
    company: Company
    skills: List[str]

employee = Employee(
    name="John",
    company={
        "name": "TechCorp",
        "address": {
            "street": "123 Main St",
            "city": "San Francisco",
            "country": "USA"
        }
    },
    skills=["Python", "FastAPI"]
)
```

### Generic Models

```python
from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar('T')

class Response(BaseModel, Generic[T]):
    data: T
    success: bool
    message: str

class User(BaseModel):
    id: int
    name: str

# Type-safe response
user_response = Response[User](
    data=User(id=1, name="John"),
    success=True,
    message="User retrieved"
)

list_response = Response[List[User]](
    data=[User(id=1, name="John"), User(id=2, name="Jane")],
    success=True,
    message="Users retrieved"
)
```

### Computed Fields

```python
from pydantic import BaseModel, computed_field

class Rectangle(BaseModel):
    width: float
    height: float

    @computed_field
    @property
    def area(self) -> float:
        return self.width * self.height

rect = Rectangle(width=5, height=10)
print(rect.area)  # 50.0
print(rect.model_dump())  # Includes 'area': 50.0
```

## Version 2.11 Features

### Build Time Performance

Version 2.11 focused on build time performance with up to 2x improvement in schema build times.

### Key Improvements

- **Faster Schema Generation:** Up to 2x faster model creation
- **Optimized Validation:** Rust-based core for speed
- **Better Type Hints:** Enhanced IDE support
- **Improved Error Messages:** More detailed validation errors

## Migration from v1 to v2

### Key Changes

```python
# v1
from pydantic import BaseModel, validator

class Model(BaseModel):
    value: int

    @validator('value')
    def check_value(cls, v):
        return v

    class Config:
        validate_assignment = True

# v2
from pydantic import BaseModel, field_validator, ConfigDict

class Model(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    value: int

    @field_validator('value')
    @classmethod
    def check_value(cls, v: int) -> int:
        return v
```

### Breaking Changes

1. **Config:** `class Config` → `model_config = ConfigDict()`
2. **Validators:** `@validator` → `@field_validator` / `@model_validator`
3. **Dict conversion:** `.dict()` → `.model_dump()`
4. **JSON:** `.json()` → `.model_dump_json()`
5. **Parse:** `.parse_obj()` → `.model_validate()`

## Best Practices

### 1. Use Type Hints

```python
from pydantic import BaseModel
from typing import List, Optional

class GoodModel(BaseModel):
    items: List[str]  # ✓ Explicit type
    count: Optional[int] = None  # ✓ Clear optional

class AvoidModel(BaseModel):
    items: list  # ✗ Avoid generic list
    count = None  # ✗ Unclear type
```

### 2. Validate Complex Logic in Model Validators

```python
from pydantic import BaseModel, model_validator

class DateRange(BaseModel):
    start_date: datetime
    end_date: datetime

    @model_validator(mode='after')
    def check_dates(self) -> 'DateRange':
        if self.end_date <= self.start_date:
            raise ValueError('end_date must be after start_date')
        return self
```

### 3. Use Field for Metadata

```python
from pydantic import BaseModel, Field

class APIModel(BaseModel):
    id: int = Field(..., description="Unique identifier", example=123)
    name: str = Field(..., min_length=1, max_length=100, example="John Doe")
```

## Official Resources

- **Main Documentation:** https://docs.pydantic.dev/latest/
- **API Reference:** https://docs.pydantic.dev/latest/api/
- **Migration Guide:** https://docs.pydantic.dev/latest/migration/
- **GitHub:** https://github.com/pydantic/pydantic
- **PyPI:** https://pypi.org/project/pydantic/
- **v2.11 Release:** https://pydantic.dev/articles/pydantic-v2-11-release

## Troubleshooting

### Common Issues

```python
# Issue: ValidationError on valid data
# Solution: Check for strict mode
class Model(BaseModel):
    model_config = ConfigDict(strict=False)  # Allow coercion

# Issue: Extra fields ignored
# Solution: Configure extra handling
class Model(BaseModel):
    model_config = ConfigDict(extra='forbid')  # Raise error on extra

# Issue: Slow validation
# Solution: Disable unnecessary features
class Model(BaseModel):
    model_config = ConfigDict(
        validate_assignment=False,  # Skip assignment validation
        validate_default=False      # Skip default validation
    )
```

---

**Quality Rating:** ⭐⭐⭐⭐⭐ Tier 1 - Official Documentation
**Source Type:** Official Library Documentation
**Verification Date:** 2025-10-06
