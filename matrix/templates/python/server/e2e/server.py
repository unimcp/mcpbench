"""
MCP Python Server for E2E Testing with StreamableHTTP Transport

This server provides tools for testing MCP client-server communication
and demonstrates StreamableHTTP transport capabilities.
"""

import contextlib
import logging
from collections.abc import AsyncIterator

import anyio
import click
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from pydantic import AnyUrl
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send

# Configure logging
logger = logging.getLogger(__name__)


@click.command()
@click.option("--port", default=8000, help="Port to listen on for HTTP")
@click.option(
    "--log-level",
    default="INFO",
    help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
)
@click.option(
    "--json-response",
    is_flag=True,
    default=False,
    help="Enable JSON responses instead of SSE streams",
)
def main(
    port: int,
    log_level: str,
    json_response: bool,
) -> int:
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    app = Server("mcp-python-e2e-server")

    @app.call_tool()
    async def handle_tool_call(
        name: str, arguments: dict
    ) -> list[
        types.TextContent
        | types.ImageContent
        | types.AudioContent
        | types.EmbeddedResource
    ]:
        """Handle all tool calls by routing based on tool name."""
        try:
            logger.info(f"=== ENTERING handle_tool_call function ===")
            logger.info(f"Tool call: name='{name}', arguments={arguments}")
            
            ctx = app.request_context
            
            if name == "send_message":
                return await handle_send_message(arguments, ctx)
            elif name == "get_server_info":
                return await handle_get_server_info(arguments, ctx)
            else:
                raise ValueError(f"Unknown tool: {name}")
                
        except Exception as e:
            logger.error(f"Exception in handle_tool_call: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def handle_send_message(
        arguments: dict, ctx
    ) -> list[
        types.TextContent
        | types.ImageContent
        | types.AudioContent
        | types.EmbeddedResource
    ]:
        """Handle send_message tool call."""
        try:
            logger.info("=== ENTERING handle_send_message function ===")
            
            # Extract message from arguments
            message = arguments.get("message", "No message provided")
            
            # Debug logging
            logger.info(f"send_message called with arguments={arguments}")
            logger.info(f"Extracted message: '{message}'")
            
            # Send a log message to demonstrate notifications
            await ctx.session.send_log_message(
                level="info",
                data=f"Received message: {message}",
                logger="message_handler",
                related_request_id=ctx.request_id,
            )
            
            result = [
                types.TextContent(
                    type="text",
                    text=f"Message received and processed: {message}",
                )
            ]
            
            logger.info("=== EXITING handle_send_message function ===")
            return result
        except Exception as e:
            logger.error(f"Exception in handle_send_message: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def handle_get_server_info(
        arguments: dict, ctx
    ) -> list[
        types.TextContent
        | types.ImageContent
        | types.AudioContent
        | types.EmbeddedResource
    ]:
        """Handle get_server_info tool call."""
        try:
            logger.info("=== ENTERING handle_get_server_info function ===")
            import datetime
            
            # Debug logging
            logger.info(f"get_server_info called with arguments={arguments}")
            
            # Send a log message
            await ctx.session.send_log_message(
                level="info",
                data="Server info requested",
                logger="server_info",
                related_request_id=ctx.request_id,
            )
            
            server_info = {
                "name": "MCP Python E2E Server",
                "version": "1.0.0",
                "timestamp": datetime.datetime.now().isoformat(),
                "transport": "StreamableHTTP",
                "language": "Python"
            }
            
            result = [
                types.TextContent(
                    type="text",
                    text=f"Server Information: {server_info}",
                )
            ]
            
            logger.info("=== EXITING handle_get_server_info function ===")
            return result
        except Exception as e:
            logger.error(f"Exception in handle_get_server_info: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        tools = [
            types.Tool(
                name="send_message",
                description="Send a message to the server and get a confirmation",
                inputSchema={
                    "type": "object",
                    "required": ["message"],
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "The message to send",
                        },
                    },
                },
            ),
            types.Tool(
                name="get_server_info",
                description="Get server information and status",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
        ]
        
        # Debug logging
        logger.info(f"list_tools called, returning {len(tools)} tools:")
        for tool in tools:
            logger.info(f"  - {tool.name}: {tool.description}")
            logger.info(f"    inputSchema: {tool.inputSchema}")
        
        return tools

    # Create the session manager
    session_manager = StreamableHTTPSessionManager(
        app=app,
        json_response=json_response,
    )

    # ASGI handler for streamable HTTP connections
    async def handle_streamable_http(
        scope: Scope, receive: Receive, send: Send
    ) -> None:
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Context manager for managing session manager lifecycle."""
        async with session_manager.run():
            logger.info("MCP Python E2E Server started with StreamableHTTP transport!")
            try:
                yield
            finally:
                logger.info("MCP Python E2E Server shutting down...")

    # Create an ASGI application using the transport
    starlette_app = Starlette(
        debug=True,
        routes=[
            Mount("/mcp", app=handle_streamable_http),
        ],
        lifespan=lifespan,
    )

    import uvicorn

    logger.info(f"Starting MCP Python E2E Server on port {port}")
    uvicorn.run(starlette_app, host="127.0.0.1", port=port)

    return 0


if __name__ == "__main__":
    main() 