from matrix import Context

from .models import KickResult
from .space_service import get_parent_space_id, get_space_child_room_ids


async def kick_from_context(
    ctx: Context,
    user_id: str,
    reason: str,
) -> KickResult:
    space_id = get_parent_space_id(ctx)

    if space_id is None:
        await ctx.room.kick_user(user_id, reason=reason)

        room_id = getattr(ctx.room, "room_id", None) or getattr(ctx.room, "id", None)

        return KickResult(
            target_user_id=user_id,
            reason=reason,
            space_id=None,
            kicked_room_ids=[room_id] if room_id else [],
        )

    room_ids = await get_space_child_room_ids(ctx, space_id)

    kicked: list[str] = []

    for room_id in room_ids:
        response = await ctx.bot.client.room_kick(
            room_id=room_id,
            user_id=user_id,
            reason=reason,
        )

        if response:
            kicked.append(room_id)

    return KickResult(
        target_user_id=user_id,
        reason=reason,
        space_id=space_id,
        kicked_room_ids=kicked,
    )
