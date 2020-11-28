'''
main.py

Create a websocket server.
Listen for messages of types:
- New game request: {"type": "new_game"}
- Game updates: {"type": "update", "game_ID": "", "player_ID":"", "word_num": ""}

Send back responses:
- New game creation: {"type": "new_game", "created": "success", "game_ID": ""}
- Game updates: {"type":"update", "game_ID": "", "status": "in_progress", "updates": [
                            {"player_ID": 0, "progress": 0.50},
                            {"player_ID": 1, "progress:: 0.66}
                        ]  
                }
- Game finished: {"type: "update", "game_ID": "", "status": "finished", "winner_ID": 0}
'''


if __name__=="__main__":
    print("Initializing TypeRacer WS Server!")