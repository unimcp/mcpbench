# MCP E2E Test Templates

This directory contains end-to-end test templates for MCP (Model Context Protocol) compatibility testing.

## Structure

```
mcpbench/matrix/templates/
├── python/
│   └── client/
│       └── e2e/
│           └── test_connection.py
└── typescript/
    └── server/
        └── e2e/
            ├── src/
            │   └── server.ts
            ├── package.json
            └── tsconfig.json
```

## Running the Tests

### 1. Start the TypeScript Server

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

### 2. Run the Python Client Test

In another terminal, navigate to the Python client directory:

```bash
cd mcpbench/matrix/templates/python/client/e2e
```

Run the test:

```bash
python test_connection.py
```

## Test Flow

The e2e test performs the following:

1. **Server Setup**: TypeScript server starts and listens on port 8000
2. **Client Connection**: Python client connects using streamable HTTP transport
3. **Tool Discovery**: Client calls `list_tools` to discover available tools
4. **Message Test**: Client calls `send_message` tool with a test message
5. **Server Info Test**: Client calls `get_server_info` tool
6. **Cleanup**: Client disconnects and server continues running

## Available Tools

The TypeScript server provides two tools:

- `send_message`: Accepts a message parameter and returns a confirmation
- `get_server_info`: Returns server information including name, version, and timestamp

## Environment Variables

- `MCP_SERVER_HOST`: Server host (default: localhost)
- `MCP_SERVER_PORT`: Server port (default: 8000)
- `MCP_CONNECTION_TIMEOUT`: Connection timeout in seconds (default: 30)

## Expected Output

When running successfully, you should see:

1. Server logs showing the server starting and tools being registered
2. Client logs showing connection establishment and tool calls
3. Tool responses with the expected data

## Troubleshooting

- Ensure Node.js 18+ is installed for the TypeScript server
- Ensure Python 3.8+ is installed for the Python client
- Check that port 8000 is available
- The TypeScript server uses the official `@modelcontextprotocol/sdk` npm package 