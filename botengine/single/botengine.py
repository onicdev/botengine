import asyncio
import traceback
from datetime import datetime
from typing import Type, Callable
from telegram import Update, Bot
from .context import BaseContext
from ..tree import EngineTree
from .models import BaseBotUser


class BotEngine:
    __slots__ = (
        "context_cls",
        "tree",
        "_token",
        "_user_model",
        "_polling_last_update_id",
    )

    def __init__(self, token: str, context_cls: Type[BaseContext]):
        self._token = token
        self.context_cls = context_cls
        self.tree = EngineTree()
        self._user_model: Type[BaseBotUser] = self.context_cls.user_model

    async def start_polling(self) -> None:
        print("Warning: use polling only for development purposes.")
        self._polling_last_update_id = 0
        bot = Bot(self._token)
        async with bot:
            while True:
                updates = await bot.get_updates(
                    offset=self._polling_last_update_id, read_timeout=999
                )
                if len(updates) > 0:
                    self._polling_last_update_id = updates[-1].update_id + 1
                    for update in updates:
                        handle_update = await self.get_update_handler(bot)
                        try:
                            await handle_update(update)
                        except:  # pylint: disable=bare-except
                            print()
                            traceback.print_exc()
                            print()
                await asyncio.sleep(0.2)

    async def process_webhook(self, update_raw: dict) -> None:
        bot = Bot(self._token)
        async with bot:
            update = Update.de_json(update_raw, bot)
            handle_update = await self.get_update_handler(bot)
            await handle_update(update)

    async def get_update_handler(
        self, bot: Bot
    ) -> Callable[[Update, BaseContext], None]:
        async def handle_update(update: Update) -> None:
            user = self._user_model.find_one(
                {
                    "chat_id": update.effective_chat.id,
                    "user_id": update.effective_user.id,
                }
            )
            if user is None:
                user = await self._user_model.insert_one_async(
                    self._user_model(
                        chat_id=update.effective_chat.id,
                        user_id=update.effective_user.id,
                        first_name=update.effective_user.first_name,
                        last_name=update.effective_user.last_name,
                        username=update.effective_user.username,
                        banned=False,
                        update_dt=datetime.utcnow(),
                        create_dt=datetime.utcnow(),
                    )
                )
            else:
                if user.banned is True:
                    return

            context = self.context_cls()
            context.set_bot(bot)
            context.set_user(user)

            if user.state != "":
                context.state = user.state

            await self.tree.process(update, context)

            await self._user_model.update_one_async(
                {"_id": user.id},
                {
                    "state": context.state,
                    "update_dt": datetime.utcnow(),
                },
            )

        return handle_update
