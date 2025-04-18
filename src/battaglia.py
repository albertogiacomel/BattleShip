import random
import pandas as pd
import uuid
from flask import Flask, request, redirect, render_template
from battleship_ai import BattleshipAI  # Importiamo la nostra AI

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

def can_place_ship(ship, board, row, col, direction):
    row=int(row)
    col=int(col)
    
    # Verifica che la nave non esca dal tabellone
    if direction == "horizontal" and col + ship > len(board):
        return False
    if direction == "vertical" and row + ship > boardSize:
        return False   

    # Verifica sovrapposizioni con altre navi
    if direction == "horizontal":
        # Controlla sovrapposizioni in orizzontale
        for i in range(0, ship):
            if board[row][col + i].startswith("S"):
                return False
            
        # Controlla anche lo spazio intorno alla nave
        for r in range(max(0, row - 1), min(boardSize, row + 2)):
            for c in range(max(0, col - 1), min(len(board), col + ship + 1)):
                if 0 <= r < boardSize and 0 <= c < len(board) and board[r][c].startswith("S"):
                    return False
                
    if direction == "vertical":
        # Controlla sovrapposizioni in verticale
        for i in range(0, ship):
            if board[row + i][col].startswith("S"):
                return False
                
        # Controlla anche lo spazio intorno alla nave
        for r in range(max(0, row - 1), min(boardSize, row + ship + 1)):
            for c in range(max(0, col - 1), min(len(board), col + 2)):
                if 0 <= r < boardSize and 0 <= c < len(board) and board[r][c].startswith("S"):
                    return False
                    
    return True  # La nave può essere posizionata

def place_ship(fleet, ship, board, row, col, direction, id):
    if can_place_ship(ship, board, row, col, direction):
        # Crea la nave
        tmpShip = Ship(fleet.player)
        tmpShip.id = id
        tmpShip.activeCells = ship
        # Posiziona la nave sul tabellone
        if direction == "horizontal":
            for i in range(0, ship):
                board[row][col + i] = "S" + str(i+1)
                tmpShip.cells.append({"row": row, "col": col+i, "hit": False})    
        else:
            for i in range(0, ship):
                board[row + i][col] = "S" + str(i+1)
                tmpShip.cells.append({"row": row+i, "col": col, "hit": False})
        fleet.shipList.append(tmpShip)       
        return True  # Nave posizionata con successo
    else:
        return False

def create_table(board):
    return pd.DataFrame(board)

def checkSink(fleet, row, col):
    for ship in fleet.shipList:
        ship.calc_hit(row, col)
        if ship.isDestroyed:
            fleet.activeShips -= 1
            fleet.shipList.remove(ship)
            return True
    return False

def handle_move(row, col, opponent_board, board_shoots, fleet):
    result = empty_cell
    if opponent_board[row][col].startswith("S"):
        if checkSink(fleet, row, col):
            board_shoots[row][col] = "A"
            result = "A"
        else:
            board_shoots[row][col] = "X"
            result = "X"
    else:
        board_shoots[row][col] = "O"
        result = "O"
    return result

# Inizializzazione dell'AI
ai = BattleshipAI(boardSize)
ai_difficulty = 'smart'  # Può essere 'random', 'hunting', o 'smart'

def get_computer_move_random(board_shoots, board_size):
    """Seleziona una mossa casuale tra le celle non ancora colpite"""
    available_cells = []
    for row in range(board_size):
        for col in range(board_size):
            if board_shoots[row][col] == empty_cell:
                available_cells.append((row, col))
    
    if available_cells:
        return random.choice(available_cells)
    else:
        # Fallback nel caso (improbabile) in cui tutte le celle siano state colpite
        return random.randint(0, board_size - 1), random.randint(0, board_size - 1)

def get_computer_move_hunting(board_shoots, board_size):
    """
    Versione migliorata dell'algoritmo di caccia.
    Cerca celle colpite e poi colpisce le celle adiacenti.
    """
    # Cerca celle colpite ("X")
    hits = []
    for row in range(board_size):
        for col in range(board_size):
            if board_shoots[row][col] == 'X':
                hits.append((row, col))
    
    if hits:
        # Trova le celle disponibili adiacenti a una cella colpita
        for hit_row, hit_col in hits:
            # Controlla le celle in orizzontale e verticale (non in diagonale)
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                r, c = hit_row + dr, hit_col + dc
                if 0 <= r < board_size and 0 <= c < board_size and board_shoots[r][c] == empty_cell:
                    return r, c
    
    # Se non ci sono celle colpite o non ci sono celle adiacenti disponibili, scegli casualmente
    return get_computer_move_random(board_shoots, board_size)

