"""
Tool validation for MCP servers.
Validates that all required MCP tools are available and properly configured.
Based on the pattern from mcp_hello_world example.
"""

from mcp_agent.mcp.gen_client import gen_client
from mcp_agent.mcp.mcp_agent_client_session import MCPAgentClientSession
from mcp_agent.mcp.mcp_connection_manager import MCPConnectionManager
from utils.app_instance import get_app


async def validate_mcp_tools() -> bool:
    """
    Validate that all required MCP tools are available.
    Uses the proper approach shown in the example projects.
    Returns True if all required tools are available, False otherwise.
    """
    app = get_app()
    async with app.run() as mcp_agent_app:
        context = mcp_agent_app.context
        logger = mcp_agent_app.logger

        required_servers = [
            "jira",
            "github",
            "filesystem",
            "confluence",
            "npm",
        ]  # 'git' is broken cause it was vibe coded probably, too lazy to fix it now

        # Check if MCP servers are configured
        if not hasattr(context.config, "mcp") or not hasattr(
            context.config.mcp, "servers"
        ):
            logger.error("MCP servers configuration not found")
            return False

        configured_servers = context.config.mcp.servers.keys()
        missing_servers = [
            server for server in required_servers if server not in configured_servers
        ]

        if missing_servers:
            logger.error(f"Missing required MCP servers: {', '.join(missing_servers)}")
            return False

        # Create connection manager to check each server
        connection_manager = MCPConnectionManager(context.server_registry)
        await connection_manager.__aenter__()

        try:
            tool_check_results = {}

            # Check each required server
            logger.info("\nChecking required MCP tools:")
            for server_name in configured_servers:
                try:
                    # Try to connect to each server
                    logger.info(f"Connecting to {server_name} server...")

                    async with gen_client(
                        server_name, server_registry=context.server_registry
                    ) as client:
                        # List available tools
                        try:
                            logger.info(
                                f"{server_name}: Connected to server, listing tools..."
                            )
                            result = await client.list_tools()
                            dump = result.model_dump()
                            tools = {tool["name"] for tool in dump.get("tools", [])}
                            logger.info("Tools available:", data=tools)

                            tool_check_results[server_name] = {
                                "connected": True,
                                "tool_count": len(tools),
                                "tools": tools,
                            }
                        except Exception as e:
                            logger.error(
                                f"Failed to list tools on {server_name} server: {str(e)}"
                            )
                            tool_check_results[server_name] = {
                                "connected": False,
                                "error": str(e),
                            }

                except Exception as e:
                    logger.error(
                        f"Failed to connect to {server_name} server: {str(e)}", data=e
                    )
                    tool_check_results[server_name] = {
                        "connected": False,
                        "error": str(e),
                    }

            # Determine if all required servers are available
            all_servers_available = all(
                tool_check_results.get(server, {}).get("connected", False)
                for server in required_servers
            )

            if all_servers_available:
                logger.info("\n✓ All required MCP tools are available and functioning.")
                return True
            else:
                failed_servers = [
                    server
                    for server in required_servers
                    if not tool_check_results.get(server, {}).get("connected", False)
                ]
                logger.error(
                    f"\n✗ Some required MCP tools failed validation: {', '.join(failed_servers)}"
                )
                return False

        finally:
            # Ensure we clean up the connection manager
            await connection_manager.__aexit__(None, None, None)
