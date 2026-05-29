# strands_demo

A small set of [Strands Agents](https://strandsagents.com/) demos that build up
from a one-line "hello agent" to a multi-agent system that introspects the
Raspberry Pi it's running on.

All demos use Claude Sonnet 4.6 on Amazon Bedrock (`us.anthropic.claude-sonnet-4-6`
in `us-west-2`). You'll need AWS credentials with Bedrock access on the model.

## Setup

```bash
pip install strands-agents
export AWS_REGION=us-west-2   # plus your usual AWS credentials
```

The Pi telemetry demos (`pi_*.py`) are written for Raspberry Pi OS — they read
`/proc` directly and shell out to `vcgencmd`. They'll only return meaningful
data on an actual Pi.

## The demos, in order

### 1. `my_agent.py` — smallest possible agent

One-shot agent created with just a model ID. Asks a single question
("Tell me about Amazon Bedrock.") and prints the response. Useful as a
sanity check that Strands + Bedrock credentials are wired up.

```bash
python my_agent.py
```

### 2. `strands_demo.py` — agent with tools

Adds two trivial `@tool`-decorated Python functions (`add`, `word_length`) and
shows the agent picking the right tool per sub-question. Also switches from a
bare model ID to an explicit `BedrockModel` so you can see where temperature,
region, etc. get configured.

```bash
python strands_demo.py
```

### 3. `pi_telemetry_agent.py` — single agent, real tools

A single agent that answers questions about the Pi it's running on, using the
telemetry tools defined in `pi_tools.py` (device info, SoC temperature, CPU
load, memory, disk, uptime, throttling history).

The system prompt is tuned to be terse — it answers only what was asked,
calls the minimum tools needed, and only flags problems when relevant.

```bash
python pi_telemetry_agent.py           # run preset scenarios
python pi_telemetry_agent.py --chat    # interactive prompt
```

Preset scenarios cover individual checks (thermal, CPU, memory, disk,
uptime, throttling) plus one multi-tool "full health report" with a final
HEALTHY / WARNING / CRITICAL verdict.

### 4. `pi_multi_agent.py` — "Agents as Tools" pattern

Same telemetry, restructured as a three-specialist team behind an
orchestrator:

```
User → Orchestrator → { hardware_specialist, performance_specialist, capacity_specialist }
```

Each specialist owns a slice of the tools:

| Specialist                | Tools                                    |
| ------------------------- | ---------------------------------------- |
| `hardware_specialist`     | `pi_info`, `cpu_temperature`, `throttling_status` |
| `performance_specialist`  | `cpu_usage`, `memory_usage`              |
| `capacity_specialist`     | `disk_usage`, `uptime`                   |

The orchestrator exposes each specialist as a tool via `agent.as_tool(...)`
and routes the user's question to the smallest set of specialists that can
answer it (calling all three in parallel for broad health checks).

```bash
python pi_multi_agent.py           # run preset scenarios
python pi_multi_agent.py --chat    # interactive prompt
```

## Shared module

### `pi_tools.py`

Plain `@tool`-decorated functions that read Raspberry Pi telemetry from
`/proc` and `vcgencmd`. Imported by both `pi_telemetry_agent.py` and
`pi_multi_agent.py`:

- `pi_info` — model, hostname, kernel, OS
- `cpu_temperature` — SoC temperature in °C
- `cpu_usage` — CPU % busy plus 1/5/15-minute load averages
- `memory_usage` — total / used / available RAM
- `disk_usage` — disk stats for a given path (default `/`)
- `uptime` — seconds and pretty `Xd Yh Zm` form
- `throttling_status` — decoded `vcgencmd get_throttled` flags
