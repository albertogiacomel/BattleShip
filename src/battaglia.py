import random
import pandas as pd
import uuid
from flask import Flask, request, redirect, render_template, jsonify
from battleship_ai import BattleshipAI

# Crea i tabelloni di gioco
boardSize = 10
ships = [1, 1, 1, 1, 2, 2, 2, 3, 3, 4]
empty_cell = '.'

class Ship():
    def __init__(self, num):
        self.player = num
        self.id = 0
        self.cells = []
        self.destroyedCells = 0
        self.activeCells = 0
        self.isDestroyed = False
    
    def calc_hit(self, row, col):
        for i in range(0, len(self.cells)):
            if self.cells[i]["row"] == row and self.cells[i]["col"] == col:
                self.cells[i]["hit"] = True
                self.destroyedCells += 1
        if self.destroyedCells == self.activeCells:
            self.isDestroyed = True
            return True
        return False

class Fleet():
    def __init__(self, num, ships):
        self.player = num
        self.ships = ships.copy()
        self.activeShips = len(self.ships)
        self.shipList = []
        self.destroyedShips = []  # Nuovo elenco per tenere traccia delle navi affondate

    def checkVictory(self):
        if self.activeShips == 0:
            return True
        return False
    
    def restart(self):
        self.shipList.clear()
        self.destroyedShips.clear()  # Puliamo anche le navi affondate
        self.activeShips = len(self.ships)

    def get_remaining_ship_sizes(self):
        """Restituisce le dimensioni delle navi rimanenti"""
        return [ship.activeCells for ship in self.shipList]

def init():
    global board1, board2, board1_shoots, board2_shoots, boardSize, ships, fleet1, fleet2, hit1, hit2, ai_player
    board1 = [[empty_cell] * boardSize for i in range(boardSize)]
    board1_shoots = [[empty_cell] * boardSize for i in range(boardSize)]
    board2 = [[empty_cell] * boardSize for i in range(boardSize)]
    board2_shoots = [[empty_cell] * boardSize for i in range(boardSize)]
    fleet1 = Fleet(0, ships)
    fleet2 = Fleet(1, ships)
    hit1 = 0
    hit2 = 0
    
    # Inizializza l'IA
    ai_player = BattleshipAI(boardSize)
    ai_player.reset(ships)

    # Posiziona le navi casualmente
    place_ships_randomly(fleet1, board1)
    place_ships_randomly(fleet2, board2)

def place_ships_randomly(fleet, board):
    """Posiziona le navi casualmente sulla plancia"""
    for ship_size in fleet.ships:
        while True:
            direction = random.choice(["horizontal", "vertical"])
            row = random.randint(0, boardSize-1)
            col = random.randint(0, boardSize-1)
            # Check if the ship can be placed at the specified location
            if can_place_ship(ship_size, board, row, col, direction):          
                place_ship(fleet, ship_size, board, row, col, direction, uuid.uuid4().int)
                break

def can_place_ship(ship, board, row, col, direction):
    row = int(row)
    col = int(col)
    
    # Controlla se la nave è fuori dai limiti della plancia
    if direction == "horizontal" and col + ship > len(board):
        return False
    if direction == "vertical" and row + ship > boardSize:
        return False

    # Controlla le celle adiacenti (per evitare navi troppo vicine)
    start_row = max(0, row - 1)
    end_row = min(boardSize - 1, row + ship if direction == "vertical" else row + 1)
    start_col = max(0, col - 1)
    end_col = min(boardSize - 1, col + ship if direction == "horizontal" else col + 1)
    
    for r in range(start_row, end_row + 1):
        for c in range(start_col, end_col + 1):
            if board[r][c] != empty_cell:
                return False
                
    return True

