from datetime import UTC, datetime
from .openweather_service import WeatherPayload


def format_weather(city: str, data: WeatherPayload) -> str:
    current_time = _city_time(data["timestamp"]).strftime("%Y-%m-%d %H:%M")
    weather = data["weather"][0]
    main = data["main"]

    visibility_m = data["visibility"]
    visibility_ft = (
        f"{round(visibility_m * 3.280839895):,}ft"
        if visibility_m is not None
        else "n/a"
    )

    description = weather["description"].title()

    temperature = _format_temperature(main["temp"])
    feels_like = _format_temperature(main["feels_like"])
    temp_min = _format_temperature(main["temp_min"])
    temp_max = _format_temperature(main["temp_max"])

    humidity = main["humidity"]
    pressure = main["pressure"]
    visibility = _format_visibility(visibility_m, visibility_ft)

    return (
        f"### Weather for {city}\n"
        f"<pre>"
        f"{'Local time:':<14} {current_time}\n"
        f"{'Description:':<14} {description}\n"
        f"{'Temperature:':<14} {temperature}\n"
        f"{'- Min:':<14} {temp_min}\n"
        f"{'- Max:':<14} {temp_max}\n"
        f"{'Feels like:':<14} {feels_like}\n"
        f"{'Humidity:':<14} {humidity}%\n"
        f"{'Pressure:':<14} {pressure:,} hPa\n"
        f"{'Visibility:':<14} {visibility}\n"
        f"</pre>"
    )


def _city_time(timestamp: int) -> datetime:
    """Get the local time for the city from a normalized timestamp."""

    return datetime.fromtimestamp(timestamp, UTC)


def _format_visibility(visibility_m: int | None, visibility_ft: str) -> str:
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
