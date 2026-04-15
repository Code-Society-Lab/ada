from sqlmodel import Field
from sqlmodel_toolkit import Model


class Message(Model):
    id: int | None = Field(default=None, primary_key=True)
    content: str
    timestamp: str
    sender: str
    event_id: str
    is_command: bool
