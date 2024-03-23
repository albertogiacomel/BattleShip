import random
import uuid
<<<<<<< HEAD
from flask import Flask, request, redirect, render_template

# Crea i tabelloni di gioco
boardSize = 10
ships = [1,1,1,1,2,2,2,3,3,4]
empty_cell = '.'
=======
import pandas as pd
>>>>>>> 6997d9c3a02d4cb5f4669ce8c5c1881286b89b39

class Ship():
    def __init__(self, num, size):
        self.player = num
        self.id = 0
        self.size = size
        self.cells = []
        self.hit_cells = 0
        self.is_destroyed = False

    def hit(self, row, col):
        for cell in self.cells:
            if cell["row"] == row and cell["col"] == col:
                cell["hit"] = True
                self.hit_cells += 1
                if self.hit_cells == self.size:
                    self.is_destroyed = True
                return

    def is_alive(self):
        return not self.is_destroyed

<<<<<<< HEAD

       
=======
>>>>>>> 6997d9c3a02d4cb5f4669ce8c5c1881286b89b39
class Fleet():
    def __init__(self, num, ships):
        self.player = num
        self.ships = ships
        self.active_ships = len(ships)
        self.ship_list = []

    def check_victory(self):
        return self.active_ships == 0

    def restart(self):
<<<<<<< HEAD
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
=======
        self.ship_list.clear()
        self.active_ships = len(self.ships)
>>>>>>> 6997d9c3a02d4cb5f4669ce8c5c1881286b89b39

def init_board(size):
    return [['..'] * size for i in range(size)]

def can_place_ship(ship, board, row, col, direction):
    row = int(row)
    col = int(col)

    if (col + ship.size > len(board) or row + ship.size > len(board)):
        return False

    if (direction == "horizontal"):
        for i in range(0, ship.size):
            if board[row][col + i].startswith("S"):
                return False
    if (direction == "vertical"):
        for i in range(0, ship.size):
            if board[row + i][col].startswith("S"):
                return False
    return True

def place_ship(fleet, ship, board, row, col, direction, id):
    if can_place_ship(ship, board, row, col, direction):
        tmp_ship = Ship(fleet.player, ship.size)
        tmp_ship.id = id
        tmp_ship.active_cells = ship.size

        if direction == "horizontal":
            for i in range(0, ship.size):
                board[row][col + i] = "S" + str(i + 1)
                tmp_ship.cells.append({"row": row, "col": col + i, "hit": False})
        else:
            for i in range(0, ship.size):
                board[row + i][col] = "S" + str(i + 1)
                tmp_ship.cells.append({"row": row + i, "col": col, "hit": False})

        fleet.ship_list.append(tmp_ship)
        return True
    else:
        return False

def create_table(board):
    return pd.DataFrame(board)

def check_sink(fleet, row, col):
    for ship in fleet.ship_list:
        ship.hit(row, col)
        if ship.is_destroyed:
            fleet.active_ships -= 1
            fleet.ship_list.remove(ship)
            return True
    return False

<<<<<<< HEAD
def handle_move(row, col, opponent_board, board_shoots, fleet):
    if opponent_board[row][col].startswith("S"):
        if checkSink(fleet, row, col):
=======
def handle_fire(fleet, board, board_shoots, row, col):
    if board[row][col].startswith("S"):
        if check_sink(fleet, row, col):
>>>>>>> 6997d9c3a02d4cb5f4669ce8c5c1881286b89b39
            board_shoots[row][col] = "A"
        else:
            board_shoots[row][col] = "X"
    else:
        board_shoots[row][col] = "O"
<<<<<<< HEAD
    
# Crea l'interfaccia grafica web
init()
=======


from flask import Flask, render_template, request, redirect, session
from game_logic import *

>>>>>>> 6997d9c3a02d4cb5f4669ce8c5c1881286b89b39
app = Flask(__name__, template_folder="templates")

# Initialize game state
board_size = 15
ships = [1, 2, 2, 3, 4, 4, 5]
fleet1 = Fleet(0, ships)
fleet2 = Fleet(1, ships)
board1 = init_board(board_size)
board2 = init_board(board_size)
board1_shoots = init_board(board_size)
board2_shoots = init_board(board_size)

@app.route("/")
def index():
<<<<<<< HEAD
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
=======
    if fleet2.check_victory():
        return render_template("index.html", board1=create_table(board1),
                               board1_shoots=create_table(board1_shoots),
                               board2=create_table(board2),
                               winner="Player 1")
    return render_template("index.html", board1=create_table(board1),
                               board1_shoots=create_table(board1_shoots),
                               board2=create_table(board2),
                               hit1=session.get("hit1", 0))
>>>>>>> 6997d9c3a02d4cb5f4669ce8c5c1881286b89b39

@app.route("/place", methods=["GET", "POST"])
def place():
    if request.method == "GET":
        if "player" not in session:
            session["player"] = 0
        return render_template("place.html", ships=ships, boardSize=board_size)

    player = session["player"]
    ship = int(request.form["ship"])
    row = int(request.form["row"])
    col = int(request.form["col"])
    direction = request.form["direction"]

<<<<<<< HEAD
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
=======
    if player
>>>>>>> 6997d9c3a02d4cb5f4669ce8c5c1881286b89b39
