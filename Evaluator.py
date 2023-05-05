import chess


class Evaluator:

    def all_evaluation_functions(self):
        eval_functions = [
                self.evaluate_piece_activity,
                self.evaluate_piece_mobility,
                self.evaluate_king_safety,
                self.evaluate_pawn_structure,
                self.evaluate_discs_stability,
                self.evaluate_material_balance,
                self.evaluate_space_control]
        return eval_functions

    """
       The evaluation metrics used are: material balance, pawn structure, king safety, and piece mobility.
       """
    def evaluate_byAllMetrics(self, fen):

        # Load the FEN positio
        material_balance = self.evaluate_material_balance(fen)
        pawn_structure = self.evaluate_pawn_structure(fen)
        king_safety = self.evaluate_king_safety(fen)
        piece_activity = self.evaluate_piece_activity(fen)
        piece_mobility = self.evaluate_piece_mobility(fen)
        space_control = self.evaluate_space_control(fen)
        # Return the evaluation metrics as a dictionary
        return {"material_balance": material_balance, "pawn_structure": pawn_structure,
                "king_safety": king_safety, "piece_mobility": piece_mobility,
                "piece_activity": piece_activity, "space_control": space_control}

    """
    It calculates the material balance by assigning a point value
    to each chess piece and then summing up the values for each side. 
    """

    def evaluate_material_balance(self, fen):

        # Define piece values (in centipawns)
        # Fine-tune the piece values based on your own analysis or game data.
        values = {'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000}

        # Initialize material balances for white and black to 0
        white_balance, black_balance = 0, 0

        # Split the FEN string to get the position and active color
        position, active_color, _, _, _, _ = fen.split()

        # Loop through each square in the position
        for square in position:
            # If the square contains a piece
            if square != '/' and not square.isdigit():
                # Get the piece value and add it to the appropriate balance
                piece_value = values[square.upper()]

                # Apply position-specific knowledge to adjust piece values
                # For example, in an endgame with a passed pawn, the value of the pawns may be much higher than in a typical position.
                if square == 'P' and position.count('p') == 0 and position.count('P') == 1:
                    piece_value += 100

                if square == 'p' and position.count('P') == 0 and position.count('p') == 1:
                    piece_value -= 100

                if square == 'K' and position.count('P') == 0 and position.count('p') == 0:
                    # If there are no pawns on the board, the king is more valuable in the endgame.
                    piece_value += 1000

                if square == 'k' and position.count('P') == 0 and position.count('p') == 0:
                    piece_value -= 1000

                # Add the piece value to the appropriate balance
                if square.islower():
                    black_balance += piece_value
                else:
                    white_balance += piece_value

        # If it's Black's turn to move, swap the balances
        if active_color == 'b':
            white_balance, black_balance = -black_balance, -white_balance

        return white_balance - black_balance

    """
    It evaluates the pawn structure of a given position by looking at each pawn on the board
    and calculating a score based on factors such as whether the pawn is isolated or doubled.
    """

    def evaluate_pawn_structure(self, fen):
        # Convert FEN string to board representation
        board = chess.Board(fen)

        # Define scores for each type of pawn structure
        isolated_pawn_score = -10
        doubled_pawn_score = -5
        backward_pawn_score = -8
        passed_pawn_score = 20

        # Initialize score counters
        white_pawn_score = 0
        black_pawn_score = 0

        # Evaluate each pawn on the board
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is not None and piece.piece_type == chess.PAWN:
                pawn_score = 0
                color = piece.color
                file = chess.square_file(square)
                rank = chess.square_rank(square)

                # Check for isolated pawn
                if (file > 0 and not board.has_piece(chess.PAWN, color, chess.square(file - 1, rank))) and \
                        (file < 7 and not board.has_piece(chess.PAWN, color, chess.square(file + 1, rank))):
                    pawn_score += isolated_pawn_score

                # Check for doubled pawn
                if board.pieces_mask(chess.PAWN, color) & chess.BB_FILES[file] \
                        & ~chess.BB_SQUARES[square]:
                    pawn_score += doubled_pawn_score

                # Check for backward pawn
                if color == chess.WHITE and \
                        not board.has_piece(chess.PAWN, chess.WHITE, chess.BB_RANKS[:rank]) and \
                        board.has_piece(chess.PAWN, chess.BLACK, chess.BB_RANKS[rank + 1:]):
                    pawn_score += backward_pawn_score
                elif color == chess.BLACK and \
                        not board.has_piece(chess.PAWN, chess.BLACK, chess.BB_RANKS[rank + 1:]) and \
                        board.has_piece(chess.PAWN, chess.WHITE, chess.BB_RANKS[:rank]):
                    pawn_score += backward_pawn_score

                # Check for passed pawn
                if color == chess.WHITE and \
                        not board.has_piece(chess.PAWN, chess.BLACK, chess.BB_RANKS[:rank]) and \
                        not board.has_piece(chess.PAWN, chess.WHITE, chess.BB_RANKS[rank + 1:]) and \
                        (board.attacks_mask(square) & board.pieces_mask(chess.PAWN, color)).count() == 1:
                    pawn_score += passed_pawn_score
                elif color == chess.BLACK and \
                        not board.has_piece(chess.PAWN, chess.WHITE, chess.BB_RANKS[rank + 1:]) and \
                        not board.has_piece(chess.PAWN, chess.BLACK, chess.BB_RANKS[:rank]) and \
                        (board.attacks_mask(square) & board.pieces_mask(chess.PAWN, color)).count() == 1:
                    pawn_score += passed_pawn_score

                if color == chess.WHITE:
                    white_pawn_score += pawn_score
                else:
                    black_pawn_score += pawn_score

            # Return the difference between white and black pawn scores
            return white_pawn_score - black_pawn_score

    """
    It evaluates the safety of the king by looking at factors such as the number 
    of attackers and the presence of a pawn shield.
    """

    def evaluate_king_safety(self, fen):
        # Convert FEN string to board representation
        board = chess.Board(fen)

        # Define weights for each type of king safety feature
        king_safety_weights = {
            "king_attacks": 1,
            "pawn_shield": 1,
            "pawn_storm": 1
        }

        # Initialize score counters
        white_score = 0
        black_score = 0

        # Evaluate king safety for each side
        for color in [chess.WHITE, chess.BLACK]:
            # Get king position
            king_square = board.king(color)

            # Evaluate king attacks
            king_attackers = board.attackers(not color, king_square)
            king_attacks = len(king_attackers)
            if king_attacks > 0:
                if color == chess.WHITE:
                    black_score += king_safety_weights["king_attacks"] * king_attacks
                else:
                    white_score += king_safety_weights["king_attacks"] * king_attacks

            # Evaluate pawn shield
            pawn_shield = 0
            pawn_shield_squares = chess.SquareSet()
            for square in chess.SQUARES:
                if board.piece_type_at(square) == chess.PAWN and board.color_at(square) == color:
                    pawn_shield_squares |= chess.SquareSet(square) | chess.SquareSet(
                        square + 8) | \
                                           chess.SquareSet(square + 7) | chess.SquareSet(
                        square + 9)
            pawn_shield_attackers = pawn_shield_squares & board.attackers(not color, king_square) & chess.SQUARES[
                not color]
            pawn_shield = len(pawn_shield_attackers)
            if pawn_shield > 0:
                if color == chess.WHITE:
                    black_score += king_safety_weights["pawn_shield"] * pawn_shield
                else:
                    white_score += king_safety_weights["pawn_shield"] * pawn_shield

            # Evaluate pawn storm
            pawn_storm = 0
            for file in range(0, 8):
                if board.piece_type_at(chess.square(file, 1 if color == chess.WHITE else 6)) == chess.PAWN and \
                        board.piece_type_at(chess.square(file, 2 if color == chess.WHITE else 5)) == chess.PAWN and \
                        board.color_at(chess.square(file, 1 if color == chess.WHITE else 6)) == color:
                    pawn_storm_squares = chess.SquareSet()
                    pawn_storm_squares |= chess.SquareSet(chess.square(file, 2 if color == chess.WHITE else 5)) | \
                                          chess.SquareSet(chess.square(file, 3 if color == chess.WHITE else 4))
                    pawn_storm_attackers = pawn_storm_squares & board.attackers(not color, king_square) & chess.SQUARES[
                        not color]
                    pawn_storm = len(pawn_storm_attackers)
                    if pawn_storm > 0:
                        if color == chess.WHITE:
                            black_score += king_safety_weights["pawn_storm"] * pawn_storm
                        else:
                            white_score += king_safety_weights["pawn_storm"] * pawn_storm

        # Return score difference
        return white_score - black_score

    """
    It evaluates the mobility of each piece on the board by looking
    at the number of legal moves available to each piece.
    """

    def evaluate_piece_mobility(self, fen):
        board = chess.Board(fen)
        # Evaluate the piece mobility based on the number and quality of legal moves available to each piece
        white_mobility_score = self.count_piece_mobility(board, chess.WHITE)
        black_mobility_score = self.count_piece_mobility(board, chess.BLACK)
        return white_mobility_score - black_mobility_score

    """
     It evaluates the activity of the pieces based on the number of squares attacked by the pieces of each color. 
    """

    def evaluate_piece_activity(self, fen):
        board = chess.Board(fen)
        white_pieces = board.pieces(chess.PAWN, chess.WHITE) | board.pieces(chess.KNIGHT, chess.WHITE) | board.pieces(
            chess.BISHOP, chess.WHITE) | board.pieces(chess.ROOK, chess.WHITE) | board.pieces(chess.QUEEN, chess.WHITE)
        black_pieces = board.pieces(chess.PAWN, chess.BLACK) | board.pieces(chess.KNIGHT, chess.BLACK) | board.pieces(
            chess.BISHOP, chess.BLACK) | board.pieces(chess.ROOK, chess.BLACK) | board.pieces(chess.QUEEN, chess.BLACK)
        white_activity = sum([len(list(board.attacks(square))) for square in white_pieces])
        black_activity = sum([len(list(board.attacks(square))) for square in black_pieces])
        return white_activity - black_activity

    def count_piece_mobility(self, board, color):
        mobility_score = 0
        for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
            for square in board.pieces(piece_type, color):
                piece_mobility = len(list(board.generate_legal_moves(square)))
        mobility_score += self.piece_value(
            piece_type) * piece_mobility / 28  # Normalize the score by the maximum possible mobility
        return mobility_score

    """
    It calculates the number of attacks that each player has on six central squares
    (e4, d4, c4, f4, g4, h4 for white, and e5, d5, c5, f5, g5, h5 for black), and returns the difference between them as the control score. 
    """
    def evaluate_space_control(self, fen):
        board = chess.Board(fen)
        white_control = len(list(board.attacks(chess.E4))) + len(list(board.attacks(chess.D4))) + len(
            list(board.attacks(chess.C4))) + len(list(board.attacks(chess.F4))) + len(
            list(board.attacks(chess.G4))) + len(list(board.attacks(chess.H4)))
        black_control = len(list(board.attacks(chess.E5))) + len(list(board.attacks(chess.D5))) + len(
            list(board.attacks(chess.C5))) + len(list(board.attacks(chess.F5))) + len(
            list(board.attacks(chess.G5))) + len(list(board.attacks(chess.H5)))
        return white_control - black_control



    """
    Stable discs are the discs on the board that can't be flipped by the opponent,
    which means they are in a safe position and can't be taken back.
    The function calculates the difference between the number of white stable discs and the number of black stable discs, and returns the result.
    """
    def evaluate_discs_stability(self, fen):
        board = chess.Board(fen)
        white_stable_discs, black_stable_discs = self.get_stable_discs(board, chess.WHITE)
        return white_stable_discs - black_stable_discs

    def piece_value(self, piece_type):
        if piece_type == chess.PAWN:
            return 1
        elif piece_type == chess.KNIGHT:
            return 3
        elif piece_type == chess.BISHOP:
            return 3
        elif piece_type == chess.ROOK:
            return 5
        elif piece_type == chess.QUEEN:
            return 9

    def get_stable_discs(self, board, color):
        stable_discs = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is not None and piece.color == color:
                if self.is_stable_disc(board, square):
                    stable_discs += 1
        opponent_color = chess.WHITE if color == chess.BLACK else chess.BLACK
        opponent_stable_discs = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is not None and piece.color == opponent_color:
                if self.is_stable_disc(board, square):
                    opponent_stable_discs += 1
        return stable_discs, opponent_stable_discs

    def is_stable_disc(self, board, square):
        piece = board.piece_at(square)
        if piece is None:
            return False
        color = piece.color
        rank, file = chess.square_rank(square), chess.square_file(square)
        # Check horizontal stability
        for f in range(0, file):
            if board.piece_at(chess.square(rank, f)) is None:
                break
        else:
            return True
        for f in range(file + 1, 8):
            if board.piece_at(chess.square(rank, f)) is None:
                break
        else:
            return True
        # Check vertical stability
        for r in range(0, rank):
            if board.piece_at(chess.square(r, file)) is None:
                break
        else:
            return True
        for r in range(rank + 1, 8):
            if board.piece_at(chess.square(r, file)) is None:
                break
        else:
            return True
        # Check diagonal stability
        for d in range(1, min(file + 1, rank + 1)):
            if board.piece_at(chess.square(rank - d, file - d)) is None:
                break
        else:
            return True
        for d in range(1, min(8 - file, 8 - rank)):
            if board.piece_at(chess.square(rank + d, file + d)) is None:
                break
        else:
            return True
        for d in range(1, min(8 - file, rank + 1)):
            if board.piece_at(chess.square(rank - d, file + d)) is None:
                break
        else:
            return True
        for d in range(1, min(file + 1, 8 - rank)):
            if board.piece_at(chess.square(rank + d, file - d)) is None:
                break
        else:
            return True
        return False
