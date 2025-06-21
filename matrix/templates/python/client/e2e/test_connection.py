import asyncio
import logging
import os
from typing import Optional, List, Any
import json
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class E2EConnectionTest:
    """End-to-end connection test for MCP client connecting to TypeScript server."""
    
    def __init__(self):
        """Initialize the test with configuration."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize connection parameters
        self.connection_params = {
            "host": os.getenv("MCP_SERVER_HOST", "localhost"),
            "port": int(os.getenv("MCP_SERVER_PORT", "8000")),
            "timeout": int(os.getenv("MCP_CONNECTION_TIMEOUT", "30"))
        }
    
    def _load_config(self) -> dict:
        """Load test configuration from file."""
        config_path = os.getenv("TEST_CONFIG_PATH", "config.json")
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found at {config_path}, using defaults")
            return {}
    
    async def setup(self):
        """Set up the test environment."""
        self.logger.info("Setting up test environment")
        
        # Create streamable HTTP transport
        http_url = f"http://{self.connection_params['host']}:{self.connection_params['port']}/mcp"
        self.logger.info(f"Connecting to streamable HTTP endpoint: {http_url}")
        
        try:
            # Create streamable HTTP transport
            result = await self.exit_stack.enter_async_context(
                streamablehttp_client(http_url)
            )
            print('DEBUG: result type:', type(result))
            print('DEBUG: result len:', len(result) if hasattr(result, '__len__') else 'N/A')
            print('DEBUG: result contents:', result)
            # (do not unpack or use result yet)

            # Create client session
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(result[0], result[1])
            )

            # Initialize session
            try:
                await self.session.initialize()
                self.logger.info("Successfully initialized client session")
            except Exception as e:
                self.logger.error(f"Failed to initialize session: {e}")
                # Try to get more details about the error
                if hasattr(e, 'response') and e.response:
                    try:
                        response_body = await e.response.aread()
                        self.logger.error(f"Response body: {response_body}")
                    except:
                        pass
                raise
            
        except Exception as e:
            self.logger.error(f"Failed to set up test environment: {e}")
            await self.cleanup()
            raise
    
    async def test_list_tools(self) -> List[Any]:
        """Test listing available tools."""
        if not self.session:
            raise RuntimeError("Client session not initialized")
        
        self.logger.info("Testing list_tools")
        try:
            tools_response = await self.session.list_tools()
            tools = []
            
            for item in tools_response:
                if isinstance(item, tuple) and item[0] == "tools":
                    tools.extend(item[1])
            
            self.logger.info(f"Successfully retrieved {len(tools)} tools")
            return tools
            
        except Exception as e:
            self.logger.error(f"Failed to list tools: {e}")
            raise
    
    async def test_send_message(self, message: str) -> str:
        """Test sending a message to the server."""
        if not self.session:
            raise RuntimeError("Client session not initialized")
        
        self.logger.info(f"Testing send_message with: {message}")
        try:
            result = await self.session.call_tool("send_message", {"message": message})
            self.logger.info(f"Successfully sent message: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            raise
    
    async def test_get_server_info(self) -> str:
        """Test getting server information."""
        if not self.session:
            raise RuntimeError("Client session not initialized")
        
        self.logger.info("Testing get_server_info")
        try:
            result = await self.session.call_tool("get_server_info", {})
            self.logger.info(f"Successfully got server info: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to get server info: {e}")
            raise
    
    async def cleanup(self):
        """Clean up test resources."""
        self.logger.info("Cleaning up test environment")
        try:
            await self.exit_stack.aclose()
            self.session = None
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            raise

async def main():
    """Run the e2e connection test."""
    test = E2EConnectionTest()
    try:
        await test.setup()
        
        # Test list_tools
        tools = await test.test_list_tools()
        print("Available tools:")
        for tool in tools:
            print(tool.__dict__ if hasattr(tool, '__dict__') else str(tool))
        
        # Test send_message
        result = await test.test_send_message("Hello from Python client!")
        print(f"Message result: {result}")
        
        # Test get_server_info
        server_info = await test.test_get_server_info()
        print(f"Server info: {server_info}")
        
    finally:
        await test.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 