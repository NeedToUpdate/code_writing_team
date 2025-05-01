from mcp_agent.agents.agent import Agent


async def create_code_reviewer_agent():
    code_reviewer = Agent(
        name="code_reviewer",
        instruction="""
        You are an expert code reviewer agent with deep technical expertise. You never make assumptions and always refer to your notes.
        Your responsibilities:
        1. Review the code provided by the coder agent.
        2. Ensure that the code is clean, well-documented, and follows best practices.
        3. Check for any potential bugs or performance issues.
        4. Provide constructive feedback and suggestions for improvement.
        5. Ensure that the code meets the requirements and acceptance criteria provided by the project manager.
        """,
        server_names=[
            "filesystem",
            "sequentialthinking",
        ],  # Needs filesystem access to read code files
    )

    return code_reviewer
