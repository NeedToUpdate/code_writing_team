"""- Automated Ticket Processor

This script orchestrates a team of AI agents that automatically process Jira tickets:
1. Read Jira tickets by ticket key
2. Clone the relevant repository mentioned in the ticket
3. Create and maintain task files for each ticket
4. Create task lists and implement code changes
5. Create pull requests and update documentation

The workflow is orchestrated using MCP (Model Context Protocol) agents.

Usage:
    python main.py PROJ-123
"""

import asyncio
import logging
import os
import re
import sys

# Local workflow imports
from workflows.validate_mcp_tools import validate_mcp_tools
from workflows.process_ticket import process_ticket

# Local utility imports
from utils.config import setup_logging
from utils.app_instance import get_app

# Ensure we're running from the code_writing_team directory so config files are found
# Change directory to the location of this script
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)


async def run_workflow(ticket_key: str, workspace_path: str):
    """Run the main workflow with a specified ticket key."""

    # Step 1: Validate MCP tools
    tools_valid = await validate_mcp_tools()
    if not tools_valid:
        return "Failed: Missing required MCP tools."

    # Step 2: Process the selected ticket
    result = await process_ticket(ticket_key, workspace_path)
    return result


def main():
    """Main entry point for the application."""
    setup_logging()

    logger = logging.getLogger("coding_crew")

    # Parse command line arguments
    if len(sys.argv) < 2:
        logger.info("Error: No ticket key provided.")
        logger.info("Usage: python main.py PROJ-123")
        sys.exit(1)

    ticket_key = sys.argv[1].strip()
    if not re.match(r"^[A-Z]+-\d+$", ticket_key):
        logger.info(f"Error: '{ticket_key}' doesn't look like a valid ticket key.")
        logger.info("Expected format: PROJ-123")
        sys.exit(1)

    # Use current directory as workspace path
    workspace_path = os.getcwd()

    logger.info(f"\n{'='*80}")
    logger.info(f"Starting work on ticket {ticket_key}")
    logger.info(f"{'='*80}\n")

    try:
        result = asyncio.run(run_workflow(ticket_key, workspace_path))
        logger.info(f"\n{'-'*80}")
        logger.info(f"Workflow result: {result}")
        logger.info(f"{'-'*80}\n")
    except Exception as e:
        logging.exception(f"Error in workflow: {e}")
        logger.info(f"\nERROR: Encountered a problem: {e}")
        logger.info("Check the logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
