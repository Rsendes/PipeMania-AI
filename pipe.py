"""Resolução do problema PipeMania."""

# Grupo 44:
# 96859 Filipe Resendes
# 90173 Rafael Ferreira

import sys
from sys import stdin
from copy import deepcopy

from search import (
    Problem,
    Node,
    astar_search,
    breadth_first_tree_search,
    depth_first_tree_search,
    greedy_search,
    recursive_best_first_search,
)

inverse_direction = {
    'C': 'B',
    'B': 'C',
    'E': 'D',
    'D': 'E'
}

fecho_checks = {
    'C': 'C',
    'B': 'B',
    'E': 'E',
    'D': 'D'
}

bifurcacao_checks = {
    'C': ['C', 'E', 'D'],
    'B': ['B', 'E', 'D'],
    'E': ['C', 'B', 'E'],
    'D': ['C', 'B', 'D']
}

volta_checks = {
    'C': ['C', 'E'],
    'B': ['B', 'D'],
    'E': ['B', 'E'],
    'D': ['C', 'D']
}

ligacao_checks = {
    'V': ['C', 'B'],
    'H': ['E', 'D']
}

class PipeManiaState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = PipeManiaState.state_id
        PipeManiaState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id

class Board:
    """Representação interna de um tabuleiro de PipeMania."""
    def __init__(self, board):
        self.board = board
        self.max_row = len(self.board) - 1
        self.max_col = len(self.board[0]) - 1

    class Piece:
        """Representação de uma peça do Board"""
        def __init__(self, type, direction):
            self.type = type
            self.direction = direction
            self.is_final = False
            if type != 'L':
                self.possibilities = ['C', 'B', 'E', 'D']
            else:
                self.possibilities = ['V', 'H']
        
        def remove_possibility(self, possibility):
            self.possibilities.remove(possibility)
        
        def has_possibility(self, possibility):
            return possibility in self.possibilities
        
        def is_fecho(self):
            return self.type == 'F'
        
        def is_bifurcacao(self):
            return self.type == 'B'
        
        def is_volta(self):
            return self.type == 'V'
        
        def is_ligacao(self):
            return self.type == 'L'
        
        def check_final(self):
            if not self.is_final and len(self.possibilities) == 1:
                self.is_final = True
                self.direction = self.possibilities[0]

    def get_piece(self, row: int, col: int) -> Piece:
        """Devolve a peça na respetiva posição do tabuleiro."""
        return self.board[row][col]
    
    def get_adjacent_piece(self,row: int, col: int, direction: str, ) -> Piece:
        """Devolve a peça adjacente à peça na respetiva posição do tabuleiro."""
        if direction == 'C':
            return self.get_up_piece(row, col)
        elif direction == 'B':
            return self.get_down_piece(row, col)
        elif direction == 'E':
            return self.get_left_piece(row, col)
        elif direction == 'D':
            return self.get_right_piece(row, col)
    
    def get_up_piece(self, row: int, col: int) -> Piece:
        """Devolve a peça imediatamente acima."""
        if row == 0:
            return None
        return self.board[row-1][col]
    
    def get_down_piece(self, row: int, col: int) -> Piece:
        """Devolve a peça imediatamente abaixo."""
        if row == self.max_row:
            return None
        return self.board[row+1][col]
    
    def get_right_piece(self, row: int, col: int) -> Piece:
        """Devolve a peça imediatamente à direita."""
        if col == self.max_col:
            return None
        return self.board[row][col+1]
    
    def get_left_piece(self, row: int, col: int) -> Piece:
        """Devolve a peça imediatamente à esquerda."""
        if col == 0:
            return None
        return self.board[row][col-1]
    
    def check_if_pointing(self, row: int, col: int, direction: str) -> bool:
        """Verifica se a peça adjacente á peça na respetiva posição do tabuleiro está apontada."""

        adjacent_piece = self.get_adjacent_piece(row, col, direction)

        if adjacent_piece is None:
            return False
        
        inversed_direction = inverse_direction[direction]

        if adjacent_piece.is_fecho() and inversed_direction in fecho_checks[adjacent_piece.direction]:
            return True
        elif adjacent_piece.is_bifurcacao() and inversed_direction in bifurcacao_checks[adjacent_piece.direction]:
            return True
        elif adjacent_piece.is_volta() and inversed_direction in volta_checks[adjacent_piece.direction]:
            return True
        elif adjacent_piece.is_ligacao() and inversed_direction in ligacao_checks[adjacent_piece.direction]:
            return True
        return False
    
    def check_if_poiting_possible(self, row: int, col: int, direction: str) -> bool:
        """Verifica se a peça adjacente á peça na respetiva posição do tabuleiro tem possibilidades que apontam para a peça atual."""

        adjacent_piece = self.get_adjacent_piece(row, col, direction)

        if adjacent_piece is None:
            return False
        
        inversed_direction = inverse_direction[direction]

        for possibility in adjacent_piece.possibilities:
            if adjacent_piece.is_fecho() and inversed_direction in fecho_checks[possibility]:
                return True
            elif adjacent_piece.is_bifurcacao() and inversed_direction in bifurcacao_checks[possibility]:
                return True
            elif adjacent_piece.is_volta() and inversed_direction in volta_checks[possibility]:
                return True
            elif adjacent_piece.is_ligacao() and inversed_direction in ligacao_checks[possibility]:
                return True

        return False
    
    def check_if_only_poiting_possible(self, row: int, col: int, direction: str) -> bool:
        """Verifica se a peça adjacente á peça na respetiva posição do tabuleiro apenas tem possiblidades que apontam para a peça atual."""

        adjacent_piece = self.get_adjacent_piece(row, col, direction)

        if adjacent_piece is None:
            return False
        
        inversed_direction = inverse_direction[direction]

        for possibility in adjacent_piece.possibilities:
            if adjacent_piece.is_fecho() and inversed_direction not in fecho_checks[possibility]:
                return False
            elif adjacent_piece.is_bifurcacao() and inversed_direction not in bifurcacao_checks[possibility]:
                return False
            elif adjacent_piece.is_volta() and inversed_direction not in volta_checks[possibility]:
                return False
            elif adjacent_piece.is_ligacao() and inversed_direction not in ligacao_checks[possibility]:
                return False

        return True

    def get_value(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro."""
        piece = self.board[row][col]
        return piece.type + piece.direction
    
    def get_adjacent(self, adj, row, col):
        """Devolve o valor do adjacente."""
        if adj == 'C':
            return self.get_up(row, col)
        elif adj == 'B':
            return self.get_down(row, col)
        elif adj == 'E':
            return self.get_left(row, col)
        elif adj == 'D':
            return self.get_right(row, col)
    
    def get_left(self, row: int, col: int) -> str:
        """Devolve o valor imediatamente à esquerda."""
        if col == 0:
            return None
        return self.get_value(row, col-1)
    
    def get_right(self, row: int, col: int) -> str:
        """Devolve o valor imediatamente à direita."""
        if col == self.max_col:
            return None
        return self.get_value(row, col+1)
    
    def get_up(self, row: int, col: int) -> str:    
        """Devolve o valor imediatamente acima."""
        if row == 0:
            return None
        return self.get_value(row-1, col)
    
    def get_down(self, row: int, col: int) -> str:  
        """Devolve o valor imediatamente abaixo."""
        if row == self.max_row:
            return None
        return self.get_value(row+1, col)
    
    def print_board(self):
        """Imprime o tabuleiro."""
        output = ""
        for row in range(self.max_row + 1):
            for col in range(self.max_col + 1):
                output += str(self.get_value(row, col))
                output += "\t"
            output = output.rstrip("\t")
            output += "\n"
        output = output.rstrip("\n")
        print(output)

    def parse_restrictions(self):

        def outside_check(board, piece, checks):
            """Verifica se a peça tem possibilidades ligadas ao exterior e remove-as."""
            for direction, possibilities in checks.items():
                if piece.has_possibility(direction):
                    for possibility in possibilities:
                        if board.get_adjacent(possibility, row, col) is None:
                            piece.remove_possibility(direction)
                            break
        
        def next_fecho_check(board, piece):
            """Remove as possibilidades que ligam a outro fecho."""
            directions = ['C', 'B', 'E', 'D']
            for direction in directions:
                if board.get_adjacent_piece(row, col, direction) is not None:
                    if board.get_adjacent_piece(row, col, direction).is_fecho():
                        if piece.has_possibility(direction):
                            piece.remove_possibility(direction)

        board = self
        
        for row in range(board.max_row + 1):
            for col in range(board.max_col + 1):

                piece = board.get_piece(row, col)

                if piece.is_fecho():
                    outside_check(board, piece, fecho_checks)
                    next_fecho_check(board, piece)            

                elif piece.is_bifurcacao():
                    outside_check(board, piece, bifurcacao_checks)

                elif piece.is_volta():
                    outside_check(board, piece, volta_checks)

                elif piece.is_ligacao():
                    outside_check(board, piece, ligacao_checks)

                piece.check_final()             

    @staticmethod
    def parse_instance():
        """Lê o test do standard input (stdin) que é passado como argumento
        e retorna uma instância da classe Board.
        Por exemplo:
            $ python3.8 pipe.py < tests/test-01.txt
        """
        board = []
        row = 0
        col = 0
        
        line = stdin.readline().strip()

        while(line):
            pieces = line.split('\t')
            boardRow = []

            for piece_string in pieces:
                type = piece_string[0]
                direction = piece_string[1]
                piece = Board.Piece(type, direction)
                boardRow.append(piece)
                col +=1

            board.append(boardRow)
            line = stdin.readline().strip()
            row+=1

        new_instance = Board(board)
        new_instance.parse_restrictions()
        return new_instance
            

class PipeMania(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        super().__init__(PipeManiaState(board))

    def actions(self, state: PipeManiaState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        # action = (row, col, direction) position and direction to be removed

        def remove_unmatched_directions(piece, checks, adj):
            """Remove as direções que não correspondem ao adjacente."""
            for direction in checks.keys():
                if adj not in checks[direction] and piece.has_possibility(direction) and (row, col, direction) not in actions:
                    actions.append((row, col, direction))
                
        def remove_matched_directions(piece, checks, adj):
            """Remove as direções que correspondem ao adjacente."""
            for direction in checks.keys():
                if adj in checks[direction] and piece.has_possibility(direction) and (row, col, direction) not in actions:
                    actions.append((row, col, direction))
        
        actions = []

        board = state.board                

        for row in range(board.max_row + 1):
            for col in range(board.max_col + 1):
                piece = board.get_piece(row, col)
                piece.check_final()
                if not piece.is_final:
                    for adj in ['C', 'B', 'E', 'D']:
                        if board.get_adjacent_piece(row, col, adj) is not None and board.get_adjacent_piece(row, col, adj).is_final:
                            if board.check_if_pointing(row, col, adj):
                                if piece.is_fecho():
                                    remove_unmatched_directions(piece, fecho_checks, adj)
                                elif piece.is_bifurcacao():
                                    remove_unmatched_directions(piece, bifurcacao_checks, adj)
                                elif piece.is_volta():
                                    remove_unmatched_directions(piece, volta_checks, adj)
                                elif piece.is_ligacao():
                                    remove_unmatched_directions(piece, ligacao_checks, adj)
                            else:
                                if piece.is_fecho():
                                    remove_matched_directions(piece, fecho_checks, adj)
                                elif piece.is_bifurcacao():
                                    remove_matched_directions(piece, bifurcacao_checks, adj)
                                elif piece.is_volta():
                                    remove_matched_directions(piece, volta_checks, adj)
                                elif piece.is_ligacao():
                                    remove_matched_directions(piece, ligacao_checks, adj)
                        else:
                            if not board.check_if_poiting_possible(row, col, adj):
                                if piece.is_fecho():
                                    remove_matched_directions(piece, fecho_checks, adj)
                                elif piece.is_bifurcacao():
                                    remove_matched_directions(piece, bifurcacao_checks, adj)
                                elif piece.is_volta():
                                    remove_matched_directions(piece, volta_checks, adj)
                                elif piece.is_ligacao():
                                    remove_matched_directions(piece, ligacao_checks, adj)
                            elif board.check_if_only_poiting_possible(row, col, adj):
                                if piece.is_fecho():
                                    remove_unmatched_directions(piece, fecho_checks, adj)
                                elif piece.is_bifurcacao():
                                    remove_unmatched_directions(piece, bifurcacao_checks, adj)
                                elif piece.is_volta():
                                    remove_unmatched_directions(piece, volta_checks, adj)
                                elif piece.is_ligacao():
                                    remove_unmatched_directions(piece, ligacao_checks, adj)
        
        return actions
                                                                 

    def result(self, state: PipeManiaState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""

        if action is None:
            return state

        row, col, direction = action
        piece = state.board.get_piece(row, col)
        piece.remove_possibility(direction)
        piece.check_final()

        state_copy = deepcopy(state)
        
        return state_copy

    def goal_test(self, state: PipeManiaState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        for row in range(state.board.max_row + 1):
            for col in range(state.board.max_col + 1):
                piece = state.board.get_piece(row, col)
                if not piece.is_final:
                    return False
        return True

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        cont = 0
        board = node.state.board
        for row in range(board.max_row + 1):
            for col in range(board.max_col + 1):
                piece = board.get_piece(row, col)
                if not piece.is_final:
                    cont += len(piece.possibilities)
        return cont

if __name__ == "__main__":
    # Ler o ficheiro do standard input,
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.
    board = Board.parse_instance()
    problem = PipeMania(board)
    
    result = astar_search(problem)

    if result is not None:
        result = result.state
        result.board.print_board()
