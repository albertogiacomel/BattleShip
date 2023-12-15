import random
import pandas as pd
import uuid
from flask import Flask, render_template, request, redirect

# Navi
ships = [2, 3, 4, 4, 5]

# Crea i tabelloni di gioco
board1 = [['..'] * 15 for i in range(15)]
board1_shoots = [['..'] * 15 for i in range(15)]
board2 = [['..'] * 15 for i in range(15)]
fleet1 = []
fleet2 = []

class Fleet(object):
    def __init__(self):
        self.player = '0'
        self.ships = []
        self.destroyed = 0
        self.active = len(ships)

class Sheep(object):
    def __init__(self):
        self.player = '0'
        self.coordinates = []
        self.destroyed = 0
        self.active = len(ships)

def can_place_ship(ship, board, row, col, direction):
    row=int(row)
    col=int(col)
    
    if (col+ship > len(board) or row+ship > len(board)):
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

def place_ship(player, ship, board, row, col, direction, id):
    if can_place_ship(ship, board, row, col, direction):
          # Place the ship on the board
        if direction == "horizontal":
            for i in range(0 , ship):
                board[row][col + i] = "S"+ str(i+1)
                player.append((id, row, col+i))
        else:
            for i in range(0 , ship):
                board[row + i][col] = "S"+ str(i+1)
                player.append((id, row+i, col))
        return True  # Ship placed successfully
    else:
        return False

def create_table(board):
    df = pd.DataFrame(board)
    return df


for ship in ships:
    while True:
        direction = random.choice(["horizontal", "vertical"])
        row = random.randint(0, len(board1)-1)
        col = random.randint(0, len(board1)-1)
        # Check if the ship can be placed at the specified location
        if can_place_ship(ship, board1, row, col, direction):          
            place_ship(player1, ship, board1, row, col, direction, uuid.uuid4().int)
            break
    while True:
        direction = random.choice(["horizontal", "vertical"])
        row = random.randint(0, len(board2)-1)
        col = random.randint(0, len(board2)-1)
        # Check if the ship can be placed at the specified location
        if can_place_ship(ship, board2, row, col, direction):
            place_ship(player2, ship, board2, row, col, direction, uuid.uuid4().int)
            break

def check_sink(row, col):
    for i in range(0 , len(player2)):
        for j in range(3):
            if player2[i][j] == row and player2[i][j+1] == col: 
                return True

# Crea l'interfaccia grafica web
app = Flask(__name__, template_folder="templates")

@app.route("/")
def index():
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
        board1_shoots[row ][col ] = "X"
        winner = check_sink(row ,col )
    else:
        board1_shoots[row][col] = "O"

    # Aggiorna l'interfaccia grafica
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
