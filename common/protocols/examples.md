# MCP Protocol Examples and Testing Scenarios

## Message Exchange Examples

### 1. Initialization Sequence

```json
// Client -> Server: Initialize Request
{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "client_info": {
            "name": "test-client",
            "version": "1.0.0",
            "capabilities": {
                "sampling": {
                    "supported": true,
                    "version": "1.0.0"
                },
                "roots": {
                    "supported": true,
                    "version": "1.0.0"
                }
            }
        }
    }
}

// Server -> Client: Initialize Response
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "server_info": {
            "name": "test-server",
            "version": "1.0.0",
            "capabilities": {
                "resources": {
                    "supported": true,
                    "version": "1.0.0"
                },
                "tools": {
                    "supported": true,
                    "version": "1.0.0"
                }
            }
        }
    }
}
```

### 2. Resource Operations

```json
// Client -> Server: List Resources Request
{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "resources/list",
    "params": {
        "filter": {
            "type": "document"
        }
    }
}

// Server -> Client: List Resources Response
{
    "jsonrpc": "2.0",
    "id": 2,
    "result": {
        "resources": [
            {
                "id": "doc1",
                "type": "document",
                "metadata": {
                    "title": "Test Document",
                    "created": "2024-03-26T10:00:00Z"
                }
            }
        ]
    }
}

// Client -> Server: Read Resource Request
{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "resources/read",
    "params": {
        "resource_id": "doc1"
    }
}

// Server -> Client: Read Resource Response
{
    "jsonrpc": "2.0",
    "id": 3,
    "result": {
        "content": "This is the content of the document",
        "metadata": {
            "mime_type": "text/plain",
            "size": 35
        }
    }
}

// Client -> Server: Subscribe to Resource Updates
{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "resources/subscribe",
    "params": {
        "resource_id": "doc1"
    }
}

// Server -> Client: Resource Updated Notification
{
    "jsonrpc": "2.0",
    "method": "notifications/resources/updated",
    "params": {
        "resource_id": "doc1",
        "change_type": "modified",
        "metadata": {
            "modified": "2024-03-26T11:00:00Z"
        }
    }
}

// Client -> Server: Unsubscribe from Resource Updates
{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "resources/unsubscribe",
    "params": {
        "resource_id": "doc1"
    }
}

// Server -> Client: Resources List Changed Notification
{
    "jsonrpc": "2.0",
    "method": "notifications/resources/list_changed",
    "params": {
        "added": ["doc2"],
        "removed": ["doc1"]
    }
}
```

### 3. Tool Operations

```json
// Client -> Server: List Tools Request
{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/list",
    "params": {}
}

// Server -> Client: List Tools Response
{
    "jsonrpc": "2.0",
    "id": 4,
    "result": {
        "tools": [
            {
                "name": "search",
                "description": "Search for documents",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "limit": {
                            "type": "number",
                            "description": "Maximum number of results"
                        }
                    }
                }
            }
        ]
    }
}

// Client -> Server: Call Tool Request
{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
        "name": "search",
        "arguments": {
            "query": "test query",
            "limit": 10
        }
    }
}

// Server -> Client: Progress Notification
{
    "jsonrpc": "2.0",
    "method": "progress",
    "params": {
        "operation_id": "search-1",
        "status": "running",
        "progress": 50,
        "message": "Searching..."
    }
}

// Server -> Client: Tool Call Response
{
    "jsonrpc": "2.0",
    "id": 5,
    "result": {
        "result": {
            "matches": [
                {
                    "id": "match1",
                    "score": 0.95
                }
            ]
        }
    }
}

// Server -> Client: Tools List Changed Notification
{
    "jsonrpc": "2.0",
    "method": "notifications/tools/list_changed",
    "params": {
        "added": ["new_tool"],
        "removed": ["old_tool"]
    }
}
```

### 4. Sampling Operations

