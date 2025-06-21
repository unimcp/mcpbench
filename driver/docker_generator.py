#!/usr/bin/env python3
"""
Docker environment generator for MCPBench compatibility testing.

This module generates Docker environments for cross-language MCP
compatibility testing. It creates Docker Compose files, Dockerfiles,
and port mappings for all client-server combinations in the N×N
compatibility matrix.

The module uses template-based generation to create consistent
Docker environments across different language combinations and
handles port allocation to avoid conflicts during parallel testing.

Key Features:
- Docker Compose file generation for client-server combinations
- Template-based Dockerfile generation
- Automatic port allocation and mapping
- Support for all official MCP SDKs
- Cross-language compatibility testing environments

Usage:
    python docker_generator.py
    
    # Or import and use programmatically
    from docker_generator import DockerGenerator
    
    generator = DockerGenerator(Path("docker"), Path("matrix"))
    generator.generate_docker_files()
"""

import json
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import yaml
import logging

from language_config import (
    get_supported_languages,
    get_base_image,
    get_github_repo,
    get_port_range,
    get_commands
)
from constants import (
    SDK_INFO_FILE,
    CLIENT, SERVER, DIR_TEMPLATES, DIR_TESTS, DIR_DRIVER, DIR_DOCKER, DIR_MATRIX,
    DOCKER_COMPOSE_TEMPLATE, CLIENT_SERVER_COMPOSE_TEMPLATE, DOCKERFILE_TEMPLATE,
    PLACEHOLDER_VERSION, PLACEHOLDER_LANGUAGE, PLACEHOLDER_PORT,
    PLACEHOLDER_ROLE, PLACEHOLDER_COMMAND, PLACEHOLDER_CLIENT_LANG,
    PLACEHOLDER_CLIENT_VER, PLACEHOLDER_CLIENT_PORT, PLACEHOLDER_SERVER_LANG,
    PLACEHOLDER_SERVER_VER, PLACEHOLDER_SERVER_PORT, PLACEHOLDER_CLIENT_COMMAND,
    PLACEHOLDER_SERVER_COMMAND
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DockerGenerator:
    """
    Docker environment generator for MCPBench compatibility testing.
    
    This class generates Docker environments for all client-server
    combinations in the compatibility matrix. It handles template
    processing, port allocation, and file generation for Docker
    Compose and Dockerfile configurations.
    
    The generator creates isolated environments for each language
    combination to ensure clean testing without interference.
    
    Attributes:
        docker_dir: Directory containing Docker-related files
        matrix_dir: Directory containing the compatibility matrix
        templates_dir: Directory containing Docker templates
        sdk_info_path: Path to SDK information JSON file
        sdkinfo: Loaded SDK information
        port_mapping: Mapping of combinations to port pairs
    """
    
    def __init__(self, docker_dir: Path, matrix_dir: Path):
        """
        Initialize the Docker generator.
        
        Args:
            docker_dir: Directory for Docker-related files
            matrix_dir: Directory containing the compatibility matrix
            
        The initializer sets up paths, loads SDK information, and
        generates port mappings for all test combinations.
        """
        self.docker_dir = docker_dir
        self.matrix_dir = matrix_dir
        self.templates_dir = docker_dir / DIR_TEMPLATES
        self.sdk_info_path = docker_dir.parent / DIR_DRIVER / SDK_INFO_FILE
        self.sdkinfo = self._load_sdk_info()
        self.port_mapping = self._generate_port_mapping()
        
        logger.info(f"Docker dir: {self.docker_dir}")
        logger.info(f"Matrix dir: {self.matrix_dir}")
        logger.info(f"Templates dir: {self.templates_dir}")
        logger.info(f"SDK info path: {self.sdk_info_path}")

    def _load_sdk_info(self) -> Dict[str, Any]:
        """
        Load SDK information from JSON file.
        
        Returns:
            Dictionary containing SDK information
            
        Raises:
            SystemExit: If the file is not found or contains invalid JSON
            
        This method loads the SDK information file that contains
        version data, compatibility matrices, and configuration
        for all supported languages.
        """
        logger.debug(f"Loading SDK info from: {self.sdk_info_path}")
        try:
            with open(self.sdk_info_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"SDK info file not found: {self.sdk_info_path}")
            sys.exit(1)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in SDK info file: {self.sdk_info_path}")
            sys.exit(1)

    def _generate_port_mapping(self) -> Dict[str, Tuple[int, int]]:
        """
        Generate a mapping of client-server combinations to unique port pairs.
        
        Returns:
            Dict mapping combination key (f"{client_lang}-{client_ver}-{server_lang}-{server_ver}") 
            to tuple of (client_port, server_port)
            
        This method creates a port mapping that ensures no conflicts
        during parallel testing. It allocates ports starting from 15000
        with sufficient spacing between client and server ports.
        """
        port_mapping = {}
        used_ports = set()  # Track all used ports
        base_port = 15000  # Start from port 15000
        port_increment = 1  # Increment by 1 for each new combination
        
        # Generate all valid combinations
        combinations = self.generate_all_test_combinations()
        
        # Sort combinations to ensure consistent port allocation
        combinations.sort(key=lambda x: (
            x["client_lang"],
            x["client_ver"],
            x["server_lang"],
            x["server_ver"]
        ))
        
        # Assign ports to each combination
        for combination in combinations:
            key = f"{combination['client_lang']}-{combination['client_ver']}-{combination['server_lang']}-{combination['server_ver']}"
            
            # Find next available port pair
            while True:
                client_port = base_port
                server_port = base_port + 8
                
                # Check if either port is already used
                if client_port in used_ports or server_port in used_ports:
                    base_port += port_increment
                    continue
                
                # Ports are available, use them
                port_mapping[key] = (client_port, server_port)
                used_ports.add(client_port)
                used_ports.add(server_port)
                base_port += port_increment
                break
            
            logger.debug(f"Assigned ports for {key}: client={client_port}, server={server_port}")
        
        return port_mapping

    def _get_language_command(self, lang: str, role: str) -> str:
        """
        Get the command to run for a language and role.
        
        Args:
            lang: Language name (python, typescript, rust)
            role: Role (client or server)
            
        Returns:
            Command string to run the specified role in the language
            
        This method retrieves the appropriate command for running
        client or server implementations in each language.
        """
        commands = get_commands(lang)
        return commands.get(role, "")

    def _load_template(self, template_path: Path) -> str:
        """
        Load and validate a template file.
        
        Args:
            template_path: Path to the template file
            
        Returns:
            Template content as string
            
        Raises:
            FileNotFoundError: If the template file doesn't exist
            
        This method loads template files and validates their existence
        before processing.
        """
        logger.info(f"Looking for template at: {template_path}")
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(template_path, 'r') as f:
            return f.read()

    def _generate_dockerfile(self, lang: str, role: str, version: str) -> str:
        """
        Generate Dockerfile for a specific language and role.
        
        Args:
            lang: Language name (python, typescript, rust)
            role: Role (client or server)
            version: SDK version
            
        Returns:
            Generated Dockerfile content as string
            
        This method processes Dockerfile templates by replacing
        placeholders with actual values for the specific language,
        role, and version combination.
        """
        logger.info(f"Generating Dockerfile for {lang} {role} {version}")
        template_path = self.templates_dir / lang / role / DOCKERFILE_TEMPLATE
        template = self._load_template(template_path)

        # Replace placeholders
        dockerfile = template.replace(PLACEHOLDER_VERSION, version)
        dockerfile = dockerfile.replace(PLACEHOLDER_LANGUAGE, lang)
        dockerfile = dockerfile.replace(PLACEHOLDER_ROLE, role)
        dockerfile = dockerfile.replace(PLACEHOLDER_COMMAND, self._get_language_command(lang, role))

        return dockerfile

    def _generate_docker_compose(self, lang: str, version: str, role: str, port: int) -> str:
        """
        Generate docker-compose.yml for a language and version.
        
        Args:
            lang: Language name (python, typescript, rust)
            version: SDK version
            role: Role (client or server)
            port: Port number to use
            
        Returns:
            Generated docker-compose.yml content as string
            
        This method creates single-service Docker Compose files
        for individual language/version/role combinations.
        """
        template_path = self.templates_dir / DOCKER_COMPOSE_TEMPLATE
        try:
            template = self._load_template(template_path)
        except FileNotFoundError:
            logger.error(f"Docker Compose template not found: {template_path}")
            return ""

        # Replace placeholders
        compose = template.replace(PLACEHOLDER_VERSION, version)
        compose = compose.replace(PLACEHOLDER_LANGUAGE, lang)
        compose = compose.replace(PLACEHOLDER_PORT, str(port))
        compose = compose.replace(PLACEHOLDER_ROLE, role)
        compose = compose.replace(PLACEHOLDER_COMMAND, self._get_language_command(lang, role))

        return compose

    def _generate_client_server_compose(
        self,
        client_lang: str,
        client_ver: str,
        client_port: int,
        server_lang: str,
        server_ver: str,
        server_port: int
    ) -> str:
        """
        Generate client-server docker-compose.yml.
        
        Args:
            client_lang: Client language name
            client_ver: Client version
            client_port: Client port number
            server_lang: Server language name
            server_ver: Server version
            server_port: Server port number
            
        Returns:
            Generated client-server docker-compose.yml content as string
            
        This method creates multi-service Docker Compose files
        that include both client and server services for testing
        cross-language compatibility.
        """
        template_path = self.templates_dir / CLIENT_SERVER_COMPOSE_TEMPLATE
        try:
            template = self._load_template(template_path)
        except FileNotFoundError:
            logger.error(f"Client-server compose template not found: {template_path}")
            return ""

        # Replace placeholders
        compose = template.replace(PLACEHOLDER_CLIENT_LANG, client_lang)
        compose = compose.replace(PLACEHOLDER_CLIENT_VER, client_ver)
        compose = compose.replace(PLACEHOLDER_CLIENT_PORT, str(client_port))
        compose = compose.replace(PLACEHOLDER_SERVER_LANG, server_lang)
        compose = compose.replace(PLACEHOLDER_SERVER_VER, server_ver)
        compose = compose.replace(PLACEHOLDER_SERVER_PORT, str(server_port))
        compose = compose.replace(PLACEHOLDER_CLIENT_COMMAND, self._get_language_command(client_lang, CLIENT))
        compose = compose.replace(PLACEHOLDER_SERVER_COMMAND, self._get_language_command(server_lang, SERVER))

        return compose

    def generate_all_test_combinations(self) -> List[Dict[str, str]]:
        """
        Generate all valid client-server test combinations.
        
        Returns:
            List of dictionaries containing test combination information
            
        This method creates all possible client-server combinations
        based on the compatibility matrix in the SDK information.
        Each combination includes language and version information
        for both client and server.
        """
        combinations = []
        for client_lang, client_versions in self.sdkinfo.items():
            for client_ver, client_info in client_versions.items():
                # Get compatibility matrix for this client version
                compatibility = client_info.get("compatibility_matrix", {})
                
                # For each server language in the compatibility matrix
                for server_lang, server_versions in compatibility.items():
                    # For each compatible server version
                    for server_ver in server_versions:
                        if server_ver in self.sdkinfo.get(server_lang, {}):
                            combinations.append({
                                "client_lang": client_lang,
                                "client_ver": client_ver,
                                "server_lang": server_lang,
                                "server_ver": server_ver
                            })
        
        return combinations

    def generate_docker_files(self) -> None:
        """
        Generate all Docker files for the compatibility matrix.
        
        This method orchestrates the generation of all Docker-related
        files including:
        - Individual Docker Compose files for each language/version/role
        - Client-server Docker Compose files for cross-language testing
        - Dockerfiles for each language/version/role combination
        
        The method creates the necessary directory structure and
        generates all files based on templates and SDK information.
        """
        logger.info("Starting Docker file generation...")
        
        # Generate individual service files
        for lang, versions in self.sdkinfo.items():
            for version, version_info in versions.items():
                for role in [CLIENT, SERVER]:
                    # Create directory structure
                    service_dir = self.docker_dir / lang / role / version
                    service_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Generate Dockerfile
                    dockerfile_content = self._generate_dockerfile(lang, role, version)
                    dockerfile_path = service_dir / "Dockerfile"
                    with open(dockerfile_path, 'w') as f:
                        f.write(dockerfile_content)
                    
                    # Generate docker-compose.yml
                    port = version_info["ports"][0] if version_info["ports"] else 8000
                    compose_content = self._generate_docker_compose(lang, version, role, port)
                    compose_path = service_dir / "docker-compose.yml"
                    with open(compose_path, 'w') as f:
                        f.write(compose_content)
        
        # Generate client-server combination files
        combinations = self.generate_all_test_combinations()
        for combination in combinations:
            compose_content = self.generate_test_compose(combination)
            if compose_content:
                # Create combination directory
                combo_dir = self.docker_dir / "combinations" / f"{combination['client_lang']}-{combination['client_ver']}-{combination['server_lang']}-{combination['server_ver']}"
                combo_dir.mkdir(parents=True, exist_ok=True)
                
                # Write docker-compose.yml
                compose_path = combo_dir / "docker-compose.yml"
                with open(compose_path, 'w') as f:
                    f.write(compose_content)
        
        logger.info("Docker file generation completed")

    def generate_test_compose(self, combination: Dict[str, str]) -> str:
        """
        Generate Docker Compose file for a specific test combination.
        
        Args:
            combination: Dictionary containing client and server information
            
        Returns:
            Generated docker-compose.yml content as string
            
        This method creates a Docker Compose file for a specific
        client-server combination using the port mapping to ensure
        no conflicts during testing.
        """
        key = f"{combination['client_lang']}-{combination['client_ver']}-{combination['server_lang']}-{combination['server_ver']}"
        
        if key not in self.port_mapping:
            logger.warning(f"No port mapping found for combination: {key}")
            return ""
        
        client_port, server_port = self.port_mapping[key]
        
        return self._generate_client_server_compose(
            combination['client_lang'],
            combination['client_ver'],
            client_port,
            combination['server_lang'],
            combination['server_ver'],
            server_port
        )


def main() -> None:
    """
    Main entry point for the Docker generator.
    
    This function initializes the Docker generator and performs
    the complete Docker file generation process. It handles
    command-line execution and provides logging feedback.
    """
    script_dir = Path(__file__).parent
    docker_dir = script_dir.parent / DIR_DOCKER
    matrix_dir = script_dir.parent / DIR_MATRIX
    
    print("MCPBench Docker Generator")
    print("========================")
    
    generator = DockerGenerator(docker_dir, matrix_dir)
    generator.generate_docker_files()
    
    print("Docker generation completed successfully!")


if __name__ == "__main__":
    main() 