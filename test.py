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

    # draw tiles
    for player in players:
        if player.wind == 'East': # banker draws 14 tiles
            drawTile(player, publicTiles, 14)
        else: # other players draw 13 tiles
            drawTile(player, publicTiles, 13)
        player.tiles['closed'] = sortTiles(player.tiles['closed'])
        updateTai(player, 'East')

    discardedTiles = []
    return publicTiles, discardedTiles

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
        elif tile[1] == 'Drgaon':
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

def updateTai(player, roundWind):
    '''
    Updates player's tai count based on open tiles
    '''
    taiCounter = 0
    # convert roundWind to numeric value
    if roundWind == 'East':
        roundWindNumeric = 1
    elif roundWind == 'South':
        roundWindNumeric = 2
    elif roundWind == 'West':
        roundWindNumeric = 3
    else:
        roundWindNumeric = 4

    # check each tile set for tais
    for tileSets in player.tiles['open']:
        if tileSets[0][1] == 'Dragon' or tileSets[0][1] == 'Animal':
            taiCounter += 1
        elif tileSets[0][1] == 'Flower' and int(tileSets[0][0][-1]) == int(roundWindNumeric):
            taiCounter += 1
    
    # update player's tai
    player.tai = taiCounter

p1 = Player(1, 'Player1', 'Player1', {'closed':[],'open':[]}, [])
p2 = Player(2, 'Player2', 'Player2', {'closed':[],'open':[]}, [])
p3 = Player(3, 'Player3', 'Player3', {'closed':[],'open':[]}, [])
p4 = Player(4, 'Player4', 'Player4', {'closed':[],'open':[]}, [])


publicTiles, discardedTiles = startGame([p1,p2,p3,p4])

isGame = False
while isGame == False:
    #drawTile()
    isGame = True
    
print(p1.tiles, p1.tai)
