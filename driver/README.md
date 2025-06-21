# MCPBench Driver Module

## Overview

The `driver` module is the core automation engine of MCPBench, responsible for orchestrating the entire compatibility testing framework. It provides tools for SDK information management, Docker environment generation, and test execution across the N×N language compatibility matrix.

## Architecture

The driver module follows a modular architecture with clear separation of concerns:

```
driver/
├── README.md                    # This documentation
├── constants.py                 # Centralized constants and configuration
├── config.py                    # Test configuration and SDK version management
├── language_config.py           # Language-specific configurations
├── sdkinfo_generator.py         # SDK information extraction and management
├── docker_generator.py          # Docker environment generation
├── run_tests.py                 # Test execution orchestration
├── runner.py                    # Test runner utilities
├── run_test.py                  # Individual test execution
└── tests/                       # Test utilities and helpers
```

## Core Components

### 1. Constants (`constants.py`)
Centralized configuration file containing all constants, file paths, messages, and placeholders used throughout the framework.

**Key Features:**
- File path definitions
- GitHub API configuration
- Docker template placeholders
- Error messages and logging strings
- Environment variable definitions

### 2. Configuration (`config.py`)
Manages test configuration, SDK version information, and compatibility matrices.

**Key Features:**
- SDK version tracking with metadata
- Compatibility matrix management
- Test category definitions
- Timeout configurations
- Docker configuration management

### 3. Language Configuration (`language_config.py`)
Language-specific settings and configurations for supported MCP SDKs.

**Key Features:**
- GitHub repository mappings
- Port allocation schemes
- Docker base images
- Package manager configurations
- Environment variable definitions

### 4. SDK Information Generator (`sdkinfo_generator.py`)
Automated SDK information extraction and management from official repositories.

**Key Features:**
- GitHub API integration for release information
- Automated version detection
- Compatibility matrix generation
- Test structure creation
- Package file generation

### 5. Docker Generator (`docker_generator.py`)
Generates Docker environments for cross-language testing.

**Key Features:**
- Docker Compose file generation
- Port mapping and allocation
- Template-based Dockerfile generation
- Client-server environment setup

### 6. Test Runner (`run_tests.py`)
Orchestrates test execution across the compatibility matrix.

**Key Features:**
- Docker container management
- Test result collection
- Parallel test execution
- Error handling and recovery

## Usage Patterns

### 1. SDK Information Management

```python
from sdkinfo_generator import SDKVersionUpdater

# Update SDK information from GitHub
updater = SDKVersionUpdater(Path("sdkinfo.json"))
updater.update()
```

### 2. Docker Environment Generation

```python
from docker_generator import DockerGenerator

# Generate Docker environments for all combinations
generator = DockerGenerator(Path("docker"), Path("matrix"))
generator.generate_docker_files()
```

### 3. Test Execution

```python
from run_tests import TestRunner

# Run all compatibility tests
runner = TestRunner(Path("driver"))
runner.run_all_tests()
```

### 4. Configuration Management

```python
from config import TestConfig

# Load SDK configurations
TestConfig.load_sdk_info()

# Get test matrix
matrix = TestConfig.get_test_matrix(
    client_lang="python",
    server_lang="typescript"
)
```

## Configuration Files

### SDK Information (`sdkinfo.json`)
JSON file containing SDK version information, compatibility matrices, and metadata.

```json
{
  "python": {
    "1.0.0": {
      "version": "1.0.0",
      "release_date": "2024-01-01T00:00:00Z",
      "is_latest": true,
      "compatibility_matrix": {
        "typescript": ["1.0.0", "1.1.0"],
        "rust": ["1.0.0"]
      }
    }
  }
}
```

### Language Configuration
Language-specific settings defined in `language_config.py`:

- GitHub repository URLs
- Port allocation ranges
- Docker base images
- Package manager commands
- Environment variables

## Error Handling

The driver module implements comprehensive error handling:

1. **GitHub API Rate Limiting**: Automatic retry with exponential backoff
2. **Docker Failures**: Graceful degradation and cleanup
3. **Network Issues**: Retry mechanisms for external API calls
4. **Configuration Errors**: Validation and fallback mechanisms

## Logging

Structured logging is implemented throughout the module:

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Processing SDK information")
logger.error("Failed to fetch releases", exc_info=True)
```

## Testing

The driver module includes its own test suite:

```bash
# Run driver tests
cd mcpbench/driver
python -m pytest tests/

# Run specific test categories
python -m pytest tests/test_sdkinfo_generator.py
python -m pytest tests/test_docker_generator.py
```

## Performance Considerations

1. **Parallel Processing**: SDK information fetching uses concurrent requests
2. **Caching**: SDK information is cached to avoid repeated API calls
3. **Resource Management**: Docker containers are properly cleaned up
4. **Memory Efficiency**: Large datasets are processed incrementally

## Security

1. **GitHub Token**: Secure handling of API tokens via environment variables
2. **Docker Security**: Containers run with minimal privileges
3. **Input Validation**: All external inputs are validated and sanitized
4. **Error Information**: Sensitive information is not logged

## Contributing

When contributing to the driver module:

1. **Follow PEP 8**: Maintain consistent code style
2. **Add Tests**: Include tests for new functionality
3. **Update Documentation**: Keep this README and docstrings current
4. **Type Hints**: Use type hints for all function parameters and returns
5. **Error Handling**: Implement proper error handling and logging

## Dependencies

Core dependencies for the driver module:

```
requests>=2.31.0          # HTTP client for GitHub API
docker>=6.1.0             # Docker SDK for Python
PyYAML>=6.0               # YAML processing for Docker Compose
semver>=3.0.0             # Semantic versioning
pathlib                   # Path manipulation (Python 3.4+)
typing                    # Type hints (Python 3.5+)
```

## Troubleshooting

### Common Issues

1. **GitHub API Rate Limiting**
   - Set `GITHUB_TOKEN` environment variable
   - Check rate limit status in logs

2. **Docker Permission Errors**
   - Ensure Docker daemon is running
   - Check user permissions for Docker

3. **Port Conflicts**
   - Verify port ranges in `language_config.py`
   - Check for existing services using required ports

4. **SDK Version Issues**
   - Validate version format in `sdkinfo.json`
   - Check GitHub repository accessibility

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

1. **Plugin Architecture**: Support for custom language configurations
2. **Cloud Integration**: Support for cloud-based testing environments
3. **Performance Metrics**: Detailed performance benchmarking
4. **CI/CD Integration**: Automated testing in CI/CD pipelines
5. **Monitoring**: Real-time test execution monitoring 