"""
Centralized configuration for language-specific settings in MCPBench.

This module contains all language-specific configurations used throughout the
MCPBench framework. It provides a single source of truth for language-specific
settings such as GitHub repositories, port allocations, Docker configurations,
and package manager commands.

The module supports three official MCP SDKs:
- Python SDK (modelcontextprotocol/python-sdk)
- TypeScript SDK (modelcontextprotocol/typescript-sdk)  
- Rust SDK (modelcontextprotocol/rust-sdk)

Each language has configurations for:
- GitHub repository URLs
- Port allocation ranges
- Docker base images
- Package manager commands
- File patterns and extensions
- Environment variables

Usage:
    from language_config import get_language_config, get_supported_languages
    
    # Get all configuration for a specific language
    config = get_language_config('python')
    
    # Get list of supported languages
    languages = get_supported_languages()
"""

# =============================================================================
# GitHub Repository Configuration
# =============================================================================

GITHUB_REPOS = {
    'python': 'modelcontextprotocol/python-sdk',
    'typescript': 'modelcontextprotocol/typescript-sdk',
    'rust': 'modelcontextprotocol/rust-sdk'
}
"""
Mapping of language names to their official GitHub repository URLs.

Each repository contains the official MCP SDK implementation for that language.
The format is 'organization/repository-name'.
"""

# =============================================================================
# Port Allocation Configuration
# =============================================================================

PORT_RANGES = {
    'python': (8000, 8015),      # 16 ports: 8000-8015
    'typescript': (8016, 8031),  # 16 ports: 8016-8031
    'rust': (8032, 8047)         # 16 ports: 8032-8047
}
"""
Port allocation ranges for each language to avoid conflicts during testing.

Each language gets a dedicated range of 16 ports to accommodate multiple
test scenarios and parallel execution. Ports are allocated as follows:
- Python: 8000-8015
- TypeScript: 8016-8031  
- Rust: 8032-8047

The format is (start_port, end_port) inclusive.
"""

# =============================================================================
# Language-Specific Commands
# =============================================================================

LANGUAGE_COMMANDS = {
    'python': {
        'client': 'python -m basic_client',
        'server': 'python -m basic_server'
    },
    'typescript': {
        'client': 'npm run start:client',
        'server': 'npm run start:server'
    },
    'rust': {
        'client': 'cargo run --example basic_client',
        'server': 'cargo run --example basic_server'
    }
}
"""
Commands for running client and server implementations in each language.

These commands are used in Docker containers and test environments to
start the appropriate client or server implementation. Each command
assumes the working directory contains the necessary source files
and dependencies.
"""

# =============================================================================
# Docker Base Images
# =============================================================================

DOCKER_BASE_IMAGES = {
    'python': 'python:3.11-slim',
    'typescript': 'node:20-slim',
    'rust': 'rust:1.75-slim'
}
"""
Docker base images for each language.

These are the official Docker images used as base images for building
test containers. The images are chosen for their stability, security,
and minimal size while providing all necessary runtime dependencies.
"""

# =============================================================================
# Package Manager Configuration
# =============================================================================

PACKAGE_MANAGERS = {
    'python': {
        'install': 'pip install -r requirements.txt',
        'package_file': 'requirements.txt'
    },
    'typescript': {
        'install': 'npm install',
        'package_file': 'package.json'
    },
    'rust': {
        'install': 'cargo build --release',
        'package_file': 'Cargo.toml'
    }
}
"""
Package manager configurations for each language.

Contains the commands and file names used by each language's package
manager for dependency installation and project configuration.
"""

# =============================================================================
# File Pattern Configuration
# =============================================================================

FILE_PATTERNS = {
    'python': {
        'source': '*.py',
        'test': '*_test.py',
        'config': '*.ini'
    },
    'typescript': {
        'source': '*.ts',
        'test': '*.test.ts',
        'config': '*.json'
    },
    'rust': {
        'source': '*.rs',
        'test': '*_test.rs',
        'config': '*.toml'
    }
}
"""
File patterns for different file types in each language.

Used for file discovery, filtering, and organization in test templates
and build processes. Patterns follow standard conventions for each language.
"""

# =============================================================================
# Environment Variable Configuration
# =============================================================================

ENV_VARIABLES = {
    'python': {
        'PYTHONPATH': '/app',
        'PYTHONUNBUFFERED': '1'
    },
    'typescript': {
        'NODE_ENV': 'development',
        'NODE_PATH': '/app'
    },
    'rust': {
        'RUST_LOG': 'info',
        'RUST_BACKTRACE': '1'
    }
}
"""
Environment variables for each language runtime.

These variables are set in Docker containers and test environments to
configure the runtime behavior of each language's SDK and test framework.
"""


