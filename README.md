# Code Writing Team

An automated AI-powered software development system that processes Jira tickets and implements code changes using a team of specialized AI agents.

## Overview

This project automates the entire software development lifecycle from ticket intake to PR creation using a team of AI agents powered by Model Context Protocol (MCP) and Anthropic's Claude models. The system can:

1. Read Jira tickets and extract requirements
2. Clone relevant repositories
3. Organize tasks and create implementation plans
4. Write code according to specifications
5. Review code for quality and correctness
6. Create pull requests with all required changes
7. Update documentation in Confluence

## Architecture

The system operates with specialized AI agents:

- **Task Organizer**: Analyzes tickets, creates task plans, and manages workflow
- **Coder**: Implements code changes based on requirements
- **Code Reviewer**: Reviews code for quality, correctness and best practices

The workflow is orchestrated by the MCP Orchestrator, which manages agent interactions and task execution.

## Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- Jira and Confluence access
- GitHub access with appropriate permissions
- Anthropic API key (Claude 3.7 Sonnet model)

## Installation

### 1. Clone this repository

```bash
git clone <repository-url>
cd code_writing_team
```

### 2. Install dependencies using uv

```bash
uv pip sync uv.lock
```

### 3. Set up configuration

Copy and configure your secrets file:

```bash
cp mcp_agent.secrets.example.yaml mcp_agent.secrets.yaml
```

Edit `mcp_agent.secrets.yaml` with your actual API keys and credentials.

## Known Issues

⚠️ **Important**: The git-mcp server is currently non-functional. You will need to manually clone repositories into the `repos/` folder before running the system against a ticket. Once cloned, the AI agents will detect the existing repositories and work with them without attempting to clone.

Example of manually cloning a repository:

```bash
# Create the repos directory if it doesn't exist
mkdir -p repos

# Clone the repository needed for your ticket
git clone https://github.com/username/repository.git repos/repository
```

Ensure the repository name matches what is specified in the Jira ticket for the AI agents to locate it correctly.

## Usage

Run the system by providing a Jira ticket key:

```bash
python main.py PROJ-123
```

The system will:

1. Validate MCP tools
2. Process the ticket
3. Clone the relevant repository
4. Create a task file in the `tasks/` directory
5. Implement code changes
6. Create a pull request
7. Update the task file with progress

## Project Structure

- `main.py`: Entry point for the application
- `agents/`: Specialized AI agent implementations
  - `code_reviewer.py`: Code review agent
  - `coder.py`: Implementation agent
  - `task_organizer.py`: Task organization agent
- `workflows/`: Workflow orchestration modules
  - `process_ticket.py`: Main ticket processing workflow
  - `clone_repository.py`: Repository cloning workflow
  - `ensure_task_file_exists.py`: Task file management
- `utils/`: Utility modules
  - `config.py`: Configuration management
  - `app_instance.py`: Application instance management
- `repos/`: Cloned repositories for ticket implementation
- `tasks/`: Task files for each ticket

## Configuration

The system uses three configuration files:

- `mcp_agent.config.yaml`: General configuration for MCP servers and settings
- `mcp_agent.secrets.yaml`: Sensitive credentials and API keys (not committed to version control)
- `.env`: Environment variables for Docker and local development

### Environment Variables (.env)

The `.env` file contains configuration used for both local development and Docker:

```properties
# Default ticket ID (can be overridden when running docker-compose)
TICKET_ID=AI-8

# Git user configuration
GIT_AUTHOR_NAME=YourName
GIT_AUTHOR_EMAIL=your.email@example.com
```

Key variables:

- `TICKET_ID`: Default Jira ticket to process when running in Docker
- `GIT_AUTHOR_NAME` and `GIT_AUTHOR_EMAIL`: Git user identity for commits

When using Docker, you can override the ticket ID:

```bash
TICKET_ID=PROJ-123 docker-compose up
```

## Development

### Adding a new MCP server

1. Add the server configuration to `mcp_agent.config.yaml`
2. Add required environment variables to `mcp_agent.secrets.yaml`
3. Update the `validate_mcp_tools.py` to check for the new server

### Adding a new agent

1. Create a new agent file in the `agents/` directory
2. Implement the agent with specialized capabilities
3. Add the agent to the orchestrator in `process_ticket.py`

## Troubleshooting

### Common Issues

- **Missing MCP tools**: Ensure all required MCP servers are configured correctly
- **API rate limits**: Check for rate limiting in Jira, GitHub, or Anthropic APIs
- **Permission issues**: Verify API tokens have appropriate permissions

### Logs

Logs are output to the console by default. Set the log level in `mcp_agent.config.yaml`.

## License

[Add your license information here]

## Contributing

[Add your contribution guidelines here]
