# Model Context Protocol (MCP) Compatibility Testing

This directory contains the base protocol definition for Model Context Protocol compatibility testing between different SDK versions.

## Protocol Overview

The Model Context Protocol (MCP) is an open protocol that enables seamless integration between LLM applications and external data sources and tools. It provides a standardized way to connect LLMs with the context they need.

### Core Components

1. **Base Protocol**
   - JSON-RPC 2.0 message format
   - Stateful connections
   - Server and client capability negotiation
   - Authentication framework

2. **Server Features**
   - **Resources**: Context and data for users or AI models
   - **Prompts**: Templated messages and workflows
   - **Tools**: Functions for AI models to execute

3. **Client Features**
   - **Sampling**: Server-initiated agentic behaviors and recursive LLM interactions

## Message Format

All messages MUST follow the JSON-RPC 2.0 specification:

### Requests
```json
{
  "jsonrpc": "2.0",
  "id": "string | number",
  "method": "string",
  "params": {
    "key": "unknown"
  }
}
```

### Responses
```json
{
  "jsonrpc": "2.0",
  "id": "string | number",
  "result": {
    "key": "unknown"
  },
  "error": {
    "code": "number",
    "message": "string",
    "data": "unknown"
  }
}
```

### Notifications
```json
{
  "jsonrpc": "2.0",
  "method": "string",
  "params": {
    "key": "unknown"
  }
}
```

## Authentication

MCP supports multiple authentication methods:

1. **HTTP-based Transport**
   - Uses the MCP Authorization framework
   - Required for HTTP-based implementations

2. **STDIO Transport**
   - Uses environment variables for credentials
   - Required for STDIO-based implementations

3. **Custom Authentication**
   - Negotiable between client and server
   - Implementation-specific

## Implementation Requirements

### Base Protocol Implementation

All SDK implementations must:
1. Support JSON-RPC 2.0 message format
2. Implement stateful connections
3. Support capability negotiation
4. Handle all defined error codes
5. Follow security principles
6. Support message batching (receiving)

### Server Implementation

Servers must implement:
1. Resource management
   - List available resources
   - Get specific resource details
2. Tool management
   - List available tools
   - Execute tools with parameters
3. Prompt handling
   - Support templated messages
   - Manage workflows

### Client Implementation

Clients must implement:
1. Sampling capabilities
   - Handle sampling requests
   - Process constraints
   - Return results

## Security Requirements

All implementations must adhere to these security principles:

1. **User Consent and Control**
   - Explicit consent for data access
   - User control over shared data
   - Clear authorization flows

2. **Data Privacy**
   - Explicit consent for data exposure
   - Protected user data
   - Appropriate access controls

3. **Tool Safety**
   - Treat tool descriptions as untrusted
   - Require explicit user consent
   - Clear documentation of tool behavior

4. **LLM Sampling Controls**
   - User approval for sampling
   - Control over prompts
   - Limited server visibility

## Testing Requirements

Each SDK implementation must:
1. Support all required operations
2. Handle all defined error cases
3. Implement proper security measures
4. Support capability negotiation
5. Follow version compatibility guidelines
6. Support JSON-RPC message formats
7. Implement appropriate authentication

## Version Compatibility

When implementing this protocol:
- Follow semantic versioning
- Document version-specific behaviors
- Maintain backward compatibility
- Document breaking changes
- Support capability negotiation

## References

- [MCP Specification 2025-03-26](https://modelcontextprotocol.io/specification/2025-03-26)
- [MCP Base Protocol](https://modelcontextprotocol.io/specification/2025-03-26/basic)
- [MCP Specification 2024-11-05](https://modelcontextprotocol.io/specification/2024-11-05)
- [MCP Schema](https://github.com/modelcontextprotocol/specification/blob/main/schema/2024-11-05/schema.ts) 