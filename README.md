# py-mcws
A package for connecting Minecraft and Python.

---

## Installation

```sh
pip install py-mcws
```

## Example

```python
import py_mcws

class MyWsClient(py_mcws.WsClient):
    def on_ready(self):
        print(f"{self.host}:{self.port} ready!")

        # events to receive
        self.events = ["PlayerMessage", "PlayerDied"]

    async def on_connect(self):
        print("Connected!")

        # executing a command
        await self.command("say Hello")

    async def on_disconnect(self):
        print("Disconnected!")

    async def on_player_message(self, event):
        print(event)

    async def on_player_died(self, event):
        print(event)

MyWsClient().start(host="0.0.0.0", port=19132)
```

## Connecting

Join a world (singleplayer or on a BDS, including Realms) as an Operator and type:

```cmd
/connect host:port
```

## Events

[List of Events](https://gist.github.com/jocopa3/5f718f4198f1ea91a37e3a9da468675c#file-mcpe-w10-event-names)
Note that function names use the `snake_case` version of the event names, unlike the `CamelCase` used
everywhere else (including on the list). This is to be more consistent with the typical Python naming style.

```python
self.events = ["PlayerMessage"]

async def event_player_message(self, event):
    print(event)
```

## Commands

```python
cmd = await self.command("say hello")
print(cmd)
```
