async def check_ticket_completed(ticket_key: str, task_content: str) -> bool:
    """
    Check if the ticket has already been completed based on the task file content.
    """
    if not task_content:
        return False
        
    # Check for completion markers in task content
    completion_markers = [
        "PR created and submitted",
        "Pull request created",
        "Task completed",
        "All work completed",
        "Status: Completed",
        "COMPLETED"
    ]
    
    for marker in completion_markers:
        if marker.lower() in task_content.lower():
            return True
            
    return False
