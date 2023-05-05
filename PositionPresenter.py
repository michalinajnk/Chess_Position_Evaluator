from colorama import Fore, Back, Style

class PositionPresenter:
    def __init__(self, fenPosition):
       self.fenPosition = fenPosition

    def setPosition(self, fenPosition):
        self.fenPosition = fenPosition

    def display(self):
        fen_fields = self.fenPosition.split()

        # Extract the board state
        board_state = fen_fields[0]
        rows = board_state.split("/")
        board = []
        for row in rows:
            board_row = []
            for square in row:
                if square.isdigit():
                    # Add an empty square for each number
                    for i in range(int(square)):
                        board_row.append(".")
                else:
                    # Add the piece to the board
                    board_row.append(square)
            board.append(board_row)

        # Extract other information
        turn = fen_fields[1]
        castling_rights = fen_fields[2]
        en_passant_target = fen_fields[3]
        halfmove_clock = fen_fields[4]
        fullmove_number = fen_fields[5]


        # Print the board state
        # Print the board state
        for row in board:
            print(row)
