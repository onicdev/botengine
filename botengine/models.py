from datetime import datetime
from bson.objectid import ObjectId
from pydantic import Field
from pymongo import IndexModel, ASCENDING
from pydango import Model, UndefinedConnection


class BaseBotTemplate(Model):
    data: dict = Field(default_factory=dict)
    update_dt: datetime
    create_dt: datetime

    class Meta:
        connection = UndefinedConnection()
        collection_name = "bot_template"


class BaseBotInstance(Model):
    token: str
    data: dict = Field(default_factory=dict)
    update_dt: datetime
    create_dt: datetime

    class Meta:
        connection = UndefinedConnection()
        collection_name = "bot_instances"


class BaseBotUser(Model):
    instance_id: ObjectId
    chat_id: int
    user_id: int
    first_name: str
    last_name: str = None
    username: str = None
    state: str = ""
    store: dict = Field(default_factory=dict)
    banned: bool
    update_dt: datetime
    create_dt: datetime

    class Meta:
        connection = UndefinedConnection()
        collection_name = "bot_users"
        indexes = [
            IndexModel([("instance_id", ASCENDING)], background=True),
            IndexModel(
                [("chat_id", ASCENDING), ("user_id", ASCENDING)],
                background=True,
                unique=True,
            ),
        ]
