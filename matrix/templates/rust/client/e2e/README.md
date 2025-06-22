# Rust E2E Client

A Rust-based MCP client for end-to-end testing with TypeScript and Python servers.

## Features

- Connects to MCP servers using StreamableHTTP transport
- Tests multiple tools: `send_message`, `get_server_info`, and `increment`
- Comprehensive logging and error handling
- Compatible with both TypeScript and Python MCP servers

## Prerequisites

- Rust toolchain (latest stable)
- Access to the Rust SDK (`rust-sdk` directory at the same level as `mcpbench`)

## Building

```bash
cd matrix/templates/rust/client/e2e
cargo build
```

## Running

### Connect to TypeScript Server (default port 8000)
```bash
cargo run
# or explicitly
cargo run -- http://localhost:8000/mcp
```

### Connect to Python Server (port 8001)
```bash
cargo run -- http://localhost:8001/mcp
```

### Connect to Custom Server
```bash
cargo run -- http://localhost:YOUR_PORT/mcp
```

## Test Scenarios

The client will automatically test the following tools if they are available:

1. **send_message** - Sends a test message to the server
2. **get_server_info** - Retrieves server information
3. **increment** - Tests the increment tool (TypeScript server)

## Expected Output

```
Connecting to MCP server at http://localhost:8000/mcp...
✓ Connected to MCP server
Server info: {...}

=== MCP E2E Test Started ===

1. Listing available tools...
Available tools:
  - send_message: Send a message to the server and get a confirmation
    Schema: {...}
  - get_server_info: Get server information and status
    Schema: {...}

2. Testing send_message tool...
Tool result:
  Message received and processed: Hello from Rust E2E client!

3. Testing get_server_info tool...
Tool result:
  Server Information: {...}

✓ All E2E tests completed successfully!
✓ Disconnected from MCP server
```

## Troubleshooting

### Build Issues
- Ensure the Rust SDK path is correct in `Cargo.toml`
- The path should be `../../../../../rust-sdk/crates/rmcp`

### Connection Issues
- Verify the server is running on the specified port
- Check that the server URL includes the `/mcp` path
- Ensure the server supports StreamableHTTP transport

### Tool Testing Issues
- Some tools may not be available on all servers
- The client will skip tools that are not available
- Check server logs for detailed error information 