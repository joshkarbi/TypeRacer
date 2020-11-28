from essential_generators import DocumentGenerator
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
        self.gen = DocumentGenerator()

        #Store paragraph to this object
        self.paragraph = self.gen.paragraph()

        #Store length of paragraph to this object
        self.paragraphLength = len(self.paragraph.split())
        

    def updatePlayerProgress(self, playerID, wordsCompleted):
        #Calculate % of paragraph player has completed
        percentComplete = 100*(wordsCompleted/self.paragraphLength)

        #Update player's progress property
        self.playersProgress[playerID] = percentComplete

        #If the player has completed the paragraph, they win.
        if percentComplete == 100:
            self.isGameDone = True
            self.winPlayerID = playerID
        
        #Return the progress
        return {"playerID": playerID, "progress": percentComplete}


    def run(self):
        while not self.isGameDone:

            message = self.qRecv.recv()

            if message.type == "join_game":
                self.qSend.send(self.joinGame())

            else:
                playerID = message.player_ID
                wordCount = message.word_num
                playerProgress = self.updatePlayerProgress(playerID, wordCount)
                self.qSend.send(playerProgress)

    
    def joinGame(self):
        self.playerIDCount += 1
        return {"playerID": self.playerIDCount, "paragraph": self.paragraph}






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