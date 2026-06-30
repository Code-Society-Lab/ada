from matrix import Context


async def is_moderator(ctx: Context) -> bool:
    power_levels = ctx.room.matrix_room.power_levels
    sender_level = power_levels.get_user_level(ctx.sender)

    return sender_level >= power_levels.defaults.kick
