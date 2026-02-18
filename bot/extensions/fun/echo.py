from matrix import Bot, Context


def setup(bot: Bot) -> None:
    @bot.command("echo")
    async def echo(ctx: Context) -> None:
        parts = ctx.body.split(maxsplit=1)
        if len(parts) < 2:
            await ctx.reply("Usage: echo <text>")
            return
        await ctx.reply(parts[1])
