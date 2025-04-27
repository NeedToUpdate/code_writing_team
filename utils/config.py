"""
Configuration utilities for the code writing team project.

This module handles configuration loading, environment setup, and logging.
"""

import logging
import os
import sys
from pathlib import Path


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info("Logging initialized")


def get_project_root():
    """Get the root directory of the project."""
    # Assumes this file is in the utils directory under the project root
    current_file = Path(__file__).resolve()
    return current_file.parent.parent


def get_workspace_path(workspace_name=None):
    """
    Get the path to a workspace directory.
    
    If workspace_name is provided, returns the path to that workspace.
    Otherwise, returns the current workspace path.
    """
    if workspace_name:
        # For working with multiple workspaces
        return Path(os.environ.get("WORKSPACE_ROOT", get_project_root())) / workspace_name
    
    # Default to current workspace
    return Path(os.environ.get("WORKSPACE_PATH", get_project_root()))