```json
// Server -> Client: Create Message Request
{
    "jsonrpc": "2.0",
    "id": 7,
    "method": "sampling/createMessage",
    "params": {
        "prompt": "Generate a summary of the following text",
        "constraints": {
            "max_tokens": 100,
            "temperature": 0.7
        }
    }
}

// Client -> Server: Create Message Response
{
    "jsonrpc": "2.0",
    "id": 7,
    "result": {
        "message": "Here is a concise summary of the provided text...",
        "metadata": {
            "tokens_used": 45,
            "model": "gpt-4"
        }
    }
}
```

### 5. Prompt Operations

```json
// Client -> Server: List Prompts Request
{
    "jsonrpc": "2.0",
    "id": 8,
    "method": "prompts/list",
    "params": {
        "filter": {
            "type": "completion"
        }
    }
}

// Server -> Client: List Prompts Response
{
    "jsonrpc": "2.0",
    "id": 8,
    "result": {
        "prompts": [
            {
                "id": "prompt1",
                "type": "completion",
                "name": "Code Generation",
                "description": "Generate code based on requirements",
                "template": "Generate code for: {{requirement}}",
                "metadata": {
                    "created": "2024-03-26T10:00:00Z",
                    "version": "1.0.0"
                }
            }
        ]
    }
}

// Client -> Server: Get Prompt Request
{
    "jsonrpc": "2.0",
    "id": 9,
    "method": "prompts/get",
    "params": {
        "prompt_id": "prompt1"
    }
}

// Server -> Client: Get Prompt Response
{
    "jsonrpc": "2.0",
    "id": 9,
    "result": {
        "prompt": {
            "id": "prompt1",
            "type": "completion",
            "name": "Code Generation",
            "description": "Generate code based on requirements",
            "template": "Generate code for: {{requirement}}",
            "parameters": {
                "requirement": {
                    "type": "string",
                    "description": "The requirement to generate code for"
                }
            },
            "metadata": {
                "created": "2024-03-26T10:00:00Z",
                "version": "1.0.0",
                "author": "System"
            }
        }
    }
}

// Client -> Server: Create Prompt Request
{
    "jsonrpc": "2.0",
    "id": 10,
    "method": "prompts/create",
    "params": {
        "prompt": {
            "type": "completion",
            "name": "Document Summary",
            "description": "Generate a summary of a document",
            "template": "Summarize the following document:\n{{document}}",
            "parameters": {
                "document": {
                    "type": "string",
                    "description": "The document to summarize"
                }
            }
        }
    }
}

// Server -> Client: Create Prompt Response
{
    "jsonrpc": "2.0",
    "id": 10,
    "result": {
        "prompt_id": "prompt2",
        "metadata": {
            "created": "2024-03-26T12:00:00Z",
            "version": "1.0.0"
        }
    }
}

// Server -> Client: Prompts List Changed Notification
{
    "jsonrpc": "2.0",
    "method": "notifications/prompts/list_changed",
    "params": {
        "added": ["prompt2"],
        "removed": ["prompt1"]
    }
}
```

### 6. Additional Notifications

```json
// Server -> Client: Progress Notification
{
    "jsonrpc": "2.0",
    "method": "notifications/progress",
    "params": {
        "operation_id": "long-running-op",
        "status": "processing",
        "progress": 75,
        "message": "Processing data..."
    }
}

// Server -> Client: Message Notification
{
    "jsonrpc": "2.0",
    "method": "notifications/message",
    "params": {
        "level": "info",
        "message": "Operation completed successfully",
        "data": {
            "operation_id": "op-123",
            "duration_ms": 1500
        }
    }
}

// Server -> Client: Cancelled Notification
{
    "jsonrpc": "2.0",
    "method": "notifications/cancelled",
    "params": {
        "operation_id": "op-123",
        "reason": "user_requested"
    }
}

// Server -> Client: Initialized Notification
{
    "jsonrpc": "2.0",
    "method": "notifications/initialized",
    "params": {
        "version": "1.0.0",
        "capabilities": {
            "resources": true,
            "tools": true
        }
    }
}
```

### 7. Error Handling

