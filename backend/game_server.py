'''
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
from game import Game
from multiprocessing import Process, Queue

class GameServer:
    def __init__(self):
        self.jobs = []
        self.rooms = defaultdict(list) # map a game ID to a list of websockets
        self.responses = {} # Map a game ID to a multiprocessing.Queue used to stream responses back from the game processor


        self.send_queues = {} # Map game ID to a sending multiprocessing Queue
        self.recv_queues = {} # Map a game ID to a sending multiprocessing Queue
        self.game_objs = {} # Map a game ID to a Game instance

    async def __register(self, ws, game_ID: str):
        self.rooms[game_ID].append(ws)

    async def handle_new_game(self, ws, message: Dict[Any, Any]):
        # TODO: Generate a unique string ID
        new_game_ID = str(random.randint(1, 5)) # For testing

        await self.__register(ws, new_game_ID)

        # Fork process to run the game

        this_game_sending = Queue()
        this_game_recving = Queue()

        this_game = Game(this_game_sending, this_game_recving)
        self.send_queues[new_game_ID] = this_game_sending
        self.recv_queues[new_game_ID] = this_game_recving
        self.game_objs[new_game_ID] = this_game

        # We set the target of a process to call the run (start the game)
        p = Process(target=this_game.run)
        self.jobs.append(p)
        p.start()
            
        response = json.dumps({"type": "new_game", "created": "success", "game_ID": str(new_game_ID), "paragraph": this_game.paragraph})
        return response

    async def handle_join_game(self, ws, message: Dict[Any, Any]):
        game_ID = message.get("game_ID")
        if game_ID not in self.game_objs.keys():
            response = {"error": "The provided game ID does not exist."}
        else:
            # The game exists, add this websocket to that room.
            await self.__register(ws, game_ID)

            # Send a join game message to the game process
            self.send_queues[game_ID].put(message)
            seen_response = False
            while seen_response==False:
                seen_response = True
                joined = self.recv_queues[message.get("game_ID")].get()
                response = {"type": "join_game", "game_ID": game_ID, "paragraph": joined["paragraph"], "player_IDs": list(range(joined["player_ID"] + 1)  )}       
                return json.dumps(response)

    async def handle_get_games(self, ws, message: Dict[Any, Any]):
        response = {"type": "get_games", "games": list(self.rooms.keys())}
        return json.dumps(response)

    async def handle_game_update(self, ws, message: Dict[Any, Any]):
        response = {"error": "Not sure how to handle message.", "message": message}
        return json.dumps(response)

    def shutdown(self):
        # Kill all processing
        for key in self.game_objs.keys():
            self.send_queues.get(key).put({"type": "kill_game"})