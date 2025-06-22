# MCP E2E Test Templates

This directory contains end-to-end test templates for MCP (Model Context Protocol) compatibility testing.

## Structure

```
mcpbench/matrix/templates/
├── python/
│   ├── client/
│   │   └── e2e/
│   │       └── test_connection.py
│   └── server/
│       └── e2e/
│           ├── server.py
│           └── requirements.txt
├── typescript/
│   ├── client/
│   │   └── e2e/
│   │       ├── src/
│   │       │   └── client.ts
│   │       ├── package.json
│   │       └── tsconfig.json
│   └── server/
│       └── e2e/
│           ├── src/
│           │   └── server.ts
│           ├── package.json
│           └── tsconfig.json
└── rust/
    └── client/
        └── e2e/
            ├── src/
            │   └── main.rs
            ├── Cargo.toml
            └── README.md
```

## Test Scenarios

### Scenario 1: TypeScript Server + Python Client

#### 1. Start the TypeScript Server

First, navigate to the TypeScript server directory and install dependencies:

```bash
cd mcpbench/matrix/templates/typescript/server/e2e
npm install
```

Then start the server:

```bash
# Development mode (with tsx)
npm run dev

# Or build and run
npm run build
npm start
```

The server will start on port 8000 (or the port specified in `MCP_SERVER_PORT` environment variable).

#### 2. Run the Python Client Test

In another terminal, navigate to the Python client directory:

```bash
cd mcpbench/matrix/templates/python/client/e2e
```

Run the test:

```bash
python test_connection.py
```

### Scenario 2: Python Server + TypeScript Client

#### 1. Start the Python Server

First, navigate to the Python server directory and install dependencies:

```bash
cd mcpbench/matrix/templates/python/server/e2e
pip install -r requirements.txt
```

Then start the server:

```bash
python server.py --port 8000
```

The server will start on port 8000 (or the port specified with `--port`).

#### 2. Run the TypeScript Client Test

In another terminal, navigate to the TypeScript client directory:

```bash
cd mcpbench/matrix/templates/typescript/client/e2e
npm install
```

Run the test:

```bash
# Development mode (with tsx)
npm run dev

# Or build and run
npm run build
npm start
```

### Scenario 3: TypeScript/Python Server + Rust Client

#### 1. Start a Server

Start either the TypeScript server (port 8000) or Python server (port 8001) as described above.

#### 2. Run the Rust Client Test

In another terminal, navigate to the Rust client directory:

```bash
cd mcpbench/matrix/templates/rust/client/e2e
```

Build the client:

```bash
cargo build
```

Run the test:

```bash
# Connect to TypeScript server (default)
cargo run

# Connect to Python server
cargo run -- http://localhost:8001/mcp

# Connect to custom server
cargo run -- http://localhost:YOUR_PORT/mcp
```

## Test Flow

All scenarios perform the following:

1. **Server Setup**: Server starts and listens on specified port
2. **Client Connection**: Client connects using StreamableHTTP transport
3. **Tool Discovery**: Client calls `list_tools` to discover available tools
4. **Message Test**: Client calls `send_message` tool with a test message
5. **Server Info Test**: Client calls `get_server_info` tool
6. **Additional Tests**: Rust client also tests `increment` tool if available
7. **Cleanup**: Client disconnects and server continues running

## Available Tools

### Common Tools (All Servers)
- `send_message`: Accepts a message parameter and returns a confirmation
- `get_server_info`: Returns server information including name, version, and timestamp

### TypeScript Server Additional Tools
- `increment`: Accepts a value parameter and returns the incremented value

## Environment Variables

- `MCP_SERVER_URL`: Server URL (default: http://localhost:8000/mcp)
- `MCP_SERVER_HOST`: Server host (default: localhost)
- `MCP_SERVER_PORT`: Server port (default: 8000)
- `MCP_CONNECTION_TIMEOUT`: Connection timeout in seconds (default: 30)

## Expected Output

When running successfully, you should see:

1. Server logs showing the server starting and tools being registered
2. Client logs showing connection establishment and tool calls
3. Tool responses with the expected data
4. Notification messages from the server

## Prerequisites

- **Node.js 18+** for TypeScript components
- **Python 3.8+** for Python components  
- **Rust toolchain** for Rust components
- **Access to SDKs**: Ensure the respective SDKs are available in the parent directory

## Troubleshooting

- Ensure all required toolchains are installed
- Check that the target ports are available
- All servers use StreamableHTTP transport for real-time communication
- The TypeScript components use the official `@modelcontextprotocol/sdk` npm package
- The Python components use the official `mcp` Python package
- The Rust components use the official `rmcp` crate from the Rust SDK 