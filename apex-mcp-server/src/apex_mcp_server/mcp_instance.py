#!/usr/bin/env python3
"""
Shared FastMCP instance for all tools and resources.

This module provides a single FastMCP instance that all tools, resources,
and the main server use to ensure proper registration.
"""

from mcp.server.fastmcp import FastMCP

# Create the single shared FastMCP instance
mcp = FastMCP("Apex Memory")
