import pytest
import json
from typing import Dict, Any
import asyncio
from pathlib import Path

class Transport:
    """Base transport class for MCP communication"""
    def __init__(self):
        self.connected = False
        self.messages = []

    async def connect(self) -> None:
        """Establish connection"""
        self.connected = True

    async def disconnect(self) -> None:
        """Close connection"""
        self.connected = False

    async def send(self, message: Dict[str, Any]) -> None:
        """Send a message"""
        if not self.connected:
            raise ConnectionError("Not connected")
        self.messages.append(message)

    async def receive(self) -> Dict[str, Any]:
        """Receive a message"""
        if not self.connected:
            raise ConnectionError("Not connected")
        if not self.messages:
            raise TimeoutError("No messages available")
        return self.messages.pop(0)

class Client:
    """MCP client implementation"""
    def __init__(self, transport: Transport):
        self.transport = transport
        self.initialized = False
        self.capabilities = {}

    async def connect(self) -> None:
        """Connect to server"""
        await self.transport.connect()

    async def disconnect(self) -> None:
        """Disconnect from server"""
        await self.transport.disconnect()

    async def initialize(self) -> None:
        """Initialize client with server"""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "client_info": {
                    "name": "test-client",
                    "version": "1.0.0",
                    "capabilities": {
                        "sampling": {
                            "supported": True,
                            "version": "1.0.0"
                        },
                        "roots": {
                            "supported": True,
                            "version": "1.0.0"
                        }
                    }
                }
            }
        }
        await self.transport.send(request)
        response = await self.transport.receive()
        
        if "error" in response:
            raise Exception(f"Initialization failed: {response['error']}")
        
        self.initialized = True
        self.capabilities = response["result"]["server_info"]["capabilities"]

@pytest.fixture
def transport():
    """Create a transport instance"""
    return Transport()

@pytest.fixture
def client(transport):
    """Create a client instance"""
    return Client(transport)

@pytest.mark.asyncio
async def test_transport_connection(transport):
    """Test basic transport connection"""
    # Test initial state
    assert not transport.connected
    
    # Test connection
    await transport.connect()
    assert transport.connected
    
    # Test disconnection
    await transport.disconnect()
    assert not transport.connected

@pytest.mark.asyncio
async def test_client_initialization(client):
    """Test client initialization with server"""
    # Test initial state
    assert not client.initialized
    
    # Connect client
    await client.connect()
    assert client.transport.connected
    
    # Initialize client
    await client.initialize()
    assert client.initialized
    assert "resources" in client.capabilities
    assert "tools" in client.capabilities
    
    # Disconnect client
    await client.disconnect()
    assert not client.transport.connected

@pytest.mark.asyncio
async def test_transport_message_exchange(transport):
    """Test message exchange through transport"""
    await transport.connect()
    
    # Test sending message
    test_message = {"jsonrpc": "2.0", "id": 1, "method": "test"}
    await transport.send(test_message)
    assert len(transport.messages) == 1
    
    # Test receiving message
    received = await transport.receive()
    assert received == test_message
    assert len(transport.messages) == 0
    
    # Test receiving with no messages
    with pytest.raises(TimeoutError):
        await transport.receive()
    
    await transport.disconnect()

@pytest.mark.asyncio
async def test_client_error_handling(client):
    """Test client error handling"""
    await client.connect()
    
    # Test sending message when not initialized
    with pytest.raises(Exception):
        await client.initialize()
    
    # Test sending message when disconnected
    await client.disconnect()
    with pytest.raises(ConnectionError):
        await client.transport.send({"jsonrpc": "2.0", "id": 1, "method": "test"}) 