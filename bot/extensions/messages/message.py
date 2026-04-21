from sqlalchemy import BigInteger
from sqlmodel import Field
from sqlmodel_toolkit import Model


class Message(Model):
    id: int | None = Field(default=None, primary_key=True)
    content: str
    timestamp: int = Field(sa_type=BigInteger)
    sender: str
    event_id: str
    room_id: str
    is_command: bool

    @property
    def url(self) -> str:
        return f"https://matrix.to/#/{self.room_id}/{self.event_id}"