def place_ship(fleet, ship, board, row, col, direction, id):
    if can_place_ship(ship, board, row, col, direction):
        # Create Ship
        tmpShip = Ship(fleet.player)
        tmpShip.id = id
        tmpShip.activeCells = ship
        # Place the ship on the board
        if direction == "horizontal":
            for i in range(0, ship):
                board[row][col + i] = "S" + str(i+1)
                tmpShip.cells.append({"row": row, "col": col+i, "hit": False})    
        else:
            for i in range(0, ship):
                board[row + i][col] = "S" + str(i+1)
                tmpShip.cells.append({"row": row+i, "col": col, "hit": False})
        fleet.shipList.append(tmpShip)       
        return True  # Ship placed successfully
    else:
        return False

def create_table(board):
    return pd.DataFrame(board)

def checkSink(fleet, row, col):
    """Controlla se una nave è stata affondata e aggiorna lo stato della flotta"""
    for i, ship in enumerate(fleet.shipList[:]):  # Crea una copia della lista per iterare in sicurezza
        if ship.calc_hit(row, col):
            # La nave è stata colpita
            fleet.activeShips -= 1
            # La rimuoviamo dalla lista di navi attive
            sunk_ship = fleet.shipList.pop(i)
            # La aggiungiamo alla lista di navi affondate
            fleet.destroyedShips.append(sunk_ship)
            return True, ship.activeCells
    return False, 0

def handle_move(row, col, opponent_board, board_shoots, fleet):
    """Gestisce un colpo e restituisce il risultato"""
    result = ""
    if opponent_board[row][col].startswith("S"):
        sunk, ship_size = checkSink(fleet, row, col)
        if sunk:
            board_shoots[row][col] = "A"  # "A" for "Affondata" (Sunk)
            result = "A"  # Affondata
        else:
            board_shoots[row][col] = "X"  # "X" for hit
            result = "X"  # Colpita
    else:
        board_shoots[row][col] = "O"  # "O" for miss
        result = "O"  # Mancata
    
    return result

def get_ai_move():
    """Ottiene la mossa dall'IA"""
    row, col = ai_player.get_move()
    return row, col

# Crea l'applicazione Flask
app = Flask(__name__, template_folder="templates")

@app.route("/")
def index():
    """Pagina principale del gioco"""
    if fleet2.checkVictory():
        return render_template("index.html", 
                              board1=create_table(board1), 
                              board1_shoots=create_table(board1_shoots), 
                              board2=create_table(board2), 
                              winner="Player 1", 
                              fleet1=fleet1, 
                              fleet2=fleet2,
                              game_status="finished")
    if fleet1.checkVictory():
        return render_template("index.html", 
                              board1=create_table(board1), 
                              board1_shoots=create_table(board1_shoots), 
                              board2=create_table(board2), 
                              winner="Computer", 
                              fleet1=fleet1, 
                              fleet2=fleet2,
                              game_status="finished")
    
    return render_template("index.html", 
                          board1=create_table(board1), 
                          board1_shoots=create_table(board1_shoots), 
                          board2=create_table(board2), 
                          hit1=hit1, 
                          hit2=hit2,
                          fleet1=fleet1, 
                          fleet2=fleet2,
                          game_status="playing")

@app.context_processor
def utility_processor():
    """Processore per il rendering delle celle"""
    def render_cell_content(value):
        if value == ".":
            return '<img src="static/images/fog.png" alt="Fog" width="100%" height="100%"/>'
        elif value == "O":
            return '<img src="static/images/water.png" alt="Water" width="100%" height="100%"/>'
        elif value == "A" or value == "X":
            return '<img src="static/images/fire.png" alt="Fire" width="100%" height="100%"/>'
        else:
            return value
    return dict(render_cell_content=render_cell_content)

@app.template_filter('num_to_ascii')
def num_to_ascii(num):
    """Converte un numero in un carattere ASCII"""
    return chr(num + 65)

