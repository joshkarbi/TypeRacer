from essential_generators import DocumentGenerator

class Game:

    #All players should be available to start game - users cannot join late
    def startGame(self, numOfPlayers):
        #Generate random paragraph
        self.gen = DocumentGenerator()

        #Store paragraph to this object
        self.paragraph = self.gen.paragraph()

        #Store length of paragraph to this object
        self.paragraphLength = len(self.paragraph.split())

        #Store playerIDs to determine winner
        self.playersProgress = [0]*numOfPlayers

        #Return paragraph text
        return self.paragraph
        

    def updatePlayerProgress(self, playerID, wordsCompleted):
        #Calculate % of paragraph player has completed
        percentComplete = 100*(wordsCompleted/self.paragraphLength)

        #Update player's progress property
        self.playersProgress[playerID] = percentComplete

        #If the player has completed the paragraph, they win.
        if percentComplete == 100:
            self.gameIsDone()
        
        #Otherwise, return the progress
        else:
            return self.playersProgress

    def gameIsDone(self):
        return #what??




#How to use

#create game object
game = Game()

#start game by entering number of players, returns the paragraph that everyone will be writing
paragraph = game.startGame(5)

#update a single player's progress by passing playerID and num of words completed (defined by split())
#returns array of progresses indexed by playerID
playersProgress = game.updatePlayerProgress(1, 10))