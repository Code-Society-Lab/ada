# Ada Matrix Bot

The official [Matrix](https://matrix.org) bot of [Code Society](https://github.com/Code-Society-Lab),
built with [`Code-Society-Lab/matrixpy`](https://github.com/Code-Society-Lab/matrixpy).

## Quick Start

1. Create a virtualenv and install dependencies:

```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev]"
```

2. Create a `.env` file at the root of the project with your credentials:

```bash
   # Username + password
   ADA_USERNAME=@yourbot:matrix.org
   ADA_PASSWORD=your_password

   # Or username + token
   ADA_USERNAME=@yourbot:matrix.org
   ADA_TOKEN=your_token

   # Optional: extension API keys
   ADA_OPENWEATHER_API_KEY=your_openweather_api_key
```

3. Run the bot:

```bash
   ada start
```

By default it runs in `development` mode. To use a different environment:

```bash
   ada start --env production
```

Or point directly at a config file:

```bash
   ada start --config /path/to/config.yaml
```

If startup loops warnings like `'next_batch' is a required property`, your token is likely invalid or expired.
Regenerate `ADA_TOKEN` or switch to `ADA_PASSWORD` auth in your `.env`.

## Configuration

Config files live in `config/` and are selected by environment:

```
config/
  production.yaml
  development.yaml
  staging.yaml
```

Static values like `HOMESERVER` and `PREFIX` go in the YAML file. Secrets are never committed —
they live in a `.env` file and are referenced as environment variable placeholders:

```yaml
HOMESERVER: "https://matrix.org"
USERNAME: ${ADA_USERNAME}
PASSWORD: ${ADA_PASSWORD}
PREFIX: "!"
LOG_LEVEL: "INFO"
```

## Extensions

Extensions are self-contained modules that add commands and event handlers to the bot.
Each extension must define an `extension` attribute at the module level:

```python
from matrix import Extension, Context

extension = Extension("ping")


@extension.command()
async def ping(ctx: Context) -> None:
    await ctx.reply("Pong!")
```

Drop the file under `bot/extensions/` and it will be auto-discovered and loaded on startup — no registration needed.

### Rules

- The file must define an `extension` attribute, or the bot will raise a `RuntimeError` on startup.
- The extension name passed to `Extension()` should match the module's purpose.
- Each extension should stay focused on a single feature.

## Weather Extension

The `weather` extension reads its API key from `extensions.weather.api_key`,
which is already sets in `ADA_OPENWEATHER_API_KEY` in the configs.
