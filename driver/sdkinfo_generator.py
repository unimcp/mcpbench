#!/usr/bin/env python3
"""
SDK Information Generator for MCPBench.

This module provides automated SDK information extraction and management
for the MCPBench compatibility testing framework. It fetches release
information from official MCP SDK GitHub repositories and generates
compatibility matrices for cross-language testing.

The module consists of three main classes:
- SDKVersionUpdater: Fetches and updates SDK version information
- TestStructureCreator: Creates test directory structure
- PackageFileGenerator: Generates package files for each language

Key Features:
- GitHub API integration for release information
- Automated version detection and parsing
- Compatibility matrix generation
- Test structure creation
- Package file generation
- Backup and restore functionality

Usage:
    python sdkinfo_generator.py
    
    # Or import and use programmatically
    from sdkinfo_generator import SDKVersionUpdater
    
    updater = SDKVersionUpdater(Path("sdkinfo.json"))
    updater.update()
"""

import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import semver
import time
import sys
import os
import shutil

from language_config import (
    get_supported_languages,
    get_base_image,
    get_github_repo,
    get_port_range
)
from constants import (
    SDK_INFO_FILE, SDK_INFO_BACKUP,
    GITHUB_API_BASE, GITHUB_TOKEN_ENV, CLIENT, SERVER,
    PYTHON_REQUIREMENTS, TYPESCRIPT_PACKAGE, RUST_CARGO,
    PYTHON_PACKAGE, TYPESCRIPT_PACKAGE, RUST_PACKAGE,
    DIR_TEMPLATES, DIR_TESTS, DIR_MATRIX,
    MSG_CREATING_NEW, MSG_INVALID_JSON, MSG_NO_RELEASES,
    MSG_ADDING_VERSION, MSG_VERSION_EXISTS, MSG_UPDATE_SUCCESS,
    MSG_UPDATE_ERROR, MSG_RESTORED_BACKUP, MSG_SETUP_COMPLETE,
    MSG_CREATED_DIRS, MSG_RATE_LIMIT, MSG_FETCH_ERROR,
    MSG_RUST_VERSION_ERROR, MSG_RUST_VERSION_WARNING,
    MSG_RELEASE_INFO_WARNING, MSG_INVALID_VERSION,
    PYTHON_PACKAGE_PLACEHOLDER, RUST_PACKAGE_PLACEHOLDER,
    TYPESCRIPT_PACKAGE_PLACEHOLDER
)


