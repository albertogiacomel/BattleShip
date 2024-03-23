import random
import pandas as pd
import uuid
from flask import Flask, request, redirect, render_template

# Crea i tabelloni di gioco
boardSize = 10
ships = [1,1,1,1,2,2,2,3,3,4]
empty_cell = '.'

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
    
    def restart(self):
        self.shipList.clear()
        self.activeShips = len(self.ships)

def get_computer_move(board_shoots, board_size):
    """
    Get a valid move from the computer player.
    
    Args:
        board_shoots (list): The board representing the computer's previous shots.
        board_size (int): The size of the board.
        
    Returns:
        tuple: A tuple containing the row and column of the computer's move.
    """
    # Check if there are any remaining hits to target
    for row in range(board_size):
        for col in range(board_size):
            if board_shoots[row][col] == 'X':
                # Find the next available cell around the hit
                available_cells = get_available_cells_around(row, col, board_shoots, board_size)
                if available_cells:
                    return random.choice(available_cells)
    
    # If no remaining hits, choose a random cell
    while True:
        row = random.randint(0, board_size - 1)
        col = random.randint(0, board_size - 1)
        if board_shoots[row][col] == empty_cell:
            return row, col

def get_available_cells_around(row, col, board_shoots, board_size):
    """
    Get a list of available cells around a given cell.
    
    Args:
        row (int): The row of the cell.
        col (int): The column of the cell.
        board_shoots (list): The board representing the computer's previous shots.
        board_size (int): The size of the board.
        
    Returns:
        list: A list of tuples containing the available cells around the given cell.
    """
    available_cells = []
    for r in range(max(0, row - 1), min(board_size, row + 2)):
        for c in range(max(0, col - 1), min(board_size, col + 2)):
            # Check if it's not the current cell and not a diagonal cell
            if (r, c) != (row, col) and abs(r - row) != abs(c - col):
                if board_shoots[r][c] == empty_cell:
                    available_cells.append((r, c))
    return available_cells

def init():
    global board1, board2, board1_shoots, board2_shoots, boardSize, ships, fleet1, fleet2, hit1, hit2
    board1 = [[empty_cell] * boardSize for i in range(boardSize)]
    board1_shoots = [[empty_cell] * boardSize for i in range(boardSize)]
    board2 = [[empty_cell] * boardSize for i in range(boardSize)]
    board2_shoots = [[empty_cell] * boardSize for i in range(boardSize)]
    fleet1 = Fleet(0, ships)
    fleet2 = Fleet(1, ships)
    hit1 = 0
    hit2 = 0
    for ship in ships:
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
    return pd.DataFrame(board)

def checkSink(fleet, row, col):
    for ship in fleet.shipList:
        ship.calc_hit(row,col)
        if ship.isDestroyed:
            fleet.activeShips -= 1
            fleet.shipList.remove(ship)
            return True
    return False

def handle_move(row, col, opponent_board, board_shoots, fleet):
    if opponent_board[row][col].startswith("S"):
        if checkSink(fleet, row, col):
            board_shoots[row][col] = "A"
        else:
            board_shoots[row][col] = "X"
    else:
        board_shoots[row][col] = "O"
    
# Crea l'interfaccia grafica web
init()
app = Flask(__name__, template_folder="templates")

@app.route("/")
def index():
    if fleet2.checkVictory():
        return render_template("index.html", board1=create_table(board1), board1_shoots=create_table(board1_shoots), board2=create_table(board2), winner="Player 1", fleet1=fleet1, fleet2=fleet2)
    if fleet1.checkVictory():
        return render_template("index.html", board1=create_table(board1), board1_shoots=create_table(board1_shoots), board2=create_table(board2), winner="Computer", fleet1=fleet1, fleet2=fleet2)
    
    return render_template("index.html", board1=create_table(board1), board1_shoots=create_table(board1_shoots), board2=create_table(board2), hit1=hit1, fleet1=fleet1, fleet2=fleet2)

@app.context_processor
def utility_processor():
    def render_cell_content(value):
# Se la cella è un
        if value == ".":
            return '<img src="static/images/fog.png" alt="Fog" width="100%" height="100%"/>'
        elif value == "O":
            return '<img src="static/images/water.png" alt="Water" width="100%" height="100%"/>'
        elif value == "A" or value == "X":
            return '<img src="static/images/fire.png" alt="Fire" width="100%" height="100%"/>'
        else:
            return value

    return dict(render_cell_content=render_cell_content)

# Custom filter to convert a number to its ASCII character
@app.template_filter('num_to_ascii')
def num_to_ascii(num):
    """
    Converts a number to its corresponding ASCII character.
    
    Args:
        num (int): The number to be converted.
        
    Returns:
        str: The ASCII character corresponding to the input number.
    """
    # Check if the input is within the valid ASCII range
    return chr(num + 65)

@app.route("/place", methods=["GET", "POST"])
def place():
    # Check the request method
    if request.method == "GET":
        # Render the place ship form
        return render_template("place.html", ships=ships, boardSize=boardSize)

    # Retrieve request data
    player = request.form["player"]
    ship = int(request.form["ship"])
    row = int(request.form["row"])
    col = int(request.form["col"])
    direction = request.form["direction"]

    if player == "0":
        # Check if the ship can be placed
        if not can_place_ship(ship, board1, row, col, direction):
            return render_template("place.html", error="Invalid ship placement", ships=ships,  boardSize=boardSize)
        else:
             # Place the ship
            place_ship(fleet1, ship, board1, row, col, direction, uuid.uuid4().int)
    else:
        # Check if the ship can be placed
        if not can_place_ship(ship, board2, row, col, direction):
            return render_template("place.html", error="Invalid ship placement", ships=ships,  boardSize=boardSize)
        else:
             # Place the ship
            place_ship(fleet2, ship, board2, row, col, direction, uuid.uuid4().int)
   

    # Aggiorna l'interfaccia grafica
    return redirect("/")


@app.route("/fire", methods=["POST"])
def fire():
    global hit1 , hit2
   #Player 1
    hit1 += 1
    if "Fire" in request.form is not None:
        # Ottieni i dati della richiesta
        row = int(request.form["row"])
        col = int(request.form["col"])
  
    if "Random" in request.form is not None:
         row = random.randint(0, boardSize-1)
         col = random.randint(0, boardSize-1)
    handle_move(row, col, board2, board1_shoots, fleet2)
   
    #Player 2 - Computer's move
    computer_row, computer_col = get_computer_move(board2_shoots, boardSize)
    handle_move(computer_row, computer_col, board1, board2_shoots, fleet1)
    handle_move(computer_row, computer_col, board1, board1, fleet1)
    hit2 += 1
    # Aggiorna l'interfaccia grafica
    return redirect("/")

@app.route("/restart", methods=["POST"])
def restart():
    init()
    # Aggiorna l'interfaccia grafica
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)