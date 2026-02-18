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
3. Run the bot:
   ```bash
   ada
   ```

If startup loops warnings like `'next_batch' is a required property`, your token is usually invalid/expired.
Regenerate `TOKEN` or switch to `PASSWORD` auth in `config/bot.yaml`.

## Extension Pattern

Each extension module exports:

```python
def setup(bot):
    ...
```

By default, the bot auto-discovers and loads every extension module under
`bot.extensions`.