def get_computer_move(board_shoots, board_size):
    """
    Seleziona la strategia di AI in base alla difficoltà impostata
    """
    global ai_difficulty
    
    if ai_difficulty == 'random':
        return get_computer_move_random(board_shoots, board_size)
    elif ai_difficulty == 'hunting':
        return get_computer_move_hunting(board_shoots, board_size)
    elif ai_difficulty == 'smart':
        # Usa l'AI avanzata
        return ai.get_move()
    else:
        # Fallback al metodo casuale
        return get_computer_move_random(board_shoots, board_size)

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
    
    # Reset dell'AI
    ai.reset()
    
    # Posiziona le navi per entrambi i giocatori
    for ship in ships:
        # Posiziona nave per il giocatore 1
        while True:
            direction = random.choice(["horizontal", "vertical"])
            row = random.randint(0, boardSize-1)
            col = random.randint(0, boardSize-1)
            if can_place_ship(ship, board1, row, col, direction):          
                place_ship(fleet1, ship, board1, row, col, direction, uuid.uuid4().int)
                break
        
        # Posiziona nave per il giocatore 2 (computer)
        while True:
            direction = random.choice(["horizontal", "vertical"])
            row = random.randint(0, boardSize-1)
            col = random.randint(0, boardSize-1)
            if can_place_ship(ship, board2, row, col, direction):
                place_ship(fleet2, ship, board2, row, col, direction, uuid.uuid4().int)
                break

# Crea l'interfaccia grafica web
init()
app = Flask(__name__, template_folder="templates")

@app.route("/")
def index():
    if fleet2.checkVictory():
        return render_template("index.html", 
                               board1=create_table(board1), 
                               board1_shoots=create_table(board1_shoots), 
                               board2=create_table(board2), 
                               winner="Player 1", 
                               fleet1=fleet1, 
                               fleet2=fleet2)
    if fleet1.checkVictory():
        return render_template("index.html", 
                               board1=create_table(board1), 
                               board1_shoots=create_table(board1_shoots), 
                               board2=create_table(board2), 
                               winner="Computer", 
                               fleet1=fleet1, 
                               fleet2=fleet2)
    
    return render_template("index.html", 
                           board1=create_table(board1), 
                           board1_shoots=create_table(board1_shoots), 
                           board2=create_table(board2), 
                           hit1=hit1, 
                           fleet1=fleet1, 
                           fleet2=fleet2,
                           ai_difficulty=ai_difficulty)

@app.context_processor
def utility_processor():
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

# Filtro personalizzato per convertire un numero in carattere ASCII
@app.template_filter('num_to_ascii')
def num_to_ascii(num):
    """
    Converte un numero nel carattere ASCII corrispondente.
    
    Args:
        num (int): Il numero da convertire.
        
    Returns:
        str: Il carattere ASCII corrispondente al numero.
    """
    return chr(num + 65)

@app.route("/place", methods=["GET", "POST"])
def place():
    # Controlla il metodo della richiesta
    if request.method == "GET":
        # Renderizza il form per posizionare la nave
        return render_template("place.html", ships=ships, boardSize=boardSize)

    # Recupera i dati della richiesta
    player = request.form["player"]
    ship = int(request.form["ship"])
    row = int(request.form["row"])
    col = int(request.form["col"])
    direction = request.form["direction"]

    if player == "0":
        # Controlla se la nave può essere posizionata
        if not can_place_ship(ship, board1, row, col, direction):
            return render_template("place.html", error="Invalid ship placement", ships=ships,  boardSize=boardSize)
        else:
             # Posiziona la nave
            place_ship(fleet1, ship, board1, row, col, direction, uuid.uuid4().int)
    else:
        # Controlla se la nave può essere posizionata
        if not can_place_ship(ship, board2, row, col, direction):
            return render_template("place.html", error="Invalid ship placement", ships=ships,  boardSize=boardSize)
        else:
             # Posiziona la nave
            place_ship(fleet2, ship, board2, row, col, direction, uuid.uuid4().int)
   
    # Aggiorna l'interfaccia grafica
    return redirect("/")


@app.route("/fire", methods=["POST"])
def fire():
    global hit1, hit2
    # Player 1
    hit1 += 1
    row = None
    col = None
    
    # Ottieni le coordinate del colpo del giocatore
    if "row" in request.form and "col" in request.form:
        row = int(request.form["row"])