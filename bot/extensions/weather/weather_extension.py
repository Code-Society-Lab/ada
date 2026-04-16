from matrix import Context, Extension
from .openweather_service import (
    WeatherError,
    _normalize_city_name,
    _fetch_weather,
    _format_weather,
)

extension = Extension("weather")


def _get_api_key() -> str | None:
    return extension.bot.config.get("api_key", section="extensions.weather")


@extension.check
async def has_api_key(_ctx: Context) -> bool:
    return _get_api_key() is not None


@extension.command(
    "weather", description="Show current weather information for a city."
)
async def weather(ctx: Context, *city: str) -> None:
    city_name = _normalize_city_name(city)

    api_key = _get_api_key()
    if not api_key:
        await ctx.reply("Weather is not configured.")
        return

    result = _fetch_weather(city_name, api_key)
    match result:
        case WeatherError.NOT_FOUND:
            await ctx.reply(f"Could not find weather data for {city_name}.")
        case WeatherError.UNAVAILABLE:
            await ctx.reply("Weather service is temporarily unavailable.")
        case _:
            await ctx.reply(_format_weather(city_name, result))
