"""Module for managing the global MCP application instance."""

from mcp_agent.app import MCPApp

# Create a singleton instance of MCPApp
app = MCPApp(name="coding_crew")

def get_app():
    """Get the global MCPApp instance."""
    return app