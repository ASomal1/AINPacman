# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

#KAANse


from pacman import Directions
from game import Agent
import api
import random
import game
import util

class Map:
    def __init__(self, width, height):
        """
            1. create a 2d matrix matching the width and height passed through the constructor.
            2. set the self variables of width and height to match the ones passed in the consructor.
            :param width: width of map
            :param height: height of map
        """
        self.internalMap = [[0 for x in range(width)] for y in
                            range(height)] # 1.
        self.width = width # 2.
        self.height = height # 2.


    def printInternalMap(self):
        """
            Prints the map in its actual form.
            1. Initialise variable to decrease height (to print in reverse order)
            2. Loop through whole map and print it out in decreasing order of height (upside down)
        """
        tmpl = self.height #1.
        for i in range(self.height):
            for j in range(self.width):
                print str((self.internalMap[tmpl - 1][j])) + " ",
            tmpl = tmpl - 1
            print
        print

    """
        1. Set the (x,y) coordinate a value within the map
        2. Get the (x,y) coordinate value within the map
    """
    def setValue(self, x, y, value):  # 1.
        self.internalMap[y][x] = value

    def getValue(self, x, y):  # 2.
        return self.internalMap[y][x]

    def updateMap(self, food, walls, ghosts, capsules, rewardForFood, rewardForGhost, rewardForCapsules):
        """
            Essentially initialises the map with the rewards and '%'s for walls.
            1. Loop through map
            2. initialise a 'node' variable to store a tuple coordinate of the current i,j values of the iteration as (i,j)
            3. Check if the node is in food, walls, ghosts or capsules, update their values within the map accordingly.
            :param food: food from the api passed in
            :param walls: walls from the api passed in
            :param ghosts: ghosts from the api passed in
            :param capsules: capsules from the api passed in
            :return: nothing to return, just want an effect on the map
        """
        for i in range(self.width): # 1.
            for j in range(self.height): # 1.
                node = (i, j) # 2.
                if node in food: # 3.
                    self.setValue(i, j, rewardForFood) # 3.
                elif node in walls: # 3.
                    self.setValue(i, j, "%") # 3.
                if node in ghosts: # 3.
                    self.setValue(i, j, rewardForGhost) # 3.
                if node in capsules: # 3.
                    self.setValue(i,j,rewardForCapsules) # 3.



