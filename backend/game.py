import json, random
from multiprocessing import Queue

class Game:

    def __init__(self,qRecv, qSend):
        # Set initial variables
        self.isGameDone = False
        self.winPlayerID = -1
        self.playerIDCount = -1

        # Set the queue object used to receive messages from server parent
        self.qRecv = qRecv

        # Set the queue object used to send messages from server parent
        self.qSend = qSend

        # Generate random paragraph
        with open('paragraph_bank.json') as paragraph_bank_file:
            paraBank = json.load(paragraph_bank_file)
            randIndex = random.randint(0,len(paraBank)-1)

            # Store paragraph to this object
            self.paragraph = paraBank[randIndex]

        # Store length of paragraph to this object
        self.paragraphLength = len(self.paragraph.split())
        

    def updatePlayerProgress(self, playerID, wordsCompleted):
        # Calculate % of paragraph player has completed
        percentComplete = 100*(wordsCompleted/self.paragraphLength)

        # Round to nearest integer
        percentComplete = round(percentComplete)

        # If the player has completed the paragraph, they win.
        if percentComplete == 100:
            self.isGameDone = True
            self.winPlayerID = playerID
        
        # Return the progress
        return {"player_ID": playerID, "progress": percentComplete}


    def run(self):
        # Continuous loop until the game finishes
        while not self.isGameDone:

            # Recieve message from server parent
            message = self.qRecv.get()

            # Execute joinGame() if that is the message type
            if message.get("type") == "join_game":
                self.qSend.put(self.joinGame())

            # Break this while loop if kill game is requested
            elif message.get("type") == "kill_game":
                self.isGameDone = True

            # Otherwise assume the message is a player's progress update
            else:
                playerID = message.get("player_ID")
                wordCount = message.get("word_num")
                playerProgress = self.updatePlayerProgress(playerID, wordCount)
                self.qSend.put(playerProgress)

    # Return a new player id and the game's paragraph
    def joinGame(self):
        self.playerIDCount += 1
        return {"player_ID": self.playerIDCount, "paragraph": self.paragraph}