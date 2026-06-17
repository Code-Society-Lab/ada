from matrix import Context, Room


def get_parent_space_id(ctx: Context) -> str | None:
    matrix_room = ctx.room.matrix_room
    parents: set[str] = matrix_room.parents

    return next(iter(parents), None)


async def collect_space_child_room_ids(
    ctx: Context,
    room: Room,
    room_ids: list[str],
    seen: set[str],
    depth: int = 0,
) -> None:
    """Collect non-space child room IDs from a Matrix space."""
    if depth >= 10:
        return

    for child_room_id in room.children:
        if child_room_id in seen:
            continue

        seen.add(child_room_id)

        child_room = ctx.bot.get_room(child_room_id)
        if child_room is None:
            continue

        if child_room.room_type == "m.space":
            await collect_space_child_room_ids(
                ctx,
                child_room,
                room_ids,
                seen,
                depth + 1,
            )
            continue

        room_ids.append(child_room_id)
