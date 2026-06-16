from dataclasses import dataclass


@dataclass(frozen=True)
class KickResult:
    target_user_id: str
    reason: str
    space_id: str | None
    kicked_room_ids: list[str]
