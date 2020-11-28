'''
main.py

Create a websocket server.
Listen for messages of types:
- New game request: {"type": "new_game"}
- List games request: {"type": "get_games"}
- Join game request: {"type": "join_game", "game_ID": 0}
- Game updates: {"type": "update", "game_ID": "", "player_ID":"", "word_num": 0}

Send back responses:

If we got a new game request:
    - New game creation: {"type": "new_game", "created": "success", "game_ID": "", "paragraph": ""}
If we got a list games request: 
    - Send back list {"type": "get_games": "games": ["ID-1", "ID-2", "ID-3", ... ]}
If we got a join game request:
    - Join game successful: {"type": "join_game", "game_ID": "", "paragraph": "", "player_IDs": ["", "", ""] }
If we got a game update:
    - Game updates: {"type":"update", "game_ID": "", "status": "in_progress", "updates": [
                                {"player_ID": 0, "progress": 0.50},
                                {"player_ID": 1, "progress": 0.66}
                            ]  
                    }
    - Game finished: {"type: "update", "game_ID": "", "status": "finished", "winner_ID": 0}
'''

import asyncio, json, traceback
import websockets, random
from collections import defaultdict 
from typing import Dict, List, Any
from multiprocessing import Process, Queue, Event
from threading import Thread

class GameServerState:
    def __init__(self):
        self.rooms = defaultdict(List[websockets.WebSocketCommonProtocol]) # map a game ID to a list of websockets
        self.responses = Dict[str, Queue] # Map a game ID to a multiprocessing.Queue used to stream responses back from the game processor

state = GameServerState()

async def register(websocket, game_ID: str):
    state.rooms[game_ID].append(websocket)

async def ws_connection_handle(websocket, path):    
    try:
        await websocket.send(json.dumps({"type": "connected"}) )
        async for message in websocket:
            data = json.loads(message)
            if data.get("type") == "new_game":
                # new_game_ID = str(random.randint(123456789, 987654321))
                new_game_ID = str(random.randint(1, 5)) # For testing

                await register(websocket, new_game_ID)

                # Fork process to run the game

                response = {"type": "new_game", "created": "success", "game_ID": str(new_game_ID), "paragraph": ""}
                await websocket.send(json.dumps(response) )

            elif data.get("type") == "join_game":
                game_id = data.get("game_ID")
                if game_id not in state.rooms.keys():
                    response = {"error": "The provided game ID does not exist."}
                else:
                    # The game exists, add this websocket to that room.
                    await register(websocket, data.get("game_ID"))
                    response = {"type": "join_game", "game_ID": data.get("game_ID"), "paragraph": "", "player_IDs": []}
                print("Response: ", response)
                await websocket.send( json.dumps(response) )
    
    except websockets.exceptions.ConnectionClosed as e:
        print("Connection closed. Code", e.code, " reason", e.reason)
    except Exception as e:
        await websocket.close()
        print("Caught exception", e)


def ws_handle(loop):
    loop.run_forever()

if __name__=="__main__":
    with open("config.json") as config_file:
        config = json.load(config_file)
        print("Initializing TypeRacer WS Server!")

        # Create a thread to handle the WS server and its async event loop
        flag = Event()


        main_event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(main_event_loop)
        start_server = websockets.serve(ws_connection_handle, host=config["host"], port=config["port"], origins=config["origins"] if len(config["origins"])>0 else None)
        
        main_event_loop.run_until_complete(start_server)

        ws_handler_thread = Thread(target=ws_handle, args=[main_event_loop])
        ws_handler_thread.start()
        
        input("Enter anything to kill the server...\n")

        print("Closing down server . . . ")
        main_event_loop.stop()