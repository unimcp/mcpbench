/**
 * MCP TypeScript Client for E2E Testing with StreamableHTTP Transport
 * 
 * This client connects to an MCP server and tests basic functionality
 * including tool discovery, tool calls, and notifications.
 */

import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js';
import {
  ListToolsRequest,
  ListToolsResultSchema,
  CallToolRequest,
  CallToolResultSchema,
  LoggingMessageNotificationSchema,
} from '@modelcontextprotocol/sdk/types.js';

interface TestConfig {
  serverUrl: string;
  timeout: number;
}

class MCPE2EClient {
  private client: Client | null = null;
  private transport: StreamableHTTPClientTransport | null = null;
  private config: TestConfig;
  private notificationCount = 0;

  constructor(config: TestConfig) {
    this.config = config;
  }

  async connect(): Promise<void> {
    console.log(`Connecting to MCP server at ${this.config.serverUrl}...`);

    try {
      // Create a new client
      this.client = new Client({
        name: 'mcp-typescript-e2e-client',
        version: '1.0.0'
      });

      // Set up error handler
      this.client.onerror = (error) => {
        console.error('\x1b[31mClient error:', error, '\x1b[0m');
      };

      // Create transport
      this.transport = new StreamableHTTPClientTransport(
        new URL(this.config.serverUrl),
        {}
      );

      // Set up notification handlers
      this.client.setNotificationHandler(LoggingMessageNotificationSchema, (notification) => {
        this.notificationCount++;
        console.log(`\n\x1b[36mNotification #${this.notificationCount}:\x1b[0m ${notification.params.level} - ${notification.params.data}`);
      });

      // Connect the client
      await this.client.connect(this.transport);
      console.log('\x1b[32m✓ Connected to MCP server\x1b[0m');
    } catch (error) {
      console.error('\x1b[31m✗ Failed to connect:', error, '\x1b[0m');
      throw error;
    }
  }

  async disconnect(): Promise<void> {
    if (this.transport) {
      try {
        await this.transport.close();
        console.log('\x1b[32m✓ Disconnected from MCP server\x1b[0m');
      } catch (error) {
        console.error('\x1b[31m✗ Error disconnecting:', error, '\x1b[0m');
      } finally {
        this.client = null;
        this.transport = null;
      }
    }
  }

  async listTools(): Promise<void> {
    if (!this.client) {
      throw new Error('Not connected to server');
    }

    try {
      const toolsRequest: ListToolsRequest = {
        method: 'tools/list',
        params: {}
      };
      
      console.log('\n\x1b[35m[DEBUG] Sending list_tools request:\x1b[0m', JSON.stringify(toolsRequest, null, 2));
      
      const toolsResult = await this.client.request(toolsRequest, ListToolsResultSchema);

      console.log('\n\x1b[35m[DEBUG] Received list_tools response:\x1b[0m', JSON.stringify(toolsResult, null, 2));

      console.log('\n\x1b[33mAvailable tools:\x1b[0m');
      if (toolsResult.tools.length === 0) {
        console.log('  No tools available');
      } else {
        for (const tool of toolsResult.tools) {
          console.log(`  - ${tool.name}: ${tool.description}`);
          console.log(`    Schema: ${JSON.stringify(tool.inputSchema, null, 2)}`);
        }
      }
    } catch (error) {
      console.error('\x1b[31m✗ Error listing tools:', error, '\x1b[0m');
      throw error;
    }
  }

  async callTool(name: string, args: Record<string, unknown>): Promise<void> {
    if (!this.client) {
      throw new Error('Not connected to server');
    }

    try {
      const request: CallToolRequest = {
        method: 'tools/call',
        params: {
          name,
          arguments: args
        }
      };

      console.log(`\n\x1b[35m[DEBUG] Sending call_tool request for '${name}':\x1b[0m`, JSON.stringify(request, null, 2));
      
      const result = await this.client.request(request, CallToolResultSchema);

      console.log(`\n\x1b[35m[DEBUG] Received call_tool response for '${name}':\x1b[0m`, JSON.stringify(result, null, 2));

      console.log('\x1b[33mTool result:\x1b[0m');
      result.content.forEach(item => {
        if (item.type === 'text') {
          console.log(`  ${item.text}`);
        } else {
          console.log(`  ${item.type} content:`, item);
        }
      });
    } catch (error) {
      console.error(`\x1b[31m✗ Error calling tool ${name}:\x1b[0m`, error);
      throw error;
    }
  }

  async runE2ETest(): Promise<void> {
    console.log('\n\x1b[35m=== MCP E2E Test Started ===\x1b[0m');

    try {
      // Step 1: List available tools
      console.log('\n\x1b[33m1. Listing available tools...\x1b[0m');
      await this.listTools();

      // Step 2: Call send_message tool
      console.log('\n\x1b[33m2. Testing send_message tool...\x1b[0m');
      await this.callTool('send_message', { 
        message: 'Hello from TypeScript E2E client!' 
      });

      // Step 3: Call get_server_info tool
      console.log('\n\x1b[33m3. Testing get_server_info tool...\x1b[0m');
      await this.callTool('get_server_info', {});

      console.log('\n\x1b[32m✓ All E2E tests completed successfully!\x1b[0m');
      console.log(`\x1b[36mTotal notifications received: ${this.notificationCount}\x1b[0m`);

    } catch (error) {
      console.error('\x1b[31m✗ E2E test failed:', error, '\x1b[0m');
      throw error;
    }
  }
}

// Main execution function
async function main(): Promise<void> {
  const config: TestConfig = {
    serverUrl: process.env.MCP_SERVER_URL || 'http://localhost:8000/mcp',
    timeout: parseInt(process.env.MCP_CONNECTION_TIMEOUT || '30000')
  };

  const client = new MCPE2EClient(config);

  try {
    await client.connect();
    await client.runE2ETest();
  } catch (error) {
    console.error('\x1b[31m✗ Test execution failed:', error, '\x1b[0m');
    process.exit(1);
  } finally {
    await client.disconnect();
  }
}

// Run the client if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error: unknown) => {
    console.error('Error running MCP client:', error);
    process.exit(1);
  });
}

export { MCPE2EClient, TestConfig }; 