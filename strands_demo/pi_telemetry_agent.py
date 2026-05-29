"""Physical AI Demo 1 — a Strands agent that answers telemetry questions
about this Raspberry Pi using local system tools.

Dependencies: only the Python standard library + ``strands-agents``.
Tested on Raspberry Pi 5 / Raspberry Pi OS. ``vcgencmd`` ships with
Raspberry Pi OS by default; the other tools read ``/proc`` directly.

Run modes:
- ``python pi_telemetry_agent.py``           runs the preset scenarios one by one.
- ``python pi_telemetry_agent.py --chat``    drops into an interactive prompt."""

import sys

from strands import Agent
from strands.models import BedrockModel

from pi_tools import (
    cpu_temperature,
    cpu_usage,
    disk_usage,
    memory_usage,
    pi_info,
    throttling_status,
    uptime,
)

bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-6",
    region_name="us-west-2",
    temperature=0.3,
)

SYSTEM_PROMPT = (
    "You are an on-device assistant running on a Raspberry Pi.\n"
    "\n"
    "Behavior:\n"
    "- Answer ONLY what the user asked. Do not volunteer extra telemetry.\n"
    "- Call the minimum set of tools needed; skip tools the question doesn't require.\n"
    "- Keep answers short: 1-2 sentences for a single fact, a few labeled lines for "
    "  multi-part questions. No preamble, no recap of the question.\n"
    "- Use plain text only. No emoji, no markdown headings, no bullet decoration.\n"
    "- Only mention a problem (high temp, low memory, throttling, low disk) if the "
    "  user asked about health, or if a value is genuinely abnormal."
)

agent = Agent(
    model=bedrock_model,
    system_prompt=SYSTEM_PROMPT,
    tools=[
        pi_info,
        cpu_temperature,
        cpu_usage,
        memory_usage,
        disk_usage,
        uptime,
        throttling_status,
    ],
)


SCENARIOS = [
    ("Identify the device", "What Raspberry Pi am I running on, and what OS?"),
    ("Thermal check", "How hot is the SoC right now? Is that healthy?"),
    ("CPU load", "How busy is the CPU at the moment?"),
    ("Memory pressure", "How much RAM is in use vs. available?"),
    ("Storage", "How full is the root filesystem?"),
    ("Uptime", "How long has this Pi been running since the last boot?"),
    ("Throttling history", "Has this Pi ever been throttled or seen under-voltage?"),
    (
        "Full health report (multi-tool)",
        "Give me a complete health report for this Pi. Check the device "
        "identity, temperature, CPU load, memory, root disk, uptime, and "
        "throttling history, then end with a single overall verdict: "
        "HEALTHY, WARNING, or CRITICAL, and one sentence on why.",
    ),
]


def run_scenarios() -> None:
    for i, (title, prompt) in enumerate(SCENARIOS, start=1):
        print(f"\n=== Scenario {i}/{len(SCENARIOS)}: {title} ===")
        print(f"User: {prompt}\n")
        agent(prompt)


def run_chat() -> None:
    print("Pi telemetry agent — type a question, or 'quit' to exit.")
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
