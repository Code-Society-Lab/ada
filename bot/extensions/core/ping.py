from matrix import Bot, Context


def setup(bot: Bot) -> None:
    @bot.command("ping")
    async def ping(ctx: Context) -> None:
        await ctx.reply("Pong!")
