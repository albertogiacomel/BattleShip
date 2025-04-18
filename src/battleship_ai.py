import numpy as np
import random

class BattleshipAI:
    def __init__(self, board_size=10):
        """
        Inizializza l'IA per la battaglia navale.
        
        Args:
            board_size (int): La dimensione del tabellone.
        """
        self.board_size = board_size
        self.probability_map = np.ones((board_size, board_size))
        self.shots_taken = np.zeros((board_size, board_size), dtype=bool)
        self.hits = []
        self.potential_targets = []
        self.mode = "hunt"  # Due modalità: "hunt" (caccia) o "target" (bersaglio)
        self.last_hit = None
        self.direction = None
        self.consecutive_hits = 0
        self.remaining_ships = []
        self.ship_sizes = []
    
    def reset(self, ship_sizes=[1, 1, 1, 1, 2, 2, 2, 3, 3, 4]):
        """
        Resetta l'IA per una nuova partita.
        
        Args:
            ship_sizes (list): Le dimensioni delle navi rimaste nel gioco.
        """
        self.probability_map = np.ones((self.board_size, self.board_size))
        self.shots_taken = np.zeros((self.board_size, self.board_size), dtype=bool)
        self.hits = []
        self.potential_targets = []
        self.mode = "hunt"
        self.last_hit = None
        self.direction = None
        self.consecutive_hits = 0
        self.remaining_ships = ship_sizes.copy()
        self.ship_sizes = ship_sizes.copy()
        
    def update_ship_sunk(self, ship_size):
        """
        Aggiorna lo stato quando una nave viene affondata.
        
        Args:
            ship_size (int): La dimensione della nave affondata.
        """
        if ship_size in self.remaining_ships:
            self.remaining_ships.remove(ship_size)
        
        # Resetta lo stato di tracking dopo l'affondamento
        self.hits = []
        self.potential_targets = []
        self.mode = "hunt"
        self.last_hit = None
        self.direction = None
        self.consecutive_hits = 0
        
        # Aggiorna la mappa di probabilità
        self._update_probability_map()
    
    def register_shot_result(self, row, col, result):
        """
        Registra il risultato di un colpo sparato dall'IA.
        
        Args:
            row (int): La riga del colpo.
            col (int): La colonna del colpo.
            result (str): Il risultato del colpo ('X' per colpito, 'A' per affondato, 'O' per mancato).
        """
        self.shots_taken[row, col] = True
        
        if result == 'X':  # Colpito
            self.hits.append((row, col))
            self.mode = "target"
            self.last_hit = (row, col)
            self.consecutive_hits += 1
            
            # Aggiorna i potenziali bersagli
            self._update_potential_targets(row, col)
            
        elif result == 'A':  # Affondato
            self.hits.append((row, col))
            # Cerca di determinare la dimensione della nave affondata
            ship_size = self.consecutive_hits + 1
            self.update_ship_sunk(ship_size)
            
        else:  # Mancato
            # Se siamo in modalità bersaglio e abbiamo una direzione
            if self.mode == "target" and self.direction:
                # Cambia direzione
                self._change_direction()
        
        # Aggiorna la mappa delle probabilità
        self._update_probability_map()
    
    def _update_potential_targets(self, row, col):
        """
        Aggiorna i potenziali bersagli dopo un colpo andato a segno.
        
        Args:
            row (int): La riga dell'ultimo colpo andato a segno.
            col (int): La colonna dell'ultimo colpo andato a segno.
        """
        self.potential_targets = []
        
        # Se abbiamo più di un colpo andato a segno, determina la direzione
        if len(self.hits) > 1:
            self._determine_direction()
            
            # Se abbiamo una direzione, aggiungi solo i bersagli in quella direzione
            if self.direction:
                if self.direction == "horizontal":
                    # Aggiungi i bersagli a sinistra e a destra
                    left = col - 1
                    right = col + 1
                    
                    while left >= 0 and not self.shots_taken[row, left]:
                        self.potential_targets.append((row, left))
                        left -= 1
                    
                    while right < self.board_size and not self.shots_taken[row, right]:
                        self.potential_targets.append((row, right))
                        right += 1
                else:  # vertical
                    # Aggiungi i bersagli sopra e sotto
                    up = row - 1
                    down = row + 1
                    
                    while up >= 0 and not self.shots_taken[up, col]:
                        self.potential_targets.append((up, col))
                        up -= 1
                    
                    while down < self.board_size and not self.shots_taken[down, col]:
                        self.potential_targets.append((down, col))
                        down += 1
                return
        
        # Se non abbiamo una direzione, aggiungi tutti i bersagli adiacenti
        # Sopra
        if row > 0 and not self.shots_taken[row-1, col]:
            self.potential_targets.append((row-1, col))
        # Sotto
        if row < self.board_size-1 and not self.shots_taken[row+1, col]:
            self.potential_targets.append((row+1, col))
        # Sinistra
        if col > 0 and not self.shots_taken[row, col-1]:
            self.potential_targets.append((row, col-1))
        # Destra
        if col < self.board_size-1 and not self.shots_taken[row, col+1]:
            self.potential_targets.append((row, col+1))
    
    def _determine_direction(self):
        """
        Determina la direzione della nave colpita.
        """
        # Controlla se tutti i colpi sono sulla stessa riga
        rows = [hit[0] for hit in self.hits]
        cols = [hit[1] for hit in self.hits]
        
        if len(set(rows)) == 1:
            self.direction = "horizontal"
        elif len(set(cols)) == 1:
            self.direction = "vertical"
    
    def _change_direction(self):
        """
        Cambia la direzione di attacco quando necessario.
        """
        # Se la direzione corrente non funziona, prova l'altra
        if self.direction == "horizontal":
            self.direction = "vertical"
        else:
            self.direction = "horizontal"
        
        # Aggiorna i potenziali bersagli
        if self.last_hit:
            self._update_potential_targets(self.last_hit[0], self.last_hit[1])
    
    def _update_probability_map(self):
        """
        Aggiorna la mappa delle probabilità in base alle navi rimanenti e ai colpi effettuati.
        """
        # Resetta la mappa delle probabilità
        self.probability_map = np.ones((self.board_size, self.board_size))
        
        # Imposta a zero le celle dove abbiamo già sparato
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.shots_taken[i, j]:
                    self.probability_map[i, j] = 0
        
        # Per ogni dimensione di nave rimasta
        for ship_size in self.remaining_ships:
            # Aggiorna le probabilità orizzontali
            for row in range(self.board_size):
                for col in range(self.board_size - ship_size + 1):
                    if all(not self.shots_taken[row, col+i] or (row, col+i) in self.hits for i in range(ship_size)):
                        for i in range(ship_size):
                            if not self.shots_taken[row, col+i]:
                                self.probability_map[row, col+i] += 1
            
            # Aggiorna le probabilità verticali
            for col in range(self.board_size):
                for row in range(self.board_size - ship_size + 1):
                    if all(not self.shots_taken[row+i, col] or (row+i, col) in self.hits for i in range(ship_size)):
                        for i in range(ship_size):
                            if not self.shots_taken[row+i, col]:
                                self.probability_map[row+i, col] += 1
    
    def get_move(self):
        """
        Ottiene la prossima mossa dell'IA.
        
        Returns:
            tuple: Una tupla contenente la riga e la colonna del prossimo colpo.
        """
        # Se siamo in modalità bersaglio e abbiamo potenziali bersagli
        if self.mode == "target" and self.potential_targets:
            # Scegli un bersaglio dalla lista
            return self.potential_targets.pop(0)
        
        # Altrimenti, scegli la cella con la probabilità più alta
        best_probability = 0
        best_moves = []
        
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.probability_map[i, j] > best_probability and not self.shots_taken[i, j]:
                    best_probability = self.probability_map[i, j]
                    best_moves = [(i, j)]
                elif self.probability_map[i, j] == best_probability and not self.shots_taken[i, j]:
                    best_moves.append((i, j))
        
        # Se abbiamo mosse valide, scegliamo una casualmente
        if best_moves:
            return random.choice(best_moves)
        
        # Se non abbiamo mosse valide, scegliamo una cella casuale che non è stata ancora colpita
        available_moves = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                if not self.shots_taken[i, j]:
                    available_moves.append((i, j))
        
        if available_moves:
            return random.choice(available_moves)
        
        # Se non ci sono mosse disponibili, restituisci una casuale (non dovrebbe mai accadere)
        return (random.randint(0, self.board_size-1), random.randint(0, self.board_size-1))