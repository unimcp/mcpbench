use std::sync::Arc;
use tokio::sync::Mutex;
use rmcp::{
    model::{CallToolResult, Content, CallToolRequestParam, ListToolsResult, ServerInfo, ProtocolVersion, ServerCapabilities},
    service::ServiceExt,
    transport::streamable_http_server::StreamableHttpService,
    Error as McpError,
    ServerHandler,
    tool,
};

#[derive(Clone)]
struct TestServer {
    message: Arc<Mutex<String>>,
}

impl TestServer {
    fn new() -> Self {
        Self {
            message: Arc::new(Mutex::new("No message".to_string())),
        }
    }

    async fn handle_message(&self, message: String) -> Result<CallToolResult, McpError> {
        let mut current = self.message.lock().await;
        *current = message;
        Ok(CallToolResult::success(vec![Content::text(
            format!("Received message: {}", current)
        )]))
    }
}

#[tool(tool_box)]
impl TestServer {
    #[tool(description = "Send a message to the server")]
    async fn send_message(&self, message: String) -> Result<CallToolResult, McpError> {
        self.handle_message(message).await
    }
}

impl ServerHandler for TestServer {
    fn call_tool(
        &self,
        request: CallToolRequestParam,
        _context: rmcp::service::RequestContext<rmcp::service::RoleServer>,
    ) -> impl std::future::Future<Output = Result<CallToolResult, McpError>> + Send + '_ {
        async move {
            match request.name.as_str() {
                "send_message" => {
                    let message = request.arguments
                        .and_then(|args| args.get("message"))
                        .and_then(|v| v.as_str())
                        .unwrap_or("No message")
                        .to_string();
                    self.handle_message(message).await
                }
                _ => Err(McpError::method_not_found::<rmcp::model::CallToolRequestMethod>()),
            }
        }
    }

    fn list_tools(
        &self,
        _request: Option<rmcp::model::PaginatedRequestParam>,
        _context: rmcp::service::RequestContext<rmcp::service::RoleServer>,
    ) -> impl std::future::Future<Output = Result<ListToolsResult, McpError>> + Send + '_ {
        async move {
            Ok(ListToolsResult {
                tools: vec![rmcp::model::Tool {
                    name: "send_message".into(),
                    description: Some("Send a message to the server".into()),
                    input_schema: Arc::new(serde_json::json!({
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Message to send"
                            }
                        },
                        "required": ["message"]
                    }).as_object().unwrap().clone()),
                    annotations: None,
                }],
                next_cursor: None,
            })
        }
    }

    fn get_info(&self) -> ServerInfo {
        ServerInfo {
            protocol_version: ProtocolVersion::new(0, 1, 0),
            capabilities: ServerCapabilities::default(),
            server_info: rmcp::model::ServerInfo {
                name: "Test Server".into(),
                version: "0.1.0".into(),
            },
            instructions: None,
        }
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Configure logging
    env_logger::init();
    log::info!("Starting MCP server...");

    // Create server instance
    let server = TestServer::new();

    // Create streamable HTTP server
    let transport = StreamableHttpService::new(
        std::env::var("MCP_SERVER_HOST").unwrap_or_else(|_| "0.0.0.0".to_string()),
        std::env::var("MCP_SERVER_PORT")
            .unwrap_or_else(|_| "8000".to_string())
            .parse::<u16>()
            .expect("Invalid port number"),
    )?;

    // Start server
    log::info!("Server listening on {}", transport.addr());
    server.serve(transport).await?;

    Ok(())
} 