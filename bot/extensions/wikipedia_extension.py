import asyncio
import requests
from matrix import Extension, Context

type WikiPayload = tuple[str, list[str], list[str], list[str]]

_RESULT_LIMIT = 3
_REQUEST_TIMEOUT = 5
_USER_AGENT = "AdaBot/1.0 (https://github.com/Code-Society-Lab/ada)"
_API_URL = "https://en.wikipedia.org/w/api.php"


extension = Extension("wikipedia")


@extension.command(
    usage="wiki <search query>",
    description="Search Wikipedia and display the top results.",
)
async def wiki(ctx: Context, *args: str) -> None:
    if not args:
        raise ValueError("Please provide a search query. Usage: !wiki <search query>")

    query = " ".join(args).strip()
    if len(query) > 300:
        raise ValueError(
            "Search query is too long. Please limit it to 300 characters or less."
        )
    payload = await asyncio.to_thread(_search_wikipedia, query)
    result_message = _format_results(query, payload)
    await ctx.reply(result_message)


@wiki.error(exception=requests.RequestException)
async def wiki_unreachable(ctx: Context, error: requests.RequestException) -> None:
    await ctx.reply("Sorry, something went wrong while contacting Wikipedia")


@wiki.error(exception=ValueError)
async def wiki_invalid(ctx: Context, error: ValueError) -> None:
    await ctx.reply(str(error))


def _search_wikipedia(query: str) -> WikiPayload:
    params: dict[str, str | int] = {
        "action": "opensearch",
        "format": "json",
        "namespace": 0,
        "limit": _RESULT_LIMIT,
        "search": query,
    }
    response = requests.get(
        _API_URL,
        params=params,
        headers={"User-Agent": _USER_AGENT},
        timeout=_REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def _format_results(query: str, payload: WikiPayload) -> str:
    if (
        not isinstance(payload, (list, tuple))
        or len(payload) < 4
        or not isinstance(payload[1], list)
        or not isinstance(payload[3], list)
    ):
        raise ValueError("Unexpected response format from Wikipedia API.")

    titles, urls = payload[1], payload[3]
    if not titles:
        raise ValueError(f"No results found for '{query}'.")

    result_lines = [
        f"> **{i}.** [{title}](<{url}>)"
        for i, (title, url) in enumerate(zip(titles, urls), start=1)
    ]
    header = f'#### Wikipedia results for "_{query}_"'
    return f"{header}\n\n" + "\n".join(result_lines)
