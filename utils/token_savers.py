"""

This will save on tokens when a task file already exists, as it will not need to be generated again.

"""

import os

from utils.config import get_workspace_path


def get_task_file_prompt(ticket_key: str) -> str:
    workspace = get_workspace_path()
    content = ""

    if os.path.exists(f"{workspace}/tasks/{ticket_key}.md"):
        with open(f"{workspace}/tasks/{ticket_key}.md", "r") as file:
            task_file_content = file.read()
        content = f"""It seems the task file for ticket {ticket_key} already exists. Here is the content of the task file contents so you dont need to read it using a tool, saving on tokens.
        ========= START OF TASK FILE ==========
{task_file_content}
========= END OF TASK FILE ===========
        """
    return content


def get_repo_folder() -> str:
    """Get the folder structure for the repos folder."""
    workspace = get_workspace_path()

    folders = []

    if not os.path.exists(f"{workspace}/repos"):
        os.makedirs(f"{workspace}/repos")
        return "there is already a repos folder, so no need to create one, however it is empty."

    for root, dirs, files in os.walk(f"{workspace}/repos"):
        for dir in dirs:
            if dir.strip():  # Skip empty folder names
                folders.append(os.path.join(root, dir))

    # format it as a string with new lines
    folder_string = "\n".join(folders)
    return f"""
    The following folders were found in the repos folder:
    {folder_string}
    """