class SDKVersionUpdater:
    """
    Automated SDK version information updater.
    
    This class handles fetching SDK release information from GitHub
    repositories, parsing version data, and updating the local SDK
    information file. It supports all official MCP SDKs and handles
    rate limiting, error recovery, and backup functionality.
    
    The class uses the GitHub API to fetch release information and
    constructs compatibility matrices based on version availability
    across different SDKs.
    
    Attributes:
        sdkinfo_path: Path to the SDK information JSON file
        github_api_base: Base URL for GitHub API
        repos: Dictionary mapping languages to GitHub repository URLs
        current_info: Currently loaded SDK information
        session: Requests session for API calls
    """
    
    def __init__(self, sdkinfo_path: Path):
        """
        Initialize the SDK version updater.
        
        Args:
            sdkinfo_path: Path to the SDK information JSON file
            
        The initializer sets up the GitHub API session, loads current
        SDK information, and prepares for fetching new release data.
        """
        self.sdkinfo_path = sdkinfo_path
        self.github_api_base = GITHUB_API_BASE
        self.repos = {lang: get_github_repo(lang) for lang in get_supported_languages()}
        self.current_info = self._load_current_info()
        self.session = requests.Session()
        
        # Add GitHub token if available for higher rate limits
        github_token = os.environ.get(GITHUB_TOKEN_ENV)
        if github_token:
            self.session.headers.update({
                'Authorization': f'token {github_token}'
            })

    def _load_current_info(self) -> Dict:
        """
        Load current SDK information from JSON file.
        
        Returns:
            Dictionary containing current SDK information
            
        Raises:
            SystemExit: If the file contains invalid JSON
            
        This method handles file creation for new installations and
        JSON validation for existing files.
        """
        try:
            with open(self.sdkinfo_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(MSG_CREATING_NEW.format(self.sdkinfo_path))
            return {lang: {} for lang in get_supported_languages()}
        except json.JSONDecodeError:
            print(MSG_INVALID_JSON.format(self.sdkinfo_path))
            sys.exit(1)

    def _get_rust_version_from_cargo(self) -> str:
        """
        Get Rust SDK version from Cargo.toml file.
        
        Returns:
            Version string from Cargo.toml
            
        This method fetches the Cargo.toml file from the Rust SDK
        repository and extracts the version field. It handles base64
        decoding of the file content and version parsing.
        """
        url = f"{self.github_api_base}/{self.repos['rust']}/contents/{RUST_CARGO}"
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                content = response.json()
                if 'content' in content:
                    import base64
                    cargo_content = base64.b64decode(content['content']).decode('utf-8')
                    for line in cargo_content.split('\n'):
                        if line.startswith('version = '):
                            version = line.split('=')[1].strip().strip('"')
                            return self._parse_version(version)
            print(MSG_RUST_VERSION_WARNING)
            return "0.1.0"  # Default version if we can't fetch
        except Exception as e:
            print(MSG_RUST_VERSION_ERROR.format(e))
            return "0.1.0"  # Default version if we can't fetch

    def _get_latest_releases(self) -> Dict[str, List[Dict]]:
        """
        Get latest releases from GitHub for each SDK.
        
        Returns:
            Dictionary mapping language to list of release information
            
        This method fetches release information for all supported
        languages. For Rust, it creates a synthetic release from
        Cargo.toml since the Rust SDK doesn't use GitHub releases.
        """
        releases = {}
        for lang, repo in self.repos.items():
            print(f"Fetching releases for {lang} from {repo}")
            if lang == "rust":
                # For Rust, create a synthetic release from Cargo.toml
                version = self._get_rust_version_from_cargo()
                print(f"Created synthetic release for Rust: {version}")
                releases[lang] = [{
                    "tag_name": f"v{version}",
                    "published_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                }]
                continue

            url = f"{self.github_api_base}/{repo}/releases"
            try:
                print(f"Fetching from URL: {url}")
                response = self.session.get(url)
                if response.status_code == 200:
                    releases[lang] = response.json()
                    print(f"Found {len(releases[lang])} releases for {lang}")
                elif response.status_code == 403:
                    print(MSG_RATE_LIMIT.format(lang))
                    sys.exit(1)
                else:
                    print(f"Error fetching releases for {lang}: {response.status_code}")
                    print(f"Response: {response.text}")
            except requests.exceptions.RequestException as e:
                print(MSG_FETCH_ERROR.format(lang, e))
            
            # Respect GitHub API rate limits
            time.sleep(1)
        
        return releases

    def _parse_version(self, version_str: str) -> str:
        """
        Parse version string to ensure consistent format.
        
        Args:
            version_str: Raw version string from GitHub
            
        Returns:
            Normalized version string
            
        This method handles various version formats including:
        - Pre-release versions (rc, alpha, beta)
        - Version prefixes (v1.0.0)
        - Invalid version strings (with fallback)
        """
        # Remove 'v' prefix if present
        version_str = version_str.lstrip('v')
        # Handle pre-release versions
        if 'rc' in version_str:
            # Convert rc to -rc for semver compatibility
            version_str = version_str.replace('rc', '-rc')
        try:
            return str(semver.VersionInfo.parse(version_str))
        except ValueError as e:
            print(MSG_INVALID_VERSION.format(version_str, e))
            # For pre-release versions, try to extract the base version
            if 'rc' in version_str:
                base_version = version_str.split('rc')[0]
                try:
                    return str(semver.VersionInfo.parse(base_version))
                except ValueError:
                    pass
            return version_str

    def _get_release_info(self, lang: str, version: str, tag_name: str) -> Dict:
        """
        Get release information from GitHub API or fallback to main repo.
        
        Args:
            lang: Language name
            version: Version string
            tag_name: GitHub tag name
            
        Returns:
            Dictionary containing release information
            
        This method attempts to fetch detailed release information
        from the GitHub API. If that fails, it falls back to basic
        information from the main repository.
        """
        repo = self.repos[lang]
        url = f"{self.github_api_base}/{repo}/releases/tags/{tag_name}"
        
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                release_data = response.json()
                return {
                    "github_repo": release_data.get("html_url", f"https://github.com/{repo}"),
                    "release_date": release_data.get("published_at", datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")),
                    "package_name": self._get_package_name(lang, version)
                }
        except Exception as e:
            print(MSG_RELEASE_INFO_WARNING.format(lang, version, e))
        
        # Fallback to main repo URL
        return {
            "github_repo": f"https://github.com/{repo}",
            "release_date": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "package_name": self._get_package_name(lang, version)
        }

    def _get_package_name(self, lang: str, version: str) -> str:
        """
        Get package name based on language and version.
        
        Args:
            lang: Language name
            version: Version string
            
        Returns:
            Package specification string for the package manager
            
        This method formats package names according to the conventions
        of each language's package manager.
        """
        if lang == "python":
            return PYTHON_PACKAGE_PLACEHOLDER.format(PYTHON_PACKAGE, version)
        elif lang == "typescript":
            return TYPESCRIPT_PACKAGE_PLACEHOLDER.format(TYPESCRIPT_PACKAGE)
        elif lang == "rust":
            return RUST_PACKAGE_PLACEHOLDER.format(RUST_PACKAGE, version)
        return ""

    def _get_compatibility_matrix(self, lang: str, all_versions: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Get compatibility matrix for a given SDK version.
        
        Args:
            lang: Language name
            all_versions: Dictionary of all available versions per language
            
        Returns:
            Compatibility matrix mapping language to list of compatible versions
            
        This method creates a compatibility matrix by:
        1. Including self-compatibility (same language)
        2. Adding cross-language compatibility
        3. Filtering out pre-release versions
        4. Limiting to the latest 2 versions per language
        """
        matrix = {}
        
        # Add self-compatibility (same language)
        if lang in all_versions:
            # Get versions for the same language
            same_lang_versions = all_versions[lang]
            # Filter out pre-release versions
            stable_versions = [v for v in same_lang_versions if 'rc' not in v]
            # Take the latest 2 versions
            matrix[lang] = stable_versions[:2]
        
        # Add cross-language compatibility
        for other_lang in self.repos.keys():
            if other_lang != lang:
                # Get versions for the other language from all_versions
                other_versions = all_versions.get(other_lang, [])
                # Filter out pre-release versions
                stable_versions = [v for v in other_versions if 'rc' not in v]
                # Take the latest 2 versions
                matrix[other_lang] = stable_versions[:2]
        
        return matrix

    def _update_sdk_info(self, releases: Dict[str, List[Dict]]):
        """
        Update SDK information with latest releases.
        
        Args:
            releases: Dictionary of release information per language
            
        This method processes the fetched release information and
        updates the SDK information with new versions, compatibility
        matrices, and metadata.
        """
        print(f"Updating SDK info with releases: {json.dumps(releases, indent=2)}")
        # First pass: collect all versions
        all_versions = {}
        for lang, lang_releases in releases.items():
            all_versions[lang] = []
            for release in lang_releases:
                version = self._parse_version(release['tag_name'])
                all_versions[lang].append(version)
        
        # Second pass: update SDK info with compatibility matrices
        for lang, lang_releases in releases.items():
            if lang not in self.current_info:
                self.current_info[lang] = {}
            
            for release in lang_releases:
                version = self._parse_version(release['tag_name'])
                
                # Check if version already exists
                if version in self.current_info[lang]:
                    print(MSG_VERSION_EXISTS.format(version, lang))
                    continue
                
                print(MSG_ADDING_VERSION.format(version, lang))
                
                # Get release information
                release_info = self._get_release_info(lang, version, release['tag_name'])
                
                # Get compatibility matrix
                compatibility_matrix = self._get_compatibility_matrix(lang, all_versions)
                
                # Create version info
                version_info = {
                    "version": version,
                    "release_date": release_info["release_date"],
                    "github_repo": release_info["github_repo"],
                    "package_name": release_info["package_name"],
                    "docker_image": get_base_image(lang),
                    "ports": [str(p) for p in range(*get_port_range(lang))],
                    "is_latest": True,  # Mark as latest for now
                    "compatibility_matrix": compatibility_matrix
                }
                
                # Update is_latest flags
                for existing_version in self.current_info[lang]:
                    self.current_info[lang][existing_version]["is_latest"] = False
                
                self.current_info[lang][version] = version_info

    def _backup_current_info(self):
        """Create a backup of current SDK information."""
        if self.sdkinfo_path.exists():
            shutil.copy2(self.sdkinfo_path, self.sdkinfo_path.with_suffix('.json.bak'))

    def _save_sdk_info(self):
        """Save updated SDK information to JSON file."""
        try:
            with open(self.sdkinfo_path, 'w') as f:
                json.dump(self.current_info, f, indent=2)
            print(MSG_UPDATE_SUCCESS.format(self.sdkinfo_path))
        except Exception as e:
            print(MSG_UPDATE_ERROR.format(e))
            # Restore from backup if save fails
            if self.sdkinfo_path.with_suffix('.json.bak').exists():
                shutil.copy2(self.sdkinfo_path.with_suffix('.json.bak'), self.sdkinfo_path)
                print(MSG_RESTORED_BACKUP)

    def update(self):
        """
        Perform the complete SDK information update process.
        
        This method orchestrates the entire update process:
        1. Creates a backup of current information
        2. Fetches latest releases from GitHub
        3. Updates SDK information with new versions
        4. Saves the updated information
        5. Creates test structure and package files
        """
        print("Starting SDK information update...")
        
        # Create backup
        self._backup_current_info()
        
        # Fetch latest releases
        releases = self._get_latest_releases()
        
        # Update SDK information
        self._update_sdk_info(releases)
        
        # Save updated information
        self._save_sdk_info()
        
        # Create test structure and package files
        base_path = self.sdkinfo_path.parent.parent
        structure_creator = TestStructureCreator(base_path)
        structure_creator.create_structure(self.current_info)
        
        package_generator = PackageFileGenerator(base_path)
        package_generator.generate_package_files(self.current_info)
        
        print(MSG_SETUP_COMPLETE)


class TestStructureCreator:
    """
    Creates test directory structure for SDK versions.
    
    This class generates the directory structure needed for testing
    each SDK version. It creates language-specific directories and
    organizes them by version and role (client/server).
    
    Attributes:
        base_path: Base path for the test structure
    """
    
    def __init__(self, base_path: Path):
        """
        Initialize the test structure creator.
        
        Args:
            base_path: Base path for creating the test structure
        """
        self.base_path = base_path

    def create_structure(self, sdkinfo: Dict):
        """
        Create test directory structure for all SDK versions.
        
        Args:
            sdkinfo: SDK information dictionary
            
        This method creates directories for each language, version,
        and role combination to support the N×N compatibility matrix.
        """
        for lang, versions in sdkinfo.items():
            for version, version_info in versions.items():
                print(MSG_CREATED_DIRS.format(lang, version))
                
                # Create directories for each role
                for role in [CLIENT, SERVER]:
                    # Create main directory structure
                    dir_path = self.base_path / DIR_MATRIX / DIR_TEMPLATES / lang / role / version
                    dir_path.mkdir(parents=True, exist_ok=True)
                    
                    # Create subdirectories for different test types
                    for test_type in ["e2e", "unit", "integration"]:
                        (dir_path / test_type).mkdir(exist_ok=True)


class PackageFileGenerator:
    """
    Generates package files for different languages and versions.
    
    This class creates the appropriate package files (requirements.txt,
    package.json, Cargo.toml) for each SDK version to ensure proper
    dependency management in test environments.
    
    Attributes:
        base_path: Base path for generating package files
    """
    
    def __init__(self, base_path: Path):
        """
        Initialize the package file generator.
        
        Args:
            base_path: Base path for generating package files
        """
        self.base_path = base_path

    def generate_package_files(self, sdkinfo: Dict):
        """
        Generate package files for all SDK versions.
        
        Args:
            sdkinfo: SDK information dictionary
            
        This method creates package files for each language and version
        combination to ensure proper dependency management.
        """
        for lang, versions in sdkinfo.items():
            for version, version_info in versions.items():
                self._generate_language_package_files(lang, version, version_info)

    def _generate_language_package_files(self, lang: str, version: str, version_info: Dict):
        """
        Generate package files for a specific language and version.
        
        Args:
            lang: Language name
            version: Version string
            version_info: Version information dictionary
        """
        if lang == "python":
            self._generate_python_requirements(version, version_info)
        elif lang == "typescript":
            self._generate_typescript_package_json(version, version_info)
        elif lang == "rust":
            self._generate_rust_cargo_toml(version, version_info)

    def _generate_python_requirements(self, version: str, version_info: Dict):
        """
        Generate Python requirements.txt file.
        
        Args:
            version: Python SDK version
            version_info: Version information dictionary
        """
        requirements_content = f"""# Python MCP SDK Requirements
# Generated for version {version}

# Core MCP SDK
{version_info['package_name']}

# Testing dependencies
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0

# Development dependencies
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0
"""
        
        # Write requirements file for each role
        for role in [CLIENT, SERVER]:
            req_file = self.base_path / DIR_MATRIX / DIR_TEMPLATES / "python" / role / version / PYTHON_REQUIREMENTS
            req_file.parent.mkdir(parents=True, exist_ok=True)
            with open(req_file, 'w') as f:
                f.write(requirements_content)

    def _generate_typescript_package_json(self, version: str, version_info: Dict):
        """
        Generate TypeScript package.json file.
        
        Args:
            version: TypeScript SDK version
            version_info: Version information dictionary
        """
        package_json_content = f"""{{
  "name": "mcp-typescript-{version}",
  "version": "{version}",
  "description": "TypeScript MCP SDK Test Environment",
  "main": "index.js",
  "scripts": {{
    "test": "jest",
    "build": "tsc",
    "start:client": "ts-node src/client.ts",
    "start:server": "ts-node src/server.ts"
  }},
  "dependencies": {{
    "@modelcontextprotocol/sdk": "latest"
  }},
  "devDependencies": {{
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0",
    "ts-node": "^10.9.0",
    "jest": "^29.0.0",
    "@types/jest": "^29.0.0"
  }}
}}
"""
        
        # Write package.json for each role
        for role in [CLIENT, SERVER]:
            pkg_file = self.base_path / DIR_MATRIX / DIR_TEMPLATES / "typescript" / role / version / TYPESCRIPT_PACKAGE
            pkg_file.parent.mkdir(parents=True, exist_ok=True)
            with open(pkg_file, 'w') as f:
                f.write(package_json_content)

    def _generate_rust_cargo_toml(self, version: str, version_info: Dict):
        """
        Generate Rust Cargo.toml file.
        
        Args:
            version: Rust SDK version
            version_info: Version information dictionary
        """
        cargo_content = f"""[package]
name = "mcp-rust-{version}"
version = "{version}"
edition = "2021"

[dependencies]
mcp-rust-sdk = "={version}"
tokio = {{ version = "1.0", features = ["full"] }}
serde = {{ version = "1.0", features = ["derive"] }}
serde_json = "1.0"

[dev-dependencies]
tokio-test = "0.4"
"""
        
        # Write Cargo.toml for each role
        for role in [CLIENT, SERVER]:
            cargo_file = self.base_path / DIR_MATRIX / DIR_TEMPLATES / "rust" / role / version / RUST_CARGO
            cargo_file.parent.mkdir(parents=True, exist_ok=True)
            with open(cargo_file, 'w') as f:
                f.write(cargo_content)


def main():
    """
    Main entry point for the SDK information generator.
    
    This function initializes the SDK version updater and performs
    the complete update process. It handles command-line execution
    and provides user feedback throughout the process.
    """
    script_dir = Path(__file__).parent
    sdkinfo_path = script_dir / SDK_INFO_FILE
    
    print("MCPBench SDK Information Generator")
    print("==================================")
    
    updater = SDKVersionUpdater(sdkinfo_path)
    updater.update()


if __name__ == "__main__":
    main() 