import asyncio
import json
import sys
import uuid
from enum import Enum

import websockets.exceptions
import websockets.server


class MCWSClient:
    def start(self, host="0.0.0.0", port=19132):
        self._ws_base = websockets.server.serve(self.receive, host, port)
        self.loop.run_until_complete(self._ws_base)
        self.ws = self._ws_base.ws_server
        self.host = host
        self.port = port
        self.events = []
        self.loop = asyncio.get_event_loop()
        self.on_ready()
        self.loop.run_forever()

    def on_ready(self):
        # overwrite in subclassed file
        print(f"{self.host}:{self.port} ready!")

    def camel_to_snake(self, s):
        return "".join(["_" + c.lower() if c.isupper() else c for c in s]).lstrip("_")

    async def receive(self, websocket, path):
        self.ws = websocket
        await self.listen_to_events()
        await self.event("connect")  # self.on_connect()
        try:
            while True:
                data = await self.ws.recv()
                msg = json.loads(data)
                await self.parse_command(msg)
        except (
            websockets.exceptions.ConnectionClosedOK,
            websockets.exceptions.ConnectionClosedError,
            websockets.exceptions.ConnectionClosed,
        ):
            await self.event("disconnect")  # self.on_disconnect()
            sys.exit()

    async def listen_to_events(self):
        for event in self.events:
            if isinstance(event, Enum):
                event = event.value

            await self.ws.send(
                json.dumps(
                    {
                        "body": {"eventName": event},
                        "header": {
                            "requestId": "00000000-0000-0000-0000-000000000000",
                            "messagePurpose": "subscribe",
                            "version": 1,
                            "messageType": "commandRequest",
                        },
                    }
                )
            )

    async def parse_command(self, message):
        if message["header"]["messagePurpose"] == "event":
            event_name = self.camel_to_snake(message["body"]["eventName"])
            await self.event(event_name, message)
        elif message["header"]["messagePurpose"] == "error":
            await self.event("error", message)

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
        await self.ws.send(cmd_json)
        data = await self.ws.recv()
        msg = json.loads(data)
        if (
            msg["header"]["messagePurpose"] == "commandResponse"
            and msg["header"]["requestId"] == uuid4
        ):
            return msg
        else:
            return None

    async def event(self, name, *args):
        func = f"self.on_{name}"
        if args == ():
            try:
                await eval(f"{func}()")
            except NameError as e:
                print(f"on_{name}")
        else:
            try:
                await eval(f"{func}({args})")
            except NameError as e:
                print(f"on_{name}")
