from typing import Callable, Union
from telegram import Update
from .context import BaseContext


class EngineTree:
    def __init__(self):
        self.router_funcs = []
        self.node_funcs = {}
        self.setup_func = None

    async def process(self, update: Update, context: BaseContext):
        if context.state is None:
            context.state = "start"
            context.is_output = True

        for router in self.router_funcs:
            routing_result = await router(update, context)
            if routing_result is not None:
                if not isinstance(routing_result, str):
                    raise ValueError()

                context.is_output = True
                context.state = routing_result

        await self.execute_node(update, context)

    async def run(self, tree_node_name: str, update: Update, context: BaseContext):
        context.state = tree_node_name
        context.is_output = True
        await self.execute_node(update, context)

    async def execute_node(self, update: Update, context: BaseContext):
        tree_node = self.node_funcs.get(context.state, None)
        if tree_node is not None:
            await tree_node(update, context)
        else:
            error_node = self.node_funcs.get("handle_error")
            await error_node(update, context)

    def node(
        self, func: Callable[[Update, BaseContext], None]
    ) -> Callable[[Update, BaseContext], None]:
        self.node_funcs[func.__name__] = func
        return func

    def router(
        self, func: Callable[[Update, BaseContext], Union[str, None]]
    ) -> Callable[[Update, BaseContext], Union[str, None]]:
        self.router_funcs.append(func)
        return func
