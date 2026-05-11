import logging
import requests

from collections.abc import Mapping
from enum import Enum
from typing import cast
from typing import NotRequired, TypedDict

logger = logging.getLogger(__name__)

OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


class WeatherCondition(TypedDict):
    """OpenWeather condition fields used when formatting a forecast."""

    description: str
    icon: NotRequired[str]  # TODO: figure out how to render icons


class MainPayload(TypedDict):
    """OpenWeather temperature and atmosphere fields used by the formatter."""

    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    pressure: int
    humidity: int


class WeatherPayload(TypedDict):
    """TypedDict for the weather fields used when formatting a forecast."""

    weather: list[WeatherCondition]
    main: MainPayload
    visibility: int | None
    timestamp: int


class WeatherError(Enum):
    """List of possible errors when fetching weather data."""

    NOT_FOUND = "not_found"
    UNAVAILABLE = "unavailable"


def fetch_weather(
    api_key: str,
    city: str,
) -> WeatherPayload | WeatherError:
    """Retrieve weather information for the specified city."""

    try:
        response = requests.get(
            OPENWEATHER_URL,
            params={"appid": api_key, "q": city},
            timeout=10,
        )

        if response.status_code == 404:
            return WeatherError.NOT_FOUND

        response.raise_for_status()
        return _normalize_weather_payload(response.json())
    except requests.HTTPError as error:
        logger.warning("Weather API HTTP error for %r: %s", city, error)
    except (requests.ConnectionError, requests.Timeout) as error:
        logger.warning("Weather API connection error for %r: %s", city, error)
    except (KeyError, TypeError, ValueError) as error:
        logger.warning("Weather API payload error for %r: %s", city, error)

    return WeatherError.UNAVAILABLE


def _normalize_weather_payload(payload: object) -> WeatherPayload:
    raw_payload = cast(Mapping[str, object], payload)
    timezone = int(cast(int | str, raw_payload.get("timezone", 0)))
    raw_visibility = raw_payload.get("visibility")

    return {
        "weather": cast(list[WeatherCondition], raw_payload["weather"]),
        "main": cast(MainPayload, raw_payload["main"]),
        "visibility": (
            int(cast(int | str, raw_visibility)) if raw_visibility is not None else None
        ),
        "timestamp": int(cast(int | str, raw_payload["dt"])) + timezone,
    }
