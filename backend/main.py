'''
main.py

Create a websocket server.
Listen for messages of types:
- New game request: {"type": "new_game"}
- List games request: {"type": "get_games"}
- Join game request: {"type": "join_game", "game_ID": 0}
- Player ready status update: {"type": "player_status", "game_ID": "", player_ID": "", "status", "ready"}
- Game updates: {"type": "update", "game_ID": "", "player_ID":"", "word_num": 0}

Send back responses:

If we got a new game request:
    - New game creation: {"type": "new_game", "created": "success", "game_ID": "", "paragraph": ""}
If we got a list games request: 
    - Send back list {"type": "get_games": "games": ["ID-1", "ID-2", "ID-3", ... ]}
If we got a join game request:
    - Join game successful (will send to all players in the game): {"type": "join_game", "game_ID": "", "paragraph": "", "player_IDs": ["", "", ""] }
When starting the game:
    - All players are ready: {"type": "game_status", "game_ID": "","status": "countdown", "time_length_seconds": 3}
    - Game started: {"type": "game_status", "game_ID": "","status": "started"}
If we got a game update:
    - Game updates: {"type":"update", "game_ID": "", "status": "in_progress", "updates": [
                                {"player_ID": 0, "progress": 0.50},
                                {"player_ID": 1, "progress": 0.66}
                            ]  
                    }
    - Game finished: {"type: "update", "game_ID": "", "status": "finished", "winner_ID": 0}
'''

import asyncio, json, traceback, sys
import websockets, random
from collections import defaultdict 
from typing import Dict, List, Any
from multiprocessing import Process, Queue, Event
from threading import Thread
from game_server import GameServer


game_server = GameServer()

async def ws_connection_handle(websocket, path):    
    try:
        await websocket.send(json.dumps({"type": "connected"}) )
        async for message in websocket:
            try:
                data = json.loads(message)
                if data.get("type") == "new_game":
                    await websocket.send( await game_server.handle_new_game(websocket, data) )

                elif data.get("type") == "join_game":
                    await game_server.handle_join_game(websocket, data)

                elif data.get("type") == "get_games":
                    await websocket.send( await game_server.handle_get_games(websocket, data) )

                elif data.get("type") == "update":
                    await game_server.handle_game_update(data)

                elif data.get("type") == "player_status":
                    await game_server.handle_player_status(data)
                
                elif data.get("type") == "disconnect":
                    await websocket.send(json.dumps({"message": "Closing your connection."}))
                    await websocket.close()
                    await game_server.handle_disconnect(websocket)

            except json.JSONDecodeError as e:
                print("Failed to parse JSON from client:", message)
                await websocket.send(json.dumps({"error": "Invalid JSON."}))
        
            except websockets.exceptions.ConnectionClosed as e:
                print("Connection closed. Code", e.code, " reason", e.reason)
    
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback, limit=10, file=sys.stdout)
    
        print("Caught exception", e)

async def echo_server(stop, config):
    async with websockets.serve(ws_connection_handle, host=config["host"], port=config["port"], origins=config["origins"] if len(config["origins"])>0 else None):
        pass


import signal
def ws_handle():
    input("Enter anything to kill server...")
    signal.alarm(3)
    print("Exiting in 3 seconds . . .")


if __name__=="__main__":
    with open("config.json") as config_file:
        config = json.load(config_file)

        async def echo_server(stop):
            async with websockets.serve(ws_connection_handle, host=config["host"], port=config["port"], origins=config["origins"] if len(config["origins"])>0 else None):
                await stop

        loop = asyncio.get_event_loop()

        # The stop condition is set when receiving SIGALRM signal.
        stop = loop.create_future()
        loop.add_signal_handler(signal.SIGALRM, stop.set_result, None)

        # Run the server until user enters some stdin input.
        print("Initializing TypeRacer WS Server!")

        # Thread that listens for user stdin and generates the alarm signal.
        listener_thread = Thread(target=ws_handle)
        listener_thread.start()

        loop.run_until_complete(echo_server(stop))

        game_server.shutdown()
        listener_thread.join()