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
    def event_ready(self):
        print(f"{self.host}:{self.port} ready!")

        # events to receive
        self.events = ["PlayerMessage", "PlayerDied"]
    
    async def event_connect(self):
        print("Connected!")

        # executing a command
        await self.command("say Hello")
    
    async def event_disconnect(self):
        print("Disconnected!")

    async def event_PlayerMessage(self, event):
        print(event)

    async def event_PlayerDied(self, event):
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

```python
self.events = ["PlayerMessage"]

async def event_PlayerMessage(self, event):
    print(event)
```

## Commands

```python
cmd = await self.command("say hello")
print(cmd)
```

## Scoreboards

```python
scoreboard = py_mcws.ScoreBoard("name"、"Display Name")
await scoreboard.show()
```
