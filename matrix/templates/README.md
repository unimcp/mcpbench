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
└── typescript/
    ├── client/
    │   └── e2e/
    │       ├── src/
    │       │   └── client.ts
    │       ├── package.json
    │       └── tsconfig.json
    └── server/
        └── e2e/
            ├── src/
            │   └── server.ts
            ├── package.json
            └── tsconfig.json
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

## Test Flow

Both scenarios perform the following:

1. **Server Setup**: Server starts and listens on port 8000
2. **Client Connection**: Client connects using StreamableHTTP transport
3. **Tool Discovery**: Client calls `list_tools` to discover available tools
4. **Message Test**: Client calls `send_message` tool with a test message
5. **Server Info Test**: Client calls `get_server_info` tool
6. **Cleanup**: Client disconnects and server continues running

## Available Tools

Both servers provide the same tools:

- `send_message`: Accepts a message parameter and returns a confirmation
- `get_server_info`: Returns server information including name, version, and timestamp

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

## Troubleshooting

- Ensure Node.js 18+ is installed for TypeScript components
- Ensure Python 3.8+ is installed for Python components
- Check that port 8000 is available
- Both servers use StreamableHTTP transport for real-time communication
- The TypeScript components use the official `@modelcontextprotocol/sdk` npm package
- The Python components use the official `mcp` Python package 