from typing import TypeVar, Generic, Type
from telegram import Bot
from .models import BaseBotUser

UserModel = TypeVar("UserModel", bound=Type[BaseBotUser])


class BaseContext(Generic[UserModel]):

    __slots__ = (
        "_bot",
        "_user",
        "_state",
        "_is_output",
    )

    user_model: Type[UserModel]

    def __init__(self) -> None:
        self._bot = None
        self._user = None
        self._state = None
        self._is_output = False

    def set_bot(self, bot: Bot):
        if self._bot is not None:
            raise ValueError()
        self._bot = bot

    def set_user(self, user: UserModel):
        if self._user is not None:
            raise ValueError()
        self._user = user

    @property
    def bot(self) -> Bot:
        return self._bot

    @property
    def user(self) -> UserModel:
        return self._user

    @property
    def state(self) -> str:
        return self._state

    @state.setter
    def state(self, value: str):
        if not isinstance(value, str):
            raise ValueError()

        self._state = value

    @property
    def is_output(self) -> bool:
        return self._is_output

    @is_output.setter
    def is_output(self, value: bool):
        if not isinstance(value, bool):
            raise ValueError()

        self._is_output = value
