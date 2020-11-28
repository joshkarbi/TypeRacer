'''
main.py

Create a websocket server.
Listen for messages of types:
- New game request: {"type": "new_game"}
- Join game request: {"type": "join_game", "game_ID": 0}
- Game updates: {"type": "update", "game_ID": "", "player_ID":"", "word_num": ""}

Send back responses:

If we got a new game request:
    - New game creation: {"type": "new_game", "created": "success", "game_ID": "", "paragraph": ""}
If we got a join game request:
    - Join game successful: {"type": "join_game", "game_ID": "", "paragraph": "" }
If we got a game update:
    - Game updates: {"type":"update", "game_ID": "", "status": "in_progress", "updates": [
                                {"player_ID": 0, "progress": 0.50},
                                {"player_ID": 1, "progress:: 0.66}
                            ]  
                    }
    - Game finished: {"type: "update", "game_ID": "", "status": "finished", "winner_ID": 0}
'''


if __name__=="__main__":
    print("Initializing TypeRacer WS Server!")