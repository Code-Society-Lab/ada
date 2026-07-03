from matrix import Context, Space, Room
from matrix.errors import MatrixError

from .models import KickResult
from .space_service import get_parent_space


async def kick_from_rooms(
    user_id: str,
    rooms: list[Room],
    *,
    reason: str | None = None,
    space: Space | None = None,
) -> KickResult:
    kicked: list[str] = []
    failed: list[str] = []
    seen: set[str] = set()

    for room in rooms:
        if room.room_id in seen:
            continue
        seen.add(room.room_id)

        try:
            members = await room.get_members()
            if user_id not in members:
                # this will skip rooms where the user is not a member
                continue

            await room.kick_user(user_id, reason=reason)

            members_after = await room.get_members()
            if user_id in members_after:
                # if the user is still in the room after the kick,
                # we consider it a failure (should not happen)
                failed.append(room.room_id)
            else:
                kicked.append(room.room_id)

        except MatrixError:
            failed.append(room.room_id)

    return KickResult(
        target_user_id=user_id,
        reason=reason,
        space_id=space.room_id if space else None,
        kicked_room_ids=kicked,
        failed_room_ids=failed,
    )


async def kick_from_context(
    ctx: Context,
    user_id: str,
    reason: str | None = None,
) -> KickResult:
    space: Space | None = get_parent_space(ctx)

    if space:
        children = space.get_children(depth=3)
        children.append(space)

        return await kick_from_rooms(
            user_id,
            children,
            reason=reason,
            space=space,
        )

    return await kick_from_rooms(user_id, [ctx.room], reason=reason)
