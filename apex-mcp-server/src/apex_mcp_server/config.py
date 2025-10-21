#!/usr/bin/env python3
"""Configuration for Apex MCP Server."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class ApexMCPConfig(BaseSettings):
    """Configuration for Apex MCP Server."""

    # Apex API Configuration
    apex_api_url: str = Field(
        default="http://localhost:8000",
        description="Base URL for Apex Memory System API"
    )
    apex_api_timeout: int = Field(
        default=30,
        description="HTTP request timeout in seconds"
    )

    # LLM Configuration (for ask_apex)
    anthropic_api_key: Optional[str] = Field(
        default=None,
        description="Anthropic API key for Claude"
    )
    anthropic_model: str = Field(
        default="claude-3-7-sonnet-20250219",
        description="Claude model for ask_apex orchestration"
    )

    # Default User/Group IDs
    default_user_id: str = Field(
        default="default",
        description="Default user ID for memory operations"
    )
    default_group_id: str = Field(
        default="default",
        description="Default group ID for Graphiti operations"
    )

    # ask_apex Configuration
    ask_apex_max_queries: int = Field(
        default=6,
        description="Maximum number of queries ask_apex can orchestrate"
    )
    ask_apex_max_synthesis_tokens: int = Field(
        default=2000,
        description="Maximum tokens for narrative synthesis"
    )
    ask_apex_enable_caching: bool = Field(
        default=True,
        description="Enable prompt caching for ask_apex"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global config instance
config = ApexMCPConfig()
