import re
from agents.code_reviewer import create_code_reviewer_agent
from agents.coder import create_coder_agent
from agents.project_manager import create_task_organizer_agent
from utils.token_savers import get_repo_folder, get_task_file_prompt
from mcp_agent.workflows.llm.augmented_llm import RequestParams
from workflows.check_ticket_completed import check_ticket_completed
from workflows.ensure_task_file_exists import ensure_task_file_exists
from utils.app_instance import get_app
from mcp_agent.workflows.llm.augmented_llm_anthropic import AnthropicAugmentedLLM
from mcp_agent.workflows.orchestrator.orchestrator import Orchestrator


async def process_ticket(ticket_key: str, workspace_path: str) -> str:
    """Process a single Jira ticket through the entire workflow."""
    app = get_app()
    async with app.run() as mcp_agent_app:
        logger = mcp_agent_app.logger
        logger.info(f"Starting processing of Jira ticket: {ticket_key}")

        # Check for existing task file - if it exists, we're resuming work
        existing_task_content = await ensure_task_file_exists(
            ticket_key, workspace_path
        )

        # Check if ticket is already completed
        if existing_task_content and await check_ticket_completed(
            ticket_key, existing_task_content
        ):
            logger.info(f"Ticket {ticket_key} appears to be already completed.")
            logger.info(f"INFO: Ticket {ticket_key} appears to be already completed.")
            logger.info(
                "Please check the task file for details or manually delete it to start over."
            )
            return f"Ticket {ticket_key} already completed"

        # Create all our specialized agents
        task_organizer = await create_task_organizer_agent()
        coder = await create_coder_agent()
        code_reviewer = await create_code_reviewer_agent()

        # Step 1: Ticket intake - read the ticket details
        logger.info(f"Reading ticket {ticket_key}...")

        task_organizer_solo_agent = await task_organizer.attach_llm(
            AnthropicAugmentedLLM
        )

        ticket_details = await task_organizer_solo_agent.generate_str(
            f"""Get complete details for Jira ticket {ticket_key}. 
            Include all fields, comments, and attachments.
            f"Format the response as a structured summary.

            You can ignore parts of the ticket that are not relevant to the implementation, such as:
            - Comments that are not relevant to the implementation
            - Attachments that are not relevant to the implementation
            - Fields that are not relevant to the implementation like dates, assignee, etc.

            Combining the comments, attachments, and ticket details, provide a complete overview of the ticket in an executive summary
            The summary should be in step by step format of everything needed to be done to complete the ticket.

            Save that summary to a file in the tasks directory at tasks/{ticket_key}.md.

            If the ticket is not found or doesn't exist, return the message TICKET_NOT_FOUND.
            If the ticket is empty or has no description, return the message TICKET_EMPTY.
            IF the ticket does not specify a repository, return the message TICKET_NO_REPO.
            If the ticket is not accessible, return the message TICKET_NOT_ACCESSIBLE.

            Along with this, set up the initial git repository for the ticket.
            The repository should be cloned to repos/

            Remember to double check the current state of the task file. If there is an indication this ticket was already completed, 
            return the message TICKET_ALREADY_COMPLETED. But also mark the ticket as done.

            {get_task_file_prompt(ticket_key)}
            {get_repo_folder()}
            """,
            request_params=RequestParams(model="claude-3-7-sonnet-20250219"),
        )

        logger.info(f"Ticket details: {ticket_details}")

        if (
            "TICKET_NOT_FOUND" in ticket_details
            or "TICKET_EMPTY" in ticket_details
            or "TICKET_NO_REPO" in ticket_details
            or "TICKET_NOT_ACCESSIBLE" in ticket_details
        ):
            logger.error(f"Error reading ticket {ticket_key}: {ticket_details}")
            logger.info(f"ERROR: {ticket_details}")
            return f"Error reading ticket {ticket_key}: {ticket_details}"

        task = f"""
        You are a task organizer agent, you try to make sure the team is organized, and avoids excessive replies or tool calls, hence you keep things updated and organized.
        
        You have the following information:

        {get_task_file_prompt(ticket_key)}
        {get_repo_folder()}
        
        Your responsibilities:
        1. make sure the task list has some information about the repo that relates to the ticket, if not, add it.
        2. make sure the task list is clear and concise, and does not have any duplicates.
        3. make sure the task list is up to date with the current state of the ticket.
        4. Make sure that there is a TODO list in the task file, which is a mix of the understanding of the repo and the ticket.
        5. Make the developer write code
        6. Make the reviewer review the code
        7. Make sure all changes have a commit, and that is recorded in the task list.
        8. Make sure the task list is up to date with the current state of the ticket.
        9. Make sure proper SDLC is followed, and that the task list is up to date with the current state of the ticket.


        SDLC:
        1. Read the task list at {workspace_path}/tasks/{ticket_key}.md 
        2. Write code to implement the task list
            - use the skullcandy approach, create a feat/$ticket_key-$ticket_blurb branch
        3. Review the code to make sure it is correct and follows the task list
        4 Write unit tests to make sure the code is correct and follows the task list
        5. Execute the code to make sure it is correct and follows the task list
        6. Write documentation to make sure the code is correct and follows the task list
             - documentation should be in confluense, but a /docs md file is also acceptable.
        7. Create a pull request to make sure the code is correct and follows the task list

        Analyze that all acceptance criteria are met, and that the task list is up to date with the current state of the ticket.
        Mark all tasks in the TODO list as done if they are.

        Finally add a big bold TASK COMPLETE at the top of the tasks file when you are done.
        """

        orchestrator = Orchestrator(
            llm_factory=AnthropicAugmentedLLM,
            available_agents=[
                task_organizer,
                coder,
                code_reviewer,
            ],
            # We will let the orchestrator iteratively plan the task at every step
            plan_type="full",
            human_input_callback=None,
        )

        result = await orchestrator.generate_str(
            message=task,
            request_params=RequestParams(model="claude-3-7-sonnet-20250219"),
        )

        logger.info(f"PR creation result: {result}")
        logger.info(f"INFO: Created pull request for ticket {ticket_key}.")

        logger.info(f"\nSuccessfully completed all tasks for ticket {ticket_key}!")
        return f"Successfully processed ticket {ticket_key}"
