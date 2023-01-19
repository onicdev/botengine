import asyncio
import uvloop
from bson.objectid import ObjectId
from fastapi import Request, FastAPI
from .botengine import BotEngine

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def create_webhook_app(be: BotEngine):
    app = FastAPI()

    @app.post("/botengine/webhook/{instance_id}")
    async def webhook(instance_id: str, request: Request):
        request_json = await request.json()
        asyncio.get_event_loop().create_task(
            be.process_webhook(ObjectId(instance_id), request_json)
        )
        return "ok"

    return app
