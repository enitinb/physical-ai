"""Physical AI Demo: a Strands agent that uses real Raspberry Pi hardware.

The agent reads the Sense HAT (temperature, humidity, orientation), takes
photos with the Camera Module, and shows messages on the LED matrix, all
through simple tools in sensor_tools.py.

Run modes:
- python pi_sensor_agent.py           runs the preset scenarios.
- python pi_sensor_agent.py --chat    drops into an interactive prompt.
"""

import sys

from strands import Agent
from strands.models import BedrockModel

from sensor_tools import (
    capture_image,
    read_environment,
    read_orientation,
    show_message,
)

bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-6",
    region_name="us-west-2",
    temperature=0.3,
)

SYSTEM_PROMPT = (
    "You are an on-device assistant running on a Raspberry Pi with a Sense HAT "
    "and a camera.\n"
    "\n"
    "- Answer only what the user asked, using the tools to read real sensors.\n"
    "- Take a photo or show an LED message only when the user asks for it.\n"
    "- Keep answers short and plain. No emoji, no markdown, no preamble.\n"
    "- The Sense HAT sits above the CPU, so its temperature reads a few degrees "
    "high. Mention that only if the user asks about room temperature."
)

agent = Agent(
    model=bedrock_model,
    system_prompt=SYSTEM_PROMPT,
    tools=[read_environment, read_orientation, capture_image, show_message],
)


SCENARIOS = [
    ("Environment", "What is the temperature and humidity right now?"),
    ("Orientation", "Is the Pi sitting level, or is it tilted?"),
    ("Photo", "Take a photo and tell me where you saved it."),
    ("LED message", "Show the message 'HELLO PI' on the LED matrix."),
]


def run_scenarios() -> None:
    for i, (title, prompt) in enumerate(SCENARIOS, start=1):
        print(f"\n=== Scenario {i}/{len(SCENARIOS)}: {title} ===")
        print(f"User: {prompt}\n")
        agent(prompt)


def run_chat() -> None:
    print("Pi sensor agent — type a question, or 'quit' to exit.")
    while True:
        try:
            prompt = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if prompt.lower() in {"quit", "exit", "q"}:
            return
        if not prompt:
            continue
        agent(prompt)


if __name__ == "__main__":
    if "--chat" in sys.argv[1:]:
        run_chat()
    else:
        run_scenarios()
