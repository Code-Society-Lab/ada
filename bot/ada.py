import logging
import time
from datetime import timedelta

from matrix import Bot, Context, Room, __version__ as matrix_version
from matrix.errors import CommandError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)

bot = Bot()


@bot.hook
async def on_ready():
    logger.info("Ada is up and running!")

    if main_channel_id := bot.config.get("main_room", section="bot"):
        room: Room = bot.get_room(main_channel_id)
        await room.send("Hey, I'm back online!")


@bot.hook
async def on_command_error(ctx: Context, error: CommandError) -> None:
    await ctx.reply(f"{error} Run '!help' for help on commands")


@bot.command()
async def ping(ctx: Context) -> None:
    await ctx.reply(f"Pong! {_get_latency(ctx)}ms")


@bot.command()
async def status(ctx: Context) -> None:
    human_readable_uptime = str(timedelta(seconds=int(time.time() - bot.start_at)))
    latency = _get_latency(ctx)
    extensions = ", ".join(bot.extensions.keys())
    extension_count = len(bot.extensions)
    room_count = len(bot.client.rooms)

    await ctx.reply(f"""
    *“I am in a charming state of confusion.”* - Ada Lovelace
    ──────────────────────
    **Uptime**     {human_readable_uptime}
    **Latency**    {latency}ms
    **Extensions** {extensions} ({extension_count}) 
    **Rooms**      {room_count}
    **matrix.py**  {matrix_version}
    ──────────────────────
    """.strip())


def _get_latency(ctx: Context) -> float:
    event_time = ctx.event.server_timestamp / 1000
    return round((time.time() - event_time) * 1000)
