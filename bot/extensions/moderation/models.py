from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class KickResult:
    target_user_id: str
    reason: str
    scope: Literal["room", "space"]
    space_id: str | None
    kicked_room_ids: list[str]