```json
// Client -> Server: Invalid Request
{
    "jsonrpc": "2.0",
    "id": 6,
    "method": "invalid_method",
    "params": {}
}

// Server -> Client: Error Response
{
    "jsonrpc": "2.0",
    "id": 6,
    "error": {
        "code": -32601,
        "message": "Method not implemented",
        "data": {
            "method": "invalid_method"
        }
    }
}
```

## Testing Scenarios

### 1. Basic Connectivity Tests

1. **Connection Establishment**
   - Test successful initialization
   - Test capability negotiation
   - Test invalid initialization parameters
   - Test version mismatch handling

2. **Connection Termination**
   - Test graceful shutdown
   - Test abrupt disconnection
   - Test reconnection handling

### 2. Resource Management Tests

1. **Resource Listing**
   - Test listing all resources
   - Test filtered resource listing
   - Test pagination
   - Test invalid filter handling

2. **Resource Reading**
   - Test resource content retrieval
   - Test metadata retrieval
   - Test non-existent resource handling
   - Test large resource handling

3. **Resource Subscription**
   - Test subscription to resource updates
   - Test multiple resource subscriptions
   - Test unsubscribe functionality
   - Test update notification delivery

4. **Resource Updates**
   - Test resource modification notifications
   - Test resource deletion notifications
   - Test resource creation notifications
   - Test concurrent update handling

### 3. Tool Execution Tests

1. **Basic Tool Operations**
   - Test tool listing
   - Test tool calling
   - Test parameter validation
   - Test tool list change notifications

2. **Long-running Operations**
   - Test progress notifications
   - Test operation cancellation
   - Test timeout handling
   - Test concurrent operations

### 4. Sampling Tests

1. **Message Creation**
   - Test basic message generation
   - Test with different constraints
   - Test with various prompt types
   - Test error handling

2. **Response Handling**
   - Test response validation
   - Test metadata handling
   - Test token usage tracking
   - Test model-specific features

3. **Prompt Tests**
   1. **Prompt Listing**
      - Test listing all prompts
      - Test filtered prompt listing
      - Test pagination
      - Test invalid filter handling

   2. **Prompt Retrieval**
      - Test prompt content retrieval
      - Test metadata retrieval
      - Test non-existent prompt handling
      - Test prompt version handling

   3. **Prompt Creation**
      - Test basic prompt creation
      - Test parameter validation
      - Test template validation
      - Test duplicate prompt handling

   4. **Prompt Updates**
      - Test prompt modification
      - Test version management
      - Test prompt deletion
      - Test concurrent update handling

   5. **Prompt Usage**
      - Test prompt parameter substitution
      - Test template rendering
      - Test prompt execution
      - Test error handling

### 5. Notification Tests

1. **Progress Notifications**
   - Test progress updates
   - Test status changes
   - Test completion notification
   - Test error notification

2. **Message Notifications**
   - Test different message levels
   - Test structured data
   - Test message formatting
   - Test message filtering

3. **System Notifications**
   - Test initialization notification
   - Test cancellation notification
   - Test list change notifications
   - Test concurrent notifications

### 6. Error Handling Tests

1. **Protocol Errors**
   - Test invalid JSON
   - Test missing required fields
   - Test invalid message types
   - Test batch request handling

2. **Application Errors**
   - Test resource not found
   - Test permission denied
   - Test invalid parameters
   - Test operation timeouts

### 7. Security Tests

1. **Authentication**
   - Test HTTP auth
   - Test STDIO auth
   - Test custom auth
   - Test auth failure handling

2. **Authorization**
   - Test resource access control
   - Test tool execution permissions
   - Test capability restrictions

### 8. Performance Tests

1. **Load Testing**
   - Test concurrent connections
   - Test message throughput
   - Test resource watching limits
   - Test tool execution limits

2. **Stress Testing**
   - Test large message handling
   - Test rapid connection cycling
   - Test resource update frequency
   - Test tool execution concurrency

### 9. Version Compatibility Tests

1. **Backward Compatibility**
   - Test older client with newer server
   - Test newer client with older server
   - Test capability negotiation
   - Test deprecated feature handling

2. **Forward Compatibility**
   - Test unknown message handling
   - Test new capability adoption
   - Test protocol extension support 