from strands import Agent, tool
from strands.models import BedrockModel


@tool
def add(a: float, b: float) -> float:
    """Add two numbers and return the sum.

    Args:
        a: First number.
        b: Second number.
    """
    return a + b


@tool
def word_length(text: str) -> int:
    """Return the number of characters in the given text.

    Args:
        text: The input string to measure.
    """
    return len(text)


bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-6",
    region_name="us-west-2",
    temperature=0.3,
)

agent = Agent(model=bedrock_model, tools=[add, word_length])

if __name__ == "__main__":
    agent(
        "Two questions: (1) what is 17 + 25? "
        "(2) how many characters are in the word 'strawberry'?"
    )
