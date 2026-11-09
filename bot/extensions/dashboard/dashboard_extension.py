import logging
import time
from datetime import date, datetime, timedelta
from typing import cast
from zoneinfo import ZoneInfo

import dachshund
from aiohttp import ClientError
from matrix import Bot, Context, Extension, Room
from nio import ReactionEvent, RoomMemberEvent, RoomMessageText, WhoamiError

from bot.dashboard.latency import LatencyHealth
from bot.extensions.welcome.welcome_extension import _is_new_join

logger = logging.getLogger(__name__)
extension = Extension("dashboard")

TIMEZONE = ZoneInfo("America/New_York")
# Bar charts with a bar per date, which keep only the last DAILY_DAYS days.
DAILY_SOURCES = ("commands_per_day", "reactions_per_day")
DAILY_DAYS = 30
# Dates trimmed each run, so a week of downtime still gets cleaned up.
TRIM_SPAN = 7

SUMMARY = """
# Welcome!
### This dashboard contains various monitoring information about **Ada**, our Matrix bot!
Hopefully, you will find something useful here.

- [Website](https://codesociety.xyz)
- [Source](https://github.com/Code-Society-Lab/ada)
"""


@extension.on_load
def setup() -> None:
    dachshund.emit("summary", value=SUMMARY)
    _trim_daily_charts()


latency_health = LatencyHealth()


@extension.hook
async def on_ready() -> None:
    await latency_health.load()
    await _check_latency()
    _report_counts()


@extension.schedule("* * * * *")
async def report_counts() -> None:
    _report_counts()


@extension.schedule("* * * * *")
async def check_latency() -> None:
    await _check_latency()


@extension.schedule("5 0 * * *")
async def trim_daily_charts() -> None:
    _trim_daily_charts()


@extension.event
async def on_message(room: Room, event: RoomMessageText) -> None:
    _record_message(room, event)


@extension.event
async def on_react(_room: Room, event: ReactionEvent) -> None:
    _record_reaction(event.key)


@extension.event
async def on_member_join(_room: Room, event: RoomMemberEvent) -> None:
    if _is_new_join(event):
        _record_member_flow(joined=1, left=0)


@extension.event
async def on_member_leave(_room: Room, event: RoomMemberEvent) -> None:
    if _is_leave(event):
        _record_member_flow(joined=0, left=1)


@extension.hook
async def on_command(ctx: Context) -> None:
    if ctx.command:
        _record_command(ctx.command.name)


def _record_message(room: Room, event: RoomMessageText) -> None:
    latency_health.record_message(_latency_ms(event.server_timestamp))
    dachshund.emit(
        "message",
        date=_today(),
        author=event.sender,
        room=_room_name(room),
        value=1,
    )


def _record_reaction(emoji: str) -> None:
    dachshund.emit("reactions_per_day", date=_today(), value=1)
    dachshund.emit("reaction_emojis", emoji=emoji, value=1)


def _record_member_flow(*, joined: int, left: int) -> None:
    dachshund.emit("member_flow", joined=joined, left=left)
    _report_counts()


def _record_command(name: str) -> None:
    dachshund.emit("on_command", name=name, value=1)
    dachshund.emit("commands_per_day", date=_today(), value=1)


async def _check_latency() -> None:
    """Time a round trip to the homeserver, the bot's equivalent of a ping."""
    started = time.perf_counter()

    try:
        response = await cast(Bot, extension.bot).client.whoami()
    except (ClientError, TimeoutError) as error:
        logger.warning("Latency check failed: %s", error)
        return

    if isinstance(response, WhoamiError):
        logger.warning("Latency check failed: %s", response.message)
        return

    latency_health.record_check(round((time.perf_counter() - started) * 1000))


def _report_counts() -> None:
    rooms = cast(Bot, extension.bot).get_rooms()

    dachshund.emit("room_count", value=len(rooms))
    # Distinct users, so someone in several rooms counts once.
    members: set[str] = set().union(*(room.users for room in rooms))
    dachshund.emit("member_count", value=len(members))


def _trim_daily_charts(now: date | None = None) -> None:
    """Remove the bars older than DAILY_DAYS from the per-day charts."""
    now = now or date.fromisoformat(_today())

    for days_ago in range(DAILY_DAYS + 1, DAILY_DAYS + 1 + TRIM_SPAN):
        old = (now - timedelta(days=days_ago)).isoformat()

        for source in DAILY_SOURCES:
            dachshund.emit(source, date=old, _delete=True)


def _today() -> str:
    """Today's date, the day starting at midnight Eastern."""
    return datetime.now(TIMEZONE).date().isoformat()


def _latency_ms(server_timestamp: int) -> int:
    """Time between the homeserver receiving an event and Ada seeing it."""
    return max(0, round(time.time() * 1000 - server_timestamp))


def _room_name(room: Room) -> str:
    """A public room by name, any other as "private", so its name stays hidden."""
    if room.join_rule != "public":
        return "private"

    return room.display_name


def _is_leave(event: RoomMemberEvent) -> bool:
    return event.membership == "leave" and event.prev_membership == "join"
