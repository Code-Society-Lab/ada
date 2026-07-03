from matrix import Context, Space


def get_parent_space(ctx: Context) -> Space | None:
    parent_ids: set[str] = ctx.room.matrix_room.parents
    parent_id = next(iter(parent_ids), None)

    if not parent_id:
        return None

    return ctx.bot.get_space(parent_id)
