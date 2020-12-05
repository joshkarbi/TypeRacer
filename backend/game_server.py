'''
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
    - Join game successful: {"type": "join_game", "game_ID": "", "paragraph": "", "player_IDs": ["", "", ""] }
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

import asyncio, json, traceback
import websockets, random
from collections import defaultdict 
from typing import Dict, List, Any
from multiprocessing import Process, Queue, Event
from threading import Thread
from game import Game
from multiprocessing import Process, Queue
from enum import Enum
from uuid import uuid4

class PlayerStatus(Enum):
    JOINED=0
    READY=1
    QUIT=2

class GameServer:
    def __init__(self):
        self.game_ids = []
        self.rooms = defaultdict(list) # map a game ID to a list of websockets


        self.send_queues = {} # Map game ID to a sending multiprocessing Queue
        self.recv_queues = {} # Map a game ID to a sending multiprocessing Queue
        self.game_objs = {} # Map a game ID to a Game instance
        self.player_states = defaultdict(dict) # Map game ID -> player ID ->  [
                            #     {"player_ID": 0, "progress": 0.50},
                            #     {"player_ID": 1, "progress": 0.66}
                            # ]  
        self.game_player_percentages = defaultdict(list) # map a game ID to list of id to percentage done

    async def __register(self, ws, game_ID: str):
        self.rooms[game_ID].append(ws)

    async def handle_new_game(self, ws, message: Dict[Any, Any]):
        # Generate a unique string ID
        new_game_ID = str(uuid4())
        while new_game_ID in self.game_ids:
            new_game_ID = str(uuid4())
        self.game_ids.append(new_game_ID)

        # Fork process to run the game
        this_game_sending = Queue()
        this_game_recving = Queue()

        this_game = Game(this_game_sending, this_game_recving)
        self.send_queues[new_game_ID] = this_game_sending
        self.recv_queues[new_game_ID] = this_game_recving
        self.game_objs[new_game_ID] = this_game

        # We set the target of a process to call the run (start the game)
        p = Process(target=this_game.run)
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
                players = list(range(joined["player_ID"] + 1) )
                this_players_ID = players[-1]

                response = {"type": "join_game", "game_ID": game_ID, "paragraph": joined["paragraph"], "player_ID": this_players_ID, "all_player_IDs": players}     
                self.player_states[game_ID][this_players_ID] = PlayerStatus.JOINED
                await self.send_to_all_in_game(game_ID, response)

    async def handle_get_games(self, ws, message: Dict[Any, Any]):
        # Check for any games that have timed out (i.e. no messaged in past 5 minutes)
        for id in self.game_ids:
            if self.recv_queues[id].empty() == False and self.recv_queues[id].get()=="Done":
                # Remove those
                self.__handle_finished_game(id)
                print("Removed ", id)
        
        # Send back all active games
        response = {"type": "get_games", "games": self.game_ids}
        return json.dumps(response)

    async def send_to_all_in_game(self, game_ID: str, message: Any):
        for ws in self.rooms[game_ID]:
            try:
                await ws.send(json.dumps(message))
            except websockets.WebSocketException as e:
                self.rooms[game_ID].remove(ws)

    async def handle_player_status(self, message: Dict[Any, Any]):
        response = {"error": "Not sure how to handle message.", "message": message}

        # If all players ready, send countdown start to all websockets in this game ID
        # {"type": "player_status", "game_ID": "", player_ID": "", "status", "ready"}
        game_ID = message.get("game_ID")
        if message.get("status") == "ready":
            self.player_states[game_ID][message.get("player_ID")] = PlayerStatus.READY
        
        if all(self.player_states[game_ID][x]==PlayerStatus.READY for x in self.player_states[game_ID].keys()):
            print("All players are ready in game ID", game_ID, "!")

            # Tell players starting in 3 seconds
            message = {"type": "game_status", "game_ID": game_ID,"status": "countdown", "time_length_seconds": 3}
            await self.send_to_all_in_game(game_ID, message)
            
            await asyncio.sleep(3)

            # Send game has started
            message = {"type": "game_status", "game_ID": game_ID, "status": "started"}
            await self.send_to_all_in_game(game_ID, message)
            for x in self.player_states[game_ID].keys():
                self.game_player_percentages[game_ID].append ({"player_ID": x, "progress": 0.0})

    def __handle_finished_game(self, game_ID):
        self.game_ids.remove(game_ID)
        self.send_queues.pop(game_ID)
        self.recv_queues.pop(game_ID)
        self.game_objs.pop(game_ID)
        self.player_states.pop(game_ID)
        self.game_player_percentages.pop(game_ID) # map a game ID to list of id to percentage done

    async def handle_game_update(self,  message: Dict[Any, Any]):
        response = {"error": "Not sure how to handle message.", "message": message}
        print(message)
        # Expect: {"type": "update", "game_ID": "", "player_ID":"", "word_num": 0}
        game_ID = message.get("game_ID")
        if game_ID not in self.game_objs.keys():
            # do nothing for now
            pass
        else:
            # The game exists.
            # Send the update to the game process
            self.send_queues[game_ID].put(message)
            seen_response = False
            while seen_response==False:
                seen_response = True
                response = self.recv_queues[game_ID].get()
                print(response)

                # response looks like {"player_ID": playerID, "progress": percentComplete}
                for player in range(len(self.game_player_percentages[game_ID])):
                    if self.game_player_percentages[game_ID][player].get("player_ID") == response.get("player_ID"):
                        self.game_player_percentages[game_ID][player]["progress"] = response.get("progress")

                if response.get("progress") == 100.0:
                    # The game is done!
                    await self.send_to_all_in_game(game_ID, {"type": "update", "game_ID": game_ID, "status": "finished", "winner_ID": response.get("player_ID")})
                    self.__handle_finished_game(game_ID)
                    print("Remaining games: ", self.game_ids)
                else:
                    await self.send_to_all_in_game(game_ID,{"type":"update", "game_ID": game_ID, "status": "in_progress", "updates": self.game_player_percentages[game_ID] })

    def shutdown(self):
        # Kill all processing
        for key in self.game_objs.keys():
            self.send_queues.get(key).put({"type": "kill_game"})