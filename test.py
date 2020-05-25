import sys
import sqlite3
from random import shuffle

db = sqlite3.connect('mahjong.db', check_same_thread=False)

class Player:
    def __init__(self, userid, username, displayName, tiles, flowers, tai = 0, wind=None):
        self.userid = userid
        self.username = username
        self.displayName = displayName
        self.tiles = tiles
        self.flowers = flowers
        self.tai = tai

    def updateTai(self, roundWind):
        '''
        Updates player's tai count based on open tiles
        '''
        taiCounter = 0
        # convert roundWind to numeric value
        roundWindNumeric = windIndex(roundWind)

        # check each tile set for tais
        for tileSets in self.tiles['open']:
            if tileSets[0][1] == 'Dragon' or tileSets[0][1] == 'Animal':
                taiCounter += 1
            elif tileSets[0][1] == 'Flower' and int(tileSets[0][0][-1]) == int(roundWindNumeric):
                taiCounter += 1
        
        # update player's tai
        self.tai = taiCounter

def windIndex(wind):
    '''
    Returns wind as a number.
    East = 1
    South = 2
    West = 3
    South = 4
    '''
    if wind == 'East':
        windIndex = 1
    elif wind == 'South':
        windIndex = 2
    elif wind == 'West':
        windIndex = 3
    else:
        windIndex = 4
    return windIndex

def sortTiles(tiles):
    '''
    Group tiles by suit and order by ascending
    '''
    dots = ['Dot',[]]
    bamboos = ['Bamboo',[]]
    characters = ['Character',[]]
    winds = ['Wind',[]]
    dragons = ['Dragon',[]]
    final = []

    # group tiles by suit
    for tile in tiles:
        if tile[1] == 'Dot':
            dots[1].append(tile[0])
        elif tile[1] == 'Bamboo':
            bamboos[1].append(tile[0])
        elif tile[1] == 'Character':
            characters[1].append(tile[0])
        elif tile[1] == 'Wind':
            winds[1].append(tile[0])
        elif tile[1] == 'Dragon':
            dragons[1].append(tile[0])
    
    # sort each group
    dots[1].sort()
    bamboos[1].sort()
    characters[1].sort()
    winds[1].sort(key=lambda x: 1 if x=='East' else 2 if x=='South' else 3 if x=='West' else 4)
    dragons[1].sort()

    # recombine tiles
    for group in [dots, bamboos, characters, dragons, winds]:
        for tile in group[1]:
            final.append((tile, group[0]))
    
    return final

def startGame(players):
    winds = ['East', 'South', 'West', 'North']

    # get tile types
    tilesNormal = db.execute("SELECT Value, Suit FROM Tiles WHERE Suit NOT IN ('Animal', 'Flower')").fetchall()
    tilesSpecial = db.execute("SELECT Value, Suit FROM Tiles WHERE Suit IN ('Animal', 'Flower')").fetchall()

    # establish all tiles in the game
    publicTiles = []
    for _ in range(4):
        for tile in tilesNormal:
            publicTiles.append(tile)
    for tile in tilesSpecial:
        publicTiles.append(tile)
    
    # shuffle tiles
    shuffle(publicTiles)
    shuffle(winds)

    # assign wind to players
    for i in range(len(players)):
        players[i].wind = winds[i]
    players.sort(key=lambda x: 1 if x.wind=='East' else 2 if x.wind=='South' else 3 if x.wind=='West' else 4)

    # draw tiles
    for player in players:
        if player.wind == 'East': # banker draws 14 tiles
            drawTile(player, publicTiles, 14)
        else: # other players draw 13 tiles
            drawTile(player, publicTiles, 13)
        player.tiles['closed'] = sortTiles(player.tiles['closed'])
        player.updateTai('East')

    discardedTiles = []
    return publicTiles, discardedTiles, players

def drawTile(player, publicTiles, n):
    '''
    Take n number of tiles from the end
    '''
    for _ in range(n):
        if publicTiles[-1][1] == 'Flower' or publicTiles[-1][1] == 'Animal':
            player.tiles['open'].append([publicTiles.pop()])
            drawTileSpecial(player, publicTiles)
        else:
            player.tiles['closed'].append(publicTiles.pop())

def drawTileSpecial(player, publicTiles):
    '''
    Take 1 tile from the start
    '''
    if publicTiles[0][1] == 'Flower' or publicTiles[0][1] == 'Animal':
        player.tiles['open'].append([publicTiles.pop(0)])
        drawTileSpecial(player, publicTiles)
    else:
        player.tiles['closed'].append(publicTiles.pop(0))