def get_language_config(lang: str) -> dict:
    """
    Get all configuration for a specific language.
    
    Args:
        lang: Language name (python, typescript, rust)
        
    Returns:
        dict: Dictionary containing all language-specific configuration including:
            - port_range: Tuple of (start_port, end_port)
            - commands: Dict of client/server commands
            - base_image: Docker base image name
            - package_manager: Dict of install command and package file
            - file_patterns: Dict of file patterns
            - env_variables: Dict of environment variables
            - github_repo: GitHub repository URL
            
    Raises:
        ValueError: If the language is not supported
        
    Example:
        >>> config = get_language_config('python')
        >>> print(config['port_range'])
        (8000, 8015)
        >>> print(config['commands']['client'])
        'python -m basic_client'
    """
    if lang not in PORT_RANGES:
        raise ValueError(f"Unsupported language: {lang}")
        
    return {
        'port_range': PORT_RANGES[lang],
        'commands': LANGUAGE_COMMANDS[lang],
        'base_image': DOCKER_BASE_IMAGES[lang],
        'package_manager': PACKAGE_MANAGERS[lang],
        'file_patterns': FILE_PATTERNS[lang],
        'env_variables': ENV_VARIABLES[lang],
        'github_repo': GITHUB_REPOS[lang]
    }


def get_supported_languages() -> list:
    """
    Get list of all supported languages.
    
    Returns:
        list: List of supported language names
        
    Example:
        >>> languages = get_supported_languages()
        >>> print(languages)
        ['python', 'typescript', 'rust']
    """
    return list(PORT_RANGES.keys())


def get_port_range(lang: str) -> tuple:
    """
    Get port range for a language.
    
    Args:
        lang: Language name (python, typescript, rust)
        
    Returns:
        tuple: Port range as (start_port, end_port)
        
    Raises:
        ValueError: If the language is not supported
        
    Example:
        >>> port_range = get_port_range('python')
        >>> print(port_range)
        (8000, 8015)
    """
    if lang not in PORT_RANGES:
        raise ValueError(f"Unsupported language: {lang}")
    return PORT_RANGES[lang]


def get_commands(lang: str) -> dict:
    """
    Get commands for a language.
    
    Args:
        lang: Language name (python, typescript, rust)
        
    Returns:
        dict: Dictionary with 'client' and 'server' commands
        
    Raises:
        ValueError: If the language is not supported
        
    Example:
        >>> commands = get_commands('python')
        >>> print(commands['client'])
        'python -m basic_client'
    """
    if lang not in LANGUAGE_COMMANDS:
        raise ValueError(f"Unsupported language: {lang}")
    return LANGUAGE_COMMANDS[lang]


def get_base_image(lang: str) -> str:
    """
    Get base image for a language.
    
    Args:
        lang: Language name (python, typescript, rust)
        
    Returns:
        str: Docker base image name
        
    Raises:
        ValueError: If the language is not supported
        
    Example:
        >>> image = get_base_image('python')
        >>> print(image)
        'python:3.11-slim'
    """
    if lang not in DOCKER_BASE_IMAGES:
        raise ValueError(f"Unsupported language: {lang}")
    return DOCKER_BASE_IMAGES[lang]


def get_package_manager(lang: str) -> dict:
    """
    Get package manager info for a language.
    
    Args:
        lang: Language name (python, typescript, rust)
        
    Returns:
        dict: Dictionary with 'install' command and 'package_file' name
        
    Raises:
        ValueError: If the language is not supported
        
    Example:
        >>> pkg_mgr = get_package_manager('python')
        >>> print(pkg_mgr['install'])
        'pip install -r requirements.txt'
    """
    if lang not in PACKAGE_MANAGERS:
        raise ValueError(f"Unsupported language: {lang}")
    return PACKAGE_MANAGERS[lang]


def get_file_patterns(lang: str) -> dict:
    """
    Get file patterns for a language.
    
    Args:
        lang: Language name (python, typescript, rust)
        
    Returns:
        dict: Dictionary with file patterns for source, test, and config files
        
    Raises:
        ValueError: If the language is not supported
        
    Example:
        >>> patterns = get_file_patterns('python')
        >>> print(patterns['source'])
        '*.py'
    """
    if lang not in FILE_PATTERNS:
        raise ValueError(f"Unsupported language: {lang}")
    return FILE_PATTERNS[lang]


def get_env_variables(lang: str) -> dict:
    """
    Get environment variables for a language.
    
    Args:
        lang: Language name (python, typescript, rust)
        
    Returns:
        dict: Dictionary of environment variable names and values
        
    Raises:
        ValueError: If the language is not supported
        
    Example:
        >>> env_vars = get_env_variables('python')
        >>> print(env_vars['PYTHONPATH'])
        '/app'
    """
    if lang not in ENV_VARIABLES:
        raise ValueError(f"Unsupported language: {lang}")
    return ENV_VARIABLES[lang]


def get_github_repo(lang: str) -> str:
    """
    Get GitHub repository for a language.
    
    Args:
        lang: Language name (python, typescript, rust)
        
    Returns:
        str: GitHub repository URL in format 'organization/repository'
        
    Raises:
        ValueError: If the language is not supported
        
    Example:
        >>> repo = get_github_repo('python')
        >>> print(repo)
        'modelcontextprotocol/python-sdk'
    """
    if lang not in GITHUB_REPOS:
        raise ValueError(f"Unsupported language: {lang}")
    return GITHUB_REPOS[lang] 