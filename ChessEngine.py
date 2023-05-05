
class ChessEngine:

    def __init__(self):
        self.evaluate_func = None

    def set_eval_function(self, evaluate_func):
        self.evaluate_func = evaluate_func

    def play(self, board, depth, evaluate_func):
        self.set_eval_function(evaluate_func)
        return self.alpha_beta_search(board, depth, alpha=-float('inf'), beta=float('inf'), maximizing_player=True)

    def play_killerMoves(self, board, depth, evaluate_func):
        self.set_eval_function(evaluate_func)
        killer_moves = [[{}] for _ in range(depth + 1)]
        return self.alpha_beta_search_killerMoves(board, depth, alpha=-float('inf'), beta=float('inf'), maximizing_player=True, killer_moves=killer_moves)

    def alpha_beta_search(self, board, depth, alpha, beta, maximizing_player):
        if depth == 0 or board.is_game_over():
            return self.evaluate_func(board.fen())

        if maximizing_player:
            value = -float('inf')
            for move in board.legal_moves:
                board.push(move)
                value = max(value, self.alpha_beta_search(board, depth - 1, alpha, beta, False))
                board.pop()
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return value
        else:
            value = float('inf')
            for move in board.legal_moves:
                board.push(move)
                value = min(value, self.alpha_beta_search(board, depth - 1, alpha, beta, True))
                board.pop()
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value

    def alpha_beta_search_killerMoves(self, board, depth, alpha, beta, maximizing_player, killer_moves):
        if depth == 0 or board.is_game_over():
            return self.evaluate_func(board.fen())

        if maximizing_player:
            value = -float('inf')
            for move in board.legal_moves:
                board.push(move)
                if move in killer_moves[depth][0]:
                    value = max(value, self.alpha_beta_search_killerMoves(board, depth - 1, alpha, beta, False, killer_moves))
                else:
                    value = max(value, self.alpha_beta_search_killerMoves(board, depth - 1, alpha, beta, False, killer_moves))
                board.pop()
                alpha = max(alpha, value)
                if beta <= alpha:
                    # Add the move to the killer moves array for the current ply
                    killer_moves[depth][0][move] = killer_moves[depth][0].get(move, 0) + 1
                    break
            return value
        else:
            value = float('inf')
            for move in board.legal_moves:
                board.push(move)
                if move in killer_moves[depth][0]:
                    value = min(value, self.alpha_beta_search_killerMoves(board, depth - 1, alpha, beta, True, killer_moves))
                else:
                    value = min(value, self.alpha_beta_search_killerMoves(board, depth - 1, alpha, beta, True, killer_moves))
                board.pop()
                beta = min(beta, value)
                if beta <= alpha:
                    # Add the move to the killer moves array for the current ply
                    killer_moves[depth][0][move] = killer_moves[depth][0].get(move, 0) + 1
                    break
            return value
