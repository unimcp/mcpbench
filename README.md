# MCPBench - Model Context Protocol Compatibility Testing Framework

## Overview

MCPBench is the open standard for compatibility testing of various Model Context Protocol (MCP https://github.com/modelcontextprotocol) client and server SDK implementations. As the MCP ecosystem grows, not every server or client will be written in the same language, creating an N×N compatibility matrix where N represents the number of language SDKs available.

Our goal is to ensure seamless interoperability between different MCP implementations, regardless of the programming language used.

## Current Status

**Initial SDK Support:**
- Python SDK (Official)
- TypeScript SDK (Official) 
- Rust SDK (Official)

**Future Expansion:** Additional language SDKs will be added as the MCP ecosystem grows.

## Milestone M0 - Foundation

We have successfully demonstrated key foundational capabilities:

### 1. Git Package Information Extraction
- Automatically fetch and parse git package information from official MCP SDK repositories
- Construct language-specific compatibility matrices
- Track version information and dependencies across SDKs

### 2. Docker Compose Generation
- Generate docker-compose configurations to run client-server combinations across the language matrix
- Support for cross-language testing scenarios
- Automated environment setup for compatibility testing

### 3. End-to-End (E2E) Testing Framework
- Working Python client ↔ TypeScript server communication
- Streamable HTTP transport validation
- Tool invocation and response verification
- Session management and protocol compliance testing

## Project Structure

```
mcpbench/
├── README.md                           # This file
├── matrix/                             # Core compatibility testing framework
│   ├── templates/                      # Test templates for different scenarios
│   │   ├── python/                     # Python client/server templates
│   │   │   ├── client/
│   │   │   │   ├── e2e/               # End-to-end client tests
│   │   │   │   ├── connection/        # Connection tests
│   │   │   │   └── ...                # Other test categories
│   │   │   └── server/
│   │   │       ├── e2e/               # End-to-end server implementations
│   │   │       └── ...                # Other server templates
│   │   ├── typescript/                 # TypeScript client/server templates
│   │   │   ├── client/
│   │   │   └── server/
│   │   │       └── e2e/               # TypeScript server implementations
│   │   └── rust/                       # Rust client/server templates
│   │       ├── client/
│   │       └── server/
│   ├── driver/                         # Test orchestration and automation
│   │   ├── update_sdk_info.py         # SDK information extraction
│   │   ├── setup.py                   # Environment setup
│   │   └── docker_generator.py        # Docker compose generation
│   └── requirements.txt               # Python dependencies
└── docs/                              # Documentation and guides
```

### Key Components

**`matrix/templates/`**: Contains test templates organized by language and test type. Each template provides a working example of MCP client/server implementation for specific testing scenarios.

**`matrix/driver/`**: Core automation scripts that:
- Extract SDK information from git repositories
- Generate compatibility matrices
- Create docker-compose configurations
- Orchestrate cross-language testing

**`matrix/templates/*/e2e/`**: End-to-end test implementations demonstrating full client-server communication using the MCP protocol.

## How to Run E2E Tests

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 18+** with npm
- **Docker** (for containerized testing)

### Quick Start: Python Client ↔ TypeScript Server

1. **Install Python Dependencies**
   ```bash
   cd mcpbench/matrix/templates/python/server
   pip install -r requirements.txt
   ```

2. **Start the TypeScript Server**
   ```bash
   cd mcpbench/matrix/templates/typescript/server/e2e
   npm install
   npm run dev
   ```
   The server will start on `http://localhost:8000`

3. **Run the Python Client Test**
   ```bash
   cd mcpbench/matrix/templates/python/client/e2e
   python3 test_connection.py
   ```

### Expected Output

You should see:
- Successful connection establishment
- Tool discovery and listing
- Tool invocation and response verification
- Clean session termination

### Testing Other Language Combinations

Similar patterns can be followed for other language combinations:
- Python Client ↔ Rust Server
- TypeScript Client ↔ Python Server
- Rust Client ↔ TypeScript Server

Each combination will have its own template in the `matrix/templates/` directory.

## Roadmap

### Milestone M1 - Matrix Expansion
- **Goal**: Complete N×N compatibility matrix for Python, TypeScript, and Rust
- **Deliverables**:
  - All client-server combinations working
  - Automated matrix testing
  - Performance benchmarking
  - Protocol compliance validation

### Milestone M2 - Advanced Testing
- **Goal**: Comprehensive test coverage and edge case handling
- **Deliverables**:
  - Authentication testing
  - Error handling scenarios
  - Resource management testing
  - Notification and streaming tests
  - Load testing and stress testing

### Milestone M3 - Ecosystem Integration
- **Goal**: Integration with CI/CD and developer workflows
- **Deliverables**:
  - GitHub Actions integration
  - Automated compatibility reports
  - SDK version compatibility tracking
  - Performance regression detection

### Milestone M4 - Extended Language Support
- **Goal**: Support for additional language SDKs
- **Deliverables**:
  - Go SDK support
  - Java SDK support
  - C# SDK support
  - Community SDK integration

### Milestone M5 - Production Readiness
- **Goal**: Enterprise-grade compatibility testing
- **Deliverables**:
  - Comprehensive documentation
  - Performance SLAs
  - Security testing
  - Compliance validation

## Contributing

We welcome contributions from the MCP community! Here's how you can help:

### Getting Started

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Submit a pull request**

### Contribution Areas

- **New Language SDK Support**: Add templates and tests for additional MCP SDKs
- **Test Improvements**: Enhance existing tests or add new test scenarios
- **Documentation**: Improve guides, examples, and API documentation
- **Automation**: Enhance the testing framework and CI/CD integration
- **Performance**: Optimize test execution and add performance benchmarks

### Development Guidelines

- **Code Style**: Follow the existing code style for each language
- **Testing**: Ensure all new features include appropriate tests
- **Documentation**: Update relevant documentation for new features
- **Compatibility**: Verify that changes don't break existing functionality

### Reporting Issues

- Use GitHub Issues to report bugs or request features
- Include detailed reproduction steps
- Provide relevant logs and error messages
- Specify the affected language combinations

### Community

- Join our discussions on GitHub Discussions
- Participate in MCP community events
- Share your use cases and requirements
- Help other contributors

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Model Context Protocol team for the specification and official SDKs
- The MCP community for feedback and contributions
- Contributors who have helped build and test this framework

---

**MCPBench** - Ensuring MCP compatibility across all languages and implementations. 