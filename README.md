# Ada Matrix Bot

Scaffold for a Matrix bot inspired by the structure of
[`Code-Society-Lab/grace`](https://github.com/Code-Society-Lab/grace),
implemented with [`Code-Society-Lab/matrixpy`](https://github.com/Code-Society-Lab/matrixpy).

## Quick Start

1. Create a virtualenv and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev]"
   ```
2. Set Matrix credentials in `config/bot.yaml` (set exactly one of `PASSWORD` or `TOKEN`).
3. Optionally copy `.env.example` to `.env` for path and override settings.
4. Run the bot:
   ```bash
   ada
   ```
5. Or:
   ```bash
   python -m bot
   ```

If token auth is configured, startup performs a `whoami` preflight and fails fast with a clear error if the token is invalid.

## Project Layout

```
.
├── bot/
│   ├── bot.py                  # Bot runtime class (AdaBot)
│   ├── app.py                  # App bootstrap and runtime
│   ├── loader.py               # Extension loader (`setup(bot)`)
│   ├── settings.py             # YAML-first config + optional env overrides
│   ├── logging_setup.py        # Logging from config/logging.yaml
│   ├── extensions/
│   │   ├── core/
│   │   │   ├── ping.py
│   │   │   └── help.py
│   │   └── fun/
│   │       └── echo.py
│   └── services/
├── config/                     # bot.yaml + logging.yaml
├── db/                         # Placeholder for persistence and migrations
├── docs/
└── tests/
```

## Extension Pattern

Each extension module exports:

```python
def setup(bot):
    ...
```

The loader imports extension modules listed in `BOT_EXTENSIONS` and calls `setup(bot)`.

By default this scaffold reads `APP.EXTENSIONS` and `APP.LOG_LEVEL` from `config/bot.yaml`.
If neither `BOT_EXTENSIONS` nor `APP.EXTENSIONS` is set, extensions are auto-discovered
from `BOT_EXTENSIONS_PACKAGE` (defaults to `bot.extensions`).
Environment variables override YAML values when set.
