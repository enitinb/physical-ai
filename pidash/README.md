# pidash

A tiny, dependency-free command-line dashboard for the Raspberry Pi.

Live, auto-refreshing terminal view of CPU, memory, disk, network, temperature
and load — built with Python's standard library only (no `pip install` needed).
Reads directly from `/proc` and `/sys`.

![works on Pi 5](https://img.shields.io/badge/Raspberry%20Pi-5-c51a4a)
![python](https://img.shields.io/badge/python-3.8%2B-blue)
![no deps](https://img.shields.io/badge/dependencies-none-brightgreen)

## What it shows

- **CPU** — overall + per-core usage bars, color-coded temperature, current
  clock frequency, 1/5/15-minute load average
- **MEM / SWP** — used / total with available memory
- **DISK** — usage for real filesystems (skips `tmpfs`, `proc`, etc.)
- **NET** — live download / upload rates per interface
- **Header** — Pi model, hostname, LAN IP, uptime

Refreshes once per second. Bars turn yellow → orange → red as values climb.

## Install

```bash
git clone https://github.com/<you>/pidash.git
cd pidash
install -m 755 pidash ~/.local/bin/pidash
```

Make sure `~/.local/bin` is on your `PATH` (it is by default on Raspberry Pi OS).

## Run

```bash
pidash
```

Quit with `Ctrl-C`.

## Requirements

- Linux with `/proc` and `/sys` (so: any Raspberry Pi, or any modern Linux box)
- Python 3.8+
- A real terminal (it refuses to run if stdout isn't a TTY)

Tested on Raspberry Pi 5 running Raspberry Pi OS (kernel 6.18).

## Why

`htop` is great but heavy and doesn't show Pi-specific bits like SoC
temperature or current clock frequency in one glance. `pidash` is a small
script you can read, understand, and tweak in an afternoon.

## License

MIT
