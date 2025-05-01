import re
import json
from agents.code_reviewer import create_code_reviewer_agent
from agents.coder import create_coder_agent
from agents.comedian import create_comedian_agent
from agents.fact_checker import create_fact_checker_agent
from agents.leader import create_leader_agent
from agents.philosopher import create_philosopher_agent
from agents.project_manager import create_project_manager_agent
from agents.researcher import create_researcher_agent
from agents.token_optimizer import create_token_optimizer_agent
from agents.boomhauer import create_boomhauer_agent
from agents.writer import create_writer_agent
from mcp_agent.workflows.llm.augmented_llm import RequestParams
from utils.app_instance import get_app
from mcp_agent.workflows.llm.augmented_llm_anthropic import AnthropicAugmentedLLM
from mcp_agent.workflows.orchestrator.orchestrator import Orchestrator
from mcp_agent.agents.agent import Agent
from utils.json_extractor import extract_json_from_text
import asyncio
import argparse
import os
import re

from utils.app_instance import get_app

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)


async def get_agent(name: str) -> Agent:
    """Get the agent instance based on the name provided."""
    if name == "code_reviewer":
        return await create_code_reviewer_agent()
    elif name == "coder":
        return await create_coder_agent()
    elif name == "project_manager":
        return await create_project_manager_agent()
    elif name == "token_optimizer":
        return await create_token_optimizer_agent()
    elif name == "researcher":
        return await create_researcher_agent()
    elif name == "philosopher":
        return await create_philosopher_agent()
    elif name == "fact_checker":
        return await create_fact_checker_agent()
    elif name == "comedian":
        return await create_comedian_agent()
    elif name == "leader":
        return await create_leader_agent()
    elif name == "boomhauer":
        return await create_boomhauer_agent()
    elif name == "writer":
        return await create_writer_agent()
    else:
        raise ValueError(f"Unknown agent: {name}")


async def get_agent_prompt(agent_names: list) -> str:
    """Generate a prompt for the agents based on their names and instructions."""

    async def format_single_agent(agent_name: str) -> str:
        return f"""
    =========== {agent_name} ===========
    =========== {agent_name} RESPONSIBILITIES ===========
    {(await get_agent(agent_name)).instruction.lower().replace('you are', 'it is').replace('your', 'its').replace('you', 'it')}
    =========== END OF {agent_name} RESPONSIBILITIES ===========
    """

    formatted_agents = [await format_single_agent(name) for name in agent_names]
    return "\n".join(formatted_agents)


async def main():
    """Main entry point for the application."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Code writing team orchestration.")
    parser.add_argument("task", type=str, help="The task to be executed by the team")
    parser.add_argument(
        "-e",
        "--exclude",
        type=str,
        default="",
        help='Comma-separated list of agents to exclude (e.g., "coder,comedian")',
    )
    args = parser.parse_args()

    # Create a list of excluded agents
    excluded_agents = (
        [agent.strip() for agent in args.exclude.split(",")] if args.exclude else []
    )

    app = get_app()
    async with app.run() as mcp_agent_app:
        logger = mcp_agent_app.logger
        logger.info(f"Starting workflow...")
        logger.info(f"Task: {args.task}")
        if excluded_agents:
            logger.info(f"Excluding agents: {', '.join(excluded_agents)}")

        # Available agent names minus excluded ones
        available_agent_names = [
            name
            for name in [
                "code_reviewer",
                "coder",
                "project_manager",
                "token_optimizer",
                "researcher",
                "philosopher",
                "fact_checker",
                "comedian",
                "leader",
                "boomhauer",
                "writer",
            ]
            if name not in excluded_agents
        ]

        task_prompt = f"""
        You are a manager who needs to deliver the following task to your team of AI agents:

        {args.task}

        You need to create the initial executive summary for the task, and then assign it to the team members.
        The team members are:
        {await get_agent_prompt(available_agent_names)}

        
        1. Pick which team members are best suited for the task.
        2. Create a task slug for the task. The slug should be a short, descriptive name that summarizes the task within 2-3 words. It must be lowercase and with dashes.
        3. Give each team member a goal throughout the task. If they have a project manager, their goal would be to break down the goals into smaller tasks and manage them.
        3. Respond to this query with a perfectly structured json response that contains:
        ```{{
            "executive_summary": "A short executive summary of the task",
            "agents": [
                {{
                    "name": "agent_name",
                    "goal": "$goal_description"
                }}
            ],
            "task_slug": "$task_slug"
        }}```
        Do not use ```, do not use backticks, do not use triple quotes, do not use any other formatting. Just return the json response. NO other text, no explanations, no comments.
        The json response must be valid, and it must be perfectly structured.
        """

        logger.info(f"Task prompt: {task_prompt}")

        danny_ocean = await get_agent("leader")
        danny_ocean_solo = await danny_ocean.attach_llm(AnthropicAugmentedLLM)
        task_plan_str = await danny_ocean_solo.generate_str(task_prompt)

        logger.info(f"Task plan: {task_plan_str}")

        # Use the new JSON extraction utility to parse the response
        task_json = extract_json_from_text(task_plan_str)
        if not task_json:
            logger.error("Could not parse JSON response from task plan")
            return "Error: Could not parse JSON response from task plan"

        logger.info(f"Task plan: {json.dumps(task_json, indent=2)}")

        # build the team
        agents = []  # final agents
        for agent_info in task_json.get("agents", []):
            agent_name = agent_info.get("name")
            if (
                agent_name
                and agent_name not in excluded_agents
                and agent_name in available_agent_names
            ):
                try:
                    agent = await get_agent(agent_name)
                    agents.append(agent)
                except ValueError as e:
                    logger.warning(f"Skipping agent {agent_name}: {str(e)}")

        # format agent info into a prompt
        agent_prompts = []
        for agent_info in task_json.get("agents", []):
            if "name" in agent_info and "goal" in agent_info:
                agent_prompts.append(
                    f"name: {agent_info['name']} | goal: {agent_info['goal']}"
                )
        agent_prompts = "\n".join(agent_prompts)

        # Use task_slug with fallback to a default if missing
        task_slug = task_json.get("task_slug", "unnamed-task")

        final_prompt = f"""
        Danny Ocean has assembled a specialized team for the following mission:

        {args.task}

        Each team member has been carefully selected and given a specific role:
        {agent_prompts}
        
        Mission codename: {task_slug} 
        The team board is at ./board/{task_slug}.md
        The mission notes are at ./notes/{task_slug}.md

        If you have a project manager, they will be in charge of the board, ask them for tasks to hand out to the team, and keep them updated on the progress of the tasks..
        I fyou have a someone with ideas, make sure they reply with ideas to you to share with the team.
        """

        # create those two files
        os.makedirs("./board", exist_ok=True)
        os.makedirs("./notes", exist_ok=True)
        os.makedirs("./code", exist_ok=True)
        with open(f"./board/{task_slug}.md", "w") as f:
            f.write(f"# {task_slug}\n")
        with open(f"./notes/{task_slug}.md", "w") as f:
            f.write(f"# {task_slug}\n")

        orchestrator = Orchestrator(
            llm_factory=AnthropicAugmentedLLM,
            available_agents=agents,
            # We will let the orchestrator iteratively plan the task at every step
            plan_type="full",
            human_input_callback=None,
        )

        result = await orchestrator.generate_str(
            message=final_prompt,
            request_params=RequestParams(
                model="claude-3-5-haiku-20241022", maxTokens=8192
            ),
        )

        logger.info(f"Workflow complete!")

        logger.info(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
