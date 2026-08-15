from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from bot.extensions.weather.openweather_service import WeatherError, fetch_weather
from bot.extensions.weather.weather_helper import (
    _city_time,
    _format_temperature,
    _format_visibility,
    format_weather,
    _kelvin_to_celsius,
    _kelvin_to_fahrenheit,
)

from bot.extensions.weather.weather_extension import _normalize_city_name


def test_kelvin_to_celsius() -> None:
    assert round(_kelvin_to_celsius(273.15), 2) == 0


def test_kelvin_to_fahrenheit() -> None:
    assert round(_kelvin_to_fahrenheit(273.15), 2) == 32


def test_format_temperature() -> None:
    assert _format_temperature(273.15) == "32.00°F | 0.00°C"


def test_format_visibility_handles_missing_value() -> None:
    assert _format_visibility(None, "n/a") == "n/a"


def test_normalize_city_name_preserves_multiword_city() -> None:
    assert _normalize_city_name(("los", "angeles")) == "Los Angeles"


def test_city_time_uses_timestamp() -> None:
    assert _city_time(0) == datetime.fromtimestamp(0, UTC)


def test_fetch_weather_normalizes_openweather_payload() -> None:
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {
        "dt": 1000,
        "timezone": 3600,
        "visibility": 10000,
        "weather": [{"description": "clear sky", "icon": "01d"}],
        "main": {
            "temp": 293.15,
            "feels_like": 294.15,
            "temp_min": 292.15,
            "temp_max": 295.15,
            "humidity": 52,
            "pressure": 1014,
        },
    }

    with patch(
        "bot.extensions.weather.openweather_service.requests.get",
        return_value=fake_response,
    ):
        result = fetch_weather("api-key", "Paris")

    assert not isinstance(result, WeatherError)
    assert result["timestamp"] == 4600
    assert result["visibility"] == 10000


def test_format_weather() -> None:
    message = format_weather(
        "Paris",
        {
            "timestamp": 0,
            "visibility": 10000,
            "weather": [{"description": "clear sky", "icon": "01d"}],
            "main": {
                "temp": 293.15,
                "feels_like": 294.15,
                "temp_min": 292.15,
                "temp_max": 295.15,
                "humidity": 52,
                "pressure": 1014,
            },
        },
    )

    lines = message.render()

    assert "<h2>Weather for Paris</h2>" in lines
    assert "<table>" in lines
    assert "<strong>Local time:</strong>" in lines
    assert "1970-01-01 00:00" in lines
    assert "<strong>Description:</strong>" in lines
    assert "Clear Sky" in lines
    assert "<strong>Temperature:</strong>" in lines
    assert "68.00°F | 20.00°C" in lines
    assert "<strong>- Min:</strong>" in lines
    assert "66.20°F | 19.00°C" in lines
    assert "<strong>- Max:</strong>" in lines
    assert "71.60°F | 22.00°C" in lines
    assert "<strong>Feels like:</strong>" in lines
    assert "69.80°F | 21.00°C" in lines
    assert "<strong>Humidity:</strong>" in lines
    assert "52%" in lines
    assert "<strong>Pressure:</strong>" in lines
    assert "1,014 hPa" in lines
    assert "<strong>Visibility:</strong>" in lines
    assert "10,000m | 32,808ft" in lines
