# 12 - Authentication & Security

## 🎯 Purpose

Provides JWT-based authentication, password hashing, and security headers middleware. Protects API endpoints and user data with industry-standard security practices.

## 🛠 Technical Stack

- **JWT (JSON Web Tokens):** Stateless authentication
- **python-jose:** JWT creation and validation
- **passlib + bcrypt:** Password hashing
- **FastAPI Security:** OAuth2PasswordBearer dependency injection

## 📂 Key Files

### Authentication Service
**apex-memory-system/src/apex_memory/services/auth_service.py** (8,027 bytes)

```python
class AuthService:
    """User authentication and JWT management."""
    
    def register(email: str, password: str, full_name: str) -> User:
        """Register new user with hashed password."""
    
    def login(email: str, password: str) -> str:
        """Return JWT access token (expires 24h)."""
    
    def verify_token(token: str) -> User:
        """Validate JWT and return user."""
    
    def refresh_token(token: str) -> str:
        """Issue new token from valid existing token."""
```

### API Endpoints
**apex-memory-system/src/apex_memory/api/auth.py** (4,141 bytes)

```python
@router.post("/register")
async def register(email: str, password: str, full_name: str):
    """Create new user account."""

@router.post("/login")
async def login(email: str, password: str):
    """Get JWT access token."""

@router.get("/me")
async def get_current_user(user: User = Depends(get_current_user)):
    """Get authenticated user profile."""

@router.post("/refresh")
async def refresh_token(token: str):
    """Refresh JWT token."""
```

### Security Middleware
**apex-memory-system/src/apex_memory/main.py** (lines 48-94)

```python
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """OWASP security headers for all responses."""
    
    async def dispatch(request, call_next):
        response = await call_next(request)
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = "..."
        
        # HSTS (HTTPS enforcement)
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Prevent MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response
```

## Authentication Flow

```
┌─────────────────────────────────────┐
│ 1. User Registration                │
│    POST /api/v1/auth/register       │
│    {email, password, full_name}     │
└─────────────────────────────────────┘
              ↓
    ┌──────────────────┐
    │ Hash Password    │
    │ (bcrypt)         │
    └──────────────────┘
              ↓
    ┌──────────────────┐
    │ Store in DB      │
    │ (PostgreSQL)     │
    └──────────────────┘
              ↓
    ┌──────────────────┐
    │ Return JWT Token │
    └──────────────────┘

┌─────────────────────────────────────┐
│ 2. User Login                       │
│    POST /api/v1/auth/login          │
│    {email, password}                │
└─────────────────────────────────────┘
              ↓
    ┌──────────────────┐
    │ Verify Password  │
    │ (bcrypt.verify)  │
    └──────────────────┘
              ↓
    ┌──────────────────┐
    │ Generate JWT     │
    │ Expires: 24h     │
    └──────────────────┘
              ↓
    Return: {access_token: "eyJ..."}

┌─────────────────────────────────────┐
│ 3. Protected Endpoint Access        │
│    GET /api/v1/query/               │
│    Headers: Authorization: Bearer eyJ...│
└─────────────────────────────────────┘
              ↓
    ┌──────────────────┐
    │ Validate JWT     │
    │ (python-jose)    │
    └──────────────────┘
              ↓
    ┌──────────────────┐
    │ Get User from DB │
    └──────────────────┘
              ↓
    Execute Protected Endpoint
```

## JWT Token Structure

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_uuid",
    "email": "user@example.com",
    "exp": 1698765432,  // Expiration (24h from issue)
    "iat": 1698679032   // Issued at
  },
  "signature": "..."
}
```

## Security Headers (OWASP)

**Applied to all responses:**

1. **Content-Security-Policy**
   - Prevents XSS attacks
   - Restricts script/style sources
   - Allows API calls to Anthropic/OpenAI

2. **Strict-Transport-Security (HSTS)**
   - Enforces HTTPS for 1 year
   - Includes subdomains

3. **X-Frame-Options: DENY**
   - Prevents clickjacking
   - Disallows embedding in iframes

4. **X-Content-Type-Options: nosniff**
   - Prevents MIME-type sniffing
   - Forces declared content types

5. **Referrer-Policy**
   - Controls referrer information
   - Protects user privacy

6. **Permissions-Policy**
   - Disables geolocation, microphone, camera
   - Reduces attack surface

## Password Security

**Hashing:**
- **Algorithm:** bcrypt
- **Rounds:** 12 (default)
- **Salt:** Auto-generated per password

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
hashed = pwd_context.hash("user_password")

# Verify password
is_valid = pwd_context.verify("user_password", hashed)
```

## Configuration

```bash
# JWT Settings
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Password Requirements (enforced in frontend)
MIN_PASSWORD_LENGTH=8
REQUIRE_UPPERCASE=true
REQUIRE_NUMBER=true
REQUIRE_SPECIAL_CHAR=true
```

## Protected Routes

**Frontend (React):**
```tsx
<ProtectedRoute>
  <ConversationsPage />
</ProtectedRoute>
```

**Backend (FastAPI):**
```python
@router.get("/protected")
async def protected_endpoint(
    user: User = Depends(get_current_user)
):
    # Only authenticated users can access
    return {"user_id": user.uuid}
```

## Known Security Considerations

1. **JWT Secret:** Change default secret in production!
2. **HTTPS Required:** HSTS only activates on HTTPS
3. **CORS:** Currently `allow_origins=["*"]` - restrict for production
4. **Rate Limiting:** Not implemented - add for production
5. **Session Management:** JWT is stateless - no server-side revocation

---

**Previous Component:** [11-Configuration-Management](../11-Configuration-Management/README.md)
**Next Component:** [13-Utilities-Scripts](../13-Utilities-Scripts/README.md)
