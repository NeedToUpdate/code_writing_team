"""
A simplified test script for the code writing team workflow.
This runs a mini version of the process_ticket workflow using all three agents
with a simple orchestration prompt to "write some cool code".
"""

import asyncio
import logging
import os

# Local agent imports
from agents.code_reviewer import create_code_reviewer_agent
from agents.coder import create_coder_agent
from agents.project_manager import create_task_organizer_agent

# Utility imports
from utils.app_instance import get_app
from utils.config import setup_logging

# MCP imports
from mcp_agent.workflows.llm.augmented_llm import RequestParams
from mcp_agent.workflows.llm.augmented_llm_anthropic import AnthropicAugmentedLLM
from mcp_agent.workflows.orchestrator.orchestrator import Orchestrator
from mcp_agent.human_input.handler import console_input_callback

# Ensure we're running from the code_writing_team directory so config files are found
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)


async def run_mini_workflow():
    """Run a simplified version of the workflow with all three agents."""
    app = get_app()
    async with app.run() as mcp_agent_app:
        logger = mcp_agent_app.logger
        logger.info("Starting mini workflow test...")

        # Create all three specialized agents
        logger.info("Creating agents...")
        task_organizer = await create_task_organizer_agent()
        coder = await create_coder_agent()
        code_reviewer = await create_code_reviewer_agent()

        # Simple orchestration prompt
        prompt = """
        You are a team of AI agents working together to write some cool code.
        
        Task Organizer: First, suggest a small coding project idea that would be fun to implement.
        It should be something simple enough to do in a short demo.
        
        Coder: Implement the code for the project idea. Make it clean, well-commented,
        and use best practices. Keep it under 100 lines of code.
        
        Code Reviewer: Review the code, suggest any improvements, and provide feedback.
        
        Write the final code to a file called 'cool_code.py' in the current directory.
        """

        # Create the orchestrator with all three agents
        logger.info("Creating orchestrator...")
        orchestrator = Orchestrator(
            llm_factory=AnthropicAugmentedLLM,
            available_agents=[
                task_organizer,
                coder,
                code_reviewer,
            ],
            pl5an_type="full",
            human_input_callback=console_input_callback,
        )

        # Run the orchestrator with our simple prompt
        logger.info("Running orchestrator...")
        result = await orchestrator.generate_str(
            message=prompt,
            request_params=RequestParams(model="claude-3-7-sonnet-20250219"),
        )

        logger.info("Workflow complete!")
        logger.info(f"Result: {result}")

        return result


def main():
    """Main entry point for the test script."""
    setup_logging()
    logger = logging.getLogger("coding_crew_test")

    logger.info("\n" + "=" * 80)
    logger.info("Starting mini workflow test")
    logger.info("=" * 80 + "\n")

    try:
        result = asyncio.run(run_mini_workflow())

        logger.info("\n" + "-" * 80)
        logger.info(f"Test Result: {result}")
        logger.info("-" * 80 + "\n")

    except Exception as e:
        logging.exception(f"Error in test workflow: {e}")
        logger.info(f"\nERROR: Encountered a problem: {e}")
        logger.info("Check the logs for details.")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
