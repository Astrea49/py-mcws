import asyncio
import inspect
import json
import uuid
from enum import Enum
from typing import Any
from typing import Callable
from typing import TypeVar
from typing import Union

import websockets.exceptions
import websockets.server


FuncT = TypeVar("FuncT", bound=Callable[..., Any])


def listener(name_or_enum: Union[Enum, str]):
    def decorator(func: FuncT) -> FuncT:
        if isinstance(func, staticmethod):
            func = func.__func__
        if not inspect.iscoroutinefunction(func):
            raise TypeError("Listener function must be a coroutine function.")

        func.__mcws_listener__ = True
        func.__mcws_listener_name__ = (
            name_or_enum.value if isinstance(name_or_enum, Enum) else name_or_enum
        )
        return func

    return decorator


class MCWSClient:
    """A client for communicating between Minecraft and Python
    using WebSockets."""

    def __init__(self, host="0.0.0.0", port=8000) -> None:
        self.host = host
        self.port = port

        self._events = {}
        self._determine_events()

    async def start(self):
        """
        Starts up the client.
        Recommended if running it with another asynchronous task.
        """
        async with websockets.server.serve(self._receive, self.host, self.port):
            self.on_ready()
            await asyncio.Future()

    def run(self):
        """
        Handles running the client. This function is blocking.

        Its main usage is when a person desires to run a client by itself;
        for running it with another asynchronous task, consider `start()`.
        """
        # python is deprecating get_event_loop, so we have to make it ourselves
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

        self._ws_base = websockets.server.serve(self._receive, self.host, self.port)
        self._loop.run_until_complete(self._ws_base)
        self.on_ready()

        try:
            self._loop.run_forever()
        finally:
            self._loop.run_until_complete(self.close())

    async def close(self):
        """
        Closes the connection between the client and world, if any.
        It is recommended you run this if not using the `run()` helper method.
        """
        try:
            await self._ws.close()
        except AttributeError or websockets.exceptions.WebSocketException:
            pass

    def on_ready(self):
        """
        Runs whenever the client is ready to connect to a world/server.

        By default, the program prints that the host/port combination is
        ready, but this can be overwritten to have a different implementation.
        """
        print(f"{self.host}:{self.port} ready!")

    async def on_connect(self):
        """
        Runs whenever the client connects to a world/server.

        By default, the program prints that it has connected to the world,
        but this can be overwritten to have a different implementation.
        """
        print("Connected to world!")

    async def on_disconnect(self):
        """
        Runs whenever the client disconnects from a world/server.

        By default, the program prints that it has disconnected from the world,
        but this can be overwritten to have a different implementation.
        """
        print("Disconnected from world!")

    async def on_error(self, message):
        """
        Runs whenever the client receives an error from Minecraft.

        By default, the program prints the error, but this can be overwritten
        to have a different implementation.
        """
        print(f"Error occured: {message}")

    def _determine_events(self):
        functions = inspect.getmembers(self, predicate=inspect.ismethod)
        for _, func in functions:
            if getattr(func, "__mcws_listener__", False):
                self._events[func.__mcws_listener_name__] = func

    async def _receive(self, websocket: websockets.server.WebSocketServerProtocol):
        self._ws = websocket
        await self._listen_to_events()
        await self.on_connect()
        try:
            while True:
                data = await self._ws.recv()
                msg = json.loads(data)
                await self._parse_command(msg)
        except (
            websockets.exceptions.ConnectionClosedOK,
            websockets.exceptions.ConnectionClosedError,
            websockets.exceptions.ConnectionClosed,
        ):
            await self.on_disconnect()

    async def _listen_to_events(self):
        for event_name in self._events.keys():
            await self._ws.send(
                json.dumps(
                    {
                        "body": {"eventName": event_name},
                        "header": {
                            "requestId": "00000000-0000-0000-0000-000000000000",
                            "messagePurpose": "subscribe",
                            "version": 1,
                            "messageType": "commandRequest",
                        },
                    }
                )
            )

    async def _parse_command(self, message):
        if message["header"]["messagePurpose"] == "event":
            event_name = message["body"]["eventName"]
            await self._dispatch(event_name, message)
        elif message["header"]["messagePurpose"] == "error":
            await self.on_error(message)

    async def command(self, cmd):
        uuid4 = str(uuid.uuid4())
        cmd_json = json.dumps(
            {
                "body": {
                    "origin": {"type": "player"},
                    "commandLine": cmd,
                    "version": 1,
                },
                "header": {
                    "requestId": uuid4,
                    "messagePurpose": "commandRequest",
                    "version": 1,
                    "messageType": "commandRequest",
                },
            }
        )
        await self._ws.send(cmd_json)
        data = await self._ws.recv()
        msg = json.loads(data)
        if (
            msg["header"]["messagePurpose"] == "commandResponse"
            and msg["header"]["requestId"] == uuid4
        ):
            return msg
        else:
            return None

    async def _dispatch(self, name: str, message: dict):
        func = self._events.get(name)

        if func:
            await func(message)