def showClosedTiles(player):
    '''
    Show closed tiles and index position
    '''
    for tileIndex in range(len(player.tiles['closed'])):
        print(str(tileIndex) + ': ' + player.tiles['closed'][tileIndex][0] + ' ' + player.tiles['closed'][tileIndex][1])

def selectTileToDiscard():
    try:
        return int(input('Select tile to discard: '))
    except ValueError as e:
        print('Please enter an integer.')

def discardTile(player):
    showClosedTiles(player)
    discard = selectTileToDiscard()
    while not isinstance(discard, int) or discard < 0 or discard >= len(player.tiles['closed']): 
        print('Please enter a valid index.')
        discard = selectTileToDiscard()
    discardedTiles.append(player.tiles['closed'].pop(int(discard)))

def declareWin(player):
    decision = input('Your tiles are a winning hand. Do you want to declare a win? (y/n)')
    while decision != ('y' or 'n'):
        decision = input('Your tiles are a winning hand. Do you want to declare a win? (y/n)')
    if decision == 'y':
        return True
    else:
        return False

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
    if tile1[1] != tile2[1] or tile2[1] != tile3[1] or tile3[1] != tile1[1]:
        return False
    else:
        if tile1[1] in ['Dragon','Wind'] or tile2[1] in ['Dragon','Wind'] or tile3[1] in ['Dragon','Wind']:
            return False
        else:
            # Set cannot be a chow if any of the tiles are of the same number
            if (tile1[0] == tile2[0]) or (tile1[0] == tile3[0]) or (tile2[0] == tile3[0]):
                return False
            else:
                # sort set and check for consequtive
                tileSet = [int(tile1[0]), int(tile2[0]), int(tile3[0])]
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

def potentialAction(playerTiles, actionType, freshTile=None, isNext=False):
    '''
    Scans player's closed tiles and check if there is a possible action to play
    actionType can either be take discarded tile (1) or self-drawn (2)
    isNext identifies if the player is eligible for the Chow action
    '''
    numTiles = len(playerTiles)
    possibleActions = []

    # check if winning is possible
    hypoTiles = playerTiles.copy()
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

p1 = Player(1, 'Player1', 'Player1', {'closed':[],'open':[]}, [])
p2 = Player(2, 'Player2', 'Player2', {'closed':[],'open':[]}, [])
p3 = Player(3, 'Player3', 'Player3', {'closed':[],'open':[]}, [])
p4 = Player(4, 'Player4', 'Player4', {'closed':[],'open':[]}, [])


publicTiles, discardedTiles, playersOrdered = startGame([p1,p2,p3,p4])

isGame = False
tilesLeft = len(publicTiles)
roundNumber = 1
while isGame == False:
    for player in playersOrdered:
        # Sort player's hand
        player.tiles['closed'] = sortTiles(player.tiles['closed'])

        print(player.displayName + "'s " + 'turn')
        if roundNumber == 1 and player.wind == 'East':
            # East wind does not draw a tile on round 1
            if isWin(player.tiles['closed']):
                # Check if player can decare a win
                declareWin(player)
                if declareWin:
                    print(player.username, 'has won the game.')
                    isGame = True
            discardTile(player)
        else:
            # Draw 1 tile and discard 1 tile
            drawTile(player, publicTiles, 1)
            if isWin(player.tiles['closed']):
                # Check if player can decare a win
                declareWin(player)
                if declareWin:
                    print(player.username, 'has won the game.')
                    isGame = True
            discardTile(player)
        tilesLeft = len(publicTiles)
        print(discardedTiles)
        # Detect for possible actions
        otherPlayers = playersOrdered.copy()
        otherPlayers.remove(player)
        for otherPlayer in otherPlayers:
            possibleActions = potentialAction(otherPlayer.tiles['closed'], 1, discardedTiles[-1])
            if len(possibleActions) > 0:
                # check if player wants to exercise action
                for i in range(len(possibleActions)):
                    print(i, ':', possibleActions[i])
    roundNumber += 1
    

# tile1 = (6, 'Dot')
# tile2 = (4, 'Bamboo')
# tile3 = ('West', 'Wind')
# #print(isChow(tile1,tile2,tile3))
# print(tile1[1] in ['Dragon','Wind'] or tile2[1] in ['Dragon','Wind'] or tile3[1] in ['Dragon','Wind'])

# tiles = [('Red', 'Dragon'),('Red', 'Dragon'),('White', 'Dragon'),(1, 'Dot'),(2, 'Dot'),(3, 'Dot'),('White', 'Dragon'),('White', 'Dragon')]
# p1.tiles['closed'] = tiles
# p1.tiles['closed'] = sortTiles(p1.tiles['closed'])
# print(isWin(p1.tiles['closed']))
