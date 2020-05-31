import sqlite3
from game import *

def selectTileToDiscard():
    try:
        return int(input('Select tile to discard: '))
    except ValueError as e:
        print('Please enter an integer.')

def discardIndex(numTiles):
    discard = selectTileToDiscard()
    while not isinstance(discard, int) or discard < 0 or discard >= numTiles: 
        print('Please enter a valid index.')
        discard = selectTileToDiscard()
    return discard

db = sqlite3.connect('mahjong.db', check_same_thread=False)
# get tile types
tilesNormal = db.execute("SELECT Value, Suit FROM Tiles WHERE Suit NOT IN ('Animal', 'Flower')").fetchall()
tilesSpecial = db.execute("SELECT Value, Suit FROM Tiles WHERE Suit IN ('Animal', 'Flower')").fetchall()
# establish all tiles in the game
gameTiles = []
for _ in range(4):
    for tile in tilesNormal:
        tileObject = Tile(tile[0], tile[1])
        gameTiles.append(tileObject)
for tile in tilesSpecial:
    tileObject = Tile(tile[0], tile[1])
    gameTiles.append(tileObject)

p1 = Player(1, 'p1')
p2 = Player(2, 'p2')
p3 = Player(3, 'p3')
p4 = Player(4, 'p4')

newGame = Game([p1,p2,p3,p4], gameTiles)

newGame.startGame()
while newGame.isGame != 1:
    for player in newGame.players:
        player.showClosedTiles()
        discardSelection = discardIndex(len(player.closeTiles))
        player.discardTile(newGame.round.discardedTiles, discardSelection)
        print([[tile.value, tile.suit] for tile in newGame.round.discardedTiles])
    #newGame.isGame = 1

