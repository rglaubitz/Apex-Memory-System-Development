# UI/UX Enhancements - Implementation Guide

**Upgrade:** UI/UX Enhancements
**Document:** Step-by-Step Implementation Guide
**Status:** 🔧 Ready for Implementation
**Last Updated:** 2025-10-21

---

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites & Setup](#prerequisites--setup)
3. [Phase 1: Authentication Foundation (Week 1)](#phase-1-authentication-foundation-week-1)
4. [Phase 2: AI Conversation Hub (Week 2)](#phase-2-ai-conversation-hub-week-2)
5. [Phase 2.5: Claude Agents SDK Integration (Week 3)](#phase-25-claude-agents-sdk-integration-week-3)
6. [Phase 3: Apple Minimalist Engagement (Weeks 4-5)](#phase-3-apple-minimalist-engagement-weeks-4-5)
7. [Phase 4: Collaboration & Polish (Weeks 6-7)](#phase-4-collaboration--polish-weeks-6-7)
8. [Testing Strategy](#testing-strategy)
9. [Deployment Guide](#deployment-guide)

---

## Introduction

### Purpose

This document provides **complete step-by-step instructions** for implementing the UI/UX Enhancements upgrade following a **research-first, Apple minimalist design** approach.

### How to Use This Guide

**Before implementing each phase:**
1. ✅ Read the relevant research documentation (linked throughout)
2. ✅ Review the phase in PLANNING.md
3. ✅ Follow the step-by-step instructions below
4. ✅ Run tests after each major step
5. ✅ Check success criteria before moving to next phase

**Research Documentation:**
- All research is chunked into focused files (~150 lines each)
- Use `research/documentation/INDEX.md` to navigate
- Reference `CLAUDE-QUICK-REFERENCE.md` for quick patterns

### Implementation Philosophy

**Research-First Principles:**
- Every implementation decision backed by Tier 1-2 sources
- Read research chunks BEFORE implementing
- Reference chunks in code comments
- Follow documented patterns exactly

**Apple Minimalist Design:**
- Sleek, simple, gorgeous, expensive-looking
- **Not busy** - remove until it hurts
- Monochrome (90%) + single accent (10%)
- Typography-first, generous spacing
- Subtle animations only (fade/slide, no bounce)

---

## Prerequisites & Setup

### Environment Requirements

**Backend:**
- Python 3.11+
- PostgreSQL 14+ (with pgvector extension)
- Redis 7+
- Claude API key (Anthropic)

**Frontend:**
- Node.js 18+
- npm 9+
- Modern browser (Chrome, Firefox, Safari, Edge)

**Development Tools:**
- Git 2.30+
- Docker & Docker Compose (for databases)
- Code editor (VSCode, Cursor, etc.)

### Installation Steps

**1. Clone and Setup Repository**

```bash
# Navigate to main codebase
cd apex-memory-system

# Activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

**2. Install Frontend Dependencies**

```bash
# Navigate to frontend directory
cd src/apex_memory/frontend

# Install dependencies
npm install

# Install additional dependencies for UI/UX enhancements
npm install react-router-dom@^6.21.3 \
            zustand@^4.5.0 \
            react-hook-form@^7.49.3 \
            zod@^3.22.4 \
            @tanstack/react-query@^5.17.19 \
            react-hot-toast@^2.4.1 \
            ai@^3.0.0 \
            react-syntax-highlighter@^15.5.0 \
            recharts@^2.10.4

# Install Shadcn/ui CLI
npx shadcn@latest init
```

**3. Configure Environment Variables**

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add:
# - OPENAI_API_KEY
# - ANTHROPIC_API_KEY (for Claude)
# - Database connection strings
# - JWT_SECRET_KEY (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
```

**4. Start Development Services**

```bash
# Start databases (Neo4j, PostgreSQL, Redis, Qdrant)
cd docker
docker-compose up -d
cd ..

# Run database migrations
alembic upgrade head

# Start API server
python -m uvicorn apex_memory.main:app --reload --port 8000
```

**5. Verify Setup**

```bash
# Check API health
curl http://localhost:8000/health

# Check frontend dev server
cd src/apex_memory/frontend
npm run dev

# Open browser: http://localhost:3000
```

---

## Phase 1: Authentication Foundation (Week 1)

**Priority:** 🔴 BLOCKER for production
**Timeline:** 5 days, 25 tasks, 12 tests
**Research:** JWT best practices, FastAPI security patterns

### Overview

Implement secure user authentication with JWT tokens, role-based access control, and protected routes.

### Day 1: Backend Foundation

#### Step 1.1: Create User Database Schema

**File:** `apex-memory-system/alembic/versions/001_add_users.py`

```python
"""Add users and authentication tables

Revision ID: 001
Create Date: 2025-10-21
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Users table
    op.create_table(
        'users',
        sa.Column('uuid', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('username', sa.String(100), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255)),
        sa.Column('role', sa.String(50), server_default='user', nullable=False),
        sa.Column('is_active', sa.Boolean, server_default='true', nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text('NOW()'), nullable=False),
        sa.Column('last_login', sa.TIMESTAMP),
        sa.Column('preferences', postgresql.JSONB, server_default='{}'),
    )

    # Create indexes
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_username', 'users', ['username'])

    # API keys table
    op.create_table(
        'api_keys',
        sa.Column('uuid', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_uuid', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.uuid'), nullable=False),
        sa.Column('key_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text('NOW()'), nullable=False),
        sa.Column('expires_at', sa.TIMESTAMP),
        sa.Column('last_used', sa.TIMESTAMP),
    )

    op.create_index('idx_api_keys_user_uuid', 'api_keys', ['user_uuid'])

def downgrade():
    op.drop_table('api_keys')
    op.drop_table('users')
```

**Run migration:**
```bash
alembic upgrade head
```

#### Step 1.2: Create User Models

**File:** `apex-memory-system/src/apex_memory/models/user.py`

```python
"""User models for authentication."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Boolean, Column, String, TIMESTAMP, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from apex_memory.models.base import Base


class UserDB(Base):
    """User database model."""

    __tablename__ = "users"

    uuid = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default="user", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    last_login = Column(TIMESTAMP)
    preferences = Column(JSON, default={})


class User(BaseModel):
    """User schema for API responses."""

    uuid: UUID
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: str = "user"
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None
    preferences: dict = Field(default_factory=dict)

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenData(BaseModel):
    """JWT token payload."""

    user_uuid: str
    email: str
    role: str
```

#### Step 1.3: Create Authentication Service

**File:** `apex-memory-system/src/apex_memory/services/auth_service.py`

```python
"""Authentication service for user management."""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from apex_memory.config import settings
from apex_memory.models.user import UserDB, User, UserCreate, TokenData


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


class AuthService:
    """Service for authentication operations."""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> TokenData:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_uuid: str = payload.get("sub")
            email: str = payload.get("email")
            role: str = payload.get("role", "user")

            if user_uuid is None or email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                )

            return TokenData(user_uuid=user_uuid, email=email, role=role)

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> User:
        """Register a new user."""
        # Check if email already exists
        existing_user = db.query(UserDB).filter(UserDB.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Check if username already exists
        existing_username = db.query(UserDB).filter(UserDB.username == user_data.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

        # Create new user
        hashed_password = AuthService.get_password_hash(user_data.password)
        db_user = UserDB(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return User.from_orm(db_user)

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password."""
        db_user = db.query(UserDB).filter(UserDB.email == email).first()

        if not db_user:
            return None

        if not AuthService.verify_password(password, db_user.hashed_password):
            return None

        if not db_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive",
            )

        # Update last login
        db_user.last_login = datetime.utcnow()
        db.commit()

        return User.from_orm(db_user)

    @staticmethod
    def get_user_by_uuid(db: Session, user_uuid: UUID) -> Optional[User]:
        """Get a user by UUID."""
        db_user = db.query(UserDB).filter(UserDB.uuid == user_uuid).first()

        if not db_user:
            return None

        return User.from_orm(db_user)
```

#### Step 1.4: Create JWT Utilities

**File:** `apex-memory-system/src/apex_memory/api/dependencies.py`

```python
"""API dependencies for authentication."""
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from apex_memory.database import get_db
from apex_memory.models.user import User
from apex_memory.services.auth_service import AuthService


# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode token
    token_data = AuthService.decode_token(token)

    # Get user from database
    user = AuthService.get_user_by_uuid(db, UUID(token_data.user_uuid))

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get the current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Require admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
```

**✅ Checkpoint:** Backend foundation complete. Test database schema and models.

### Day 2: Authentication API

#### Step 2.1: Create Authentication Endpoints

**File:** `apex-memory-system/src/apex_memory/api/auth.py`

```python
"""Authentication API endpoints."""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from apex_memory.api.dependencies import get_current_active_user, get_db
from apex_memory.models.user import User, UserCreate, UserLogin, Token
from apex_memory.services.auth_service import AuthService, ACCESS_TOKEN_EXPIRE_MINUTES


router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user.

    **Returns:**
    - User object with UUID
    """
    return AuthService.register_user(db, user_data)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with email and password.

    **Returns:**
    - JWT access token
    """
    # Authenticate user
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": str(user.uuid), "email": user.email, "role": user.role},
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout (client-side token removal).

    **Note:** JWT tokens are stateless. Client should remove token from storage.
    """
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user information.

    **Returns:**
    - Current user object
    """
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_active_user)
):
    """
    Refresh access token.

    **Returns:**
    - New JWT access token
    """
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": str(current_user.uuid), "email": current_user.email, "role": current_user.role},
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
```

#### Step 2.2: Register Authentication Router

**File:** `apex-memory-system/src/apex_memory/main.py` (update)

```python
from apex_memory.api.auth import router as auth_router

# Add to app
app.include_router(auth_router)
```

#### Step 2.3: Test Authentication API

```bash
# Register a new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpass123",
    "full_name": "Test User"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpass123"

# Get current user (use token from login response)
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

**✅ Checkpoint:** Authentication API working. Tokens generated and validated.

### Day 3: Frontend Auth Components

#### Step 3.1: Create Auth Context

**File:** `src/apex_memory/frontend/src/contexts/AuthContext.tsx`

```typescript
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

interface User {
  uuid: string;
  email: string;
  username: string;
  full_name?: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load token from localStorage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token');
    if (storedToken) {
      setToken(storedToken);
      fetchCurrentUser(storedToken);
    } else {
      setIsLoading(false);
    }
  }, []);

  // Fetch current user
  const fetchCurrentUser = async (authToken: string) => {
    try {
      const response = await axios.get('/api/v1/auth/me', {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      // Token invalid, clear it
      localStorage.removeItem('auth_token');
      setToken(null);
    } finally {
      setIsLoading(false);
    }
  };

  // Login
  const login = async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await axios.post('/api/v1/auth/login', formData);
    const { access_token } = response.data;

    localStorage.setItem('auth_token', access_token);
    setToken(access_token);

    await fetchCurrentUser(access_token);
  };

  // Register
  const register = async (email: string, username: string, password: string, fullName?: string) => {
    await axios.post('/api/v1/auth/register', {
      email,
      username,
      password,
      full_name: fullName
    });

    // Auto-login after registration
    await login(email, password);
  };

  // Logout
  const logout = () => {
    localStorage.removeItem('auth_token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{
      user,
      token,
      isAuthenticated: !!user,
      isLoading,
      login,
      register,
      logout
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

#### Step 3.2: Create Login Component

**File:** `src/apex_memory/frontend/src/components/auth/Login.tsx`

```typescript
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

export function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login(email, password);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-white">
      <div className="w-full max-w-md space-y-8 px-4">
        {/* Logo/Title */}
        <div className="text-center">
          <h1 className="text-3xl font-semibold text-gray-900">Apex Memory</h1>
          <p className="mt-2 text-gray-600">Sign in to your account</p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {isLoading ? 'Signing in...' : 'Sign in'}
          </button>

          <p className="text-center text-sm text-gray-600">
            Don't have an account?{' '}
            <a href="/register" className="font-medium text-blue-600 hover:text-blue-500">
              Sign up
            </a>
          </p>
        </form>
      </div>
    </div>
  );
}
```

#### Step 3.3: Create Register Component

**File:** `src/apex_memory/frontend/src/components/auth/Register.tsx`

```typescript
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

export function Register() {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await register(email, username, password, fullName);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-white">
      <div className="w-full max-w-md space-y-8 px-4">
        <div className="text-center">
          <h1 className="text-3xl font-semibold text-gray-900">Apex Memory</h1>
          <p className="mt-2 text-gray-600">Create your account</p>
        </div>

        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                Username
              </label>
              <input
                id="username"
                type="text"
                required
                minLength={3}
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label htmlFor="full_name" className="block text-sm font-medium text-gray-700">
                Full Name (optional)
              </label>
              <input
                id="full_name"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                id="password"
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
              <p className="mt-1 text-xs text-gray-500">Minimum 8 characters</p>
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {isLoading ? 'Creating account...' : 'Sign up'}
          </button>

          <p className="text-center text-sm text-gray-600">
            Already have an account?{' '}
            <a href="/login" className="font-medium text-blue-600 hover:text-blue-500">
              Sign in
            </a>
          </p>
        </form>
      </div>
    </div>
  );
}
```

**✅ Checkpoint:** Login and Register components created. Test in browser.

### Day 4: Protected Routes

#### Step 4.1: Create ProtectedRoute Component

**File:** `src/apex_memory/frontend/src/components/auth/ProtectedRoute.tsx`

```typescript
import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

interface ProtectedRouteProps {
  requireAdmin?: boolean;
}

export function ProtectedRoute({ requireAdmin = false }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requireAdmin && user?.role !== 'admin') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-gray-900">Access Denied</h1>
          <p className="mt-2 text-gray-600">You don't have permission to access this page.</p>
        </div>
      </div>
    );
  }

  return <Outlet />;
}
```

#### Step 4.2: Update App Router

**File:** `src/apex_memory/frontend/src/App.tsx`

```typescript
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { Login } from './components/auth/Login';
import { Register } from './components/auth/Register';

// Placeholder components (implement in later phases)
import { ConversationHub } from './pages/ConversationHub';
import { DocumentBrowser } from './pages/DocumentBrowser';
import { GraphExplorer } from './pages/GraphExplorer';
import { AdminPanel } from './pages/AdminPanel';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<ConversationHub />} />
            <Route path="/vault" element={<DocumentBrowser />} />
            <Route path="/graph" element={<GraphExplorer />} />
          </Route>

          {/* Admin-only routes */}
          <Route element={<ProtectedRoute requireAdmin />}>
            <Route path="/admin" element={<AdminPanel />} />
          </Route>

          {/* Catch-all redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
```

#### Step 4.3: Configure Axios Interceptor

**File:** `src/apex_memory/frontend/src/lib/axios.ts`

```typescript
import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000'
});

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle 401 errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

**✅ Checkpoint:** Protected routes working. Unauthorized access redirects to login.

### Day 5: Testing & Polish

#### Step 5.1: Write Authentication Tests

**File:** `apex-memory-system/tests/integration/test_auth.py`

```python
"""Integration tests for authentication."""
import pytest
from fastapi.testclient import TestClient

from apex_memory.main import app


client = TestClient(app)


def test_register_user():
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "testpass123",
            "full_name": "New User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "uuid" in data


def test_register_duplicate_email():
    """Test registering with duplicate email fails."""
    # Register first user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "username": "user1",
            "password": "testpass123"
        }
    )

    # Try to register with same email
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "username": "user2",
            "password": "testpass123"
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_success():
    """Test successful login."""
    # Register user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "logintest@example.com",
            "username": "loginuser",
            "password": "testpass123"
        }
    )

    # Login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "logintest@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    """Test login with incorrect password."""
    # Register user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrongpass@example.com",
            "username": "wrongpass",
            "password": "correctpass"
        }
    )

    # Try to login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "wrongpass@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401


def test_get_current_user():
    """Test getting current user info."""
    # Register and login
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "currentuser@example.com",
            "username": "current",
            "password": "testpass123"
        }
    )

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "currentuser@example.com",
            "password": "testpass123"
        }
    )
    token = login_response.json()["access_token"]

    # Get current user
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "currentuser@example.com"


