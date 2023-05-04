from datetime import datetime
from pydantic import Field
from pymongo import IndexModel, ASCENDING
from pydango import Model, UndefinedConnection


class BaseBotUser(Model):
    chat_id: int
    user_id: int
    first_name: str
    last_name: str = None
    username: str = None
    state: str = ""
    store: dict = Field(default_factory=dict)
    blocked: bool
    update_dt: datetime
    create_dt: datetime

    class Meta:
        connection = UndefinedConnection()
        collection_name = "bot_users"
        indexes = [
            IndexModel(
                [("chat_id", ASCENDING), ("user_id", ASCENDING)],
                background=True,
                unique=True,
            ),
        ]
