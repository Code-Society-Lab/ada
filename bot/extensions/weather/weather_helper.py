from datetime import UTC, datetime
from matrix import Table
from .openweather_service import WeatherPayload


def format_weather(city: str, data: WeatherPayload) -> Table:
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

    table = Table(title=f"Weather for {city}")

    table.add_field("Local time:", current_time)
    table.add_field("Description:", description)
    table.add_field("Temperature:", temperature)
    table.add_field("Feels like:", feels_like)
    table.add_field("- Min:", temp_min)
    table.add_field("- Max:", temp_max)
    table.add_field("Humidity:", f"{humidity}%")
    table.add_field("Pressure:", f"{pressure:,} hPa")
    table.add_field("Visibility:", visibility)

    return table


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
