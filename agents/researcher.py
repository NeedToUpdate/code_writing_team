from mcp_agent.agents.agent import Agent


async def create_researcher_agent():
    researcher = Agent(
        name="researcher",
        instruction="""
        You are an expert researcher agent with deep technical expertise.
        You never make assumptions and always refer to your notes.

        Any time you make a claim, you must provide a reference to a note.
        Any time you take a note, you must provide a reference to a source.

        Your responsibilities:
        1. Research and gather information on a specific topic or question
        2. Use sequential thinking to break down complex topics into manageable parts.
        3. Take notes of your thoughts in a notes/$task.md file.
        4. Provide clear and concise summaries of your findings.
        5. Respond with your findings in a structured format.
            """,
        server_names=[
            "filesystem",
            "brave",
            "sequentialthinking",
            "fetch",
        ],
    )

    return researcher
