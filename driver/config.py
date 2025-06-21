"""
Configuration management for MCPBench test framework.

This module provides centralized configuration management for the MCPBench
compatibility testing framework. It handles SDK version information,
compatibility matrices, test categories, timeouts, and Docker configurations.

The module uses dataclasses for structured configuration and provides
class methods for loading, querying, and updating configuration data.

Key Features:
- SDK version tracking with metadata
- Compatibility matrix management
- Test category definitions and timeouts
- Docker configuration management
- Test data path management
- Report configuration

Usage:
    from config import TestConfig, SDKVersion, SDKConfig
    
    # Load SDK information
    TestConfig.load_sdk_info()
    
    # Get test matrix
    matrix = TestConfig.get_test_matrix(
        client_lang="python",
        server_lang="typescript"
    )
    
    # Get timeout for a test category
    timeout = TestConfig.get_timeout("connection")
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
from datetime import datetime
import semver
import json

@dataclass
class SDKVersion:
    """
    SDK version information with metadata.
    
    This dataclass represents a specific version of an MCP SDK with
    associated metadata such as release date, compatibility information,
    and deprecation status.
    
    Attributes:
        version: Semantic version string (e.g., "1.0.0")
        release_date: Date when this version was released
        is_latest: Whether this is the latest version
        is_deprecated: Whether this version is deprecated
        compatibility_matrix: Mapping of language -> set of compatible versions
    """
    version: str
    release_date: Optional[datetime] = None
    is_latest: bool = False
    is_deprecated: bool = False
    compatibility_matrix: Optional[Dict[str, Set[str]]] = None

@dataclass
class SDKConfig:
    """
    Configuration for a specific SDK version.
    
    This dataclass contains all configuration needed to run tests
    with a specific SDK version, including Docker settings, ports,
    and package information.
    
    Attributes:
        version: SDKVersion object containing version metadata
        docker_image: Docker image name for this SDK version
        ports: List of port numbers available for this version
        requirements_file: Path to requirements/package file
        package_name: Name of the package in package manager
        min_compatible_version: Minimum compatible version
        max_compatible_version: Maximum compatible version
    """
    version: SDKVersion
    docker_image: str
    ports: List[str]
    requirements_file: Optional[str] = None
    package_name: Optional[str] = None
    min_compatible_version: Optional[str] = None
    max_compatible_version: Optional[str] = None

class TestConfig:
    """
    Centralized test configuration management.
    
    This class provides static configuration management for the entire
    MCPBench framework. It manages SDK versions, test categories,
    timeouts, Docker configurations, and test data paths.
    
    The class uses class variables to store configuration data and
    provides class methods for loading, querying, and updating this data.
    """
    
    # SDK Versions and Configurations
    SDK_VERSIONS: Dict[str, Dict[str, SDKConfig]] = {}
    """
    Dictionary mapping language -> version -> SDKConfig.
    
    Structure:
        {
            "python": {
                "1.0.0": SDKConfig(...),
                "1.1.0": SDKConfig(...)
            },
            "typescript": {
                "1.0.0": SDKConfig(...)
            }
        }
    """

    @classmethod
    def load_sdk_info(cls) -> None:
        """
        Load SDK information from JSON file.
        
        This method reads the sdkinfo.json file and populates the
        SDK_VERSIONS class variable with SDKConfig objects. It handles
        conversion of date strings to datetime objects and compatibility
        matrix lists to sets.
        
        The JSON file should have the following structure:
        {
            "python": {
                "1.0.0": {
                    "version": "1.0.0",
                    "release_date": "2024-01-01T00:00:00Z",
                    "is_latest": true,
                    "compatibility_matrix": {
                        "typescript": ["1.0.0", "1.1.0"]
                    }
                }
            }
        }
        
        Raises:
            FileNotFoundError: If sdkinfo.json doesn't exist
            json.JSONDecodeError: If sdkinfo.json contains invalid JSON
        """
        with open(Path(__file__).parent / "sdkinfo.json", "r") as f:
            sdk_info = json.load(f)
            
        for lang, versions in sdk_info.items():
            cls.SDK_VERSIONS[lang] = {}
            for version, info in versions.items():
                # Convert release_date string to datetime if present
                release_date = None
                if info.get("release_date"):
                    release_date = datetime.fromisoformat(info["release_date"])
                
                # Convert compatibility matrix lists to sets
                compatibility_matrix = None
                if info.get("compatibility_matrix"):
                    compatibility_matrix = {
                        k: set(v) for k, v in info["compatibility_matrix"].items()
                    }
                
                sdk_version = SDKVersion(
                    version=info["version"],
                    release_date=release_date,
                    is_latest=info.get("is_latest", False),
                    is_deprecated=info.get("is_deprecated", False),
                    compatibility_matrix=compatibility_matrix
                )
                
                cls.SDK_VERSIONS[lang][version] = SDKConfig(
                    version=sdk_version,
                    docker_image=info["docker_image"],
                    ports=info["ports"],
                    requirements_file=info.get("requirements_file"),
                    package_name=info.get("package_name")
                )

    # Test categories based on SDK test organization
    TEST_CATEGORIES = [
        # Core functionality
        "connection",       # Connection establishment and management
        "transport",        # Transport layer including stdio, websocket, etc.
        "creation",         # Resource creation and initialization
        "notifications",    # Notification system
        "types",            # Type system and compatibility
        "session",          # Session management and lifecycle
        "session_group",    # Session group operations
        "auth",             # Authentication and authorization
        "config",           # Configuration handling
        "resource_cleanup", # Resource cleanup and management
        "sampling",         # Sampling operations
        "list_methods",     # Method listing and discovery
        "list_roots",       # Root listing operations
        "logging",          # Logging functionality
        
        # Protocol and Schema
        "message_protocol", # Message protocol implementation
        "message_schema",   # Message schema validation
        "deserialization",  # Data deserialization
        "complex_schema",   # Complex schema handling
        
        # Tool and Notification
        "tool_handling",    # Tool registration and handling
        "notification",     # Notification system
        
        # Language-specific
        "type_safety",      # Type safety across languages
        "async_handling",   # Async/await patterns
        "error_handling",   # Error handling patterns
        "memory_safety"     # Memory safety (Rust specific)
    ]
    """
    List of test categories for organizing compatibility tests.
    
    These categories represent different aspects of MCP protocol
    implementation that need to be tested across language combinations.
    Each category focuses on a specific functional area or protocol
    feature.
    """

    # Supported languages
    SUPPORTED_LANGUAGES = [
        "python",
        "typescript",
        "rust"
    ]
    """
    List of supported programming languages for MCP SDKs.
    
    These are the languages for which official MCP SDKs exist
    and are supported by the compatibility testing framework.
    """

    # Test timeouts (in seconds)
    TIMEOUTS = {
        # Core functionality
        "connection": 30,
        "transport": 60,
        "creation": 45,
        "notifications": 90,
        "types": 30,
        "session": 60,
        "session_group": 60,
        "auth": 45,
        "config": 30,
        "resource_cleanup": 45,
        "sampling": 30,
        "list_methods": 45,
        "list_roots": 30,
        "logging": 30,
        
        # Protocol and Schema
        "message_protocol": 60,
        "message_schema": 45,
        "deserialization": 45,
        "complex_schema": 60,
        
        # Tool and Notification
        "tool_handling": 45,
        "notification": 45,
        
        # Language-specific
        "type_safety": 30,
        "async_handling": 45,
        "error_handling": 30,
        "memory_safety": 30
    }
    """
    Timeout values for different test categories in seconds.
    
    These timeouts ensure that tests don't hang indefinitely and
    provide reasonable limits for different types of operations.
    Longer timeouts are given to operations that may take more time
    (e.g., notifications, complex schema handling).
    """

    # Docker configurations
    DOCKER_CONFIG = {
        "python": {
            "image": "python:3.11-slim",
            "ports": ["8000:8000"]
        },
        "typescript": {
            "image": "node:18-slim",
            "ports": ["8001:8001"]
        },
        "rust": {
            "image": "rust:1.75-slim",
            "ports": ["8002:8002"]
        }
    }
    """
    Docker configuration for each supported language.
    
    Contains the base Docker image and default port mapping for
    each language. These configurations are used when generating
    Docker Compose files and Dockerfiles.
    """

    # Test data paths
    TEST_DATA_PATHS = {
        # Core functionality
        "connection": Path("common/test_data/connection"),
        "transport": Path("common/test_data/transport"),
        "creation": Path("common/test_data/creation"),
        "notifications": Path("common/test_data/notifications"),
        "types": Path("common/test_data/types"),
        "session": Path("common/test_data/session"),
        "session_group": Path("common/test_data/session_group"),
        "auth": Path("common/test_data/auth"),
        "config": Path("common/test_data/config"),
        "resource_cleanup": Path("common/test_data/resource_cleanup"),
        "sampling": Path("common/test_data/sampling"),
        "list_methods": Path("common/test_data/list_methods"),
        "list_roots": Path("common/test_data/list_roots"),
        "logging": Path("common/test_data/logging"),
        
        # Protocol and Schema
        "message_protocol": Path("common/test_data/message_protocol"),
        "message_schema": Path("common/test_data/message_schema"),
        "deserialization": Path("common/test_data/deserialization"),
        "complex_schema": Path("common/test_data/complex_schema"),
        
        # Tool and Notification
        "tool_handling": Path("common/test_data/tool_handling"),
        "notification": Path("common/test_data/notification"),
        
        # Language-specific
        "type_safety": Path("common/test_data/type_safety"),
        "async_handling": Path("common/test_data/async_handling"),
        "error_handling": Path("common/test_data/error_handling"),
        "memory_safety": Path("common/test_data/memory_safety")
    }
    """
    Paths to test data for each test category.
    
    These paths point to directories containing test data, fixtures,
    and expected results for each test category. The data is used
    to validate test results and provide consistent test scenarios.
    """

    # Report configurations
    REPORT_CONFIG = {
        "junit": {
            "enabled": True,
            "output_dir": Path("reports/junit")
        },
        "html": {
            "enabled": True,
            "output_dir": Path("reports/html"),
            "template": Path("common/templates/report.html")
        },
        "json": {
            "enabled": True,
            "output_dir": Path("reports/json")
        }
    }
    """
    Configuration for different report formats.
    
    Defines which report formats are enabled and where they should
    be saved. Supported formats include JUnit XML, HTML, and JSON.
    """

    @classmethod
    def get_test_matrix(cls, 
                       client_lang: str = None, 
                       server_lang: str = None,
                       client_version: str = None,
                       server_version: str = None) -> List[Dict[str, str]]:
        """
        Generate the test matrix based on supported languages and versions.
        
        This method creates a list of test combinations based on the
        compatibility matrix. It can filter by specific languages and
        versions, or generate all possible combinations.
        
        Args:
            client_lang: Optional client language to filter by
            server_lang: Optional server language to filter by
            client_version: Optional client version to filter by
            server_version: Optional server version to filter by
            
        Returns:
            List of dictionaries, each containing:
                - client_lang: Client language
                - client_version: Client version
                - server_lang: Server language
                - server_version: Server version
                - categories: List of test categories to run
                
        Example:
            >>> matrix = TestConfig.get_test_matrix(
            ...     client_lang="python",
            ...     server_lang="typescript"
            ... )
            >>> print(len(matrix))
            4  # Assuming 2 Python versions × 2 TypeScript versions
        """
        matrix = []
        
        # Get all available languages
        client_langs = [client_lang] if client_lang else cls.SDK_VERSIONS.keys()
        server_langs = [server_lang] if server_lang else cls.SDK_VERSIONS.keys()
        
        for cl in client_langs:
            client_versions = [client_version] if client_version else cls.SDK_VERSIONS[cl].keys()
            for cv in client_versions:
                client_config = cls.SDK_VERSIONS[cl][cv]
                
                for sl in server_langs:
                    if sl == cl and cv == "latest":
                        continue  # Skip same language/latest version combinations
                        
                    server_versions = [server_version] if server_version else cls.SDK_VERSIONS[sl].keys()
                    for sv in server_versions:
                        server_config = cls.SDK_VERSIONS[sl][sv]
                        
                        # Check compatibility
                        if (client_config.version.compatibility_matrix and 
                            sl in client_config.version.compatibility_matrix and
                            sv in client_config.version.compatibility_matrix[sl]):
                            
                            matrix.append({
                                "client_lang": cl,
                                "client_version": cv,
                                "server_lang": sl,
                                "server_version": sv,
                                "categories": cls.TEST_CATEGORIES
                            })
        
        return matrix

    @classmethod
    def get_timeout(cls, category: str) -> int:
        """
        Get timeout for a specific test category.
        
        Args:
            category: Test category name
            
        Returns:
            Timeout value in seconds (defaults to 30 if category not found)
            
        Example:
            >>> timeout = TestConfig.get_timeout("connection")
            >>> print(timeout)
            30
        """
        return cls.TIMEOUTS.get(category, 30)  # Default 30 seconds

    @classmethod
    def get_docker_config(cls, language: str) -> Dict:
        """
        Get Docker configuration for a specific language.
        
        Args:
            language: Language name (python, typescript, rust)
            
        Returns:
            Dictionary containing Docker image and ports configuration
            
        Example:
            >>> config = TestConfig.get_docker_config("python")
            >>> print(config["image"])
            'python:3.11-slim'
        """
        return cls.DOCKER_CONFIG.get(language, {})

    @classmethod
    def get_sdk_config(cls, language: str, version: str) -> SDKConfig:
        """
        Get SDK configuration for a specific language and version.
        
        Args:
            language: Language name (python, typescript, rust)
            version: SDK version string
            
        Returns:
            SDKConfig object for the specified language and version
            
        Raises:
            KeyError: If language or version doesn't exist
            
        Example:
            >>> config = TestConfig.get_sdk_config("python", "1.0.0")
            >>> print(config.version.version)
            '1.0.0'
        """
        return cls.SDK_VERSIONS[language][version]

    @classmethod
    def add_sdk_version(cls, language: str, version: str, config: SDKConfig) -> None:
        """
        Add a new SDK version to the configuration.
        
        Args:
            language: Language name (python, typescript, rust)
            version: SDK version string
            config: SDKConfig object for the new version
            
        Example:
            >>> new_config = SDKConfig(...)
            >>> TestConfig.add_sdk_version("python", "1.2.0", new_config)
        """
        if language not in cls.SDK_VERSIONS:
            cls.SDK_VERSIONS[language] = {}
        cls.SDK_VERSIONS[language][version] = config

    @classmethod
    def update_compatibility_matrix(cls, language: str, version: str, 
                                  compatibility_matrix: Dict[str, Set[str]]) -> None:
        """
        Update the compatibility matrix for a specific SDK version.
        
        Args:
            language: Language name (python, typescript, rust)
            version: SDK version string
            compatibility_matrix: New compatibility matrix
            
        Example:
            >>> matrix = {"typescript": {"1.0.0", "1.1.0"}}
            >>> TestConfig.update_compatibility_matrix("python", "1.0.0", matrix)
        """
        if language in cls.SDK_VERSIONS and version in cls.SDK_VERSIONS[language]:
            cls.SDK_VERSIONS[language][version].version.compatibility_matrix = compatibility_matrix

# Initialize SDK versions from JSON file
TestConfig.load_sdk_info() 