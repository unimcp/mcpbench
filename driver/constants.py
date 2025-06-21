"""
Centralized constants for the MCPBench compatibility test framework.

This module contains all constants, configuration values, and message strings
used throughout the MCPBench framework. It serves as a single source of truth
for configuration management and ensures consistency across all components.

Constants are organized into logical groups:
- File paths and directory names
- GitHub API configuration
- Docker-related constants
- Language-specific configurations
- Error messages and logging strings
- Environment variables
- Template placeholders

Usage:
    from constants import SDK_INFO_FILE, GITHUB_API_BASE
    
    # Use constants in your code
    with open(SDK_INFO_FILE, 'r') as f:
        data = json.load(f)
"""

# =============================================================================
# Directory and File Paths
# =============================================================================

SDK_INFO_FILE = "sdkinfo.json"
"""Path to the SDK information JSON file containing version and compatibility data."""

SDK_INFO_BACKUP = "sdkinfo.json.bak"
"""Backup file for SDK information in case of corruption or errors."""

DIR_DOCKER = "docker"
"""Directory containing Docker-related files and templates."""

DIR_TEMPLATES = "templates"
"""Directory containing test templates for different scenarios."""

DIR_TESTS = "tests"
"""Directory containing test implementations and utilities."""

DIR_MATRIX = "matrix"
"""Directory containing the compatibility matrix structure."""

DIR_DRIVER = "driver"
"""Directory containing the driver module and automation scripts."""

# =============================================================================
# GitHub API Configuration
# =============================================================================

GITHUB_API_BASE = "https://api.github.com/repos"
"""Base URL for GitHub API repository endpoints."""

GITHUB_TOKEN_ENV = "GITHUB_TOKEN"
"""Environment variable name for GitHub API authentication token."""

# =============================================================================
# MCP Protocol Roles
# =============================================================================

CLIENT = "client"
"""Role identifier for MCP client implementations."""

SERVER = "server"
"""Role identifier for MCP server implementations."""

# =============================================================================
# Package Manager Files
# =============================================================================

PYTHON_REQUIREMENTS = "requirements.txt"
"""Python package requirements file name."""

TYPESCRIPT_PACKAGE = "package.json"
"""TypeScript/Node.js package configuration file name."""

RUST_CARGO = "Cargo.toml"
"""Rust package configuration file name."""

# =============================================================================
# Official MCP SDK Package Names
# =============================================================================

PYTHON_PACKAGE = "mcp-python-sdk"
"""Official Python MCP SDK package name."""

TYPESCRIPT_PACKAGE = "@modelcontextprotocol/sdk"
"""Official TypeScript MCP SDK package name."""

RUST_PACKAGE = "mcp-rust-sdk"
"""Official Rust MCP SDK package name."""

# =============================================================================
# Docker Configuration
# =============================================================================

DOCKER_COMPOSE_TEMPLATE = "docker-compose.template.yml"
"""Template file for generating Docker Compose configurations."""

CLIENT_SERVER_COMPOSE_TEMPLATE = "client-server-compose.template.yml"
"""Template file for generating client-server Docker Compose configurations."""

DOCKERFILE_TEMPLATE = "Dockerfile.template"
"""Template file for generating Dockerfiles."""

# =============================================================================
# File Patterns for Different Languages
# =============================================================================

# Python file patterns
PYTHON_SOURCE = "*.py"
"""Python source file pattern."""

PYTHON_TEST = "*_test.py"
"""Python test file pattern."""

PYTHON_CONFIG = "*.ini"
"""Python configuration file pattern."""

# TypeScript file patterns
TYPESCRIPT_SOURCE = "*.ts"
"""TypeScript source file pattern."""

TYPESCRIPT_TEST = "*.test.ts"
"""TypeScript test file pattern."""

TYPESCRIPT_CONFIG = "*.json"
"""TypeScript configuration file pattern."""

# Rust file patterns
RUST_SOURCE = "*.rs"
"""Rust source file pattern."""

RUST_TEST = "*_test.rs"
"""Rust test file pattern."""

RUST_CONFIG = "*.toml"
"""Rust configuration file pattern."""

# =============================================================================
# Environment Variables
# =============================================================================

PYTHON_PATH = "PYTHONPATH"
"""Environment variable for Python module search path."""

PYTHON_UNBUFFERED = "PYTHONUNBUFFERED"
"""Environment variable to disable Python output buffering."""

NODE_ENV = "NODE_ENV"
"""Environment variable for Node.js environment (development/production)."""

