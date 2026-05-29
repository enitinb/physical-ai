# strands_demo

A small set of [Strands Agents](https://strandsagents.com/) demos that build up
from a one-line "hello agent" to a multi-agent system that introspects the
Raspberry Pi it's running on.

**Purpose.** These samples are a learning aid for running Strands Agents — and
agentic patterns more generally — on a Raspberry Pi or comparable edge
hardware. They walk through the core building blocks (agent + model, agent +
tools, single agent over real device telemetry, multi-agent orchestration)
on a device small enough to sit on a desk, so you can see end-to-end how an
on-device agent observes its host and coordinates with peers.

All demos use Claude Sonnet 4.6 on Amazon Bedrock (`us.anthropic.claude-sonnet-4-6`
in `us-west-2`). You'll need AWS credentials with Bedrock access on the model.

> **⚠️ Demo code, not production.** These scripts are intended for learning
> and local experimentation on a personal Raspberry Pi. Review the
> [Security notes](#security-notes) section before running them on a shared
> device or exposing the chat interface beyond your own terminal.

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

**Tools:** none — the model answers from its own knowledge.

```bash
python my_agent.py
```

### 2. `strands_demo.py` — agent with tools

Adds two trivial `@tool`-decorated Python functions and shows the agent
picking the right tool per sub-question. Also switches from a bare model ID
to an explicit `BedrockModel` so you can see where temperature, region, etc.
get configured.

**Tools:**

| Tool          | What it does                              |
| ------------- | ----------------------------------------- |
| `add`         | Returns the sum of two numbers.           |
| `word_length` | Returns the character count of a string.  |

```bash
python strands_demo.py
```

### 3. `pi_telemetry_agent.py` — single agent, real tools

A single agent that answers questions about the Pi it's running on, using
the telemetry tools defined in `pi_tools.py`. The system prompt is tuned to
be terse — it answers only what was asked, calls the minimum tools needed,
and only flags problems when relevant.

**Tools** (all from `pi_tools.py`):

| Tool                | What it does                                                       |
| ------------------- | ------------------------------------------------------------------ |
| `pi_info`           | Pi model, hostname, kernel version, OS pretty name.                |
| `cpu_temperature`   | Current SoC temperature in °C (via `vcgencmd measure_temp`).       |
| `cpu_usage`         | CPU % busy over a 0.5 s sample + 1/5/15-minute load averages.      |
| `memory_usage`      | Total / used / available RAM in MB and used %.                     |
| `disk_usage`        | Total / used / free GB for the filesystem containing a given path. |
| `uptime`            | Seconds since boot plus a pretty `Xd Yh Zm` form.                  |
| `throttling_status` | Decoded `vcgencmd get_throttled` flags (under-voltage, capping…).  |

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

Each specialist owns a slice of the tools (all defined in `pi_tools.py`):

| Specialist                | Tools                                                              | Scope                              |
| ------------------------- | ------------------------------------------------------------------ | ---------------------------------- |
| `hardware_specialist`     | `pi_info`, `cpu_temperature`, `throttling_status`                  | Device identity, thermals, throttling. |
| `performance_specialist`  | `cpu_usage`, `memory_usage`                                        | Live CPU/memory pressure.          |
| `capacity_specialist`     | `disk_usage`, `uptime`                                             | Storage and time since boot.       |

The orchestrator itself has **no telemetry tools** — its only "tools" are
the three specialists exposed via `agent.as_tool(...)`. It routes the user's
question to the smallest set of specialists that can answer it (calling all
three in parallel for broad health checks).

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

## Security notes

These demos are written for clarity, not for hardening. Read this before
running them outside your own machine.

**What the code does and doesn't do**

- All telemetry tools are **read-only**: they read from `/proc`, `/etc/os-release`,
  and `/proc/device-tree/model`, or shell out to `vcgencmd` for thermals and
  throttling state. Nothing in `pi_tools.py` writes to disk, modifies system
  state, or makes network calls.
- `subprocess` is invoked with **list arguments and no `shell=True`**, so the
  internal calls aren't exposed to shell injection.
- The only tool that takes a model-controlled argument is `disk_usage(path)`,
  and it only passes that path to `shutil.disk_usage` to read stats — it does
  not read the file's contents.
- Outbound network: only the Bedrock model invocation via `strands-agents`.

**Demo-only caveats — do not skip**

- **No authentication on `--chat`.** Anyone who can run the script can drive
  the agent and consume your Bedrock quota and inference budget under your
  account. Do not expose this over a network, a shared shell, or a public
  notebook.
- **Telemetry is identifying information.** `pi_info` exposes the hostname,
  kernel, and OS version. Fine for your own Pi; consider it before pasting
  output into a public chat or screenshot.
- **Prompt-injection surface.** A chat user (or any text the model reads) can
  try to steer which tools get called. Impact here is bounded because every
  tool is read-only telemetry — there is no shell, file write, or arbitrary
  command tool — but if you extend `pi_tools.py` with anything destructive
  (rebooting, killing processes, editing files, calling APIs), you must add
  your own confirmation / allow-list logic. Don't blindly hand the agent a
  shell tool.
- **AWS credentials.** The demos use your ambient AWS credentials. Don't
  commit `~/.aws/credentials`, `.env` files, or anything else with keys.
- **No rate limiting or usage controls.** The chat loop invokes Bedrock on
  every prompt; there is no per-session cap, throttling, or budget guard.
  Monitor your account's usage and set Bedrock quotas / AWS Budgets alerts
  if you plan to leave it running.

**If you adapt this for anything beyond a personal demo**

- Put the chat behind auth (even basic SSH-only access counts).
- Move from list-of-tools to an explicit allow-list per role, and never give
  an agent a tool more powerful than the user invoking it is allowed to run.
- Treat any text the agent reads (chat input, file contents, web pages) as
  untrusted and assume it may try prompt injection.
- Log tool calls and their arguments so you can audit what the agent did.
