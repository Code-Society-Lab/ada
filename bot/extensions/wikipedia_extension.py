import asyncio
from json import loads
from urllib.error import URLError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from matrix import Extension, Context


_RESULT_LIMIT = 3
_REQUEST_TIMEOUT = 5
_USER_AGENT = "Ada-Bot/0.1 (https://github.com/Code-Society-Lab/ada)"
_API_URL = (
    "https://en.wikipedia.org/w/api.php"
    "?action=opensearch&format=json&namespace=0"
    f"&limit={_RESULT_LIMIT}&search={{query}}"
)


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
        raise ValueError("Search query is too long. Please limit it to 300 characters or less.")
    payload = await asyncio.to_thread(_search_wikipedia, query)
    result_message = _format_results(query, payload)
    await ctx.reply(result_message)


@wiki.error(exception=URLError)
async def wiki_unreachable(ctx: Context, error: URLError) -> None:
    await ctx.reply("Sorry, I couldn't reach Wikipedia.")


@wiki.error(exception=ValueError)
async def wiki_invalid(ctx: Context, error: ValueError) -> None:
    await ctx.reply(str(error))


def _search_wikipedia(query: str) -> list:
    url = _API_URL.format(query=quote_plus(query))
    req = Request(url, headers={"User-Agent": _USER_AGENT})
    with urlopen(req, timeout=_REQUEST_TIMEOUT) as response:
        return loads(response.read())


def _format_results(query: str, payload: list) -> str:
    if (
        not isinstance(payload, list)
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
    header = f"#### Wikipedia results for \"_{query}_\""
    return f"{header}\n\n" + "\n".join(result_lines)
