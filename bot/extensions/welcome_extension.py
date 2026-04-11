from nio import RoomMemberEvent, Event
from matrix import Extension, Context, Room

extension = Extension("welcome")


@extension.event
async def on_member_join(room: Room, event: RoomMemberEvent) -> None:
    if not _is_new_join(event):
        return

    await _welcome(room, event.state_key)


@extension.command("welcome")
async def welcome(ctx: Context) -> None:
    await _welcome(ctx.room, ctx.sender)


def _is_new_join(event: RoomMemberEvent) -> bool:
    return event.membership == "join" and event.prev_membership != "join"


def _member_display_name(room: Room, user_id: str) -> str:
    name = room.user_name(user_id)
    return name or user_id


async def _welcome(room: Room, user_id: str) -> None:
    member_name = _member_display_name(room, user_id)
    await room.send(f"Welcome {member_name}! Glad to have you here.")
