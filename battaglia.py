import random
import pandas as pd
import uuid
from flask import Flask, render_template, request, redirect

class Ship():
    def __init__(self, num):
        self.player = num
        self.id = 0
        self.cells = []
        self.destroyedCells = 0
        self.activeCells = 0
        self.isDestroyed = False
    def calc_hit(self,row,col):
            for i in range(0,len(self.cells)):
                if self.cells[i]["row"] == row and self.cells[i]["col"] == col:
                    self.cells[i]["hit"] = True
                    self.destroyedCells +=1
            if self.destroyedCells == self.activeCells:
                self.isDestroyed = True

       
class Fleet():
    def __init__(self, num, ships):
        self.player = num
        self.ships = ships
        self.activeShips = len(self.ships)
        self.shipList = []

    def checkVictory(self):
        if self.activeShips == 0:
            return True
        return False

# Crea i tabelloni di gioco
boardSize = 15
ships = [1,2]
board1 = [['..'] * boardSize for i in range(boardSize)]
board1_shoots = [['..'] * boardSize for i in range(boardSize)]
board2 = [['..'] * boardSize for i in range(boardSize)]
fleet1 = Fleet(0, ships)
fleet2 = Fleet(1, ships)

def init():
    for ship in fleet1.ships:
        while True:
            direction = random.choice(["horizontal", "vertical"])
            row = random.randint(0, boardSize-1)
            col = random.randint(0, boardSize-1)
            # Check if the ship can be placed at the specified location
            if can_place_ship(ship, board1, row, col, direction):          
                place_ship(fleet1, ship, board1, row, col, direction, uuid.uuid4().int)
                break
        while True:
            direction = random.choice(["horizontal", "vertical"])
            row = random.randint(0, boardSize-1)
            col = random.randint(0, boardSize-1)
            # Check if the ship can be placed at the specified location
            if can_place_ship(ship, board2, row, col, direction):
                place_ship(fleet2, ship, board2, row, col, direction, uuid.uuid4().int)
                break


def can_place_ship(ship, board, row, col, direction):
    row=int(row)
    col=int(col)
    
    if (col+ship > len(board) or row+ship > boardSize):
        return False   

    # Check if the specified location is within the board bounds
    if ( direction == "horizontal"):
         # Check for ship overlap in the row
        for i in range(0 , ship):
            if board[row][col + i].startswith("S"):
                return False
    if ( direction == "vertical"):
        for i in range(0 , ship):
            if board[row + i][col].startswith("S"):
                return False   
    return True  # Ship can be placed

def place_ship(fleet, ship, board, row, col, direction, id):
    if can_place_ship(ship, board, row, col, direction):
        # Create Ship
        tmpShip = Ship(fleet.player)
        tmpShip.id= id
        tmpShip.activeCells = ship
        # Place the ship on the board
        if direction == "horizontal":
            for i in range(0 , ship):
                board[row][col + i] = "S"+ str(i+1)
                tmpShip.cells.append({"row": row, "col": col+i, "hit":False})    
        else:
            for i in range(0 , ship):
                board[row + i][col] = "S"+ str(i+1)
                tmpShip.cells.append({"row": row+i, "col": col, "hit":False})
        fleet.shipList.append(tmpShip)       
        return True  # Ship placed successfully
    else:
        return False

def create_table(board):
    df = pd.DataFrame(board)
    return df

def checkSink(fleet, row, col):
    for ship in fleet.shipList:
        ship.calc_hit(row,col)
        if ship.isDestroyed:
            fleet.activeShips -= 1
            fleet.shipList.remove(ship)
    
# Crea l'interfaccia grafica web
init()
app = Flask(__name__, template_folder="templates")

@app.route("/")
def index():
    if fleet2.checkVictory():
            return render_template("index.html", board1=create_table(board1), board1_shoots=create_table(board1_shoots), board2=create_table(board2), winner="Player 1")
    return render_template("index.html", board1=create_table(board1), board1_shoots=create_table(board1_shoots), board2=create_table(board2))

@app.route("/place", methods=["GET", "POST"])
def place():
    # Check the request method
    if request.method == "GET":
        # Render the place ship form
        return render_template("place.html", ships=ships)

    # Retrieve request data
    player = request.form["player"]
    ship = int(request.form["ship"])
    row = int(request.form["row"])
    col = int(request.form["col"])
    direction = request.form["direction"]

    if (player=="1"):
        board = board1
    else:
        board = board2

    # Check if the ship can be placed
    if not can_place_ship(ship, board, row, col, direction):
        return render_template("place.html", error="Invalid ship placement", ships=ships)

    # Place the ship
    place_ship(ship, board, row, col, direction)

    # Aggiorna l'interfaccia grafica
    return redirect("/")


@app.route("/fire", methods=["POST"])
def fire():

    if "Fire" in request.form is not None:
        # Ottieni i dati della richiesta
        row = int(request.form["row"])
        col = int(request.form["col"])
  
    if "Random" in request.form is not None:
         row = random.randint(0, len(board1)-1)
         col = random.randint(0, len(board1)-1)

    if board2[row][col].startswith("S"):
        board1_shoots[row][col] = "X"
        checkSink(fleet2, row ,col )
    else:
        board1_shoots[row][col] = "O"

    # Aggiorna l'interfaccia grafica
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
