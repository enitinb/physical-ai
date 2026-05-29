"""Physical AI Demo 2 — Multi-agent telemetry assistant for the Raspberry Pi.

Demonstrates the Strands "Agents as Tools" pattern: three specialist
agents each own a subset of the telemetry tools, and a top-level
orchestrator routes queries to the right specialist(s) and synthesizes
the final answer.

  ┌─────────────┐
  │  User       │
  └──────┬──────┘
         │
  ┌──────▼─────────────┐
  │  Orchestrator       │
  └──┬───────┬───────┬──┘
     │       │       │
  ┌──▼──┐ ┌──▼──┐ ┌──▼───┐
  │ HW  │ │Perf │ │Capacity│
  │Agent│ │Agent│ │ Agent  │
  └─────┘ └─────┘ └────────┘

Dependencies: Python standard library + ``strands-agents``.

Run modes:
- ``python pi_multi_agent.py``           runs the preset scenarios one by one.
- ``python pi_multi_agent.py --chat``    drops into an interactive prompt."""

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


# --- Specialist agents -------------------------------------------------------

SPECIALIST_RULES = (
    "Behavior:\n"
    "- Answer ONLY what was asked. Do not volunteer extra telemetry.\n"
    "- Call the minimum set of tools needed.\n"
    "- Reply in 1-2 short labeled lines (e.g. 'Temperature: 53.2 C, normal').\n"
    "- Plain text only. No emoji, no markdown headings, no preamble."
)

hardware_agent = Agent(
    model=bedrock_model,
    system_prompt=(
        "You are the Hardware Health specialist for a Raspberry Pi. Scope: "
        "device identity, SoC temperature, throttling/under-voltage events.\n\n"
        + SPECIALIST_RULES
    ),
    tools=[pi_info, cpu_temperature, throttling_status],
)

performance_agent = Agent(
    model=bedrock_model,
    system_prompt=(
        "You are the Performance specialist for a Raspberry Pi. Scope: "
        "live CPU utilization, load averages, memory pressure.\n\n"
        + SPECIALIST_RULES
    ),
    tools=[cpu_usage, memory_usage],
)

capacity_agent = Agent(
    model=bedrock_model,
    system_prompt=(
        "You are the Capacity specialist for a Raspberry Pi. Scope: "
        "filesystem usage and uptime since last boot.\n\n"
        + SPECIALIST_RULES
    ),
    tools=[disk_usage, uptime],
)


# --- Orchestrator ------------------------------------------------------------
# Each specialist is exposed to the orchestrator as a tool via `.as_tool()`,
# so the orchestrator can call them by name and receive their text response.

orchestrator = Agent(
    model=bedrock_model,
    system_prompt=(
        "You are the lead Raspberry Pi assistant. You coordinate three "
        "specialists:\n"
        "  - hardware_specialist: device identity, SoC temperature, throttling\n"
        "  - performance_specialist: CPU usage, memory pressure\n"
        "  - capacity_specialist: disk usage, uptime\n"
        "\n"
        "Routing:\n"
        "- Call the smallest set of specialists that can answer the question.\n"
        "- For broad health checks, call all three (in parallel when possible).\n"
        "- Never invent telemetry; always rely on the specialists.\n"
        "\n"
        "Response style:\n"
        "- Answer ONLY what the user asked. Do not volunteer extra information.\n"
        "- Keep it short: one sentence for a single fact, a few labeled lines for "
        "  multi-part questions, plus a final verdict line ONLY if the user asked "
        "  for one.\n"
        "- Plain text only. No emoji, no markdown headings, no preamble or recap."
    ),
    tools=[
        hardware_agent.as_tool(
            name="hardware_specialist",
            description=(
                "Ask the Hardware Health specialist about the Pi's identity, "
                "current SoC temperature, or throttling / under-voltage events. "
                "Input: a natural-language question."
            ),
        ),
        performance_agent.as_tool(
            name="performance_specialist",
            description=(
                "Ask the Performance specialist about live CPU utilization, "
                "load averages, or memory pressure. "
                "Input: a natural-language question."
            ),
        ),
        capacity_agent.as_tool(
            name="capacity_specialist",
            description=(
                "Ask the Capacity specialist about disk usage or how long the "
                "Pi has been up. "
                "Input: a natural-language question."
            ),
        ),
    ],
)


# --- Demo driver -------------------------------------------------------------

SCENARIOS = [
    (
        "Single specialist — thermal",
        "How hot is the Pi right now, and has it ever been throttled?",
    ),
    (
        "Single specialist — performance",
        "Is the Pi under any CPU or memory pressure at the moment?",
    ),
    (
        "Single specialist — capacity",
        "How full is the disk, and how long has the Pi been up?",
    ),
    (
        "Two specialists",
        "I want to run a heavier workload soon. Based on current temperature "
        "and current CPU/memory headroom, is now a good time?",
    ),
    (
        "All specialists — full report",
        "Give me a complete health report for this Pi covering hardware, "
        "performance, and capacity, and end with a single overall verdict: "
        "HEALTHY, WARNING, or CRITICAL, with one sentence on why.",
    ),
]


def run_scenarios() -> None:
    for i, (title, prompt) in enumerate(SCENARIOS, start=1):
        print(f"\n=== Scenario {i}/{len(SCENARIOS)}: {title} ===")
        print(f"User: {prompt}\n")
        orchestrator(prompt)


def run_chat() -> None:
    print("Pi multi-agent assistant — type a question, or 'quit' to exit.")
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
        orchestrator(prompt)


if __name__ == "__main__":
    if "--chat" in sys.argv[1:]:
        run_chat()
    else:
        run_scenarios()
