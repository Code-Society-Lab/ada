import pytest
import requests
from unittest.mock import patch, MagicMock

from bot.extensions.wikipedia_extension import (
    _format_results,
    _search_wikipedia,
)


def test_format_results_renders_header_and_lines() -> None:
    payload = ("py", ["Python"], [""], ["https://en.wikipedia.org/wiki/Python"])
    result = _format_results("py", payload)

    assert '#### Wikipedia results for "_py_"' in result
    assert "> **1.** [Python](<https://en.wikipedia.org/wiki/Python>)" in result


def test_format_results_raises_on_non_list_payload() -> None:
    with pytest.raises(ValueError, match="Unexpected response format"):
        _format_results("q", {})  # type: ignore[arg-type]


def test_format_results_raises_on_short_payload() -> None:
    with pytest.raises(ValueError, match="Unexpected response format"):
        _format_results("q", [])  # type: ignore[arg-type]


def test_format_results_raises_on_wrong_inner_types() -> None:
    with pytest.raises(ValueError, match="Unexpected response format"):
        _format_results("q", ["query", 2, [""], ["https://test.link"]])  # type: ignore[arg-type]


def test_format_results_raises_on_no_results() -> None:
    with pytest.raises(ValueError, match="No results found"):
        _format_results("q", ("query", [], [""], ["https://test.link"]))


def test_search_wikipedia_calls_api_with_correct_params() -> None:
    fake_payload = ["query", ["Title"], [""], ["https://test.link"]]

    fake_response = MagicMock()
    fake_response.json.return_value = fake_payload

    with patch(
        "bot.extensions.wikipedia_extension.requests.get", return_value=fake_response
    ) as mock_get:

        result = _search_wikipedia("test query")

        mock_get.assert_called_once_with(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "opensearch",
                "format": "json",
                "namespace": 0,
                "limit": 3,
                "search": "test query",
            },
            headers={
                "User-Agent": "AdaBot/1.0 (https://github.com/Code-Society-Lab/ada)"
            },
            timeout=5,
        )
        assert result == fake_payload


def test_search_wikipedia_raises_on_http_error() -> None:
    fake_response = MagicMock()
    fake_response.raise_for_status.side_effect = requests.HTTPError("error")

    with patch(
        "bot.extensions.wikipedia_extension.requests.get", return_value=fake_response
    ):
        with pytest.raises(requests.HTTPError, match="error"):
            _search_wikipedia("python")


@pytest.mark.parametrize(
    "exception",
    [
        requests.ConnectionError("connection failed"),
        requests.Timeout("request timed out"),
    ],
)
def test_search_wikipedia_raises_on_network_error(exception) -> None:
    with patch(
        "bot.extensions.wikipedia_extension.requests.get", side_effect=exception
    ):
        with pytest.raises(type(exception), match=str(exception)):
            _search_wikipedia("python")
