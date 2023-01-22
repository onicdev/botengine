import time
from datetime import datetime
from typing import Type, Callable
from bson.objectid import ObjectId
from telegram import Update, Bot
from .context import BaseContext
from .tree import EngineTree
from .models import BaseBotTemplate, BaseBotInstance, BaseBotUser


class BotEngine:
    __slots__ = (
        "context_cls",
        "tree",
        "_template_model",
        "_instance_model",
        "_user_model",
        "_template",
        "_polling_last_update_id",
    )

    def __init__(self, context_cls: Type[BaseContext]):
        self.context_cls = context_cls
        self.tree = EngineTree()
        self._template_model: Type[BaseBotTemplate] = self.context_cls.template_model
        self._instance_model: Type[BaseBotInstance] = self.context_cls.instance_model
        self._user_model: Type[BaseBotUser] = self.context_cls.user_model
        self._template: BaseBotTemplate = (
            self.context_cls.template_model.query_single_required()
        )

    async def start_polling(self, instance_id: ObjectId) -> None:
        print("Warning: use polling only for development purposes.")
        self._polling_last_update_id = 0
        instance = await self._instance_model.query_single_required_async(
            {"_id": instance_id}
        )
        bot = Bot(instance.token)
        async with bot:
            while True:
                updates = await bot.get_updates(
                    offset=self._polling_last_update_id, read_timeout=999
                )
                if len(updates) > 0:
                    for update in updates:
                        instance = (
                            await self._instance_model.query_single_required_async(
                                {"_id": instance_id}
                            )
                        )
                        handle_update = await self.get_instance_update_handler(
                            instance, bot
                        )
                        await handle_update(update)
                    self._polling_last_update_id = updates[-1].update_id + 1
                time.sleep(0.2)

    async def process_webhook(self, instance_id: ObjectId, update_raw: dict) -> None:
        instance: BaseBotInstance = (
            await self._instance_model.query_single_required_async({"_id": instance_id})
        )
        bot = Bot(instance.token)
        async with bot:
            update = Update.de_json(update_raw, bot)
            handle_update = await self.get_instance_update_handler(instance, bot)
            await handle_update(update)

    async def get_instance_update_handler(
        self, instance: type[BaseBotInstance], bot: Bot
    ) -> Callable[[Update, BaseContext], None]:
        async def handle_update(update: Update) -> None:
            user = self._user_model.query_single(
                {
                    "chat_id": update.effective_chat.id,
                    "user_id": update.effective_user.id,
                }
            )
            if user is None:
                user = await self._user_model(
                    instance_id=instance.id,
                    chat_id=update.effective_chat.id,
                    user_id=update.effective_user.id,
                    first_name=update.effective_user.first_name,
                    last_name=update.effective_user.last_name,
                    username=update.effective_user.username,
                    blocked=False,
                    update_dt=datetime.utcnow(),
                    create_dt=datetime.utcnow(),
                ).save_async()
            else:
                if user.blocked is True:
                    return

            context = self.context_cls()
            context.set_bot(bot)
            context.set_template(self._template)
            context.set_instance(instance)
            context.set_user(user)

            if user.state != "":
                context.state = user.state

            await self.tree.process(update, context)
            context.user.update(
                state=context.state,
                store=context.user.store,
                update_dt=datetime.utcnow(),
            )

        return handle_update
