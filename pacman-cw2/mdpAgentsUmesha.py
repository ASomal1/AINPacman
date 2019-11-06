from pacman import Directions
from game import Agent
import api
import random
import game
import util

# UMESHA
class MDPAgent(Agent):
    
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"
    #Setting initial value for directions North, South, East, West to 0
        self.N = 0
        self.S = 0
        self.E = 0
        self.W = 0

    #This code was from lab 5 solution where I get the height and width of the grid
    #To be use later in the code
    def getLayoutHeight(self, corners):
        height = -1
        for i in range(len(corners)):
            if corners[i][1] > height:
                height = corners[i][1]
        return height + 1

    def getLayoutWidth(self, corners):
        width = -1
        for i in range(len(corners)):
            if corners[i][0] > width:
                width = corners[i][0]
        return width + 1

    #Here I am computing the utility of states by applying the Bellman equation
    #Using the value iteration method
    def valueIteration(self, state, utility):
        #Setting initial variables
        height = -1
        width = -1
        number = 0
        
        #Setting a value here so it does not go into infinite loop
        #The number 100 is good to improve the speed of pacman and also pass the required tests
        #Because the larger the value, the longer the game takes to run
        while number < 100:
            #Making a copy of the utility
            utilityCopy = utility.copy()
            #Calling from the api
            corners = api.corners(state)
            walls = api.walls(state)
            food = api.food(state)
            ghosts = api.ghosts(state)
            capsules = api.capsules(state)
            #setting a value for the reward, gamma and terminal state for the bellman equation
            reward = 0.2
            gamma = 0.8
            terminalState = True
     
     #Nested for loop to loop through the grid; height and width
            for a in range(self.getLayoutWidth(corners) + height):
                for b in range(self.getLayoutHeight(corners) + width):
                    current = (a, b)
                    
                    #Checking if Pacman is in the terminating state or not
                    if current not in food and current not in capsules and current not in walls and current not in ghosts:
                        #If not in any of those states then set terminating state to false
                        terminalState = False
                    else:
                        #Else set terminating state true
                        terminalState = True
                    
                    #If not in terminal state then do Bellman Equation
                    if not terminalState:
                        utility[current] = gamma * self.doTransition(state,a,b,utilityCopy) + reward
        #Enables Convergence
            number += 1
            
    
    #Depending on the direction, pacman is going to turn left or right
    def turnLeftAndRight(self, state, map, direction, x, y):
        
        #If North, then the right and left will be West and East
        if direction == "N":
            if map[(x,y+1)] == "||":
                #If there is a wall ahead then it will remain in the current position
                self.W += map[(x,y)] * 0.1 # turn left
                self.E += map[(x,y)] * 0.1 # turn right
            else:
                #If there is no wall ahead then it will move accordingly
                self.W += map[(x,y+1)] * 0.1 # turn left
                self.E += map[(x,y+1)] * 0.1 # turn right
                
        #If South, then the right and left will be West and East
        if direction == "S":
            if map[(x,y-1)] == "||":
                #If there is a wall ahead then it will remain in the current position
                self.W += map[(x,y)] * 0.1 # turn right
                self.E += map[(x,y)] * 0.1 # turn left
            else:
                #If there is no wall ahead then it will move accordingly
                self.W += map[(x,y-1)] * 0.1 # turn right
                self.E += map[(x,y-1)] * 0.1 # turn left
                
        #If East, then the right and left is South and North
        if direction == "E":
            if map[(x+1,y)] == "||":
                #If there is a wall ahead then it will remain in the current position
                self.S += map[(x,y)] * 0.1 # turn right
                self.N += map[(x,y)] * 0.1 # turn left
            else:
                #If there is no wall ahead then it will move accordingly
                self.S += map[(x+1,y)] * 0.1 # turn right
                self.N += map[(x+1,y)] * 0.1 # turn left
                
        #If West, then the right and left is North and South
        if direction == "W":
            if map[(x-1,y)] == "||":
                #If there is a wall ahead then remain in the current position
                self.N += map[(x,y)] * 0.1 # turn right
                self.S += map[(x,y)] * 0.1 # turn left
            else:
                #If there is no wall ahead then move accordingly
                self.N += map[(x-1,y)] * 0.1 # turn right
                self.S += map[(x-1,y)] * 0.1 # turn left
                
    
    def setMap(self,state, map):
        height = -1
        width = -1
        #Loops over the grid
        for a in range(self.getLayoutWidth(api.corners(state)) + width):
            for b in range(self.getLayoutHeight(api.corners(state)) + height):
                current = (a, b)
                #Positions of the ghosts are updated
                self.updateGhosts(state, map)
                
                #If position in map is empty then assign value of 0
                if current not in map.keys():
                    map[current] = 0
   
    def makeMap(self, state):
        
        #Add pacman to list to indicate the places he has already been
        visit = []
        if (api.whereAmI(state)) not in visit:
            visit.append(api.whereAmI(state))
            
        
        #Update value of walls in dictionary. Walls are assigned a value of ||
        listOfWalls = []
        walls = api.walls(state)
        dictionaryOfWalls = {}
        
        for wall in walls:
            if wall not in listOfWalls:
                listOfWalls.append(wall)
            dictionaryOfWalls.update({wall:'||'})
        
        #Update value of food in dictionary. Food is assigned a value of 20
        listOfFood = []
        food = api.food(state)
        dictionaryOfFood = {}
        
        for fud in food:
            if fud not in listOfFood:
                listOfFood.append(fud)
                
        map = {}
        
        for fud in listOfFood:
            if fud not in visit:
                map[fud] = 20
            dictionaryOfFood.update({fud:20})
        
        #Update value of capsules in food. Capsule is assigned a reward of 40
        listOfCapsules = []
        capsules = api.capsules(state)
        dictionaryOfCapsules = {}
        
        for capsule in capsules:
            if capsule not in listOfCapsules:
                listOfCapsules.append(capsule)
                
        for capsule in listOfCapsules:
            if capsule not in visit:
                map[capsule] = 40
            dictionaryOfCapsules.update({capsule:40})
        
        #Update map will wall, food and capsules
        map.update(dictionaryOfWalls)
        map.update(dictionaryOfFood)
        map.update(dictionaryOfCapsules)
        self.setMap(state, map)
                    
        return map
    
    #Updates the position of the ghosts
    def updateGhosts(self, state, map):
        ghosts = api.ghosts(state)
        listOfGhosts = []
        
        for ghost in ghosts:
            if ghost not in listOfGhosts:
                listOfGhosts.append(ghost)
        
                #Ghost is assigned a reward of -15
                for mKey in map.keys():
                    for ghost in range(len(ghosts)):
                        if mKey == (ghosts[ghost][0], ghosts[ghost][1]):
                            map[mKey] = -15
                    
            

    #Calculates transition utility
    def doTransition(self, state, x, y, transitionMap):
        
        map = {"N":0.0,"S":0.0,"E":0.0,"W":0.0}
        
        #Calculate utility of going North
        direction = "N"
        #If there is a wall ahead then stay in current position and calculate utility
        if transitionMap[(x,y+1)] == "||":
            self.N = transitionMap[(x,y)] * 0.8
            self.turnLeftAndRight(state, transitionMap, direction, x, y)
        #If there is no wall ahead then it will move accordingly and calculate utility
        else:
            self.N = transitionMap[(x,y+1)] * 0.8
            self.turnLeftAndRight(state, transitionMap, direction, x, y)
            
        #Updates map
        map.update({"N":self.N})
        map.update({"S":self.S})
        map.update({"E":self.E})
        map.update({"W":self.W})

        #Calculate utility of going South
        direction = "S"
        #If there is a wall ahead then stay in current position and calculate utility
        if transitionMap[(x,y-1)] == "||":
            self.S = transitionMap[(x,y)] * 0.8
            self.turnLeftAndRight(state, transitionMap, direction, x, y)
        #If there is no wall ahead then it will move accordingly and calculate utility
        else:
            self.S = transitionMap[(x,y-1)] * 0.8
            self.turnLeftAndRight(state, transitionMap, direction, x, y)

        #Updates map
        map.update({"N":self.N})
        map.update({"S":self.S})
        map.update({"E":self.E})
        map.update({"W":self.W})

        #Calculate utility of going East
        direction = "E"
        #If there is a wall ahead then stay in current position and calculate utility
        if transitionMap[(x+1,y)] == "||":
            self.E = transitionMap[(x,y)] * 0.8
            self.turnLeftAndRight(state, transitionMap, direction, x, y)
        #If there is no wall ahead then it will move accordingly and calculate utility
        else:
            self.E = transitionMap[(x+1,y)] * 0.8
            self.turnLeftAndRight(state, transitionMap, direction, x, y)

        #Updates map
        map.update({"N":self.N})
        map.update({"S":self.S})
        map.update({"E":self.E})
        map.update({"W":self.W})

        #Calculate utility of going West
        direction = "W"
        #If there is a wall ahead then stay in current position and calculate utility
        if transitionMap[(x-1,y)] == "||":
            self.W = transitionMap[(x,y)] * 0.8
            self.turnLeftAndRight(state, transitionMap, direction, x, y)
        #If there is no wall ahead then it will move accordingly and calculate utility
        else:
            self.W = transitionMap[(x-1,y)] * 0.8
            self.turnLeftAndRight(state, transitionMap, direction, x, y)

        #Updates map
        map.update({"N":self.N})
        map.update({"S":self.S})
        map.update({"E":self.E})
        map.update({"W":self.W})

        #Returns expected utility
        return max(map.values())
    
    #Calulates policy
    def doPolicy(self, state, x, y, policyMap):
        
        map = {"N":0.0,"S":0.0,"E":0.0,"W":0.0}
        
        #Calculate policy going North
        direction = "N"
         #If there is a wall ahead then stay in current position and calculate policy
        if policyMap[(x,y+1)] == "||":
            self.N = policyMap[(x,y)] * 0.8
            self.turnLeftAndRight(state, policyMap, direction, x, y)
        #If there is no wall ahead then it will move accordingly and calculate policy
        else:
            self.N = policyMap[(x,y+1)] * 0.8
            self.turnLeftAndRight(state, policyMap, direction, x, y)
        
        #Update map
        map.update({"N":self.N})
        map.update({"S":self.S})
        map.update({"E":self.E})
        map.update({"W":self.W})
        
        #Calculate policy going South
        direction = "S"
        #If there is a wall ahead then stay in current position and calculate policy
        if policyMap[(x,y-1)] == "||":
            self.S = policyMap[(x,y)] * 0.8
            self.turnLeftAndRight(state, policyMap, direction, x, y)
        #If there is no wall ahead then it will move accordingly and calculate policy
        else:
            self.S = policyMap[(x,y-1)] * 0.8
            self.turnLeftAndRight(state, policyMap, direction, x, y)
        
        #Update map
        map.update({"N":self.N})
        map.update({"S":self.S})
        map.update({"E":self.E})
        map.update({"W":self.W})
        
         #Calculate policy going East
        direction = "E"
        #If there is a wall ahead then stay in current position and calculate policy
        if policyMap[(x+1,y)] == "||":
            self.E = policyMap[(x,y)] * 0.8
            self.turnLeftAndRight(state, policyMap, direction, x, y)
        #If there is no wall ahead then it will move accordingly and calculate policy
        else:
            self.E = policyMap[(x+1,y)] * 0.8
            self.turnLeftAndRight(state, policyMap, direction, x, y)

        #Update map
        map.update({"N":self.N})
        map.update({"S":self.S})
        map.update({"E":self.E})
        map.update({"W":self.W})

        #Calculate policy going West
        direction = "W"
        #If there is a wall ahead then stay in current position and calculate policy
        if policyMap[(x-1,y)] == "||":
            self.W = policyMap[(x,y)] * 0.8
            self.turnLeftAndRight(state, policyMap, direction, x, y)
        #If there is no wall ahead then it will move accordingly and calculate policy
        else:
            self.W = policyMap[(x-1,y)] * 0.8
            self.turnLeftAndRight(state, policyMap, direction, x, y)

        #Update map
        map.update({"N":self.N})
        map.update({"S":self.S})
        map.update({"E":self.E})
        map.update({"W":self.W})

        #Returns the direction with the best utility
        expectedUtility = max(map.values())
        return map.keys()[map.values().index(expectedUtility)]
    
    
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"
        print "I'm at:"
        print api.whereAmI(state)

    def final(self, state):
        print "Looks like the game just ended!"
        self.N = 0
        self.S = 0
        self.E = 0
        self.W = 0


    #Controls the movement of the Pacman agent
    def getAction(self, state):

        pacman = api.whereAmI(state)
        legal = api.legalActions(state)
        
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        
        #If north then move north else make random move
        map = self.makeMap(state)
        self.valueIteration(state, map)
        if self.doPolicy(state, pacman[0], pacman[1], map) == "N":
            if Directions.NORTH in legal:
                return api.makeMove(Directions.NORTH, legal)
            else:
                choice = random.choice(legal)
                return api.makeMove(choice, legal)

        #If South then move south else make random choice
        if self.doPolicy(state, pacman[0], pacman[1], map) == "S":
            if Directions.SOUTH in legal:
                return api.makeMove(Directions.SOUTH, legal)
            else:
                choice = random.choice(legal)
                return api.makeMove(choice, legal)

        #If East then move east else make random choice
        if self.doPolicy(state, pacman[0], pacman[1], map) == "E":
            if Directions.EAST in legal:
                return api.makeMove(Directions.EAST, legal)
            else:
                choice = random.choice(legal)
                return api.makeMove(choice, legal)

        #If West then move west else make random choice
        if self.doPolicy(state, pacman[0], pacman[1], map) == "W":
            if Directions.WEST in legal:
                return api.makeMove(Directions.WEST, legal)
            else:
                choice = random.choice(legal)
                return api.makeMove(choice, legal)
            
            
