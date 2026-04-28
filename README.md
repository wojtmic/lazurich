# Lazurich
Infinitely hackable Minecraft launcher

## Features
- Instance-based management
- Symlink-based mod storage (only on Linux/macOS - preserves disk space and bandwith waste)
- Modern, intuitive Qt6 GUI
- Automated log analyzer
- Advanced dependency graph resolver
- Lightweight online instance exporting (small, single, sharable .json manifests)
- Optional CLI interface
- Cross-instance config sync
- ...and anything else via the Extension system!

## Installation
If you are on Arch Linux (or any Arch-based distro), get it from the AUR under `lazurich`. For anyone else, check [Flathub](https://linktoflathubafter.launch) or [releases](https://github.com/wojtmic/lazurich/linktoreleasesidontrememberit).<br>
**WARNING!** Lazurich is in a pre-release state. Expect bugs, crashes or slight unfinished behavior.

## System Requirements
Supported on all modern operating systems (Win 10+, Linux with 6.2+ kernel, macOS 14+ or anything that runs Python 3.14 and JVM 8-25). Lazurich is built to be cross-platform, however please note that **Linux support is prioritized**.

# Nerd Area
## Extensions
Extensions are small Python modules that can expand launcher functionality in any and all ways. The detailed guide on creating one is [here](https://linkto.docs)!

## Tech Stack
| Tech                | Version | Role                     |
|---------------------| ------- |--------------------------|
| Python              | 3.12 | Programming Language     |
| `uv` | 0.9.25 | Quick project management |
| `pyside6` (with QML) | 6.10.1 | GUI                      |
| `qasync`            | 0.28.0 | Simple async for Qt      |
| `httpx`             | 0.28.1 | Async networking         |
| `pytest`            | 9.0.2 | Unit testing             |
| `pytest-asyncio`    | 1.3.0 | Async tests              |
| `respx`             | 0.22.0 | Networking tests         |
| `loguru`            | 0.7.3 | Logging                  |

## Contributing
Feel something could be done better? The code is GPL-3.0 - feel free to open a PR! The detailed contributions are [here](https://github.com/wojtmic/lazurich/linktoCONTRIBUTINGmdfile).