def test_access_protected_endpoint_without_token():
    """Test accessing protected endpoint without token fails."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
```

#### Step 5.2: Run Tests

```bash
# Run authentication tests
pytest tests/integration/test_auth.py -v

# Run all tests
pytest
```

#### Step 5.3: Add Loading States and Error Handling

Update Login component with better UX:

```typescript
// Add to Login.tsx
<button
  type="submit"
  disabled={isLoading}
  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
>
  {isLoading ? (
    <>
      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      Signing in...
    </>
  ) : (
    'Sign in'
  )}
</button>
```

**✅ Phase 1 Complete!**

---

## Phase 2: AI Conversation Hub (Week 2)

**Priority:** 🟠 CRITICAL for user adoption
**Timeline:** 5 days, 25 tasks, 15 tests
**Research:** Read `research/documentation/INDEX.md` → Natural language processing section

### Overview

Create "ChatGPT for your knowledge graph" experience with memory-grounded responses and citations.

### Day 1: Backend Foundation

#### Step 2.1: Create Conversation Database Schema

**File:** `apex-memory-system/alembic/versions/002_add_conversations.py`

```python
"""Add conversations and messages tables

Revision ID: 002
Create Date: 2025-10-21
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Conversations table
    op.create_table(
        'conversations',
        sa.Column('uuid', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_uuid', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.uuid'), nullable=False),
        sa.Column('title', sa.String(255)),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text('NOW()'), nullable=False),
        sa.Column('last_message_at', sa.TIMESTAMP),
    )

    op.create_index('idx_conversations_user_uuid', 'conversations', ['user_uuid'])

    # Messages table
    op.create_table(
        'messages',
        sa.Column('uuid', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('conversation_uuid', postgresql.UUID(as_uuid=True), sa.ForeignKey('conversations.uuid', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),  # 'user' | 'assistant' | 'system'
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('citations', postgresql.JSONB),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text('NOW()'), nullable=False),
    )

    op.create_index('idx_messages_conversation_uuid', 'messages', ['conversation_uuid'])

def downgrade():
    op.drop_table('messages')
    op.drop_table('conversations')
```

Run migration:
```bash
alembic upgrade head
```

#### Step 2.2: Create Conversation Models

**File:** `apex-memory-system/src/apex_memory/models/conversation.py`

```python
"""Conversation models."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB

from apex_memory.models.base import Base


class ConversationDB(Base):
    """Conversation database model."""

    __tablename__ = "conversations"

    uuid = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_uuid = Column(PGUUID(as_uuid=True), ForeignKey('users.uuid'), nullable=False, index=True)
    title = Column(String(255))
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    last_message_at = Column(TIMESTAMP)


class MessageDB(Base):
    """Message database model."""

    __tablename__ = "messages"

    uuid = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    conversation_uuid = Column(PGUUID(as_uuid=True), ForeignKey('conversations.uuid', ondelete='CASCADE'), nullable=False, index=True)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    citations = Column(JSONB)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)


class Citation(BaseModel):
    """Citation for a message."""

    document_uuid: UUID
    document_title: str
    relevant_excerpt: str
    confidence_score: float = Field(ge=0.0, le=1.0)


class Message(BaseModel):
    """Message schema."""

    uuid: UUID
    conversation_uuid: UUID
    role: str  # 'user' | 'assistant' | 'system'
    content: str
    citations: Optional[List[Citation]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class Conversation(BaseModel):
    """Conversation schema."""

    uuid: UUID
    user_uuid: UUID
    title: Optional[str] = None
    created_at: datetime
    last_message_at: Optional[datetime] = None
    messages: List[Message] = Field(default_factory=list)

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    """Schema for creating a conversation."""

    title: Optional[str] = None


class MessageCreate(BaseModel):
    """Schema for creating a message."""

    content: str


class ConversationResponse(BaseModel):
    """Response from conversation query."""

    message: Message
    conversation: Conversation
```

**✅ Checkpoint: Database schema and models created for conversations.**

---

### Day 2: LLM Integration and Context Retrieval

#### Step 2.3: Create Conversation Service

**File:** `apex-memory-system/src/apex_memory/services/conversation_service.py`

```python
"""Conversation service with LLM integration."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from anthropic import Anthropic
from sqlalchemy.orm import Session

from apex_memory.models.conversation import (
    ConversationDB,
    MessageDB,
    Conversation,
    Message,
    Citation,
    ConversationCreate,
    MessageCreate,
)
from apex_memory.query_router.router import QueryRouter
from apex_memory.config import settings


class ConversationService:
    """Service for managing conversations with LLM integration."""

    def __init__(self, db: Session):
        self.db = db
        self.anthropic = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.query_router = QueryRouter()

    def create_conversation(
        self, user_uuid: UUID, conversation_data: ConversationCreate
    ) -> Conversation:
        """Create a new conversation."""
        conversation_db = ConversationDB(
            user_uuid=user_uuid,
            title=conversation_data.title,
        )
        self.db.add(conversation_db)
        self.db.commit()
        self.db.refresh(conversation_db)

        return Conversation.from_orm(conversation_db)

    def get_conversation(
        self, conversation_uuid: UUID, user_uuid: UUID
    ) -> Optional[Conversation]:
        """Get a conversation by UUID."""
        conversation = (
            self.db.query(ConversationDB)
            .filter(
                ConversationDB.uuid == conversation_uuid,
                ConversationDB.user_uuid == user_uuid,
            )
            .first()
        )

        if not conversation:
            return None

        # Load messages
        messages = (
            self.db.query(MessageDB)
            .filter(MessageDB.conversation_uuid == conversation_uuid)
            .order_by(MessageDB.created_at)
            .all()
        )

        conversation_dict = {
            "uuid": conversation.uuid,
            "user_uuid": conversation.user_uuid,
            "title": conversation.title,
            "created_at": conversation.created_at,
            "last_message_at": conversation.last_message_at,
            "messages": [Message.from_orm(msg) for msg in messages],
        }

        return Conversation(**conversation_dict)

    async def process_message(
        self, conversation_uuid: UUID, user_uuid: UUID, message_content: str
    ) -> Message:
        """Process a user message and generate AI response."""
        # 1. Save user message
        user_message = MessageDB(
            conversation_uuid=conversation_uuid,
            role="user",
            content=message_content,
        )
        self.db.add(user_message)
        self.db.commit()

        # 2. Retrieve relevant context from Apex Memory
        context = await self._retrieve_context(message_content)

        # 3. Build conversation history
        history = self._get_conversation_history(conversation_uuid)

        # 4. Generate AI response using Claude
        ai_response, citations = await self._generate_response(
            message_content, context, history
        )

        # 5. Save assistant message
        assistant_message = MessageDB(
            conversation_uuid=conversation_uuid,
            role="assistant",
            content=ai_response,
            citations=[c.dict() for c in citations] if citations else None,
        )
        self.db.add(assistant_message)

        # 6. Update conversation last_message_at
        conversation = self.db.query(ConversationDB).filter(
            ConversationDB.uuid == conversation_uuid
        ).first()
        conversation.last_message_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(assistant_message)

        return Message.from_orm(assistant_message)

    async def _retrieve_context(self, query: str) -> List[dict]:
        """Retrieve relevant context from Apex Memory System."""
        # Use query router to get optimal results
        results = await self.query_router.route_query(query)

        # Format results for LLM context
        context = []
        for result in results[:5]:  # Top 5 results
            context.append({
                "title": result.get("title", "Unknown"),
                "content": result.get("content", ""),
                "score": result.get("score", 0.0),
                "uuid": result.get("uuid"),
            })

        return context

    def _get_conversation_history(
        self, conversation_uuid: UUID, limit: int = 10
    ) -> List[dict]:
        """Get recent conversation history."""
        messages = (
            self.db.query(MessageDB)
            .filter(MessageDB.conversation_uuid == conversation_uuid)
            .order_by(MessageDB.created_at.desc())
            .limit(limit)
            .all()
        )

        # Reverse to chronological order
        messages = list(reversed(messages))

        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

    async def _generate_response(
        self, query: str, context: List[dict], history: List[dict]
    ) -> tuple[str, List[Citation]]:
        """Generate AI response using Claude with retrieved context."""
        # Build system prompt with context
        system_prompt = self._build_system_prompt(context)

        # Build message history
        messages = history + [{"role": "user", "content": query}]

        # Call Claude API
        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            system=system_prompt,
            messages=messages,
        )

        ai_response = response.content[0].text

        # Extract citations from context
        citations = [
            Citation(
                document_uuid=ctx["uuid"],
                document_title=ctx["title"],
                relevant_excerpt=ctx["content"][:200],
                confidence_score=ctx["score"],
            )
            for ctx in context
            if ctx.get("uuid")
        ]

        return ai_response, citations

    def _build_system_prompt(self, context: List[dict]) -> str:
        """Build system prompt with retrieved context."""
        prompt = """You are Apex Memory AI, an intelligent assistant with access to the user's knowledge graph.

**Context from Knowledge Graph:**

"""
        for i, ctx in enumerate(context, 1):
            prompt += f"""
[Document {i}: {ctx['title']}]
{ctx['content'][:500]}
...

"""

        prompt += """
**Instructions:**
- Answer based on the provided context when relevant
- If context doesn't contain the answer, use your general knowledge
- Cite specific documents when using information from context
- Be concise and helpful
- If you're unsure, say so
"""

        return prompt

    def list_conversations(
        self, user_uuid: UUID, limit: int = 50, offset: int = 0
    ) -> List[Conversation]:
        """List conversations for a user."""
        conversations = (
            self.db.query(ConversationDB)
            .filter(ConversationDB.user_uuid == user_uuid)
            .order_by(ConversationDB.last_message_at.desc().nullslast())
            .limit(limit)
            .offset(offset)
            .all()
        )

        return [Conversation.from_orm(conv) for conv in conversations]

    def delete_conversation(
        self, conversation_uuid: UUID, user_uuid: UUID
    ) -> bool:
        """Delete a conversation."""
        conversation = (
            self.db.query(ConversationDB)
            .filter(
                ConversationDB.uuid == conversation_uuid,
                ConversationDB.user_uuid == user_uuid,
            )
            .first()
        )

        if not conversation:
            return False

        self.db.delete(conversation)
        self.db.commit()
        return True
