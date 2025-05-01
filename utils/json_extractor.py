import re
import json
from typing import Any, Dict, Optional, Union


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract clean JSON from a text response that may contain additional non-JSON content.

    This function uses a pattern matching approach to extract JSON objects from text,
    handling both triple backtick code blocks and plain JSON within text.

    Args:
        text: The text that may contain JSON data

    Returns:
        The parsed JSON object as a Python dictionary, or None if no valid JSON was found
    """
    # First, try to find JSON within code blocks (```json ... ```)
    code_block_pattern = r"```(?:json)?\s*(\{.*?\})```"
    code_match = re.search(code_block_pattern, text, re.DOTALL)

    if code_match:
        json_str = code_match.group(1).strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # If parsing fails, continue to other methods
            pass

    # Then try finding just a JSON object anywhere in the text
    json_pattern = r"(\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\})"
    json_matches = re.findall(json_pattern, text, re.DOTALL)

    # Try each potential match
    for potential_json in json_matches:
        try:
            # Clean up the potential JSON string
            cleaned_json = potential_json.strip()
            parsed_json = json.loads(cleaned_json)
            # If we get here, we successfully parsed some JSON
            return parsed_json
        except json.JSONDecodeError:
            continue

    return None


def main():
    """Test function for extract_json_from_text"""
    test_text = """
    Based on my strategic analysis, I've developed a plan for our "surprise me" task that will leverage each team member's unique talents. Here's the structured assignment:

    {
        "executive_summary": "The Serendipity Engine project aims to create an AI system that generates genuinely surprising and delightful content across multiple formats.",
        "agents": [
            {
                "name": "project_manager",
                "goal": "Break down the serendipity engine project into manageable tasks"
            },
            {
                "name": "coder",
                "goal": "Develop the core algorithm that generates surprising but coherent outputs"
            }
        ],
        "task_slug": "serendipity-engine"
    }
    """

    result = extract_json_from_text(test_text)
    if result:
        print("Successfully extracted JSON:")
        print(json.dumps(result, indent=2))
    else:
        print("Failed to extract JSON")


if __name__ == "__main__":
    main()
