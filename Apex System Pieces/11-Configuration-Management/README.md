# 11 - Configuration Management

## 🎯 Purpose

Centralized configuration using Pydantic Settings for type-safe environment variable management. Provides validation, defaults, and easy access to all system settings.

## 🛠 Technical Stack

- **Pydantic Settings:** Type-safe config
- **python-dotenv:** .env file loading
- **Environment Variables:** 12-factor app pattern

## 📂 Key Files

**apex-memory-system/src/apex_memory/config/settings.py** (~200 lines)

```python
class Settings(BaseSettings):
    """Type-safe application settings."""
    
    # Application
    app_env: Literal["development", "staging", "production"]
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    
    # Databases (with property constructors)
    neo4j_uri: str
    postgres_host: str
    qdrant_host: str
    redis_host: str
    
    @property
    def postgres_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    # API Keys
    openai_api_key: str  # Required
    anthropic_api_key: str  # Required
    
    # Feature Flags
    graphiti_enabled: bool = True
    enable_temporal: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )
```

## Configuration Categories

### 1. Application Settings
```bash
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=true
LOG_LEVEL=INFO
```

### 2. Database Connections
```bash
# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=apexmemory2024

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=apex
POSTGRES_PASSWORD=apexmemory2024
POSTGRES_DB=apex_memory
POSTGRES_MIN_POOL_SIZE=2
POSTGRES_MAX_POOL_SIZE=20

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### 3. API Keys
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### 4. Feature Flags
```bash
GRAPHITI_ENABLED=true
ENABLE_TEMPORAL=true
ENABLE_SEMANTIC_CACHE=true
```

### 5. Performance Tuning
```bash
QUERY_TIMEOUT_SECONDS=30
INGESTION_BATCH_SIZE=50
CACHE_TTL_SECONDS=3600
MAX_CONCURRENT_REQUESTS=100
```

## Usage

```python
from apex_memory.config import Settings

# Load settings (reads from .env)
settings = Settings()

# Access type-safe properties
print(settings.postgres_url)  # Auto-constructed
print(settings.app_env)  # Validated: development|staging|production
print(settings.openai_api_key)  # Must be set or ValueError

# Use in service initialization
neo4j_driver = GraphDatabase.driver(
    settings.neo4j_uri,
    auth=(settings.neo4j_user, settings.neo4j_password)
)
```

## Validation

```python
# Pydantic validates on load:

# ✅ Valid
APP_PORT=8000  # int conversion

# ❌ Invalid
APP_PORT=invalid  # ValidationError: value is not a valid integer

# ❌ Missing required
# OPENAI_API_KEY not set → ValidationError: field required
```

---

**Previous Component:** [10-Monitoring-Observability](../10-Monitoring-Observability/README.md)
**Next Component:** [12-Authentication-Security](../12-Authentication-Security/README.md)