```

#### Step 2.4: Create Conversation API Endpoints

**File:** `apex-memory-system/src/apex_memory/api/conversations.py`

```python
"""Conversation API endpoints."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from apex_memory.api.dependencies import get_db, get_current_user
from apex_memory.models.user import User
from apex_memory.models.conversation import (
    Conversation,
    ConversationCreate,
    MessageCreate,
    ConversationResponse,
)
from apex_memory.services.conversation_service import ConversationService

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


@router.post("/", response_model=Conversation, status_code=status.HTTP_201_CREATED)
def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new conversation."""
    service = ConversationService(db)
    return service.create_conversation(current_user.uuid, conversation_data)


@router.get("/", response_model=List[Conversation])
def list_conversations(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List user's conversations."""
    service = ConversationService(db)
    return service.list_conversations(current_user.uuid, limit, offset)


@router.get("/{conversation_uuid}", response_model=Conversation)
def get_conversation(
    conversation_uuid: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific conversation."""
    service = ConversationService(db)
    conversation = service.get_conversation(conversation_uuid, current_user.uuid)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return conversation


@router.post("/{conversation_uuid}/messages", response_model=ConversationResponse)
async def send_message(
    conversation_uuid: UUID,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send a message in a conversation."""
    service = ConversationService(db)

    # Verify conversation belongs to user
    conversation = service.get_conversation(conversation_uuid, current_user.uuid)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Process message
    response_message = await service.process_message(
        conversation_uuid, current_user.uuid, message_data.content
    )

    # Get updated conversation
    updated_conversation = service.get_conversation(
        conversation_uuid, current_user.uuid
    )

    return ConversationResponse(
        message=response_message,
        conversation=updated_conversation,
    )


@router.delete("/{conversation_uuid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_uuid: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a conversation."""
    service = ConversationService(db)
    success = service.delete_conversation(conversation_uuid, current_user.uuid)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
```

Register in main app:

```python
# apex-memory-system/src/apex_memory/main.py
from apex_memory.api import conversations

app.include_router(conversations.router)
```

**✅ Checkpoint: LLM integration complete with context retrieval and citations.**

---

### Day 3: Frontend Chat Interface

#### Step 2.5: Create Chat UI Components

**File:** `apex-memory-system/frontend/src/components/ConversationHub.tsx`

```typescript
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

interface Message {
  uuid: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  citations?: Citation[];
  created_at: string;
}

interface Citation {
  document_uuid: string;
  document_title: string;
  relevant_excerpt: string;
  confidence_score: number;
}

interface Conversation {
  uuid: string;
  title?: string;
  messages: Message[];
  created_at: string;
}

export function ConversationHub() {
  const { token } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentConversation?.messages]);

  const loadConversations = async () => {
    try {
      const response = await axios.get('/api/v1/conversations/', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setConversations(response.data);

      // Auto-select first conversation
      if (response.data.length > 0) {
        setCurrentConversation(response.data[0]);
      }
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  };

  const createNewConversation = async () => {
    try {
      const response = await axios.post(
        '/api/v1/conversations/',
        { title: 'New Conversation' },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const newConv = response.data;
      setConversations([newConv, ...conversations]);
      setCurrentConversation(newConv);
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || !currentConversation) return;

    setIsLoading(true);

    try {
      const response = await axios.post(
        `/api/v1/conversations/${currentConversation.uuid}/messages`,
        { content: inputMessage },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setCurrentConversation(response.data.conversation);
      setInputMessage('');
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen">
      {/* Sidebar - Conversation List */}
      <div className="w-64 bg-gray-50 border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <button
            onClick={createNewConversation}
            className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            + New Conversation
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">
          {conversations.map((conv) => (
            <button
              key={conv.uuid}
              onClick={() => setCurrentConversation(conv)}
              className={`w-full text-left p-4 border-b border-gray-200 hover:bg-gray-100 transition-colors ${
                currentConversation?.uuid === conv.uuid ? 'bg-gray-100' : ''
              }`}
            >
              <div className="font-medium truncate">
                {conv.title || 'Untitled Conversation'}
              </div>
              <div className="text-sm text-gray-500 truncate">
                {conv.messages[conv.messages.length - 1]?.content || 'No messages'}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {currentConversation ? (
          <>
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {currentConversation.messages.map((message) => (
                <div
                  key={message.uuid}
                  className={`flex ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  <div
                    className={`max-w-2xl rounded-lg p-4 ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <div className="whitespace-pre-wrap">{message.content}</div>

                    {/* Citations */}
                    {message.citations && message.citations.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-gray-300">
                        <div className="text-sm font-medium mb-2">Sources:</div>
                        <div className="space-y-2">
                          {message.citations.map((citation, idx) => (
                            <div
                              key={citation.document_uuid}
                              className="text-sm bg-white bg-opacity-50 rounded p-2"
                            >
                              <div className="font-medium">
                                [{idx + 1}] {citation.document_title}
                              </div>
                              <div className="text-xs mt-1 text-gray-600">
                                {citation.relevant_excerpt}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t border-gray-200 p-4">
              <form onSubmit={sendMessage} className="flex gap-2">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Ask anything about your knowledge graph..."
                  disabled={isLoading}
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  type="submit"
                  disabled={isLoading || !inputMessage.trim()}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isLoading ? 'Sending...' : 'Send'}
                </button>
              </form>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            Select a conversation or create a new one to start chatting
          </div>
        )}
      </div>
    </div>
  );
}
```

**✅ Checkpoint: Basic chat UI complete with message display and citations.**

---

### Days 4-5: Voice Input and Testing

#### Step 2.6: Add Voice Input (Optional Enhancement)

**File:** `apex-memory-system/frontend/src/components/VoiceInput.tsx`

```typescript
import React, { useState, useRef } from 'react';

interface VoiceInputProps {
  onTranscript: (text: string) => void;
}

export function VoiceInput({ onTranscript }: VoiceInputProps) {
  const [isRecording, setIsRecording] = useState(false);
  const recognitionRef = useRef<any>(null);

  const startRecording = () => {
    if (!('webkitSpeechRecognition' in window)) {
      alert('Speech recognition not supported in this browser');
      return;
    }

    const SpeechRecognition = (window as any).webkitSpeechRecognition;
    recognitionRef.current = new SpeechRecognition();
    recognitionRef.current.continuous = false;
    recognitionRef.current.interimResults = false;

    recognitionRef.current.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      onTranscript(transcript);
      setIsRecording(false);
    };

    recognitionRef.current.onerror = () => {
      setIsRecording(false);
    };

    recognitionRef.current.start();
    setIsRecording(true);
  };

  const stopRecording = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <button
      type="button"
      onClick={isRecording ? stopRecording : startRecording}
      className={`p-3 rounded-lg transition-colors ${
        isRecording
          ? 'bg-red-600 text-white animate-pulse'
          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
      }`}
    >
      {isRecording ? '🔴 Recording...' : '🎤 Voice'}
    </button>
  );
}
```

Add to ConversationHub input area:

```typescript
<VoiceInput onTranscript={(text) => setInputMessage(text)} />
```

#### Step 2.7: Write Comprehensive Tests

**File:** `apex-memory-system/tests/integration/test_conversations.py`

```python
"""Integration tests for conversation feature."""
import pytest
from uuid import uuid4

from apex_memory.services.conversation_service import ConversationService
from apex_memory.models.conversation import ConversationCreate, MessageCreate


@pytest.fixture
def user_uuid():
    """Test user UUID."""
    return uuid4()


@pytest.fixture
def conversation_service(db_session):
    """Conversation service instance."""
    return ConversationService(db_session)


def test_create_conversation(conversation_service, user_uuid):
    """Test creating a conversation."""
    conversation = conversation_service.create_conversation(
        user_uuid, ConversationCreate(title="Test Conversation")
    )

    assert conversation.uuid is not None
    assert conversation.title == "Test Conversation"
    assert conversation.user_uuid == user_uuid
    assert len(conversation.messages) == 0


def test_list_conversations(conversation_service, user_uuid):
    """Test listing conversations."""
    # Create multiple conversations
    for i in range(3):
        conversation_service.create_conversation(
            user_uuid, ConversationCreate(title=f"Conversation {i}")
        )

    conversations = conversation_service.list_conversations(user_uuid)
    assert len(conversations) == 3


@pytest.mark.asyncio
async def test_process_message(conversation_service, user_uuid):
    """Test processing a message with LLM."""
    # Create conversation
    conversation = conversation_service.create_conversation(
        user_uuid, ConversationCreate(title="Test")
    )

    # Send message
    response = await conversation_service.process_message(
        conversation.uuid, user_uuid, "What is Apex Memory?"
    )

    assert response.role == "assistant"
    assert len(response.content) > 0


@pytest.mark.asyncio
async def test_message_with_context(conversation_service, user_uuid, sample_documents):
    """Test message processing retrieves relevant context."""
    conversation = conversation_service.create_conversation(
        user_uuid, ConversationCreate(title="Test")
    )

    # Ask about something in the documents
    response = await conversation_service.process_message(
        conversation.uuid, user_uuid, "Tell me about ACME Corporation"
    )

    assert response.role == "assistant"
    assert response.citations is not None
    assert len(response.citations) > 0


def test_delete_conversation(conversation_service, user_uuid):
    """Test deleting a conversation."""
    conversation = conversation_service.create_conversation(
        user_uuid, ConversationCreate(title="Test")
    )

    success = conversation_service.delete_conversation(
        conversation.uuid, user_uuid
    )
    assert success is True

    # Verify deleted
    deleted = conversation_service.get_conversation(
        conversation.uuid, user_uuid
    )
    assert deleted is None


@pytest.mark.asyncio
async def test_conversation_history(conversation_service, user_uuid):
    """Test conversation maintains history."""
    conversation = conversation_service.create_conversation(
        user_uuid, ConversationCreate(title="Test")
    )

    # Send multiple messages
    await conversation_service.process_message(
        conversation.uuid, user_uuid, "First question"
    )
    await conversation_service.process_message(
        conversation.uuid, user_uuid, "Second question"
    )

    # Get conversation
    conv = conversation_service.get_conversation(
        conversation.uuid, user_uuid
    )

    assert len(conv.messages) == 4  # 2 user + 2 assistant
```

Run tests:

```bash
pytest tests/integration/test_conversations.py -v
```

**✅ Phase 2 Complete! Chat interface with LLM integration, citations, and voice input.**

---

## Phase 2.5: Claude Agents SDK Integration (Week 3)

**Priority:** 🔴 CRITICAL for AI-native UX
**Timeline:** 5 days, 25 tasks, 15 tests
**Research:** Read `research/documentation/tool-use-api.md` and `streaming-api.md`

### Overview

Integrate Vercel AI SDK + Claude tool use for streaming responses with live tool execution visualization (Artifacts sidebar pattern).

### Day 1-2: Backend Streaming with Tool Use

#### Step 2.5.1: Install Vercel AI SDK

```bash
cd apex-memory-system
npm install ai @ai-sdk/anthropic
```

#### Step 2.5.2: Create Streaming Endpoint with Tool Definitions

**File:** `apex-memory-system/src/apex_memory/api/chat_stream.py`

```python
"""Streaming chat endpoint with Claude tool use."""
from typing import AsyncGenerator
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from anthropic import AsyncAnthropic
from pydantic import BaseModel

from apex_memory.api.dependencies import get_current_user
from apex_memory.models.user import User
from apex_memory.query_router.router import QueryRouter
from apex_memory.services.graph_service import GraphService
from apex_memory.config import settings

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """Chat request with messages."""
    messages: list[dict]
    conversation_uuid: UUID


# Define Apex-specific tools for Claude
APEX_TOOLS = [
    {
        "name": "search_knowledge_graph",
        "description": "Search across all databases (Neo4j, Qdrant, PostgreSQL) for relevant information",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_entity_relationships",
        "description": "Get relationships and connections for a specific entity in Neo4j",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_name": {
                    "type": "string",
                    "description": "Name of the entity to explore"
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Maximum relationship depth",
                    "default": 2
                }
            },
            "required": ["entity_name"]
        }
    },
    {
        "name": "get_temporal_timeline",
        "description": "Get temporal evolution of an entity or topic using Graphiti",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_name": {
                    "type": "string",
                    "description": "Entity to get timeline for"
                },
                "start_date": {
                    "type": "string",
                    "description": "Start date (YYYY-MM-DD)"
                },
                "end_date": {
                    "type": "string",
                    "description": "End date (YYYY-MM-DD)"
                }
            },
            "required": ["entity_name"]
        }
    },
    {
        "name": "find_similar_documents",
        "description": "Find documents similar to a given document using vector similarity",
        "input_schema": {
            "type": "object",
            "properties": {
                "document_uuid": {
                    "type": "string",
                    "description": "UUID of reference document"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum results",
                    "default": 5
                }
            },
            "required": ["document_uuid"]
        }
    },
    {
        "name": "get_graph_statistics",
        "description": "Get statistical overview of the knowledge graph",
        "input_schema": {
            "type": "object",
            "properties": {
                "include_metrics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Metrics to include: node_count, relationship_count, etc."
                }
            }
        }
    }
]


class ToolExecutor:
    """Executes Apex tool calls."""

    def __init__(self):
        self.query_router = QueryRouter()
        self.graph_service = GraphService()

    async def execute_tool(self, tool_name: str, tool_input: dict) -> dict:
        """Execute a tool and return results."""
        if tool_name == "search_knowledge_graph":
            results = await self.query_router.route_query(
                tool_input["query"],
                limit=tool_input.get("limit", 5)
            )
            return {"results": results}

        elif tool_name == "get_entity_relationships":
            relationships = await self.graph_service.get_entity_relationships(
                tool_input["entity_name"],
                max_depth=tool_input.get("max_depth", 2)
            )
            return {"relationships": relationships}

        elif tool_name == "get_temporal_timeline":
            timeline = await self.graph_service.get_temporal_timeline(
                tool_input["entity_name"],
                start_date=tool_input.get("start_date"),
                end_date=tool_input.get("end_date")
            )
            return {"timeline": timeline}

        elif tool_name == "find_similar_documents":
            similar = await self.query_router.find_similar_documents(
                tool_input["document_uuid"],
                limit=tool_input.get("limit", 5)
            )
            return {"similar_documents": similar}

        elif tool_name == "get_graph_statistics":
            stats = await self.graph_service.get_statistics(
                include_metrics=tool_input.get("include_metrics", [])
            )
            return {"statistics": stats}

        else:
            return {"error": f"Unknown tool: {tool_name}"}


async def stream_chat_response(
    messages: list[dict],
    user: User,
) -> AsyncGenerator[str, None]:
    """Stream chat response with tool use."""
    anthropic = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    tool_executor = ToolExecutor()

    # Initial API call
    response = await anthropic.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        tools=APEX_TOOLS,
        messages=messages,
        stream=True,
    )

    # Stream response
    async for event in response:
        if event.type == "content_block_start":
            if event.content_block.type == "tool_use":
                # Tool use started
                yield f'data: {{"type": "tool_start", "tool_name": "{event.content_block.name}"}}\n\n'

        elif event.type == "content_block_delta":
            if hasattr(event.delta, "text"):
                # Text content
                yield f'data: {{"type": "text", "text": "{event.delta.text}"}}\n\n'
            elif hasattr(event.delta, "input"):
                # Tool input accumulating
                pass

        elif event.type == "content_block_stop":
            if event.content_block.type == "tool_use":
                # Execute tool
                tool_name = event.content_block.name
                tool_input = event.content_block.input

                yield f'data: {{"type": "tool_execute", "tool_name": "{tool_name}"}}\n\n'

                result = await tool_executor.execute_tool(tool_name, tool_input)

                yield f'data: {{"type": "tool_result", "tool_name": "{tool_name}", "result": {result}}}\n\n'

        elif event.type == "message_stop":
            yield 'data: {"type": "done"}\n\n'


@router.post("/stream")
async def stream_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """Stream chat responses with tool use."""
    return StreamingResponse(
        stream_chat_response(request.messages, current_user),
        media_type="text/event-stream",
    )
```

Register in main app:

```python
from apex_memory.api import chat_stream

app.include_router(chat_stream.router)
```

**✅ Checkpoint: Streaming endpoint with 5 Apex tools defined.**

---

### Day 3: Frontend Streaming Integration

#### Step 2.5.3: Create useApexChat Hook

**File:** `apex-memory-system/frontend/src/hooks/useApexChat.ts`

```typescript
import { useChat } from 'ai/react';
import { useState } from 'react';

interface ToolExecution {
  tool_name: string;
  status: 'pending' | 'executing' | 'completed';
  result?: any;
}

export function useApexChat(conversationId: string) {
  const [toolExecutions, setToolExecutions] = useState<ToolExecution[]>([]);

  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: '/api/v1/chat/stream',
    body: {
      conversation_uuid: conversationId,
    },
    onFinish: () => {
      setToolExecutions([]);
    },
    experimental_onFunctionCall: async ({ name, arguments: args }) => {
      // Track tool execution
      setToolExecutions(prev => [
        ...prev,
        { tool_name: name, status: 'executing' }
      ]);

      // Wait for tool result from server
      // (handled by streaming endpoint)
    },
  });

  return {
    messages,
    input,
    handleInputChange,
    handleSubmit,
    isLoading,
    toolExecutions,
  };
}
```

**✅ Checkpoint: Frontend hook for streaming with tool tracking.**

---

### Days 4-5: Artifacts Sidebar and Tool Visualization

#### Step 2.5.4: Create Artifacts Sidebar Component

**File:** `apex-memory-system/frontend/src/components/ArtifactSidebar.tsx`

```typescript
import React from 'react';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet';

interface Artifact {
  type: 'search_results' | 'relationships' | 'timeline' | 'similar_docs' | 'statistics';
  title: string;
  data: any;
}

interface ArtifactSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  artifacts: Artifact[];
}

export function ArtifactSidebar({ isOpen, onClose, artifacts }: ArtifactSidebarProps) {
  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent side="right" className="w-[600px] overflow-y-auto">
        <SheetHeader>
          <SheetTitle>Tool Artifacts</SheetTitle>
        </SheetHeader>

        <div className="mt-6 space-y-6">
          {artifacts.map((artifact, idx) => (
            <div key={idx} className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-semibold text-lg mb-3">{artifact.title}</h3>

              {artifact.type === 'search_results' && (
                <SearchResultsView data={artifact.data} />
              )}

              {artifact.type === 'relationships' && (
                <RelationshipsView data={artifact.data} />
              )}

              {artifact.type === 'timeline' && (
                <TimelineView data={artifact.data} />
              )}

              {artifact.type === 'similar_docs' && (
                <SimilarDocsView data={artifact.data} />
              )}

              {artifact.type === 'statistics' && (
                <StatisticsView data={artifact.data} />
              )}
            </div>
          ))}
        </div>
      </SheetContent>
    </Sheet>
  );
}

function SearchResultsView({ data }: { data: any }) {
  return (
    <div className="space-y-3">
      {data.results.map((result: any, idx: number) => (
        <div key={idx} className="bg-gray-50 p-3 rounded">
          <div className="font-medium">{result.title}</div>
          <div className="text-sm text-gray-600 mt-1">{result.excerpt}</div>
          <div className="text-xs text-gray-400 mt-1">
            Score: {(result.score * 100).toFixed(1)}%
          </div>
        </div>
      ))}
    </div>
  );
}

function RelationshipsView({ data }: { data: any }) {
  return (
    <div className="space-y-2">
      {data.relationships.map((rel: any, idx: number) => (
        <div key={idx} className="flex items-center gap-2 text-sm">
          <span className="font-medium">{rel.from}</span>
          <span className="text-gray-400">→ {rel.type} →</span>
          <span className="font-medium">{rel.to}</span>
        </div>
      ))}
    </div>
  );
}

function TimelineView({ data }: { data: any }) {
  return (
    <div className="space-y-3">
      {data.timeline.map((event: any, idx: number) => (
        <div key={idx} className="border-l-2 border-blue-500 pl-3">
          <div className="text-sm text-gray-500">{event.date}</div>
          <div className="font-medium">{event.title}</div>
          <div className="text-sm text-gray-600 mt-1">{event.description}</div>
        </div>
      ))}
    </div>
  );
}

function SimilarDocsView({ data }: { data: any }) {
  return (
    <div className="space-y-2">
      {data.similar_documents.map((doc: any, idx: number) => (
        <div key={idx} className="bg-gray-50 p-2 rounded">
          <div className="font-medium text-sm">{doc.title}</div>
          <div className="text-xs text-gray-400">
            Similarity: {(doc.similarity * 100).toFixed(1)}%
          </div>
        </div>
      ))}
    </div>
  );
}

function StatisticsView({ data }: { data: any }) {
  return (
    <div className="grid grid-cols-2 gap-3">
      {Object.entries(data.statistics).map(([key, value]) => (
        <div key={key} className="bg-gray-50 p-3 rounded text-center">
          <div className="text-2xl font-bold">{value as string}</div>
          <div className="text-sm text-gray-600 mt-1">
            {key.replace(/_/g, ' ')}
          </div>
        </div>
      ))}
    </div>
  );
}
```

#### Step 2.5.5: Update ConversationHub with Streaming and Artifacts

**File:** Update `apex-memory-system/frontend/src/components/ConversationHub.tsx`

```typescript
import { useState } from 'react';
import { useApexChat } from '../hooks/useApexChat';
import { ArtifactSidebar } from './ArtifactSidebar';
import { ToolUseIndicator } from './ToolUseIndicator';

export function ConversationHub() {
  const [currentConversationId, setCurrentConversationId] = useState<string>('');
  const [isArtifactsOpen, setIsArtifactsOpen] = useState(false);
  const [artifacts, setArtifacts] = useState([]);

  const {
    messages,
    input,
    handleInputChange,
    handleSubmit,
    isLoading,
    toolExecutions,
  } = useApexChat(currentConversationId);

  return (
    <div className="flex h-screen">
      {/* Main chat area */}
      <div className="flex-1 flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4">
          {messages.map((message) => (
            <div key={message.id}>
              {/* Message content */}
              <div>{message.content}</div>
            </div>
          ))}

          {/* Tool execution indicators */}
          {toolExecutions.length > 0 && (
            <ToolUseIndicator executions={toolExecutions} />
          )}
        </div>

        {/* Input area */}
        <form onSubmit={handleSubmit} className="border-t p-4">
          <input
            value={input}
            onChange={handleInputChange}
            placeholder="Ask anything..."
            className="w-full px-4 py-3 border rounded-lg"
          />
        </form>
      </div>

      {/* Artifacts sidebar */}
      <ArtifactSidebar
        isOpen={isArtifactsOpen}
        onClose={() => setIsArtifactsOpen(false)}
        artifacts={artifacts}
      />
    </div>
  );
}
```

**✅ Phase 2.5 Complete! Streaming AI chat with tool use visualization and artifacts sidebar.**

---

## Phase 3: Apple Minimalist Engagement Layer (Weeks 4-5)

**Priority:** 🟡 HIGH for premium UX
**Timeline:** 2 weeks, 50 tasks, 35 tests
**Research:** Read `research/documentation/apex-integration-strategy.md`

### Week 4, Day 1-2: Design System Foundation

#### Step 3.1: Create Design System Constants

**File:** `apex-memory-system/frontend/src/styles/design-system.ts`

```typescript
/**
 * Apex Memory - Apple Minimalist Design System
 *
 * Philosophy: "Sleek, simple, gorgeous, expensive-looking, not busy"
 * Inspiration: Steve Jobs era Apple (2007-2014)
 */

export const colors = {
  // Primary palette (90% of UI)
  background: '#FFFFFF',
  surface: '#F5F5F7',      // Apple gray
  text: '#1D1D1F',         // Almost black
  textSecondary: '#86868B', // System gray

  // Accent (10% of UI)
  accent: '#007AFF',        // Apple blue

  // Depth & Glass
  shadow: 'rgba(0, 0, 0, 0.08)',
  glass: 'rgba(255, 255, 255, 0.8)',
  glassDark: 'rgba(0, 0, 0, 0.05)',
};

export const typography = {
  fontFamily: {
    primary: '-apple-system, BlinkMacSystemFont, "SF Pro", "Inter", sans-serif',
    mono: 'SF Mono, Monaco, "Courier New", monospace',
  },

  sizes: {
    display: { size: 32, weight: 600, lineHeight: 1.2 },
    headline: { size: 24, weight: 600, lineHeight: 1.3 },
    body: { size: 16, weight: 400, lineHeight: 1.6 },
    caption: { size: 14, weight: 400, lineHeight: 1.5 },
  },
};

export const spacing = {
  xs: 8,
  sm: 16,
  md: 24,
  lg: 32,
  xl: 48,
  xxl: 64,
};

export const animation = {
  // Subtle animations only (fade, slide)
  duration: {
    fast: 200,
    normal: 300,
  },
  easing: 'cubic-bezier(0.4, 0.0, 0.2, 1)',
};

export const shadows = {
  subtle: `0 1px 3px ${colors.shadow}`,
  card: `0 4px 6px ${colors.shadow}`,
  elevated: `0 10px 20px ${colors.shadow}`,
};
```

#### Step 3.2: Create Minimal Gamification Components

**File:** `apex-memory-system/frontend/src/components/ProfileAchievements.tsx`

```typescript
import React from 'react';

interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string; // Monochrome icon: ⬡⬢⬣⬤⬥
  earned: boolean;
  earned_at?: string;
}

interface ProfileAchievementsProps {
  achievements: Achievement[];
  currentStreak: number;
}

export function ProfileAchievements({ achievements, currentStreak }: ProfileAchievementsProps) {
  return (
    <div className="max-w-2xl mx-auto p-8">
      {/* Streak Display - Text Only */}
      <div className="mb-12 text-center">
        <div className="text-6xl font-semibold text-gray-900">{currentStreak}</div>
        <div className="mt-2 text-sm text-gray-500">day streak</div>
      </div>

      {/* Achievements - Monochrome Icons */}
      <div className="space-y-6">
        {achievements.map((achievement) => (
          <div
            key={achievement.id}
            className={`flex items-start gap-4 p-4 rounded-lg transition-all ${
              achievement.earned
                ? 'bg-gray-50'
                : 'bg-transparent opacity-50'
            }`}
          >
            {/* Monochrome icon */}
            <div className={`text-3xl ${achievement.earned ? 'text-gray-900' : 'text-gray-300'}`}>
              {achievement.icon}
            </div>

            {/* Text */}
            <div className="flex-1">
              <div className={`font-semibold ${achievement.earned ? 'text-gray-900' : 'text-gray-400'}`}>
                {achievement.title}
              </div>
              <div className="text-sm text-gray-500 mt-1">
                {achievement.description}
              </div>
              {achievement.earned && achievement.earned_at && (
                <div className="text-xs text-gray-400 mt-2">
                  Earned {new Date(achievement.earned_at).toLocaleDateString()}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

**No popups, no toasts, no emoji badges, no leaderboards.** Just clean profile display.

#### Step 3.3: Integrated Recommendations (Invisible Intelligence)

**File:** `apex-memory-system/frontend/src/components/SearchWithRecommendations.tsx`

```typescript
import React, { useState } from 'react';

interface SearchResult {
  uuid: string;
  title: string;
  excerpt: string;
  score: number;
  is_recommendation?: boolean;
}

export function SearchWithRecommendations() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);

  const handleSearch = async () => {
    const response = await fetch('/api/v1/search', {
      method: 'POST',
      body: JSON.stringify({ query }),
    });
    const data = await response.json();
    setResults(data.results);
  };

  return (
    <div className="max-w-3xl mx-auto p-8">
      {/* Search input */}
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
        placeholder="Search your knowledge graph..."
        className="w-full px-6 py-4 text-lg border-none bg-gray-50 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500"
      />

      {/* Results with integrated recommendations */}
      <div className="mt-8 space-y-3">
        {results.map((result) => (
          <div
            key={result.uuid}
            className="p-4 rounded-xl hover:bg-gray-50 transition-colors cursor-pointer"
          >
            <div className="font-medium text-gray-900">{result.title}</div>
            <div className="text-sm text-gray-600 mt-1">{result.excerpt}</div>

            {/* Subtle recommendation indicator */}
            {result.is_recommendation && (
              <div className="text-xs text-gray-400 mt-2">
                Based on your recent activity
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
```

**No separate recommendation cards. Integrated into search results as top result with subtle text.**

#### Step 3.4: Hidden Dashboard

**File:** `apex-memory-system/frontend/src/components/Dashboard.tsx`

```typescript
import React, { useState } from 'react';

interface Metric {
  label: string;
  value: string;
  description: string;
}

interface DashboardProps {
  metrics: Metric[];
}

export function Dashboard({ metrics }: DashboardProps) {
  const [currentMetricIndex, setCurrentMetricIndex] = useState(0);

  const currentMetric = metrics[currentMetricIndex];

  return (
    <div className="max-w-2xl mx-auto p-16">
      {/* Single metric display */}
      <div className="text-center">
        <div className="text-6xl font-semibold text-gray-900 mb-4">
          {currentMetric.value}
        </div>
        <div className="text-2xl font-medium text-gray-700 mb-2">
          {currentMetric.label}
        </div>
        <div className="text-base text-gray-500 max-w-md mx-auto">
          {currentMetric.description}
        </div>
      </div>

      {/* Pagination dots */}
      <div className="flex justify-center gap-2 mt-12">
        {metrics.map((_, idx) => (
          <button
            key={idx}
            onClick={() => setCurrentMetricIndex(idx)}
            className={`w-2 h-2 rounded-full transition-all ${
              idx === currentMetricIndex
                ? 'bg-gray-900 w-6'
                : 'bg-gray-300'
            }`}
          />
        ))}
      </div>
    </div>
  );
}
```

**Not default landing. Accessible via menu. Single-column, one metric at a time, generous spacing.**

#### Step 3.5: Subtle Briefings (Menu Badge Notification)

**File:** `apex-memory-system/frontend/src/components/AppLayout.tsx`

```typescript
import React, { useState, useEffect } from 'react';

export function AppLayout({ children }: { children: React.ReactNode }) {
  const [hasNewBriefing, setHasNewBriefing] = useState(false);
  const [isBriefingOpen, setIsBriefingOpen] = useState(false);

  useEffect(() => {
    // Check for new briefing
    checkForNewBriefing();
  }, []);

  const checkForNewBriefing = async () => {
    const response = await fetch('/api/v1/briefings/latest');
    const data = await response.json();
    setHasNewBriefing(data.has_unread);
  };

  return (
    <div className="flex h-screen">
      {/* Menu sidebar */}
      <nav className="w-16 bg-white border-r border-gray-200 flex flex-col items-center py-6 gap-6">
        {/* Menu button with badge */}
        <button
          className="relative p-2 rounded-lg hover:bg-gray-100 transition-colors"
          onClick={() => setIsBriefingOpen(true)}
        >
          <MenuIcon />
          {hasNewBriefing && (
            <span className="absolute top-1 right-1 w-2 h-2 bg-blue-500 rounded-full" />
          )}
        </button>

        {/* Other menu items... */}
      </nav>

      {/* Main content */}
      <main className="flex-1">{children}</main>

      {/* Briefing modal */}
      {isBriefingOpen && (
        <BriefingModal
          onClose={() => {
            setIsBriefingOpen(false);
            setHasNewBriefing(false);
          }}
        />
      )}
    </div>
  );
}

function BriefingModal({ onClose }: { onClose: () => void }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-20 flex items-center justify-center z-50">
      <div className="bg-white rounded-3xl p-16 max-w-3xl max-h-[80vh] overflow-y-auto shadow-2xl">
        {/* Elegant typography */}
        <h1 className="text-4xl font-semibold text-gray-900 mb-6">
          New Insights
        </h1>

        <div className="space-y-8 text-gray-700 leading-relaxed">
          <p className="text-lg">
            Your knowledge graph has evolved significantly in the past 24 hours...
          </p>

          <div className="border-l-2 border-blue-500 pl-6">
            <h2 className="text-2xl font-medium mb-3">Key Patterns Detected</h2>
            <p>ACME Corporation connections strengthened across 3 supply chains...</p>
          </div>

          {/* More briefing content */}
        </div>

        <button
          onClick={onClose}
          className="mt-12 px-8 py-3 bg-gray-900 text-white rounded-xl hover:bg-gray-800 transition-colors"
        >
          Close
        </button>
      </div>
    </div>
  );
}

function MenuIcon() {
  return (
    <svg className="w-6 h-6 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
    </svg>
  );
}
```

**No popups. Badge on menu icon. Full-screen elegant typography when opened.**

**✅ Phase 3 Complete! Apple minimalist design system with subtle engagement.**

---

## Phase 4: Collaboration & Polish (Weeks 6-7)

**Priority:** 🟢 MEDIUM for team features
**Timeline:** 2 weeks, 40 tasks, 25 tests

### Week 6: Collaboration Features

#### Step 4.1: Shared Conversations

**File:** `apex-memory-system/src/apex_memory/models/conversation_share.py`

```python
"""Conversation sharing models."""
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from apex_memory.models.base import Base


class ConversationShareDB(Base):
    """Conversation share database model."""

    __tablename__ = "conversation_shares"

    uuid = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    conversation_uuid = Column(PGUUID(as_uuid=True), ForeignKey('conversations.uuid', ondelete='CASCADE'), nullable=False)
    shared_by_user_uuid = Column(PGUUID(as_uuid=True), ForeignKey('users.uuid'), nullable=False)
    shared_with_user_uuid = Column(PGUUID(as_uuid=True), ForeignKey('users.uuid'), nullable=False)
    can_edit = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)


class ConversationShare(BaseModel):
    """Conversation share schema."""

    uuid: UUID
    conversation_uuid: UUID
    shared_by_user_uuid: UUID
    shared_with_user_uuid: UUID
    can_edit: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ShareConversationRequest(BaseModel):
    """Request to share a conversation."""

    user_email: str
    can_edit: bool = False
```

#### Step 4.2: Export Conversations

**File:** `apex-memory-system/src/apex_memory/api/export.py`

```python
"""Export conversations to various formats."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from apex_memory.api.dependencies import get_db, get_current_user
from apex_memory.models.user import User
from apex_memory.services.conversation_service import ConversationService

router = APIRouter(prefix="/api/v1/export", tags=["export"])


@router.get("/conversations/{conversation_uuid}/markdown")
async def export_markdown(
    conversation_uuid: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export conversation as Markdown."""
    service = ConversationService(db)
    conversation = service.get_conversation(conversation_uuid, current_user.uuid)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Generate Markdown
    markdown_content = f"# {conversation.title or 'Untitled Conversation'}\n\n"
    markdown_content += f"**Created:** {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    markdown_content += "---\n\n"

    for message in conversation.messages:
        role_label = "**You:**" if message.role == "user" else "**Apex AI:**"
        markdown_content += f"{role_label}\n\n{message.content}\n\n"

        if message.citations:
            markdown_content += "**Sources:**\n"
            for citation in message.citations:
                markdown_content += f"- [{citation.document_title}]\n"
            markdown_content += "\n"

        markdown_content += "---\n\n"

    return StreamingResponse(
        iter([markdown_content]),
        media_type="text/markdown",
        headers={
            "Content-Disposition": f"attachment; filename=conversation_{conversation_uuid}.md"
        },
    )
```

### Week 7: Performance Optimization

#### Step 4.3: Implement Query Caching

**File:** `apex-memory-system/src/apex_memory/cache/query_cache.py`

```python
"""Query result caching with Redis."""
import hashlib
import json
from typing import Optional, Any

import redis

from apex_memory.config import settings


class QueryCache:
    """Cache for query results."""

    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=True,
        )
        self.default_ttl = 3600  # 1 hour

    def _generate_key(self, query: str, filters: dict = None) -> str:
        """Generate cache key from query."""
        key_data = {"query": query, "filters": filters or {}}
        key_string = json.dumps(key_data, sort_keys=True)
        return f"query:{hashlib.sha256(key_string.encode()).hexdigest()}"

    def get(self, query: str, filters: dict = None) -> Optional[Any]:
        """Get cached result."""
        key = self._generate_key(query, filters)
        cached = self.redis.get(key)

        if cached:
            return json.loads(cached)

        return None

    def set(self, query: str, result: Any, filters: dict = None, ttl: int = None):
        """Cache result."""
        key = self._generate_key(query, filters)
        self.redis.setex(
            key,
            ttl or self.default_ttl,
            json.dumps(result),
        )

    def invalidate(self, query: str, filters: dict = None):
        """Invalidate cached result."""
        key = self._generate_key(query, filters)
        self.redis.delete(key)
```

**✅ Phase 4 Complete! Collaboration features and performance optimization.**

---

## Testing Strategy

### Test Organization

**Unit Tests:** `apex-memory-system/tests/unit/`
- Database models (20 tests)
- Service layer logic (25 tests)
- API endpoint validation (15 tests)

**Integration Tests:** `apex-memory-system/tests/integration/`
- End-to-end authentication flow (10 tests)
- Conversation with LLM integration (15 tests)
- Streaming with tool use (10 tests)
- Full user journey (10 tests)

**Frontend Tests:** `apex-memory-system/frontend/src/__tests__/`
- Component rendering (20 tests)
- User interactions (15 tests)
- Hook behavior (10 tests)

### Running All Tests

```bash
# Backend tests
pytest tests/ -v --cov=apex_memory --cov-report=html

# Frontend tests
cd frontend
npm test -- --coverage

# E2E tests
npm run test:e2e
```

**Target: 80%+ code coverage across all phases.**

---

## Deployment Checklist

### Pre-Deployment

- [ ] All 105 tests passing
- [ ] Code coverage >80%
- [ ] Performance benchmarks met (P90 <1s)
- [ ] Security audit complete
- [ ] Documentation updated

### Environment Variables

```bash
# Required for production
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://user:pass@host:5432/apex_memory
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=<secure-random-key>
```

### Database Migrations

```bash
# Run all migrations
alembic upgrade head

# Verify schema
psql -U apex -d apex_memory -c "\dt"
```

### Frontend Build

```bash
cd frontend
npm run build
npm run preview  # Test production build
```

---

## Next Steps After Implementation

1. **User Testing** - Gather feedback on Apple minimalist design
2. **Performance Monitoring** - Set up Grafana dashboards
3. **Feature Iteration** - Based on user analytics
4. **Mobile App** - React Native implementation
5. **Team Features** - Workspaces, permissions, activity feeds

---

**✅ IMPLEMENTATION.md Complete!**

**Total:** 2,000+ lines of step-by-step implementation guidance covering 7 weeks of development.

**Phases Documented:**
- ✅ Phase 1: Authentication Foundation (Week 1)
- ✅ Phase 2: AI Conversation Hub (Week 2)
- ✅ Phase 2.5: Claude Agents SDK Integration (Week 3)
- ✅ Phase 3: Apple Minimalist Engagement (Weeks 4-5)
- ✅ Phase 4: Collaboration & Polish (Weeks 6-7)

**Ready for implementation!**

---

**Last Updated:** 2025-10-21
**Status:** ✅ Complete - All phases documented
**Next:** Begin Phase 1 implementation or create TESTING.md
