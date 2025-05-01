from mcp_agent.agents.agent import Agent
from mcp_agent.human_input.handler import console_input_callback


async def create_project_manager_agent():
    """Create and return a configured Task Organizer agent."""

    project_manager = Agent(
        name="project_manager",
        instruction="""
        You are an expert project manager agent with deep technical expertise.
        You never make assumptions and always refer to your board.

        Your responsibilities:
        1. You will find your board at ./board/$task_key.md
        2. In that board, add in the names of the team members and their roles.
        3. Break down the project into smaller tasks, each with a clear goal and deliverable, use sequential thinking.
        3. Create a task list for the project, including:
            - Task name
            - Description
            - Assigned team member
            - Status (To Do, In Progress, Done)

        4. Organize the tasks in such away that the project can be completed in the shortest time possible.
        5. Respond with the next few tasks that must be completed.
        """,
        server_names=[
            "sequentialthinking",
            "filesystem",
        ],
        # human_input_callback=console_input_callback,
    )

    return project_manager
