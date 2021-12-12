# py-mcws
A (fork of a) library for connecting Minecraft and Python.

---

## Installation

```sh
pip install git+https://github.com/Astrea49/py-mcws.git
```

## Example

```python
import py_mcws

class MyMCWSClient(py_mcws.MCWSClient):
    def on_ready(self):
        print(f"{self.host}:{self.port} ready!")

    async def on_connect(self):
        print("Connected to world!")

        # executing a command
        await self.command("say Hello")

    async def on_disconnect(self):
        print("Disconnected from world!")

    @py_mcws.listener(py_mcws.Events.PLAYER_MESSAGE)
    async def on_player_message(self, event):
        print(event)

    @py_mcws.listener(py_mcws.Events.PLAYER_DIED)
    async def on_player_died(self, event):
        print(event)

client = MyMCWSClient(host="localhost", port=8000)
client.run()
```

## Connecting

Join a world (singleplayer or on a BDS, including Realms) as an Operator and type:

```cmd
/connect host:port
```

### Note

By default, Windows 10 and 11 prevents UWP applications from accessing a loopback connection with "localhost"
(i.e. network resources running on the same machine). If you are running a WebSocket client on your machine
and also testing said client on the same machine in a local world, the protection will kick in and you will
be unable to connect to the client.

To fix this, you will need to enable UWP loopback for Minecraft. Open `Command Prompt` as administrator and run:

```cmd
CheckNetIsolation.exe LoopbackExempt –a –p=S-1-15-2-1958404141-86561845-1752920682-3514627264-368642714-62675701-733520436
```

See [Microsoft's documentation](https://docs.microsoft.com/en-us/windows/iot-core/develop-your-app/loopback) for
more information.

## Events

[List of Events](https://gist.github.com/jocopa3/5f718f4198f1ea91a37e3a9da468675c#file-mcpe-w10-event-names)

Notes:
* The `@py_mcws.listener(event)` decorator must be used to decorate all functions corresponding with an event
in-game. However, the function decorated can be named whatever you desire.
* The library provides an enum of all of the current events for you. However, if you so desire, or if the event
is not in the enum, you may use the raw, camel-case string.

```python
@py_mcws.listener(py_mcws.Events.PLAYER_MESSAGE)
async def on_player_message(self, event):
    print(event)
```

## Commands

```python
cmd = await self.command("say hello")
print(cmd)
```
