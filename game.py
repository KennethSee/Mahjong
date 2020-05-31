import sys
from random import shuffle

class Game:
    def __init__(self, players, allTiles, windChangeCounter = 1, windIndex = 1, isGame = False):
        self.players = players
        self.allTiles = allTiles.copy()
        self.windIndex = windIndex
        self.counter = windChangeCounter
        self.isGame = isGame
        self.round = Round()

    def getWindName(self, windIndex):
        '''
        Returns name of wind from wind index argument.
        1 = East; 2 = South; 3 = West; 4 = North
        '''
        if windIndex == 1:
            return 'East'
        elif windIndex == 2:
            return 'South'
        elif windIndex == 3:
            return 'West'
        else:
            return 'North'

    def startGame(self):
        '''
        Shuffle players and assign initial temporary winds
        '''
        shuffle(self.players)
        for i in range(len(self.players)):
            self.players[i].temporaryWindIndex = i + 1

        self.startRound()

    def startRound(self):
        '''
        Distribute starting tiles to players
        '''
        # Shuffle public tiles
        self.round = Round(self.allTiles.copy(), [], len(self.allTiles))
        shuffle(self.round.publicTiles)
        # Distribute tiles to players
        for player in self.players:
            if player.temporaryWindIndex == 1:
                player.drawTile(self.round.publicTiles, 14)
            else:
                player.drawTile(self.round.publicTiles, 13)
            player.closeTiles = sortTiles(player.closeTiles)

    def addWindIndex(self):
        if self.windIndex == 4:
            self.isGame = True
        else:
            self.windIndex += 1
    
    def addWindChangeCounter(self):
        '''
        Add 1 to the wind change counter. If current counter is 4, reset the counter
        to 1 and move to the next game wind.
        '''
        if self.counter == 4:
            self.counter = 1
            self.addWindIndex()
        else:
            self.counter += 1

    def nextRound(self, winner, isDraw = 0):
        '''
        Prepares table for next round.
        If winner was the temporary East or the round ended in a draw, temporary winds do 
        not change. Else, rotate the temporary winds counter clockwise.
        '''
        for player in self.players:
            # Clear players' tiles and multipliers
            player.playerReset
            # Rotate temporary winds if the temporary East is not the winner or round is not draw
            if isDraw == 0 and winner.temporaryWindIndex != 1:
                player.rotateTemporaryWind
                self.addWindChangeCounter()

        # Clear round tiles
        self.round = Round()

class Round:
    def __init__(self, publicTiles = [], discardedTiles = [], tilesLeft = 0):
        self.publicTiles = publicTiles.copy()
        self.discardedTiles = discardedTiles.copy()
        self.tilesLeft = tilesLeft

