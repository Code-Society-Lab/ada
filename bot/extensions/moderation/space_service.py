from matrix import Context, Room
from .errors import MaxDepthReachedError


def get_parent_space_id(ctx: Context) -> str | None:
    matrix_room = ctx.room.matrix_room
    parents: set[str] = matrix_room.parents

    return next(iter(parents), None)


async def collect_space_child_room_ids(
    ctx: Context,
    room: Room,
    seen: set[str] | None = None,
    depth: int = 0,
) -> list[str]:
    """Collect child room IDs from a Matrix space, including nested spaces."""
    if seen is None:
        seen = set()

    if depth > 3:
        raise MaxDepthReachedError(
            f"Recursion depth reached {depth} while processing room "
            f"'{room.display_name}' ({room.room_id})"
        )

    room_ids: list[str] = []

    for child_room_id in room.children:
        if child_room_id in seen:
            continue

        seen.add(child_room_id)

        child_room = ctx.bot.get_room(child_room_id)
        if child_room is None:
            continue

        if child_room.room_type == "m.space":
            space_children = await collect_space_child_room_ids(
                ctx,
                child_room,
                seen,
                depth + 1,
            )
            room_ids.extend(space_children)

        room_ids.append(child_room_id)

    return room_ids
