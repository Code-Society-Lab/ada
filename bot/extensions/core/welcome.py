from matrix import Bot
from nio import MatrixRoom, RoomMemberEvent


def _is_new_join(event: RoomMemberEvent) -> bool:
    return event.membership == "join" and event.prev_membership != "join"


def _member_display_name(room: MatrixRoom, user_id: str) -> str:
    try:
        name = room.user_name(user_id)
    except Exception:
        name = None
    return name or user_id


def setup(bot: Bot) -> None:
    @bot.event(event_spec="on_member_join")
    async def welcome_new_member(room: MatrixRoom, event: RoomMemberEvent) -> None:
        if not _is_new_join(event):
            return

        # Ignore events for the bot itself.
        if event.state_key == bot.client.user:
            return

        member_name = _member_display_name(room, event.state_key)
        await bot.get_room(room.room_id).send(f"Welcome {member_name}! Glad to have you here.")