class Player:
    def __init__(self, userID, displayName, temporaryWindIndex = 0, money = 1000, openTiles = [], closeTiles = [], roundMultiplier = 0):
        self.userID = userID
        self.displayName = displayName
        self.temporaryWindIndex = temporaryWindIndex
        self.money = money
        self.openTiles = openTiles.copy()
        self.closeTiles = closeTiles.copy()
        self.roundMultiplier = roundMultiplier
    
    def playerReset(self):
        '''
        Clear tiles and multiplier
        '''
        self.openTiles = []
        self.closeTiles = []
        self.roundMultiplier = 0

    def rotateTemporaryWind(self):
        if self.temporaryWindIndex == 4:
            self.temporaryWindIndex = 1
        else:
            self.temporaryWindIndex += 1

    def drawTile(self, publicTiles, n):
        '''
        Draw n number of tiles from public tiles
        '''
        for _ in range(n):
            if publicTiles[-1].suit == 'Flower' or publicTiles[-1].suit == 'Animal':
                self.openTiles.append(TileSet(publicTiles.pop(), 'Single'))
                self.drawTileSpecial(publicTiles)
            else:
                self.closeTiles.append(publicTiles.pop())

    def drawTileSpecial(self, publicTiles):
        '''
        Take 1 tile from the start
        '''
        if publicTiles[0].suit == 'Flower' or publicTiles[0].suit == 'Animal':
            self.openTiles.append(TileSet(publicTiles.pop(0), 'Single'))
            self.drawTileSpecial(publicTiles)
        else:
            self.closeTiles.append(publicTiles.pop(0))

    def showClosedTiles(self):
        '''
        Show closed tiles and index position
        '''
        for tileIndex in range(len(self.closeTiles)):
            print(str(tileIndex) + ': ' + self.closeTiles[tileIndex].value + ' ' + self.closeTiles[tileIndex].suit)

    def discardTile(self, discardedTiles, discardIndex):
        discardedTiles.append(self.closeTiles.pop(int(discardIndex)))

    def potentialAction(self, actionType, sourcePlayer=None, freshTile=None):
        '''
        Scans player's closed tiles and check if there is a possible action to play
        actionType can either be take discarded tile (1) or self-drawn (2)
        isNext identifies if the player is eligible for the Chow action
        '''
        playerTiles = self.closeTiles
        numTiles = len(playerTiles)
        possibleActions = []
        isNext = checkIfNext(sourcePlayer, self)

        # check if winning is possible
        hypoTiles = self.closeTiles.copy()
        hypoTiles.append(freshTile)
        hypoTiles = sortTiles(hypoTiles)
        if isWin(hypoTiles):
            possibleActions.append(('Win', [-1]))
        
        # check for pong, gong, or chow
        for i in range(numTiles):
            if numTiles - i > 3:
                # check for all
                if freshTile == playerTiles[i] == playerTiles[i+1] == playerTiles[i+2]:
                    # gong is possible
                    possibleActions.append(('Gong', [freshTile, playerTiles[i], playerTiles[i+1], playerTiles[i+2]]))
                elif actionType == 1: # pong and chow only available as actions for using discarded tile
                    setOfThree = [freshTile, playerTiles[i], playerTiles[i+1]]
                    setOfThree = sortTiles(setOfThree)
                    if isPong(setOfThree[0], setOfThree[1], setOfThree[2]):
                        possibleActions.append(('Pong', setOfThree.copy()))
                    elif isChow(setOfThree[0], setOfThree[1], setOfThree[2]) and isNext == True: # only the next player can chow
                        possibleActions.append(('Chow', setOfThree.copy()))
            elif numTiles - i > 2:
                # check only for pong and chow
                setOfThree = [freshTile, playerTiles[i], playerTiles[i+1]]
                setOfThree = sortTiles(setOfThree)
                if isPong(setOfThree[0], setOfThree[1], setOfThree[2]):
                    possibleActions.append(('Pong', setOfThree.copy()))
                elif isChow(setOfThree[0], setOfThree[1], setOfThree[2]) and isNext == True: # only the next player can chow
                    possibleActions.append(('Chow', setOfThree.copy()))
        return possibleActions

class Tile:
    def __init__(self, value, suit, index=0):
        self.index = index
        self.value = value
        self.suit = suit

class Combination:
    def __init__(self, multiplier):
        self.multiplier = multiplier

class FixedCombination(Combination):
    def __init__(self, multiplier, combination):
        Combination.__init__(self, multiplier)
        self.combination = combination.copy()

class PatternCombination(Combination):
    def __init__(self, multiplier, pattern):
        Combination.__init__(self, multiplier)
        self.pattern = pattern

class TileSet:
    def __init__(self, tiles, setType):
        self.tiles = tiles
        self.setType = setType

def sortTiles(tiles):
    '''
    Group tiles by suit and order by ascending
    '''
    dots = []
    bamboos = []
    characters = []
    winds = []
    dragons = []
    final = []

    # group tiles by suit
    for tile in tiles:
        if tile.suit == 'Dot':
            dots.append(tile)
        elif tile.suit == 'Bamboo':
            bamboos.append(tile)
        elif tile.suit == 'Character':
            characters.append(tile)
        elif tile.suit == 'Wind':
            winds.append(tile)
        elif tile.suit == 'Dragon':
            dragons.append(tile)

    # take second element for sort
    def takeValue(elem):
        return elem.value

    # sort each group
    dots.sort(key=takeValue)
    bamboos.sort(key=takeValue)
    characters.sort(key=takeValue)
    winds.sort(key=lambda x: 1 if x.value=='East' else 2 if x.value=='South' else 3 if x.value=='West' else 4)
    dragons.sort(key=takeValue)

    # recombine tiles
    for group in [dots, bamboos, characters, dragons, winds]:
        for tile in group:
            final.append(tile)
    
    return final

