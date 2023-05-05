import chess
from stockfish import Stockfish
import random

class Node:
    def __init__(self, board):
        self.board = board
        self.visits = 0
        self.children = []


class RandomSearch:
    def __init__(self, initial_board, depth=10, hash_table=None):
        self.root = Node(initial_board)
        self.depth = depth
        self.engine = Stockfish(depth=depth)
        self.hash_table = hash_table
        if hash_table is None:
            self.hash_table = {}
        self.add_position(initial_board)

    def add_position(self, board):
        fen = board.fen()
        if fen in self.hash_table:
            return
        self.engine.set_fen_position(fen)
        self.hash_table[fen] = self.engine.get_evaluation()['value']

    def select(self, node):
        while node.children:
            node = random.choice(node.children)
        return node

    def expand(self, node):
        for move in node.board.legal_moves:
            new_board = node.board.copy()
            new_board.push(move)
            new_node = Node(new_board)
            node.children.append(new_node)
            self.add_position(new_board)

    def search(self, n_iterations):
        for i in range(n_iterations):
            node = self.root
            while True:
                fen = node.board.fen()
                if fen not in self.hash_table:
                    self.add_position(node.board)
                    break
                if not node.children:
                    self.expand(node)
                    break
                node = self.select(node)
        return self.hash_table


if __name__ == '__main__':
    board = chess.Board()
    mcts = RandomSearch(board)
    position_dict = mcts.search(100)
    print(f"Number of positions: {len(position_dict)}")
    pass
