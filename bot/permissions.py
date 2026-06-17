from matrix import Context


def _configured_moderators(ctx: Context) -> list[str]:
    moderators = ctx.bot.config.get(
        "moderators",
        section="bot",
        default=[],
    )

    if isinstance(moderators, str):
        return [
            moderator.strip()
            for moderator in moderators.split(",")
            if moderator.strip()
        ]

    return moderators


async def is_moderator(ctx: Context) -> bool:
    return ctx.sender in _configured_moderators(ctx)