NODE_PATH = "NODE_PATH"
"""Environment variable for Node.js module search path."""

RUST_LOG = "RUST_LOG"
"""Environment variable for Rust logging level."""

RUST_BACKTRACE = "RUST_BACKTRACE"
"""Environment variable to enable Rust backtrace on panics."""

# =============================================================================
# User-Facing Messages
# =============================================================================

# Information messages
MSG_CREATING_NEW = "Creating new {}"
"""Message template for creating new files or directories."""

MSG_ADDING_VERSION = "Adding new version {} for {}"
"""Message template for adding new SDK versions."""

MSG_UPDATE_SUCCESS = "Successfully updated {}"
"""Message template for successful updates."""

MSG_SETUP_COMPLETE = "Setup complete! Directory structure and package files created."
"""Message indicating successful setup completion."""

MSG_CREATED_DIRS = "Created directories for {} v{}"
"""Message template for directory creation."""

# Warning messages
MSG_NO_RELEASES = "Warning: No releases found for {}"
"""Warning message when no releases are found for an SDK."""

MSG_VERSION_EXISTS = "Version {} already exists for {}"
"""Warning message when a version already exists."""

MSG_RUST_VERSION_WARNING = "Warning: Could not fetch Rust SDK version from Cargo.toml"
"""Warning message when Rust SDK version cannot be fetched."""

MSG_RELEASE_INFO_WARNING = "Warning: Could not fetch release info for {} {}: {}"
"""Warning message when release information cannot be fetched."""

MSG_INVALID_VERSION = "Warning: Invalid version format {}: {}"
"""Warning message for invalid version formats."""

# Error messages
MSG_INVALID_JSON = "Error: {} contains invalid JSON"
"""Error message for invalid JSON files."""

MSG_UPDATE_ERROR = "Error updating SDK information: {}"
"""Error message for SDK update failures."""

MSG_RATE_LIMIT = "Error: GitHub API rate limit exceeded for {}\nConsider setting GITHUB_TOKEN environment variable"
"""Error message for GitHub API rate limiting."""

MSG_FETCH_ERROR = "Error fetching releases for {}: {}"
"""Error message for release fetching failures."""

MSG_RUST_VERSION_ERROR = "Error fetching Rust SDK version: {}"
"""Error message for Rust SDK version fetching failures."""

MSG_RESTORED_BACKUP = "Restored previous version from backup"
"""Message indicating backup restoration."""

# =============================================================================
# Template Placeholders
# =============================================================================

# Basic placeholders
PLACEHOLDER_VERSION = "${VERSION}"
"""Placeholder for version strings in templates."""

PLACEHOLDER_LANGUAGE = "${LANGUAGE}"
"""Placeholder for language names in templates."""

PLACEHOLDER_PORT = "${PORT}"
"""Placeholder for port numbers in templates."""

PLACEHOLDER_ROLE = "${ROLE}"
"""Placeholder for role (client/server) in templates."""

PLACEHOLDER_COMMAND = "${COMMAND}"
"""Placeholder for command strings in templates."""

# Client-specific placeholders
PLACEHOLDER_CLIENT_LANG = "${CLIENT_LANG}"
"""Placeholder for client language in templates."""

PLACEHOLDER_CLIENT_VER = "${CLIENT_VER}"
"""Placeholder for client version in templates."""

PLACEHOLDER_CLIENT_PORT = "${CLIENT_PORT}"
"""Placeholder for client port in templates."""

PLACEHOLDER_CLIENT_COMMAND = "${CLIENT_COMMAND}"
"""Placeholder for client command in templates."""

# Server-specific placeholders
PLACEHOLDER_SERVER_LANG = "${SERVER_LANG}"
"""Placeholder for server language in templates."""

PLACEHOLDER_SERVER_VER = "${SERVER_VER}"
"""Placeholder for server version in templates."""

PLACEHOLDER_SERVER_PORT = "${SERVER_PORT}"
"""Placeholder for server port in templates."""

PLACEHOLDER_SERVER_COMMAND = "${SERVER_COMMAND}"
"""Placeholder for server command in templates."""

# =============================================================================
# Package Manager Placeholders
# =============================================================================

PYTHON_PACKAGE_PLACEHOLDER = "{}=={}"
"""Python package specification format: package==version."""

RUST_PACKAGE_PLACEHOLDER = '{} = "={}"'
"""Rust package specification format: package = "=version"."""

TYPESCRIPT_PACKAGE_PLACEHOLDER = "{}"
"""TypeScript package specification format: package (version from package.json)."""

