import random
import uuid
import pandas as pd

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

class Fleet():
    def __init__(self, num, ships):
        self.player = num
        self.ships = ships
        self.active_ships = len(ships)
        self.ship_list = []

    def check_victory(self):
        return self.active_ships == 0

    def restart(self):
        self.ship_list.clear()
        self.active_ships = len(self.ships)

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
    df = pd.DataFrame(board)
    return df

def check_sink(fleet, row, col):
    for ship in fleet.ship_list:
        ship.hit(row, col)
        if ship.is_destroyed:
            fleet.active_ships -= 1
            fleet.ship_list.remove(ship)
            return True
    return False

def handle_fire(fleet, board, board_shoots, row, col):
    if board[row][col].startswith("S"):
        if check_sink(fleet, row, col):
            board_shoots[row][col] = "A"
        else:
            board_shoots[row][col] = "X"
    else:
        board_shoots[row][col] = "O"


from flask import Flask, render_template, request, redirect, session
from game_logic import *

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
    if fleet2.check_victory():
        return render_template("index.html", board1=create_table(board1),
                               board1_shoots=create_table(board1_shoots),
                               board2=create_table(board2),
                               winner="Player 1")
    return render_template("index.html", board1=create_table(board1),
                               board1_shoots=create_table(board1_shoots),
                               board2=create_table(board2),
                               hit1=session.get("hit1", 0))

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

    if player