@app.route("/place", methods=["GET", "POST"])
def place():
    """Gestisce il posizionamento manuale delle navi"""
    if request.method == "GET":
        return render_template("place.html", ships=ships, boardSize=boardSize)

    player = request.form["player"]
    ship = int(request.form["ship"])
    row = int(request.form["row"])
    col = int(request.form["col"])
    direction = request.form["direction"]

    if player == "0":
        if not can_place_ship(ship, board1, row, col, direction):
            return render_template("place.html", error="Invalid ship placement", ships=ships, boardSize=boardSize)
        else:
            place_ship(fleet1, ship, board1, row, col, direction, uuid.uuid4().int)
    else:
        if not can_place_ship(ship, board2, row, col, direction):
            return render_template("place.html", error="Invalid ship placement", ships=ships, boardSize=boardSize)
        else:
            place_ship(fleet2, ship, board2, row, col, direction, uuid.uuid4().int)

    return redirect("/")

@app.route("/fire", methods=["POST"])
def fire():
    """Gestisce l'azione di sparare"""
    global hit1, hit2
    
    # Player 1 turn (Human)
    hit1 += 1
    row, col = None, None
    
    if "Fire" in request.form:
        row = int(request.form["row"])
        col = int(request.form["col"])
    elif "Random" in request.form:
        row = random.randint(0, boardSize-1)
        col = random.randint(0, boardSize-1)
    
    # Controlla se la cella è già stata colpita
    if board1_shoots[row][col] != empty_cell:
        return jsonify({
            "status": "error", 
            "message": "Hai già sparato in questa posizione!"
        })
    
    # Gestisci il colpo del giocatore
    result = handle_move(row, col, board2, board1_shoots, fleet2)
    
    # Se il giocatore ha vinto, termina il turno
    if fleet2.checkVictory():
        return redirect("/")
    
    # Player 2 turn (AI)
    hit2 += 1
    computer_row, computer_col = get_ai_move()
    
    # Gestisci il colpo dell'IA
    ai_result = handle_move(computer_row, computer_col, board1, board2_shoots, fleet1)
    
    # Aggiorna lo stato dell'IA
    ai_player.register_shot_result(computer_row, computer_col, ai_result)
    
    # Controlla se l'IA ha affondato una nave
    if ai_result == 'A':
        # Aggiorna la conoscenza dell'IA sulle navi rimanenti
        remaining_ships = fleet1.get_remaining_ship_sizes()
        ai_player.remaining_ships = remaining_ships
    
    return redirect("/")

@app.route("/restart", methods=["POST"])
def restart():
    """Ricomincia il gioco"""
    init()
    return redirect("/")

@app.route("/difficulty", methods=["POST"])
def set_difficulty():
    """Imposta la difficoltà dell'IA"""
    difficulty = request.form.get("difficulty", "medium")
    
    # Implementazione futura: aggiustare i parametri dell'IA in base alla difficoltà
    
    return redirect("/")

@app.route("/stats", methods=["GET"])
def stats():
    """Visualizza le statistiche di gioco"""
    stats_data = {
        "player_shots": hit1,
        "ai_shots": hit2,
        "player_hits": sum(1 for row in board1_shoots for cell in row if cell in ["X", "A"]),
        "ai_hits": sum(1 for row in board2_shoots for cell in row if cell in ["X", "A"]),
        "player_ships": fleet1.activeShips,
        "ai_ships": fleet2.activeShips
    }
    
    return render_template("stats.html", stats=stats_data)

@app.context_processor
def utility_processor():
    """Processore per il rendering delle celle"""
    def render_cell_content(value):
        if value == ".":
            return '<img src="static/images/fog.png" alt="Fog" width="100%" height="100%"/>'
        elif value == "O":
            return '<img src="static/images/water.png" alt="Water" width="100%" height="100%"/>'
        elif value == "A" or value == "X":
            return '<img src="static/images/fire.png" alt="Fire" width="100%" height="100%"/>'
        elif value.startswith("S"):
            # If it's a ship cell (starting with 'S'), show the ship part number
            return value
    return dict(render_cell_content=render_cell_content)

if __name__ == "__main__":
    # Inizializza il gioco
    init()
    # Avvia l'applicazione Flask
    app.run(debug=True)