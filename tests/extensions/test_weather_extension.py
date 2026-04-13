from datetime import timedelta

from bot.extensions.weather_extension import (
    _city_time,
    _format_temperature,
    _format_visibility,
    _format_weather,
    _kelvin_to_celsius,
    _kelvin_to_fahrenheit,
    _looks_unresolved,
    _normalize_city_name,
)


def test_kelvin_to_celsius() -> None:
    assert round(_kelvin_to_celsius(273.15), 2) == 0


def test_kelvin_to_fahrenheit() -> None:
    assert round(_kelvin_to_fahrenheit(273.15), 2) == 32


def test_format_temperature() -> None:
    assert _format_temperature(273.15) == "32.00°F | 0.00°C"


def test_format_visibility_handles_missing_value() -> None:
    assert _format_visibility(None, "n/a") == "n/a"


def test_looks_unresolved_for_placeholder_values() -> None:
    assert _looks_unresolved("${ADA_OPENWEATHER_API_KEY|}") is True
    assert _looks_unresolved("$ADA_OPENWEATHER_API_KEY") is True
    assert _looks_unresolved("real-key") is False


def test_normalize_city_name_preserves_multiword_city() -> None:
    assert _normalize_city_name(("los", "angeles")) == "Los Angeles"


def test_city_time_uses_timezone_offset() -> None:
    utc_time = _city_time({"timezone": 0})
    offset_time = _city_time({"timezone": 3600})
    delta = offset_time - utc_time
    assert timedelta(minutes=59) < delta < timedelta(minutes=61)


def test_format_weather() -> None:
    message = _format_weather(
        "Paris",
        {
            "timezone": 7200,
            "visibility": 10000,
            "weather": [{"description": "clear sky", "icon": "01d"}],
            "main": {
                "temp": 293.15,
                "feels_like": 294.15,
                "humidity": 52,
                "pressure": 1014,
            },
        },
    )

    assert "### Weather for Paris" in message
    assert "**Description**: Clear Sky" in message
    assert "**Humidity**: 52%" in message
    assert "**Pressure**: 1014 hPa" in message
    assert "**Visibility**: 10,000m | 32,808ft" in message
