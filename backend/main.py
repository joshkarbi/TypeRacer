'''
main.py

Create a websocket server.
Listen for messages of types:
- New game request: {"type": "new_game"}
- Join game request: {"type": "join_game", "game_ID": 0}
- Game updates: {"type": "update", "game_ID": "", "player_ID":"", "word_num": 0}

Send back responses:

If we got a new game request:
    - New game creation: {"type": "new_game", "created": "success", "game_ID": "", "paragraph": ""}
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
import websockets
from collections import defaultdict 
import random

rooms = defaultdict(list) # map a game ID to a list of websocketss

async def register(websocket, game_ID):
    rooms[game_ID].append(websocket)

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
                if game_id not in rooms.keys():
                    response = {"error": "The provided game ID does not exist."}
                else:
                    # The game exists, add this websocket to that room.
                    await register(websocket, data.get("game_ID"))
                    response = {"type": "join_game", "game_ID": data.get("game_ID"), "paragraph": "", "player_IDs": []}
                print("Response: ", response)
                await websocket.send( json.dumps(response) )
    
    except Exception as e:
        await websocket.close()
        print("Caught exception", e)




if __name__=="__main__":
    print("Initializing TypeRacer WS Server!")

    start_server = websockets.serve(ws_connection_handle, "localhost", 6789)

    main_event_loop = asyncio.get_event_loop()

    main_event_loop.run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()