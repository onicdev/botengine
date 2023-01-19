from typing import TypeVar, Generic, Type
from telegram import Bot
from .models import BaseBotTemplate, BaseBotInstance, BaseBotUser


TemplateModel = TypeVar("TemplateModel", bound=Type[BaseBotTemplate])
InstanceModel = TypeVar("InstanceModel", bound=Type[BaseBotInstance])
UserModel = TypeVar("UserModel", bound=Type[BaseBotUser])


class BaseContext(Generic[TemplateModel, InstanceModel, UserModel]):

    __slots__ = (
        "_bot",
        "_template",
        "_instance",
        "_user",
        "_state",
        "_is_output",
    )

    template_model: Type[TemplateModel]
    instance_model: Type[InstanceModel]
    user_model: Type[UserModel]

    def __init__(self) -> None:
        self._bot = None
        self._template = None
        self._instance = None
        self._user = None
        self._state = None
        self._is_output = False

    def set_bot(self, bot: Bot):
        if self._bot is not None:
            raise ValueError()
        self._bot = bot

    def set_template(self, template: TemplateModel):
        if self._template is not None:
            raise ValueError()
        self._template = template

    def set_instance(self, instance: InstanceModel):
        if self._instance is not None:
            raise ValueError()
        self._instance = instance

    def set_user(self, user: UserModel):
        if self._user is not None:
            raise ValueError()
        self._user = user

    @property
    def bot(self) -> Bot:
        return self._bot

    @property
    def template(self) -> TemplateModel:
        return self._template

    @property
    def instance(self) -> InstanceModel:
        return self._instance

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
