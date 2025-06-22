use anyhow::Result;
use rmcp::{
    ServiceExt,
    model::{CallToolRequestParam, ClientCapabilities, ClientInfo, Implementation},
    transport::StreamableHttpClientTransport,
};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};
use std::env;

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize logging
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| format!("info,{}=debug", env!("CARGO_CRATE_NAME")).into()),
        )
        .with(tracing_subscriber::fmt::layer())
        .init();

    // Get server URL from command line args or use default
    let server_url = env::args()
        .nth(1)
        .unwrap_or_else(|| "http://localhost:8000/mcp".to_string());

    tracing::info!("Connecting to MCP server at {}...", server_url);

    let transport = StreamableHttpClientTransport::from_uri(&*server_url);
    let client_info = ClientInfo {
        protocol_version: Default::default(),
        capabilities: ClientCapabilities::default(),
        client_info: Implementation {
            name: "MCP Rust E2E Client".to_string(),
            version: "0.1.0".to_string(),
        },
    };

    let client = client_info.serve(transport).await.inspect_err(|e| {
        tracing::error!("Client error: {:?}", e);
    })?;

    tracing::info!("✓ Connected to MCP server");

    // Initialize
    let server_info = client.peer_info();
    tracing::info!("Server info: {server_info:#?}");

    tracing::info!("\n=== MCP E2E Test Started ===");

    // 1. List available tools
    tracing::info!("\n1. Listing available tools...");
    let tools = client.list_tools(Default::default()).await?;
    tracing::info!("Available tools:");
    for tool in &tools.tools {
        tracing::info!("  - {}: {}", tool.name, tool.description.as_deref().unwrap_or("No description"));
        tracing::info!("    Schema: {}", serde_json::to_string_pretty(&tool.input_schema).unwrap());
    }

    // 2. Test send_message tool if available
    if tools.tools.iter().any(|t| t.name == "send_message") {
        tracing::info!("\n2. Testing send_message tool...");
        
        let tool_result = client
            .call_tool(CallToolRequestParam {
                name: "send_message".into(),
                arguments: serde_json::json!({
                    "message": "Hello from Rust E2E client!"
                }).as_object().cloned(),
            })
            .await?;

        tracing::info!("Tool result: {tool_result:#?}");
    }

    // 3. Test get_server_info tool if available
    if tools.tools.iter().any(|t| t.name == "get_server_info") {
        tracing::info!("\n3. Testing get_server_info tool...");
        
        let tool_result = client
            .call_tool(CallToolRequestParam {
                name: "get_server_info".into(),
                arguments: serde_json::json!({}).as_object().cloned(),
            })
            .await?;

        tracing::info!("Tool result: {tool_result:#?}");
    }

    // 4. Test increment tool if available (from TypeScript server)
    if tools.tools.iter().any(|t| t.name == "increment") {
        tracing::info!("\n4. Testing increment tool...");
        
        let tool_result = client
            .call_tool(CallToolRequestParam {
                name: "increment".into(),
                arguments: serde_json::json!({
                    "value": 42
                }).as_object().cloned(),
            })
            .await?;

        tracing::info!("Tool result: {tool_result:#?}");
    }

    tracing::info!("\n✓ All E2E tests completed successfully!");

    // Cleanup
    client.cancel().await?;
    tracing::info!("✓ Disconnected from MCP server");

    Ok(())
} 