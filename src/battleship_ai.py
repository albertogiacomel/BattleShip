import numpy as np
import random
from collections import deque

class BattleshipAI:
    """
    Classe che implementa un'intelligenza artificiale per il gioco Battaglia Navale
    utilizzando una combinazione di strategie: pattern recognition, probability hunting,
    e memoria delle mosse precedenti.
    """
    def __init__(self, board_size):
        self.board_size = board_size
        self.probability_map = np.ones((board_size, board_size))
        self.shots = np.zeros((board_size, board_size), dtype=bool)  # False = non sparato, True = già sparato
        self.hits = np.zeros((board_size, board_size), dtype=bool)   # True se colpito
        self.ships_to_find = [1, 1, 1, 1, 2, 2, 2, 3, 3, 4]  # Lunghezze delle navi da trovare
        self.hunting_mode = False
        self.hit_queue = deque()  # Coda di coordinate colpite da esplorare
        self.destroyed_ships = []  # Coordinate delle navi distrutte
        self.last_hit = None
        self.hit_direction = None
        self.consecutive_hits = []
    
    def reset(self):
        """Resetta lo stato dell'AI per una nuova partita"""
        self.probability_map = np.ones((self.board_size, self.board_size))
        self.shots = np.zeros((self.board_size, self.board_size), dtype=bool)
        self.hits = np.zeros((self.board_size, self.board_size), dtype=bool)
        self.ships_to_find = [1, 1, 1, 1, 2, 2, 2, 3, 3, 4]
        self.hunting_mode = False
        self.hit_queue = deque()
        self.destroyed_ships = []
        self.last_hit = None
        self.hit_direction = None
        self.consecutive_hits = []
    
    def update(self, row, col, result):
        """
        Aggiorna lo stato dell'AI con il risultato dell'ultimo colpo
        
        Args:
            row (int): Riga del colpo
            col (int): Colonna del colpo
            result (str): Risultato del colpo ('X' = colpito, 'O' = acqua, 'A' = affondato)
        """
        # Aggiorna la mappa di probabilità
        self.shots[row, col] = True
        self.probability_map[row, col] = 0  # Zero probabilità per celle già colpite
        
        if result == 'X':  # Colpito ma non affondato
            self.hits[row, col] = True
            self.hunting_mode = True
            self.hit_queue.append((row, col))
            self.last_hit = (row, col)
            self.consecutive_hits.append((row, col))
            self._update_probabilities_after_hit(row, col)
            
        elif result == 'A':  # Colpito e affondato
            self.hits[row, col] = True
            ship_coords = set(self.consecutive_hits + [(row, col)])
            self.destroyed_ships.append(list(ship_coords))
            
            # Rimuovi la nave dalle navi da trovare
            ship_size = len(ship_coords)
            if ship_size in self.ships_to_find:
                self.ships_to_find.remove(ship_size)
            
            # Aggiorna le probabilità intorno alla nave affondata
            self._update_probabilities_after_sink(ship_coords)
            
            # Resetta lo stato di caccia
            self.consecutive_hits = []
            self.last_hit = None
            self.hit_direction = None
            
            # Se non ci sono più navi colpite ma non affondate, torna in modalità ricerca
            if len(self.hit_queue) == 0:
                self.hunting_mode = False
                
        elif result == 'O':  # Acqua
            if self.hit_direction is not None:
                # Se stavamo seguendo una direzione ma abbiamo mancato, cambia direzione
                self.hit_direction = self._opposite_direction(self.hit_direction)
    
    def get_move(self):
        """
        Determina la prossima mossa dell'AI
        
        Returns:
            tuple: Coordinate (riga, colonna) della prossima mossa
        """
        if self.hunting_mode:
            return self._get_hunting_move()
        else:
            return self._get_searching_move()
    
    def _get_hunting_move(self):
        """
        Determina la prossima mossa in modalità caccia (quando una nave è stata colpita)
        
        Returns:
            tuple: Coordinate (riga, colonna) della prossima mossa
        """
        # Se abbiamo colpi consecutivi, seguiamo la direzione
        if len(self.consecutive_hits) >= 2:
            return self._follow_direction()
        
        # Altrimenti, esploriamo intorno all'ultimo colpo
        if self.hit_queue:
            hit_row, hit_col = self.hit_queue[0]
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # destra, giù, sinistra, su
            random.shuffle(directions)
            
            for dr, dc in directions:
                r, c = hit_row + dr, hit_col + dc
                if self._is_valid_move(r, c):
                    return r, c
            
            # Se non ci sono mosse valide intorno a questa cella, rimuovila dalla coda
            self.hit_queue.popleft()
            return self._get_hunting_move()
        
        # Se la coda è vuota, torniamo in modalità ricerca
        self.hunting_mode = False
        return self._get_searching_move()
    
    def _follow_direction(self):
        """
        Continua a sparare nella direzione della nave colpita
        
        Returns:
            tuple: Coordinate (riga, colonna) della prossima mossa
        """
        if self.hit_direction is None:
            # Determina la direzione dai colpi consecutivi
            hits = self.consecutive_hits
            if hits[0][0] == hits[1][0]:  # Stessa riga, direzione orizzontale
                self.hit_direction = (0, 1) if hits[1][1] > hits[0][1] else (0, -1)
            else:  # Stessa colonna, direzione verticale
                self.hit_direction = (1, 0) if hits[1][0] > hits[0][0] else (-1, 0)
        
        # Prova a continuare nella direzione corrente
        last_r, last_c = self.consecutive_hits[-1]
        dr, dc = self.hit_direction
        r, c = last_r + dr, last_c + dc
        
        if self._is_valid_move(r, c):
            return r, c
        
        # Se non possiamo continuare in quella direzione, proviamo la direzione opposta
        self.hit_direction = self._opposite_direction(self.hit_direction)
        first_r, first_c = self.consecutive_hits[0]
        dr, dc = self.hit_direction
        r, c = first_r + dr, first_c + dc
        
        if self._is_valid_move(r, c):
            return r, c
        
        # Se non possiamo andare in nessuna direzione, torniamo alla caccia normale
        self.hit_direction = None
        if self.hit_queue:
            self.hit_queue.popleft()  # Rimuoviamo il primo elemento e proviamo di nuovo
        return self._get_hunting_move()
    
    def _get_searching_move(self):
        """
        Determina la prossima mossa in modalità ricerca (quando non ci sono navi colpite)
        
        Returns:
            tuple: Coordinate (riga, colonna) della prossima mossa
        """
        # Aggiorna la mappa di probabilità
        self._update_probability_map()
        
        # Trova la cella con la probabilità più alta
        flat_index = np.argmax(self.probability_map)
        row, col = flat_index // self.board_size, flat_index % self.board_size
        
        return row, col
    
    def _update_probability_map(self):
        """Aggiorna la mappa di probabilità basata sulle navi rimanenti e le celle colpite"""
        # Resetta la mappa di probabilità
        self.probability_map = np.zeros((self.board_size, self.board_size))
        
        # Per ogni nave rimanente, calcola la probabilità che possa stare in ogni posizione
        for ship_length in self.ships_to_find:
            ship_probabilities = self._calculate_ship_probabilities(ship_length)
            self.probability_map += ship_probabilities
        
        # Azzera le probabilità delle celle già colpite
        self.probability_map[self.shots] = 0
        
        # Pattern a scacchiera per navi di lunghezza 1
        if 1 in self.ships_to_find:
            self._apply_checkerboard_pattern()
    
    def _calculate_ship_probabilities(self, ship_length):
        """
        Calcola la probabilità che una nave di lunghezza ship_length possa stare in ogni posizione
        
        Args:
            ship_length (int): Lunghezza della nave
            
        Returns:
            np.array: Mappa di probabilità per questa nave
        """
        ship_prob = np.zeros((self.board_size, self.board_size))
        
        # Controlla le posizioni orizzontali
        for row in range(self.board_size):
            for col in range(self.board_size - ship_length + 1):
                if self._can_place_ship_horizontal(row, col, ship_length):
                    ship_prob[row, col:col+ship_length] += 1
        
        # Controlla le posizioni verticali
        for row in range(self.board_size - ship_length + 1):
            for col in range(self.board_size):
                if self._can_place_ship_vertical(row, col, ship_length):
                    ship_prob[row:row+ship_length, col] += 1
        
        return ship_prob
    
    def _can_place_ship_horizontal(self, row, col, length):
        """Controlla se una nave può essere posizionata orizzontalmente"""
        # Controlla che non ci siano colpi mancati nel range
        for c in range(col, col + length):
            if self.shots[row, c] and not self.hits[row, c]:
                return False
        
        # Controlla che ci sia spazio attorno alla nave
        for r in range(max(0, row - 1), min(self.board_size, row + 2)):
            for c in range(max(0, col - 1), min(self.board_size, col + length + 1)):
                # Se c'è una cella colpita e affondata vicino, non possiamo piazzare qui
                if (r, c) in [coord for ship in self.destroyed_ships for coord in ship]:
                    return False
        
        return True
    
    def _can_place_ship_vertical(self, row, col, length):
        """Controlla se una nave può essere posizionata verticalmente"""
        # Controlla che non ci siano colpi mancati nel range
        for r in range(row, row + length):
            if self.shots[r, col] and not self.hits[r, col]:
                return False
        
        # Controlla che ci sia spazio attorno alla nave
        for r in range(max(0, row - 1), min(self.board_size, row + length + 1)):
            for c in range(max(0, col - 1), min(self.board_size, col + 2)):
                # Se c'è una cella colpita e affondata vicino, non possiamo piazzare qui
                if (r, c) in [coord for ship in self.destroyed_ships for coord in ship]:
                    return False
        
        return True
    
    def _apply_checkerboard_pattern(self):
        """
        Applica un pattern a scacchiera alla mappa di probabilità.
        Questo è utile per trovare navi di lunghezza 1, poiché possiamo escludere
        metà delle celle del tabellone.
        """
        checker = np.zeros((self.board_size, self.board_size))
        checker[::2, ::2] = 1  # Celle pari-pari
        checker[1::2, 1::2] = 1  # Celle dispari-dispari
        
        # Aumenta la probabilità nelle celle del pattern a scacchiera
        self.probability_map *= (1 + 0.5 * checker)
    
    def _update_probabilities_after_hit(self, row, col):
        """
        Aggiorna le probabilità dopo un colpo andato a segno
        
        Args:
            row (int): Riga del colpo
            col (int): Colonna del colpo
        """
        # Aumenta la probabilità delle celle adiacenti
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            r, c = row + dr, col + dc
            if 0 <= r < self.board_size and 0 <= c < self.board_size and not self.shots[r, c]:
                self.probability_map[r, c] *= 2
    
    def _update_probabilities_after_sink(self, ship_coords):
        """
        Aggiorna le probabilità dopo aver affondato una nave
        
        Args:
            ship_coords (set): Coordinate della nave affondata
        """
        # Azzeramento delle probabilità intorno alla nave affondata
        for row, col in ship_coords:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    r, c = row + dr, col + dc
                    if 0 <= r < self.board_size and 0 <= c < self.board_size:
                        self.probability_map[r, c] = 0
                        
            # Marca la cella della nave come colpita
            self.shots[row, col] = True
            self.hits[row, col] = True
    
    def _is_valid_move(self, row, col):
        """Controlla se una mossa è valida (dentro il tabellone e non ancora colpita)"""
        return (0 <= row < self.board_size and 
                0 <= col < self.board_size and 
                not self.shots[row, col])
    
    def _opposite_direction(self, direction):
        """Restituisce la direzione opposta"""
        dr, dc = direction
        return (-dr, -dc)
