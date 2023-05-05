import json
import os
import chess.pgn
from generation_and_evaluation import RandomSearch

if __name__ == '__main__':
    # games_folder = 'games'
    # hash_table = {}
    # for game_index, file_name in enumerate(os.listdir(games_folder)):
    #     with open(os.path.join(games_folder, file_name)) as file:
    #         game = chess.pgn.read_game(file)
    #     board = game.board()
    #     moves = tuple(game.mainline_moves())
    #     for index, move in enumerate(moves):
    #         board.push(move)
    #         generator = RandomSearch(board, depth=3, hash_table=hash_table)
    #         generator.search(10)
    #         print((game_index + index / len(moves))/len(os.listdir(games_folder)))
    #     with open('positions.json', 'w') as file:
    #         json.dump(hash_table, file)
    # print(len(hash_table))

   with open('1_200_000_positions.json') as file:
       dictionary = json.load(file)
   for _ in range(300_000):
    dictionary.popitem()
    with open('1_200_000_positions.json', 'w') as file:
        json.dump(dictionary, file)
