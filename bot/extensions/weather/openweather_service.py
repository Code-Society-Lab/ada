import logging

import requests
from .weather_helper import WeatherError, WeatherPayload

logger = logging.getLogger(__name__)

OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


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
        return response.json()
    except requests.HTTPError as error:
        logger.warning("Weather API HTTP error for %r: %s", city, error)
    except (requests.ConnectionError, requests.Timeout) as error:
        logger.warning("Weather API connection error for %r: %s", city, error)

    return WeatherError.UNAVAILABLE
