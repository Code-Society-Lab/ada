from matrix import Context
from matrix.errors import MatrixError


def get_response_attr(obj, name: str, default=None):
    """Handle both dict-style and object-style response items."""
    if isinstance(obj, dict):
        return obj.get(name, default)

    return getattr(obj, name, default)


def get_parent_space_id(ctx: Context) -> str | None:
    matrix_room = getattr(ctx.room, "_matrix_room", None)

    if matrix_room is None:
        return None

    parents: set[str] = getattr(matrix_room, "parents", set()) or set()

    if not parents:
        return None

    return next(iter(parents), None)


async def get_space_child_room_ids(ctx: Context, space_id: str) -> list[str]:
    """Get non-space child rooms from a Matrix space."""
    client = ctx.bot.client

    room_ids: list[str] = []
    seen: set[str] = set()
    next_batch = None

    while True:
        response = await client.space_get_hierarchy(
            space_id=space_id,
            from_page=next_batch,
            max_depth=10,
            suggested_only=False,
        )

        if not hasattr(response, "rooms"):
            raise MatrixError(f"Could not read space hierarchy: {response}")

        for item in response.rooms:
            room_id = get_response_attr(item, "room_id")
            room_type = get_response_attr(item, "room_type", "")

            if not room_id:
                continue

            if room_type == "m.space":
                continue

            if room_id not in seen:
                seen.add(room_id)
                room_ids.append(room_id)

        next_batch = getattr(response, "next_batch", None)

        if not next_batch:
            break

    return room_ids
