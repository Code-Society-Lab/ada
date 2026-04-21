from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any, NotRequired, TypedDict


class WeatherError(Enum):
    """List of possible errors when fetching weather data."""

    NOT_FOUND = "not_found"
    UNAVAILABLE = "unavailable"


class TimezonePayload(TypedDict):
    """TypedDict for payloads that include a timezone offset."""

    timezone: int


class WeatherPayload(TimezonePayload):
    """TypedDict for the weather fields used when formatting a forecast."""

    weather: list[dict[str, Any]]
    main: dict[str, Any]
    visibility: NotRequired[int]


def format_weather(city: str, data: WeatherPayload) -> str:
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


def _city_time(data: TimezonePayload) -> datetime:
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