class MDPAgent(Agent):

    def __init__(self):
        self.initialise() #initialise the variables

    def final(self, state):
        self.initialise() #Re initialise the variables in between runs.

    def initialise(self):
        self.width = None  # assigned in getAction(..)

        self.height = None  # assigned in getAction(..)

        self.convergence = False  # value of the check to see if utilities aren't changing beyond threshold, initially 0 means initially not converged.

        self.completePolicy = None  # Storing a map containing the optimal policy after value iteration.

        self.presentMap = None  # Storing a map of the present map

        self.futureMap = None  # Storing a map of the future, used in value iteration for working with the values from the previous state.

        self.nodesAroundGhosts = None #used to store nodes around ghosts, so that they can have a different reward.

        self.printingOn = False #boolean flag to turn printing on or off, if on prints out the maps, convergence status, ghosts etc.

        self.rewardStandard = -0.1 #reward for a state with no food and no ghost, and not a state around a ghost.

        self.rewardForFood = 1 #reward for a state containing food

        self.rewardForGhost = -10 #reward for a state containing a ghost.

        self.rewardForCapsules = 2 #reward for a state containing a capsule.

        self.rewardForSpacesAroundGhosts = -5 #reward for states around a ghost

        self.threshold = 0.01  #threshold to measure difference for convergence, terminate value iteration and pacman moves when the utilities don't change more than this limit.

        self.discountFactor = 0.7 #discount factor, models pacman's patience. The closer to 1 the more patient pacman is.

        self.iteration = 0 #For printing purposes only, counts the number of iterations it takes to converge

        """
            initialise variables that will be used to store api calls, initially None
        """
        self.walls = None
        self.corners = None
        self.food = None
        self.capsules = None
        self.ghosts = None
        self.pacman = None

    def perpendicularMove(self, move, walls,moves,x,y, utilityOfCurrentPosition):
        """
            Helper function for the function 'moveWithMaxExpectedUtility'

            1. checks if the move passed in is equal to (North or South) or (East or West) because if North or South then going perpendicular will lead to going
               East or West and similarly for going East or West going perpendicular will lead to going North or South (90 degrees).

            2. In each case of (1.) the perpendicular moves expected utility is added to the dictionary which stores their expected utility
               because the probability of going perpendicular is 0.1 that is fixed since the method is for perpendicular moves. Also the utility
               that the probability is multiplied by depends on whether or not going perpendicular ends up in a wall, if it does end up in a wall
               the utility of the current position/state is taken, since if pacman tries to go into a wall it bounces back and stays in the same position.

            :param move: the current move while working out the MEU & looping over all possible moves from the function 'moveWithMaxExpectedUtility' passed in
            :param walls: walls from the api passed in
            :param moves: moves dictionary to store the expected utility of every single move pacman can do passed in, to be added to with moves[move] += ...
            :param x: x coordinate of current state value iteration is looking at passed in
            :param y: y coordinate of current state value iteration is looking at passed in
            :param utilityOfCurrentPosition: utility of the current postion value iteration is looking at passed in.
            :return: nothing to return, method used so the dictionary values of expected utilities of moves can be updated.
        """
        if move == "North" or move == "South": # 1.
            moves[move] += 0.1 * self.presentMap.getValue(x - 1, y) if not (x - 1, y) in walls else 0.1 * utilityOfCurrentPosition #2.
            moves[move] += 0.1 * self.presentMap.getValue(x + 1, y) if not (x + 1, y) in walls else 0.1 * utilityOfCurrentPosition #2.
        elif move == "West" or move == "East": # 1.
            moves[move] += 0.1 * self.presentMap.getValue(x, y + 1) if not (x, y + 1) in walls else 0.1 * utilityOfCurrentPosition #2.
            moves[move] += 0.1 * self.presentMap.getValue(x, y - 1) if not (x, y - 1) in walls else 0.1 * utilityOfCurrentPosition #2.


    def moveWithMaxExpectedUtility(self, fromState, returnDirection, walls):
        """
            Method returns the move with the maximum expected utility as the value of that move or the direction of the move with the maximum expected utility
            depending on what 'returnDirection' is, if false returns the direction North,South,East or West, if False, returns the value. This is used in value-
            iteration when returnDirection is false so the value is returned to do the calculation, and when working out the optimal policy with returnDirection
            = True so the direction is used to tell pacman which move to take.

            1. List of all possible moves from a given 'fromState'
            2. Store a dictionary of each possible move and its expected utility initially 0.
            3. Store the x and y values of the coordinate passed in as the parameter 'fromState'
            4. Store the utility of the fromState which is retrieved from the present map, to be used when pacman tries to move into a wall but
               stays in the same place.

            5 initialise variables north,south,east, west from the x and y values of the 'fromState'

            6. Loop through the list of moves in (1.)
                6.1 check which direction the iteration's current move is saying
                6.2 for each move, update its expected utility value stored in its dictionary with 0.8 * the utility of the move that it intends to make
                    that could be the actual intended move e.g. if North then y+1 from the present map(previous map, since this method is updating the future map) or
                    the utility of its current state from the present map (previous map) if the intended move happens to be a wall.
                6.3 similarly for going perpendicular use the helper function described above 'perpendicularMove' which does the same thing as (6.2.) but for
                    both perpendicular moves, and with a probability of 0.1 each. The helper function was to save repeating code since going north or south have
                    the same perpendicular moves (east,west) and the same goes for going going east or west which have the same perpendicular moves (north,south)
                    the helper function would also consider if going perpendicular would end up in a wall and if so 0.1 (probability) * utilityOfCurrentPosition
                    which is from the previous map.

            7. If the return direction parameter is True then do 7.1 and return the direction "North", "South", "East", "West", if its False then do 7.2. which
               returns the value rather than the direction.

            :param fromState: param passed from value iteration or when finding the optimal policy, the state for which we want to calculate the MEU.
            :param returnDirection: If true return the Direction of the move with maximum expected utility, if False return the value of the move with the maxiumum expected utility
            :param walls: walls passed in.
            :return: return Direction or Value based on if returnDirection is True or False, Direction or Value of move with maximum expected utility.
        """
        listOfAllPossibleMovesLegalOrNot = ["North","South","East","West"] # 1.
        moves = {"North":0,"South":0,"East":0,"West":0} # 2.
        x = fromState[0] # 3.
        y = fromState[1] # 3.
        utilityOfCurrentPosition = self.presentMap.getValue(x, y) # 4.
        north = (x, y + 1); south = (x, y - 1); east = (x + 1, y); west = (x - 1, y) # 5.

        for move in listOfAllPossibleMovesLegalOrNot: # 6.
            if move == "North": # 6.1.
                moves[move] += 0.8 * self.presentMap.getValue(x, y + 1) if not north in walls else 0.8 * utilityOfCurrentPosition # 6.2.
                self.perpendicularMove(move, walls, moves, x, y, utilityOfCurrentPosition) # 6.3.
            elif move == "South": # 6.1.
                moves[move] += 0.8 * self.presentMap.getValue(x, y - 1) if not south in walls else 0.8 * utilityOfCurrentPosition # 6.2.
                self.perpendicularMove(move, walls, moves, x, y, utilityOfCurrentPosition) # 6.3.
            elif move == "East": # 6.1.
                moves[move] += 0.8 * self.presentMap.getValue(x + 1, y) if not east in walls else 0.8 * utilityOfCurrentPosition # 6.2.
                self.perpendicularMove(move, walls, moves, x, y, utilityOfCurrentPosition) # 6.3.
            elif move == "West": # 6.1.
                moves[move] += 0.8 * self.presentMap.getValue(x - 1, y) if not west in walls else 0.8 * utilityOfCurrentPosition # 6.2.
                self.perpendicularMove(move, walls, moves, x, y, utilityOfCurrentPosition) # 6.3.
        if returnDirection: # 7.
            return max(moves, key=moves.get) # 7.1.
        else: # 7.
            return moves[max(moves, key=moves.get)] # 7.2.

    def createMap(self):
        """
            Creates and returns a map (2d matrix) of specified width and height, which is worked out by the corners of the map within 'registerInitialState'
            :return: returns a map (2d matrix) of specified width and height.
        """
        return Map(self.width, self.height)

    def reward(self, position):
        """
            Method takes a position/state, and for that position checks what it contains within the map
            1. initialises the reward to 0
            2. checks if the position contains food and does not contain a ghost and assigns a reward accordingly.
            3. checks if the position contains a capsule and doesn't contain a ghost or a food and assigns a reward accordingly.
            4. checks if the position doesn't contain a ghost, a food or a capsule and assigns a reward accordingly.
            5. checks if the position is around a ghost e.g. if its in list [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1), (x+1,y+1), (x-1,y-1),(x+1,y-1),(x-1,y+1)]
               where x and y are ghost coordinates and assigns the reward accordingly.
            6. checks if the position contains a ghost and then assigns a reward accordingly.

            7. return the reward for the position after going through all the checks.
            :param position: the position/state we want to check the reward of, for value iteration.
            :return: the reward for the position
        """
        node = position
        reward = 0 # 1.
        if node in self.food and not node in self.ghosts: # 2.
            reward = self.rewardForFood # 2.
        elif not node in self.food and not node in self.ghosts and node in self.capsules: # 3.
            reward = self.rewardForCapsules # 3.
        elif not node in self.food and not node in self.ghosts and not node in self.capsules: # 4.
            reward = self.rewardStandard # 4.
        if node in self.nodesAroundGhosts: # 5.
            reward = self.rewardForSpacesAroundGhosts # 5.
        if node in self.ghosts: # 6.
            reward = self.rewardForGhost # 6.
        return reward # 7.

    def acknowledgeGhostsIfNotScaredOrAboutToChange(self, state):
        """
            1. take the ghost states from the api ((coordinate), Boolean scared/not) tuples
            2. loop over all ghosts on map
            3. take the coordinates of the ghost and store it in a 'coords' variable
            4. take the boolean scared/not (the second element of the tuple returned by (1.) and store it in a variable called 'scared'

            5. for each ghost, check if the ghost is scared and if the ghost is already acknowledged then remove the ghost from the acknowledged ghosts list.
            6. for each ghost also check if its not scared and its not in the list of acknowledged ghosts, then add it to the list of acknowledged ghosts.

            7. consider time and store the ghosts coordinates along with how long until they stop being scared so ((ghostCoordinates), timeUntilNotScared) in 'scaredOrNot' variable
            8. loop over all ghosts on the map
                8.1 for each ghost store its coordinates in coords variable
                8.2 store the ghost's time until not scared in a time variable
                8.3 check if the time is less than 5 and the ghost is not in the acknowledged non-scared ghosts list, then add it to the list since its about to become not scared.

            :param state:
            :return: nothing to return.
        """
        noneScared = api.ghostStates(state) # 1.
        for ghost in noneScared: # 2.
            coords = ghost[0] # 3.
            scared = ghost[1]
            if scared and coords in self.ghosts: # 5.
                self.ghosts.remove(coords) # 5.
            elif not scared and not coords in self.ghosts: # 6.
                self.ghosts.append(coords) # 6.

        scaredOrNot = api.ghostStatesWithTimes(state) # 7.
        for ghost in scaredOrNot: # 8.
            coords = ghost[0] # 8.1
            time = ghost[1] # 8.2
            if time < 5 and not coords in self.ghosts: self.ghosts.append(coords) # 8.3.

    def findStatesAroundGhosts(self):
        """
            1. loop over all ghosts
            2. for each ghost store its x and y coordinate in x and y variables accordingly.
            3. loop over all positions around a ghost, around the x and y coordinates of a ghost.
                3.1. check if the position is not a wall, and if its not a wall append the position to the nodes around a ghost list.
            :return: nothing to return
        """
        for ghost in self.ghosts: # 1.
            x = ghost[0] # 2.
            y = ghost[1] # 2.
            for k in [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1), (x+1,y+1), (x-1,y-1),(x+1,y-1),(x-1,y+1)]: # 3.
                if k not in self.walls: self.nodesAroundGhosts.append(k) # 3.1.

    def runValueIterationUntilConvergence(self):
        """
            Method used for value iteration
            1. a convergence variable set to false, when this becomes true, it means the present map and the future map difference is below the threshold set.
            2. print out some information about status of convergence and the number of moves etc.

            3. While convergence is false loop
                3.1. create a variable called overalDifference and initialise it to an empty list, each element in the list will be the difference of each coordinate
                     from the future map and each corresponding coordinate from the present map so futuremap(5,5) - presentmap(5,5) etc. while checking for convergence
                     all values of this list will be summed up and checked if its below the threshold set in the class variables.

                3.2. create futureMap variable, create a new map and assign the variable the map, then initialise map with 'updateMap' to initial values.

                3.3. loop over the a map
                    3.3.1 check that the i,j values of the loop are not considered walls when considered as a coordinate (i,j)
                    3.3.2 the new value of the coordinate (i,j) is updated via the value iteration version of the bellman's equation
                          so the new value of the coordinate is equal to the reward of the coordinate (depending on whats there, food,ghost etc...)
                          plus the discount factor multiplied by the move with the maximum expected utility from the previous 'present' Map (when working out the future map)
                          (the present map is considered inside the 'moveWithMaxExpectedUtility' function)
                    3.3.3 the futureMap is updated to have the value worked out by value iteration variant of the bellman's equation.
            4. loop over the map again while checking the differences between the future and present maps after one iteration of value iteration has been done and bellman's equation variant applied.
                4.1. check that the (i,j) loop iteration coordinate is not in a wall, and if its not then append the difference of the value at (i,j) in the future map - the value (i,j) in the present map
                     to the 'overallDifference' array.
            5. check if the printing boolean flag class variable is True and if so print the sum of the overall difference.

            6. Set the present map to be equal to the future map in preparation for the next iteration of value iteration (this while loop)

            7. check whether the printing boolean flag is True and if so print the convergence boolean variable and the future map.

            8. check if the absolute value of the sum of the overall difference is below the threshold, if it is we have convergence, set convergence to True
               and break out of the while loop.
            9. increment the iteration variable (the number of times value iteration has converged.
            :return:
        """
        self.convergence = False # 1.

        if self.printingOn: print self.convergence
        if self.printingOn: print "Value iteration complete, move number: " + str(self.iteration) + " ================" # 2.

        while self.convergence == False: # 3
            overallDifference = [] # 3.1.

            self.futureMap = self.createMap() # 3.2.
            self.futureMap.updateMap(self.food, self.walls, self.ghosts, self.capsules, self.rewardForFood,self.rewardForGhost, self.rewardForCapsules) # 3.2.

            for i in range(self.width): # 3.3.
                for j in range(self.height): # 3.3.
                    if not (i, j) in self.walls: # 3.3.1
                        newVal = self.reward((i, j)) + self.discountFactor * self.moveWithMaxExpectedUtility((i, j),False,self.walls) # 3.3.2
                        self.futureMap.setValue(i, j, round(newVal, 4)) # 3.3.3

            # check difference
            for i in range(self.width): # 4.
                for j in range(self.height): # 4.
                    if not (i, j) in self.walls: overallDifference.append(round(self.futureMap.getValue(i, j) - self.presentMap.getValue(i, j), 4)) # 4.1.

            if self.printingOn: print "The total difference is: " + str(abs(sum(overallDifference)))  # 5. the overall difference between the two sets.

            self.presentMap = self.futureMap # 6.

            if self.printingOn: print "Future map: " + str(self.convergence) #7.
            if self.printingOn: self.futureMap.printInternalMap() # 7.

            if abs(sum(overallDifference)) <= self.threshold: # 8.
                self.convergence = True # 8.
                break # 8.
        self.iteration = self.iteration + 1 # 9. count the number of value iterations run per game.


    def findOptimalPolicy(self):
        """
            Method to find the optimal policy (AFTER value iteration has converged.)
            1. Create a new map and store it in the self variable 'completePolicy'
            2. loop over the map
            3. if the coordinate is not in food or in walls
                3.1. then find the value for the coordinate by taking the maximum expected utility value fro the coordinate within present map (since val iteration is done at this point)
                3.2. otherwise if the coordinate (i,j) is in food then in the completePolicy Map replace the coordinate with "F"
            4. check if the printing boolean flag is True and if so print the completePolicy Map.
            :return:
        """
        self.completePolicy = self.createMap() # 1.
        for i in range(self.width): # 2.
            for j in range(self.height): # 2.
                if (i, j) not in self.food and not (i, j) in self.walls: # 3.
                    value = self.moveWithMaxExpectedUtility((i, j), True, self.walls) # 3.1.
                    self.completePolicy.setValue(i, j, value) # 3.1.
                elif (i, j) in self.food: # 3.2.
                    self.completePolicy.setValue(i, j, "F") # 3.2.
        if self.printingOn: self.completePolicy.printInternalMap() # 4.


    def makeMoveFromOptimalPolicy(self,state):
        """
            This method picks a move for pacman to make from the optimal policy.
            1. Take pacman's coordinates, pass it into the completePolicy Map, and the direction it returns is the direction pacman will 'try' to take (non deterministically)
            :param state:
            :return:
        """
        legal = state.getLegalPacmanActions()
        if Directions.STOP in legal: legal.remove(Directions.STOP)
        return api.makeMove(self.completePolicy.getValue(self.pacman[0], self.pacman[1]), legal) # 1.

    def registerInitialState(self, state):
        """
            This function is called when the pacman agent gets created, only called once per game
            1. so it is efficient for the walls to be initialised once from this method
            2. it is also efficient for the corners to be initialised once from this method
            3. it is also efficient for the dimensions to be initialised from the corners from this method

            :param state:
            :return: nothing to return, method only for initialising stuff that only needs to be initialised once.
        """
        self.walls = api.walls(state) # 1.
        self.corners = api.corners(state) # 2.
        # dimensions
        if self.width == None and self.height == None: # 3.
            self.width = self.corners[len(self.corners) - 1][0] + 1 # 3.
            self.height = self.corners[len(self.corners) - 1][1] + 1 # 3.

    def getAction(self, state):
        """
            1. initialise the values that variables that will/can change in every move pacman makes, such as the food, ghosts, pacman's location, capeules and the nodes around the ghosts
               the code aims to minimise the API calls for efficiency purposes so these values are passed into methods than need the information rather than multiple api calls in other places.
            2. only acknowledge ghosts than are scared, so that when ghosts become scared pacman wastes no time in mediumClassic and spends more time working out how to actually get to the food.
               however, the ghosts who are 5 seconds away from becoming not-scared are still considered to attempt to avoid risk and increase the win rate.
            3. states around ghosts are given a special reward of -5 so pacman can try to avoid them and value iterations values spread accordinaly so pacman can make better decisions.
               for each ghost's coordinate these coordinates are considered if they're not in walls: (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1), (x+1,y+1), (x-1,y-1),(x+1,y-1),(x-1,y+1)
               where x and y are the ghosts coordinates (x,y)

            4. initialise a present map, only once per game.
                4.1. create a map and store it as in the 'presentMap' variable.
                4.2. update the map to its initial values of 0s and rewards and %s for walls.
                4.3. check if the printing boolean flag is on and if so print the present map when first initialised.

            5. run value iteration to update the values of the future map based on the present map (explained better/in more detail in relevant sections of the function definition)

            6. find the optimal policy, for each coordinate finding the maximum expected utility from the present map after value iteration has reached convergence and finished.

            7. if the printing flag is set to true print out the currently acknowledged ghosts, (non-scared) ghosts.

            8. return the action given by the optimal policy.


            :param state:
            :return: the move to make, given by the optimal policy worked out once the value iteration has finished.
        """
        self.food = api.food(state); self.ghosts = []; self.pacman = api.whereAmI(state); self.capsules = api.capsules(state); self.nodesAroundGhosts = [] # 1.

        self.acknowledgeGhostsIfNotScaredOrAboutToChange(state) # 2.

        self.findStatesAroundGhosts() # 3.

        if self.presentMap == None: # 4.
            self.presentMap = self.createMap()  # 4.1.
            self.presentMap.updateMap(self.food, self.walls, self.ghosts, self.capsules, self.rewardForFood, self.rewardForGhost, self.rewardForCapsules) # 4.2.
            if self.printingOn: self.presentMap.printInternalMap() # 4.

        self.runValueIterationUntilConvergence() # 5.


        self.findOptimalPolicy() # 6. find optimal policy policy

        if self.printingOn: print "Ghosts: "+str(self.ghosts) # 7.

        return self.makeMoveFromOptimalPolicy(state)

