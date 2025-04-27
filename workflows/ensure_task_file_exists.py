import os
import logging


async def ensure_task_file_exists(ticket_key: str, workspace_path: str) -> str:
    """
    Ensure the task file for the ticket exists, create it if it doesn't.
    Return the content of the task file if it exists.
    Uses standard Python file operations instead of MCP agents.
    """
    logger = logging.getLogger("coding_crew")

    # First ensure the tasks directory exists
    tasks_dir = os.path.join(workspace_path, "tasks")

    # Check if directory exists, create if needed
    if not os.path.isdir(tasks_dir):
        logger.info(f"Creating tasks directory: {tasks_dir}")
        os.makedirs(tasks_dir, exist_ok=True)
        logger.info(f"Created tasks directory: {tasks_dir}")
    else:
        logger.info(f"Tasks directory already exists: {tasks_dir}")

    # Check if task file exists
    task_file_path = os.path.join(tasks_dir, f"{ticket_key}.md")

    if os.path.isfile(task_file_path):
        logger.info(
            f"Found existing task file for {ticket_key}. Will resume from last completed step."
        )
        with open(task_file_path, "r", encoding="utf-8") as file:
            file_content = file.read()
        return file_content
    else:
        logger.info(
            f"Task file for {ticket_key} does not exist. Will be created during planning phase."
        )
        return None
