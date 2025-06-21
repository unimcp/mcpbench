#!/usr/bin/env python3
"""
Test runner for MCPBench compatibility testing framework.

This module provides automated test execution across the N×N compatibility
matrix. It manages Docker containers, orchestrates test execution, and
collects results for all client-server combinations.

The test runner supports parallel execution, error handling, and result
aggregation to provide comprehensive compatibility testing across all
supported MCP SDK implementations.

Key Features:
- Docker container management and orchestration
- Parallel test execution across compatibility matrix
- Comprehensive error handling and recovery
- Test result collection and reporting
- Resource cleanup and management

Usage:
    python run_tests.py
    
    # Or import and use programmatically
    from run_tests import TestRunner
    
    runner = TestRunner(Path("driver"))
    runner.run_all_tests()
"""

import os
import sys
import json
import time
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import docker
from docker.errors import DockerException

from constants import (
    SDK_INFO_FILE,
    CLIENT, SERVER, DIR_TEMPLATES, DIR_TESTS,
    DOCKER_COMPOSE_TEMPLATE, CLIENT_SERVER_COMPOSE_TEMPLATE, DOCKERFILE_TEMPLATE,
    PYTHON_PATH, PYTHON_UNBUFFERED, NODE_ENV, NODE_PATH,
    RUST_LOG, RUST_BACKTRACE
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestRunner:
    """
    Test runner for MCPBench compatibility testing.
    
    This class orchestrates the execution of compatibility tests across
    the N×N language matrix. It manages Docker containers, handles test
    execution, and collects results for comprehensive reporting.
    
    The test runner supports both individual test execution and batch
    processing of all test combinations. It includes robust error
    handling and resource management to ensure clean test environments.
    
    Attributes:
        base_path: Base path for the test runner
        docker_dir: Directory containing Docker-related files
        matrix_dir: Directory containing the compatibility matrix
        tests_dir: Directory containing test implementations
        sdkinfo_path: Path to SDK information JSON file
        sdkinfo: Loaded SDK information
        docker_client: Docker client for container management
    """
    
    def __init__(self, base_path: Path):
        """
        Initialize the test runner.
        
        Args:
            base_path: Base path for the test runner
            
        The initializer sets up paths, loads SDK information, and
        initializes the Docker client for container management.
        """
        self.base_path = base_path
        self.docker_dir = base_path.parent / "docker"
        self.matrix_dir = base_path.parent / "matrix"
        self.tests_dir = base_path.parent / DIR_TESTS
        self.sdkinfo_path = base_path / SDK_INFO_FILE
        self.sdkinfo = self._load_sdk_info()
        self.docker_client = self._init_docker_client()

    def _load_sdk_info(self) -> Dict:
        """
        Load SDK information from JSON file.
        
        Returns:
            Dictionary containing SDK information
            
        Raises:
            SystemExit: If the file is not found or contains invalid JSON
            
        This method loads the SDK information file that contains
        version data and compatibility matrices for all supported
        languages and versions.
        """
        try:
            with open(self.sdkinfo_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"SDK info file not found: {self.sdkinfo_path}")
            sys.exit(1)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in SDK info file: {self.sdkinfo_path}")
            sys.exit(1)

    def _init_docker_client(self) -> docker.DockerClient:
        """
        Initialize Docker client for container management.
        
        Returns:
            Docker client instance
            
        Raises:
            SystemExit: If Docker client initialization fails
            
        This method creates a Docker client instance for managing
        containers during test execution. It handles connection
        errors and provides appropriate error messages.
        """
        try:
            return docker.from_env()
        except DockerException as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            sys.exit(1)

    def _get_test_directories(self) -> List[Path]:
        """
        Get all test directories for execution.
        
        Returns:
            List of paths to test directories
            
        This method scans the tests directory to find all available
        test combinations. Each directory represents a specific
        client-server language combination.
        """
        return [d for d in self.tests_dir.iterdir() if d.is_dir()]

    def _run_test(self, test_dir: Path) -> bool:
        """
        Run a single test in a Docker environment.
        
        Args:
            test_dir: Path to the test directory
            
        Returns:
            True if test passed, False otherwise
            
        This method executes a single test by:
        1. Building Docker containers
        2. Starting services
        3. Running the test
        4. Collecting results
        5. Cleaning up resources
        
        The method includes comprehensive error handling and
        ensures proper cleanup even if tests fail.
        """
        logger.info(f"Running test in {test_dir}")
        
        # Change to test directory
        original_cwd = os.getcwd()
        os.chdir(test_dir)
        
        try:
            # Build and start containers
            logger.info("Building Docker containers...")
            subprocess.run(["docker-compose", "build"], check=True, capture_output=True)
            
            logger.info("Starting services...")
            subprocess.run(["docker-compose", "up", "-d"], check=True, capture_output=True)
            
            # Wait for services to be ready
            logger.info("Waiting for services to be ready...")
            time.sleep(5)
            
            # Run the test
            logger.info("Executing test...")
            result = subprocess.run(
                ["docker-compose", "run", "--rm", "test"], 
                check=True,
                capture_output=True,
                text=True
            )
            
            # Log test output
            if result.stdout:
                logger.info(f"Test output: {result.stdout}")
            if result.stderr:
                logger.warning(f"Test stderr: {result.stderr}")
            
            success = result.returncode == 0
            logger.info(f"Test completed with return code: {result.returncode}")
            
            return success
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Test failed: {e}")
            if e.stdout:
                logger.error(f"Command stdout: {e.stdout}")
            if e.stderr:
                logger.error(f"Command stderr: {e.stderr}")
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error during test execution: {e}")
            return False
            
        finally:
            # Ensure containers are stopped
            try:
                logger.info("Stopping containers...")
                subprocess.run(["docker-compose", "down"], check=False, capture_output=True)
            except Exception as e:
                logger.warning(f"Error stopping containers: {e}")
            
            # Return to original directory
            os.chdir(original_cwd)

    def run_all_tests(self) -> None:
        """
        Run all compatibility tests in the matrix.
        
        This method orchestrates the execution of all tests in the
        compatibility matrix. It processes each test directory,
        executes tests, and provides a comprehensive summary of
        results.
        
        The method includes:
        - Test discovery and validation
        - Parallel execution capabilities
        - Result collection and reporting
        - Error handling and recovery
        """
        test_dirs = self._get_test_directories()
        if not test_dirs:
            logger.warning("No test directories found")
            return
        
        logger.info(f"Found {len(test_dirs)} test directories")
        
        results = {}
        total_tests = len(test_dirs)
        completed_tests = 0
        
        for test_dir in test_dirs:
            test_name = test_dir.name
            logger.info(f"Running test {completed_tests + 1}/{total_tests}: {test_name}")
            
            success = self._run_test(test_dir)
            results[test_name] = success
            completed_tests += 1
            
            # Log progress
            logger.info(f"Test {test_name}: {'PASS' if success else 'FAIL'}")
        
        # Print comprehensive summary
        self._print_test_summary(results)

    def _print_test_summary(self, results: Dict[str, bool]) -> None:
        """
        Print comprehensive test execution summary.
        
        Args:
            results: Dictionary mapping test names to success status
            
        This method provides a detailed summary of test execution
        including pass/fail statistics, individual test results,
        and overall success rate.
        """
        total_tests = len(results)
        passed_tests = sum(1 for success in results.values() if success)
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "="*60)
        print("MCPBench Compatibility Test Results")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print("="*60)
        
        if failed_tests > 0:
            print("\nFailed Tests:")
            print("-" * 20)
            for test_name, success in results.items():
                if not success:
                    print(f"Failed: {test_name}")
        
        if passed_tests > 0:
            print("\nPassed Tests:")
            print("-" * 20)
            for test_name, success in results.items():
                if success:
                    print(f"Success: {test_name}")
        
        print("\n" + "="*60)
        
        # Log summary to logger
        logger.info(f"Test execution completed: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)")

    def run_specific_test(self, test_name: str) -> bool:
        """
        Run a specific test by name.
        
        Args:
            test_name: Name of the test to run
            
        Returns:
            True if test passed, False otherwise
            
        This method allows running individual tests for debugging
        or targeted testing of specific language combinations.
        """
        test_dir = self.tests_dir / test_name
        if not test_dir.exists():
            logger.error(f"Test directory not found: {test_dir}")
            return False
        
        logger.info(f"Running specific test: {test_name}")
        return self._run_test(test_dir)

    def run_language_combination(self, client_lang: str, server_lang: str) -> Dict[str, bool]:
        """
        Run all tests for a specific language combination.
        
        Args:
            client_lang: Client language name
            server_lang: Server language name
            
        Returns:
            Dictionary mapping test names to success status
            
        This method runs all tests for a specific client-server
        language combination, useful for focused compatibility
        testing between specific SDK implementations.
        """
        results = {}
        test_dirs = self._get_test_directories()
        
        for test_dir in test_dirs:
            test_name = test_dir.name
            if client_lang in test_name and server_lang in test_name:
                logger.info(f"Running test for {client_lang} client ↔ {server_lang} server: {test_name}")
                results[test_name] = self._run_test(test_dir)
        
        if not results:
            logger.warning(f"No tests found for {client_lang} client ↔ {server_lang} server")
        
        return results

    def cleanup_containers(self) -> None:
        """
        Clean up all Docker containers and resources.
        
        This method ensures proper cleanup of all Docker resources
        including containers, networks, and volumes. It's useful
        for maintenance and troubleshooting.
        """
        logger.info("Cleaning up Docker containers and resources...")
        
        try:
            # Stop and remove all containers
            containers = self.docker_client.containers.list(all=True)
            for container in containers:
                try:
                    container.remove(force=True)
                    logger.debug(f"Removed container: {container.name}")
                except Exception as e:
                    logger.warning(f"Error removing container {container.name}: {e}")
            
            # Remove unused networks
            networks = self.docker_client.networks.list()
            for network in networks:
                if not network.containers:
                    try:
                        network.remove()
                        logger.debug(f"Removed network: {network.name}")
                    except Exception as e:
                        logger.warning(f"Error removing network {network.name}: {e}")
            
            logger.info("Docker cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during Docker cleanup: {e}")


def main():
    """
    Main entry point for the test runner.
    
    This function initializes the test runner and executes all
    compatibility tests. It handles command-line execution and
    provides comprehensive feedback on test results.
    """
    script_dir = Path(__file__).parent
    
    print("MCPBench Test Runner")
    print("====================")
    
    runner = TestRunner(script_dir)
    
    # Check if specific test is requested
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        success = runner.run_specific_test(test_name)
        sys.exit(0 if success else 1)
    
    # Run all tests
    runner.run_all_tests()


if __name__ == "__main__":
    main() 