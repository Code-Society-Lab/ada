import time
import logging

from matrix import Bot, Context, Room

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)

bot = Bot()


@bot.hook
async def on_ready():
    logger.info("Ada is up and running!")

    room: Room = bot.get_room("!cHidtNcSgVLvluxHYZ:matrix.org")
    await room.send("Hey, I'm back online!")


@bot.command("ping")
async def ping(ctx: Context) -> None:
    event_time = ctx.event.server_timestamp / 1000
    latency = round((time.time() - event_time) * 1000)

    await ctx.reply(f"Pong! {latency}ms")
