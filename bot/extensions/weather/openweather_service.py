import logging
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any, TypedDict

import requests
from matrix import Extension

logger = logging.getLogger(__name__)

OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


class WeatherError(Enum):
    """List of possible errors when fetching weather data."""

    NOT_FOUND = "not_found"
    UNAVAILABLE = "unavailable"


class WeatherPayload(TypedDict):
    """TypedDict for the expected structure of the weather API response."""

    weather: list[dict[str, Any]]
    main: dict[str, Any]
    timezone: int
    visibility: int


def _fetch_weather(
    city: str,
    api_key: str,
    session: requests.Session | None = None,
) -> WeatherPayload | WeatherError:
    """Retrieve weather information for the specified city."""

    client = session or requests

    try:
        response = client.get(
            OPENWEATHER_URL,
            params={"appid": api_key, "q": city},
            timeout=10,
        )

        if response.status_code == 404:
            return WeatherError.NOT_FOUND

        response.raise_for_status()
        return response.json()
    except requests.HTTPError as error:
        logger.warning("Weather API HTTP error for %r: %s", city, error)
    except (requests.ConnectionError, requests.Timeout) as error:
        logger.warning("Weather API connection error for %r: %s", city, error)

    return WeatherError.UNAVAILABLE


def _format_weather(city: str, data: WeatherPayload) -> str:
    current_time = _city_time(data).strftime("%Y-%m-%d %H:%M")
    weather = data["weather"][0]
    main = data["main"]
    visibility_m = data.get("visibility")
    visibility_ft = (
        f"{round(visibility_m * 3.280839895):,}ft"
        if isinstance(visibility_m, int | float)
        else "n/a"
    )

    description = weather["description"].title()
    temperature = _format_temperature(main["temp"])
    feels_like = _format_temperature(main["feels_like"])
    humidity = main["humidity"]
    pressure = main["pressure"]
    visibility = _format_visibility(visibility_m, visibility_ft)

    return (
        f"### Weather for {city}\n"
        "```\n"
        f"{'Local time:':<14} {current_time}\n"
        f"{'Description:':<14} {description}\n"
        f"{'Temperature:':<14} {temperature}\n"
        f"{'Feels like:':<14} {feels_like}\n"
        f"{'Humidity:':<14} {humidity}%\n"
        f"{'Pressure:':<14} {pressure:,} hPa\n"
        f"{'Visibility:':<14} {visibility}\n"
        "```"
    )


def _city_time(data: WeatherPayload) -> datetime:
    """Get the local time for the given city using the API timezone offset."""

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


def _normalize_city_name(city_parts: tuple[str, ...]) -> str:
    return " ".join(city_parts).title().strip()
