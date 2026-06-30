from matrix import Context
from matrix.errors import MatrixError

from .errors import SpaceNotFoundError
from .models import KickResult
from .space_service import (
    get_parent_space_id,
    collect_space_child_room_ids,
)


async def kick_from_context(
    ctx: Context,
    user_id: str,
    reason: str,
) -> KickResult:
    space_id = get_parent_space_id(ctx)

    kicked: list[str] = []
    failed: list[str] = []

    if space_id is None:
        current_room_id = ctx.room.room_id
        try:
            await ctx.room.kick_user(user_id, reason=reason)
            if current_room_id:
                kicked.append(current_room_id)
        except MatrixError:
            if current_room_id:
                failed.append(current_room_id)

        return KickResult(
            target_user_id=user_id,
            reason=reason,
            space_id=None,
            kicked_room_ids=kicked,
            failed_room_ids=failed,
        )

    space = ctx.bot.get_room(space_id)
    if space is None:
        raise SpaceNotFoundError(
            f"Could not find parent space in room cache: {space_id}"
        )

    room_ids: list[str] = await collect_space_child_room_ids(ctx, space)
    if space_id not in room_ids:
        room_ids.append(space_id)

    for room_id in room_ids:
        room = ctx.bot.get_room(room_id)
        if room is None:
            failed.append(room_id)
            continue

        try:
            await room.kick_user(user_id, reason=reason)
        except MatrixError:
            failed.append(room_id)
            continue
        else:
            kicked.append(room_id)

    return KickResult(
        target_user_id=user_id,
        reason=reason,
        space_id=space_id,
        kicked_room_ids=kicked,
        failed_room_ids=failed,
    )
