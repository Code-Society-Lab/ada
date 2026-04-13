import json
from datetime import UTC, datetime, timedelta
from string import capwords
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from matrix import Context, Extension

extension = Extension("weather")

OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


@extension.command(
    "weather", description="Show current weather information for a city."
)
async def weather(ctx: Context, *city_parts: str) -> None:
    city_name = _normalize_city_name(city_parts)

    if not city_name:
        await ctx.reply("Usage: !weather <city>")
        return

    api_key = _get_api_key(ctx)
    if not api_key:
        await ctx.reply(
            "Weather is not configured. Set `extensions.weather.api_key` in config."
        )
        return

    result = _fetch_weather(city_name, api_key)
    if result == "not_found":
        await ctx.reply(f"Could not find weather data for {city_name}.")
        return
    if result == "unauthorized":
        await ctx.reply("Weather is misconfigured. Check `extensions.weather.api_key`.")
        return
    if result == "unavailable":
        await ctx.reply("Weather service is temporarily unavailable.")
        return

    await ctx.reply(_format_weather(city_name, result))


def _get_api_key(ctx: Context) -> str | None:
    for section in ("extensions.weather", "weather", "extensions"):
        try:
            value = ctx.bot.config.get("api_key", section=section)
        except Exception:
            continue

        if value and not _looks_unresolved(value):
            return value

    return None


def _fetch_weather(city: str, api_key: str) -> dict | str:
    """Retrieve weather information for the specified city."""

    query = urlencode({"appid": api_key, "q": city})
    url = f"{OPENWEATHER_URL}?{query}"

    try:
        with urlopen(url, timeout=10) as response:
            return json.load(response)
    except HTTPError as error:
        if error.code == 404:
            return "not_found"
        if error.code in (401, 403):
            return "unauthorized"
        return "unavailable"
    except URLError:
        return "unavailable"


def _format_weather(city: str, data: dict) -> str:
    current_time = _city_time(data).strftime("%Y-%m-%d %H:%M")
    weather = data["weather"][0]
    main = data["main"]
    visibility_m = data.get("visibility")
    visibility_ft = (
        f"{round(visibility_m * 3.280839895):,}ft"
        if isinstance(visibility_m, int | float)
        else "n/a"
    )

    return (
        f"### Weather for {city}\n"
        f"**Local time**: {current_time}\n"
        f"**Description**: {capwords(weather['description'])}\n"
        f"**Temperature**: {_format_temperature(main['temp'])}\n"
        f"**Feels like**: {_format_temperature(main['feels_like'])}\n"
        f"**Humidity**: {main['humidity']}%\n"
        f"**Pressure**: {main['pressure']} hPa\n"
        f"**Visibility**: {_format_visibility(visibility_m, visibility_ft)}\n"
    )


def _city_time(data: dict) -> datetime:
    """Get the timezone for the given city."""

    offset_seconds = int(data.get("timezone", 0))
    return datetime.now(UTC) + timedelta(seconds=offset_seconds)


def _format_visibility(visibility_m: int | float | None, visibility_ft: str) -> str:
    if visibility_m is None:
        return "n/a"

    return f"{visibility_m:,}m | {visibility_ft}"


def _format_temperature(kelvin: float) -> str:
    fahrenheit = _kelvin_to_fahrenheit(kelvin)
    celsius = _kelvin_to_celsius(kelvin)
    return f"{fahrenheit:.2f}°F | {celsius:.2f}°C"


def _kelvin_to_celsius(kelvin: float) -> float:
    return kelvin - 273.15


def _kelvin_to_fahrenheit(kelvin: float) -> float:
    return kelvin * 1.8 - 459.67


def _looks_unresolved(value: str) -> bool:
    return value.startswith("${") or value.startswith("$")


def _normalize_city_name(city_parts: tuple[str, ...]) -> str:
    return capwords(" ".join(city_parts).strip())
