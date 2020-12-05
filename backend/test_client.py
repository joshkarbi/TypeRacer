import asyncio
import websockets, json, time, sys

async def hello():
    uri = "ws://localhost:6789"
    async with websockets.connect(uri) as websocket:
        
        connected = await websocket.recv()
        print(connected)

        if len(sys.argv) > 1:
            game_ID = sys.argv[1]
        else:

            create_game = {"type": "new_game"}
            await websocket.send(json.dumps(create_game) )

            game_response = json.loads(await websocket.recv())
            print(game_response)
            game_ID = game_response["game_ID"]
        join_game = {"type": "join_game", "game_ID": game_ID}
        await websocket.send(json.dumps(join_game))
        
        response = json.loads(await websocket.recv())
        print(response)
        PLAYER_ID = response["player_ID"]
        player_ready = {"type":"player_status", "status": "ready", "game_ID": game_ID, "player_ID": PLAYER_ID}
        await websocket.send(json.dumps(player_ready))

        # Countdown
        response = json.loads(await websocket.recv())
        print(response)

        # Game has started
        response = json.loads(await websocket.recv())
        print(response)
        
        # Play the game
        for word in range(len(game_response["paragraph"].split(" "))):
            typed = {"type": "update", "game_ID": game_ID, "player_ID": PLAYER_ID, "word_num": word+1}
            await websocket.send(json.dumps(typed))
            print("Typed: ", typed["word_num"], "out of", len(game_response["paragraph"].split(" ")))
            time.sleep(0.2)


        # Did we get the game over message?
        while True:
            response = json.loads(await websocket.recv())
            print(response)
        
asyncio.get_event_loop().run_until_complete(hello())