def isPong(tile1, tile2, tile3):
    if tile1 == tile2 == tile3:
        return True
    else:
        return False

def isGong(tile1, tile2, tile3, tile4):
    if tile1 == tile2 == tile3 == tile4:
        return True
    else:
        return False

def isChow(tile1, tile2, tile3):
    # Set cannot be a chow if any of the tiles are Dragon or Wind suit
    # Set cannot be a chow if the tiles are not in the same suit
    if tile1.suit != tile2.suit or tile2.suit != tile3.suit or tile3.suit != tile1.suit:
        return False
    else:
        if tile1.suit in ['Dragon','Wind'] or tile2.suit in ['Dragon','Wind'] or tile3.suit in ['Dragon','Wind']:
            return False
        else:
            # Set cannot be a chow if any of the tiles are of the same number
            if (tile1.value == tile2.value) or (tile1.value == tile3.value) or (tile2.value == tile3.value):
                return False
            else:
                # sort set and check for consequtive
                tileSet = [int(tile1.value), int(tile2.value), int(tile3.value)]
                tileSet.sort()
                if (tileSet[1] - tileSet[0] == 1) and (tileSet[2] - tileSet[1] == 1):
                    # tile set is confirmed to be a chow
                    return True
                else:
                    return False

def isWin(tiles):
    '''
    Check if tiles can be used to end the game
    Assumes sorted tiles
    '''
    numTiles = len(tiles)
    n = 0
    while n < numTiles:
        if numTiles - n == 2:
            # check for eyes
            if tiles[n] == tiles[n+1]:
                # check if eyes
                n += 2
            else:
                # if no possible combination, tile set is not a winning set
                return False
        elif numTiles - n == 3:
            # check for eyes, pong, and chow
            if isPong(tiles[n], tiles[n+1], tiles[n+2]):
                # check if pong
                n += 3
            elif isChow(tiles[n], tiles[n+1], tiles[n+2]):
                # check if chow
                n += 3
            # elif tiles[n] == tiles[n+1]:
            #     # check if eyes
            #     n += 2
            else:
                # if no possible combination, tile set is not a winning set
                return False
        else:
            if isGong(tiles[n], tiles[n+1], tiles[n+2], tiles[n+3]):
                # check if gong
                n += 4
            elif isPong(tiles[n], tiles[n+1], tiles[n+2]):
                # check if pong
                n += 3
            elif isChow(tiles[n], tiles[n+1], tiles[n+2]):
                # check if chow
                n += 3
            elif tiles[n] == tiles[n+1]:
                # check if eyes
                n += 2
            else:
                # if no possible combination, tile set is not a winning set
                return False
    return True

def checkIfNext(player1, player2):
    '''
    Checks if player 2 is right after player 1
    '''
    p1Index = player1.temporaryWindIndex
    p2Index = player2.temporaryWindIndex
    if p2Index - p1Index == 1 or p2Index - p1Index == -3:
        return True
    else:
        return False

# t1 = Tile('Red', 'Dragon')
# t2 = Tile('White', 'Dragon')
# t3 = Tile('Red', 'Dragon')
# t4 = Tile('White', 'Dragon')
# t5 = Tile('Red', 'Dragon')
# t6 = Tile(1, 'Dot')
# t7 = Tile(1, 'Bamboo')
# t8 = Tile(3, 'Dot')
# t9 = Tile('South', 'Wind')
# t10 = Tile('East', 'Wind')
# t11 = Tile('South', 'Wind')

# tiles = [t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11]
# testGame = Game(['p1','p2','p3','p4'],[])
# tiles = sortTiles(tiles)
# for tile in tiles:
#     print(tile.value, tile.suit)