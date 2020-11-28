import json, random
from multiprocessing import Queue



class Game:
    #queue, multiprocessing.queue obj #two - one I recieve from, one i send back
    #queue.receive

    def __init__(self,qRecv, qSend):
        self.isGameDone = False
        self.winPlayerID = -1
        self.playerIDCount = -1

        #set the queue object used to receive messages from server parent
        self.qRecv = qRecv

        #set the queue object used to send messages from server parent
        self.qSend = qSend

        #Generate random paragraph
        with open('paragraph_bank.json') as paragraph_bank_file:
            paraBank = json.load(paragraph_bank_file)
            randIndex = random.randint(0,len(paraBank)-1)

            #Store paragraph to this object
            self.paragraph = paraBank[randIndex]

        #Store length of paragraph to this object
        self.paragraphLength = len(self.paragraph.split())
        

    def updatePlayerProgress(self, playerID, wordsCompleted):
        #Calculate % of paragraph player has completed
        percentComplete = 100*(wordsCompleted/self.paragraphLength)

        #If the player has completed the paragraph, they win.
        if percentComplete == 100:
            self.isGameDone = True
            self.winPlayerID = playerID
        
        #Return the progress
        return {"player_ID": playerID, "progress": percentComplete}


    def run(self):
        while not self.isGameDone:

            message = self.qRecv.get()

            if message.get("type") == "join_game":
                self.qSend.put(self.joinGame())

            elif message.get("type") == "kill_game":
                self.isGameDone = True

            else:
                playerID = message.get("player_ID")
                wordCount = message.get("word_num")
                playerProgress = self.updatePlayerProgress(playerID, wordCount)
                self.qSend.put(playerProgress)

    
    def joinGame(self):
        self.playerIDCount += 1
        return {"player_ID": self.playerIDCount, "paragraph": self.paragraph}


if __name__=="__main__":

    #How to use

    #create game object (switch send/recv queues in arguments)
    game = Game(qSend, qRecv)

    #join game returns paragraph and that everyone will be writing
    game.joinGame()

    #update a single player's progress by passing playerID and num of words completed (defined by split())
    #returns playerID and their progress (%) in format: {"playerID": playerID, "progress": progress}
    playersProgress = game.updatePlayerProgress(1, 10)

    #isGameDone & winPlayerID to check if game has finished
    isGameFinished = game.isGameDone