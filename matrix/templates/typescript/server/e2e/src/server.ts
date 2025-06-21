import express, { Request, Response } from 'express';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import { CallToolResult } from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';

// Create an MCP server
const createServer = () => {
  const server = new McpServer({
    name: 'e2e-test-server',
    version: '1.0.0',
  }, { 
    capabilities: { 
      logging: {},
      tools: {}
    } 
  });

  // Register a simple tool that handles messages
  server.tool(
    'send_message',
    'Send a message to the server',
    {
      message: z.string().describe('Message to send to the server'),
    },
    async ({ message }: { message: string }): Promise<CallToolResult> => {
      console.log(`Received message: ${message}`);
      return {
        content: [
          {
            type: 'text',
            text: `Server received message: ${message}`,
          },
        ],
      };
    }
  );

  // Register a tool that returns server info
  server.tool(
    'get_server_info',
    'Get information about the server',
    {},
    async (): Promise<CallToolResult> => {
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              name: 'e2e-test-server',
              version: '1.0.0',
              timestamp: new Date().toISOString(),
            }, null, 2),
          },
        ],
      };
    }
  );

  return server;
};

// Create Express app
const app = express();
app.use(express.json());

// Get port from environment or default to 8000
const PORT = process.env.MCP_SERVER_PORT ? parseInt(process.env.MCP_SERVER_PORT) : 8000;
const HOST = process.env.MCP_SERVER_HOST || '0.0.0.0';

// Handle MCP requests
app.post('/mcp', async (req: Request, res: Response) => {
  const server = createServer();
  try {
    const transport: StreamableHTTPServerTransport = new StreamableHTTPServerTransport({
      sessionIdGenerator: undefined,
    });
    await server.connect(transport);
    await transport.handleRequest(req, res, req.body);
    res.on('close', () => {
      console.log('Request closed');
      transport.close();
      server.close();
    });
  } catch (error) {
    console.error('Error handling MCP request:', error);
    if (!res.headersSent) {
      res.status(500).json({
        jsonrpc: '2.0',
        error: {
          code: -32603,
          message: 'Internal server error',
        },
        id: null,
      });
    }
  }
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Start the server
app.listen(PORT, HOST, () => {
  console.log(`MCP Server listening on ${HOST}:${PORT}`);
  console.log('Available tools: send_message, get_server_info');
});

export { createServer }; 