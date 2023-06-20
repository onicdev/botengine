import asyncio
import uvloop
from fastapi import Request, FastAPI
from .botengine import BotEngine

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def create_webhook_app(be: BotEngine, security_token: str):
    app = FastAPI()

    @app.post("/botengine/webhook/" + security_token)
    async def webhook(request: Request):
        request_json = await request.json()
        asyncio.get_event_loop().create_task(be.process_webhook(request_json))
        return "ok"

    return app
