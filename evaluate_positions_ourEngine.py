import json
import chess
from multiprocessing import Pool, Manager
from tqdm import tqdm
from Evaluator import Evaluator
from ChessEngine import ChessEngine

def compute_score(args):
    key, board_fen, evaluator, chessEngine, depth = args
    board = chess.Board(key)
    scores = {}
    for eval_func in evaluator.all_evaluation_functions():
        score = chessEngine.play_killerMoves(board=board, depth=depth, evaluate_func=eval_func)
        scores[str(eval_func)] = score
    return (key, scores)

if __name__ == '__main__':
    evaluator = Evaluator()
    chessEngine = ChessEngine()
    # Set depth
    depth = 3

    # Define the input and output file paths
    input_file_path = '1_200_000_positions.json'
    output_file_path = 'our_engine_depth4.json'

    # Load the input JSON file
    with open(input_file_path, 'r') as input_file:
        data = json.load(input_file)

    # Create a shared dictionary to store the results
    manager = Manager()
    results = manager.dict()

    # Split the data into chunks for multiprocessing
    chunk_size = 1000
    chunks = [dict(list(data.items())[i:i+chunk_size]) for i in range(0, len(data), chunk_size)]

    # Create a pool of worker processes
    with Pool() as pool:
        # Iterate through the chunks and compute the score for each 'fen' value using all evaluation functions in parallel
        for chunk_idx, chunk in enumerate(chunks):
            args_list = [(key, board_fen, evaluator, chessEngine, depth) for key, board_fen in chunk.items()]
            for key, scores in tqdm(pool.imap_unordered(compute_score, args_list), total=len(chunk)):
                results[key] = scores

        # Write the results dictionary to a new JSON file
        with open(output_file_path, 'w') as output_file:
            for key, value in tqdm(results.items(), total=len(results)):
                json.dump({key: value}, output_file)
                output_file.write('\n')
