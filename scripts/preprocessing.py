import pandas as pd
import numpy as np #nan
import os
from dotenv import load_dotenv

from data import get_filepath, save_file

load_dotenv()

def process_moves(row_in):
    """
        Looks at 'moves' column which is pgn string, extracts each players moves and when they castled
        ['move_numbers', 'white_moves', 'white_clock', 'black_moves', 'black_clock',
        'w_cstl_side', 'w_cstl_move', 'b_cstl_side', 'b_cstl_move']
    """
    #.apply() complained that it was float when didn't manually convert to string?
    moves = str(row_in["moves"])
    moves = moves.replace("{","")

    move_nums = moves.split()[::8]
    white_moves = moves.split()[1::8]
    black_moves = moves.split()[5::8]

    white_clock = [m[:-1] for m in moves.split()[3::8] ]
    black_clock = [m[:-1] for m in moves.split()[7::8] ]

    if len(black_moves) < len(white_moves):
        black_moves.append(np.nan)
        black_clock.append(np.nan)

    #deal with castling
    w_castled, w_castled_side = 0,np.nan
    b_castled, b_castled_side = 0, np.nan

    for move_num, w_move, b_move in zip(move_nums, white_moves, black_moves):
        move_num = int(move_num[:-1]) #7. -> 7

        if w_move == "O-O":
            w_castled_side = "King"
            w_castled = move_num
        elif w_move == "O-O-O":
            w_castled_side = "Queen"
            w_castled = move_num

        if b_move == "O-O":
            b_castled_side = "King"
            b_castled = move_num
        elif b_move == "O-O-O":
            b_castled_side = "Queen"
            b_castled = move_num

#     print(f"white castled {w_castled_side} side on move {w_castled}")
#     print(f"black castled {b_castled_side} side on move {b_castled}")

    row_out = {
        "move_numbers" : move_nums,
        "white_moves"  : white_moves,
        "white_clock"  : white_clock,
        "black_moves"  : black_moves,
        "black_clock"  : black_clock,

        "w_cstl_side" : w_castled_side,
        "w_cstl_move" : w_castled,
        "b_cstl_side" : b_castled_side,
        "b_cstl_move" : b_castled
    }

    return row_out

def process_winner_rating(row):
    """
        Creates new columns:
        'higher_rated_colour',  'winner_rating_diff', 'user_rating_diff',
        'user_win', 'user_colour','winner'
    """
    winner = "white" if row["result"] == "1-0" else "black" if row["result"] == "0-1" else "DRAW"

    w_rating, b_rating = row["white_rating"], row["black_rating"] #reduce line size

    higher_rated = "white" if w_rating > b_rating else "black" #assumes draw is good for black

    user_colour = "white" if row["white_username"] == "JammyNinja" else "black"

    def did_user_win(user = "JammyNinja"):
        if winner == "white" and row["white_username"] == user:
            return True
        if winner == "black" and row["black_username"] == user:
            return True
        if winner == "draw":
            return "DRAW"
        return False

    user_win = did_user_win()

    winner_rating_diff = w_rating - b_rating if winner == "white" else b_rating - w_rating
    user_rating_diff = w_rating - b_rating if user_colour == "white" else b_rating - w_rating

    row_out = {
        "higher_rated_colour" : higher_rated,
        "winner"       : winner,
        "winner_rating_diff"  : winner_rating_diff,
        "user_rating_diff" : user_rating_diff,
        "user_win"     : user_win,
        "user_colour" : user_colour
    }

    return row_out

def user_castled(row):
    """
    Creates columns containing bool indicating if user or opponent castled
    """
    user_castled = False
    opp_castled = False

    w_cstl_move = row["w_cstl_move"]
    b_cstl_move = row["b_cstl_move"]

    if row["user_colour"] == "white":
        if w_cstl_move > 0:
            user_castled = True
            user_cstl_diff = w_cstl_move - b_cstl_move
        if b_cstl_move > 0:
            opp_castled = True
    else: #user is black
        if b_cstl_move > 0:
            user_castled = True
            user_cstl_diff = b_cstl_move - w_cstl_move
        if w_cstl_move > 0:
            opp_castled = True

    # TODO
    # #create columns to do with who castled first
    # #null if user didn't castle
    # if not user_castled:
    #     user_cstl_diff = np.nan
    # #WHAT IF I CASTLE AND THEY DONT - cant subtract?

    return {
        "user_castled" : user_castled,
        "opp_castled" : opp_castled,
#             "user_cstl_diff" : user_cstl_diff,
#             "winner_cstl_diff" : win_cstl_diff
    }

def pieces_final_position(game):
    """
    starts with eighth rank, first file to eighth
    white is uppercase, black lowercase
    p: pawn, r: rook, n: knight, b: bishop, q : queen, k : king
    ['winner_ttl_pieces_count', 'loser_ttl_pieces_count', 'winner_pawns_count', 'loser_pawns_count',
    'winner_pieces_only_count', 'loser_pieces_only_count', 'pieces_count_diff', 'pawns_count_diff',
    'winner_material_ttl', 'loser_material_ttl', 'winner_pcs', 'loser_pcs']
    """
    fen = game["final_position_fen"]
    fin_pos = fen.split()[0]

    board = fin_pos.split("/")
    ttl_white_pcs, ttl_black_pcs = 0,0

    #white pieces are uppercase, black lowercase
    w_pcs = [piece for piece in "".join(board) if piece.isupper()]
    b_pcs = [piece for piece in "".join(board) if piece.islower()]
    #count total pieces (including king), and also count just the pawns
    ttl_white_pcs = len(w_pcs)
    ttl_black_pcs = len(b_pcs)
    ttl_white_pwns = len([p for p in w_pcs if p == "P"])
    ttl_black_pwns = len([p for p in b_pcs if p == "p"])

    #create material counts
    def sum_piece_values(pcs):
        """
        Accepts as input b_pcs or w_bcs and outputs the total value of what's given.
        """
        # dictionary for piece values
        chess_piece_values = {
            'P': 1,  # Pawn
            'N': 3,  # Knight
            'B': 3,  # Bishop
            'R': 5,  # Rook
            'Q': 9,  # Queen
            'K': 0,  # King (often considered to have infinite value, but in practical terms, it is 0 for valuation purposes)
        }
        count = 0
        for i in pcs:
            count += chess_piece_values[i.upper()]
        return count

    w_material_count=sum_piece_values(w_pcs)
    b_material_count=sum_piece_values(b_pcs)

    if game.winner == "white":
        win_pcs, lose_pcs = w_pcs, b_pcs
        winner_ttl_pieces_count = ttl_white_pcs
        loser_ttl_pieces_count = ttl_black_pcs
        winner_pawns_count = ttl_white_pwns
        loser_pawns_count = ttl_black_pwns
        winner_material_ttl = w_material_count
        loser_material_ttl = b_material_count

    else: #includes DRAWs
        win_pcs, lose_pcs = b_pcs, w_pcs
        winner_ttl_pieces_count = ttl_black_pcs
        loser_ttl_pieces_count = ttl_white_pcs
        winner_pawns_count = ttl_black_pwns
        loser_pawns_count = ttl_white_pwns
        winner_material_ttl = b_material_count
        loser_material_ttl = w_material_count

    #count of just the major/minor pieces, -1 to not include King,
    winner_pieces_only_count = winner_ttl_pieces_count - winner_pawns_count -1
    loser_pieces_only_count = loser_ttl_pieces_count - loser_pawns_count -1

    out = {
        #pieces on the board including king
        "winner_ttl_pieces_count" : winner_ttl_pieces_count,
        "loser_ttl_pieces_count" : loser_ttl_pieces_count,
#       #count pawns
        "winner_pawns_count" : winner_pawns_count,
        "loser_pawns_count" : loser_pawns_count,
        #count of just the major/minor pieces
        "winner_pieces_only_count" : winner_pieces_only_count,
        "loser_pieces_only_count" : loser_pieces_only_count,
        "pieces_count_diff" : winner_pieces_only_count - loser_pieces_only_count,
        "pawns_count_diff" : winner_pawns_count - loser_pawns_count,
        #count the material worth
        "winner_material_ttl" : winner_material_ttl,
        "loser_material_ttl" : loser_material_ttl,
        #might as well throw the pieces in too
        "winner_pcs" : win_pcs,
        "loser_pcs"  : lose_pcs,
    }

    return out

def add_new_columns(games_df, printing=True):
    """
        Adds the columns created by the functions above to the df passed in
    """
    orig_cols = games_df.columns

    #uses winner_rating function to calculate the winner and rating swing
    win_rating_cols = games_df.apply(process_winner_rating, axis="columns", result_type="expand")

    #uses process moves function to break down the moves into w/b, and when castled
    move_cols =       games_df.apply(process_moves, axis="columns",result_type="expand")

    #add the above columns for now, so that the below funcs know who the winner was
    games_df = pd.concat([win_rating_cols, move_cols, games_df], axis=1)

    #create final position columns, gets the material left on the board
    final_pos_cols = games_df.apply(pieces_final_position, axis="columns",result_type="expand")

    #now calculate castle cols using some of the above columns
    cstl_cols =       games_df.apply(user_castled, axis="columns", result_type="expand")
    games_df = pd.concat([games_df, cstl_cols, final_pos_cols], axis=1)

    if printing:
        print("Created win/rating columns:\n" + "\n".join([f"- {col}" for col in win_rating_cols]))
        print("Created moves columns:\n" + "\n".join([f"- {col}" for col in move_cols]))
        print("Created final position columns:\n" + "\n".join([f"- {col}" for col in final_pos_cols]))
        print("Created castling columns:\n" + "\n".join([f"- {col}" for col in cstl_cols]))
        print("\nStarted with:\n" + "\n".join([f"- {col}" for col in orig_cols]))
    return games_df

def order_columns(df):
    """ Re orders the columns for later saving"""
    cols_order_all = [
        #meta
        'date', 'start_time', 'end_time',
        'time_class', 'time_control', 'rated', 'rules',
        'url', 'moves',
        'opening_code', 'opening_name',
        'white_username', 'black_username',
        'white_clock', 'black_clock',

        #ratings/results
        'white_rating', 'black_rating',
        'result', 'white_result', 'black_result',
        'higher_rated_colour', 'winner', 'winner_rating_diff',
        'user_rating_diff', 'user_win', 'user_colour', 'move_numbers',

        #moves
        'white_moves',  'black_moves',
        'w_cstl_side', 'w_cstl_move',
        'b_cstl_side', 'b_cstl_move',
        'user_castled', 'opp_castled',

        #final position
        'final_position_fen',
        'winner_ttl_pieces_count','loser_ttl_pieces_count',
        'winner_pawns_count', 'loser_pawns_count',
        'winner_pieces_only_count', 'loser_pieces_only_count',
        'pieces_count_diff', 'pawns_count_diff',
        'winner_material_ttl', 'loser_material_ttl',
        'winner_pcs', 'loser_pcs'
    ]

    cols_pre = df.columns
    df = df[cols_order_all]

    #check to see if any columns were missed, will happen when adding brancd new columns
    removed_cols = [col for col in cols_pre if col not in cols_order_all]
    if removed_cols:
        print("You have excluded the following columns while re-ordering...\n" + "\n".join([f"- {col}" for col in removed_cols]))
        print("Was that on purpose? 👀")

    return df

def select_columns(df, select_cols=None):
    if not select_cols:
        select_cols = [
            #metadata
                'date', 'url',
                'start_time', 'end_time',
                'time_class', 'time_control',
            #   'rated', 'rules', #used to filter out unwanted games
                'white_username', 'black_username', "user_colour",
                #ratings/result
                'result', 'winner', 'higher_rated_colour',
                'white_rating', 'black_rating',
                'white_result', 'black_result',
                'winner_rating_diff', "user_rating_diff",
                #specific moves of the game
                'opening_name', 'opening_code',
                'w_cstl_side', 'w_cstl_move',
                'b_cstl_side', 'b_cstl_move',
                'user_castled', 'opp_castled',
                #final position stats
                'winner_ttl_pieces_count', 'loser_ttl_pieces_count',
                'winner_pawns_count', 'loser_pawns_count',
                'winner_pieces_only_count', 'loser_pieces_only_count',
                'pieces_count_diff', 'pawns_count_diff',
                'winner_material_ttl', 'loser_material_ttl',
                'winner_pcs', 'loser_pcs',
                #target
                'user_win'
        ]
    removed_cols = [col for col in df.columns if col not in select_cols]
    if removed_cols:
        print("You have excluded the following columns:\n" + "\n".join([f"- {c}" for c in removed_cols]))

    return df[select_cols]

def exclude_games(df, diff_max = 400):
    #if True, remove corresponding games
    constraints = {
        "chess960" : True,
        "daily" : True,
        "unrated" : True,
        "rating": True,
        "drawn" : False
    }

    queries = {
        #"title" : [ False_query, True_query] -> [to remove, to keep]
        "chess960" : ["rules != 'chess'", "rules == 'chess'"],
        "unrated" : ["rated != True", "rated == True"],
        "daily" : ["time_class == 'daily'", "time_class != 'daily'"],
        "rating" : [f"abs(winner_rating_diff) > {diff_max}", f"abs(winner_rating_diff) <= {diff_max}"],
        "drawn" :["winner == 'DRAW'", "winner != 'DRAW'"]
    }

    selected_games_df = df.copy()

    for constraint, exclude in constraints.items():
        exclude_df = df.query(queries[constraint][0])
        include_df = selected_games_df.query(queries[constraint][1])
        suffix = "include"

        if exclude:
            selected_games_df = include_df
            suffix="exclude"

        if constraint != "rating":
            print(f"Found {len(exclude_df)} {constraint} games to {suffix}")
        else:
            print(f"Found {len(exclude_df)} games with a rating difference over {diff_max} to {suffix}")

    print(f"\nExcluded a total of {len(df) - len(selected_games_df)} rows due to constraints")
    print(f"Leaving {len(selected_games_df)} games to work with")

    return selected_games_df

#TODO test not excluding, test rating change
def main():
    START_DATE= os.getenv("START_DATE")
    END_DATE  = os.getenv("END_DATE")

    filepath = get_filepath(prefix="all_games", suffix="raw", start_date=START_DATE, end_date=END_DATE)
    all_games_raw_df = pd.read_csv(filepath)

    all_games_new_cols_df = add_new_columns(all_games_raw_df)
    all_games_new_cols_df = order_columns(all_games_new_cols_df)

    #save df with all cols and rows to file
    save_file(all_games_new_cols_df, prefix="all_games", suffix= "all_cols")

    selected_games_df = exclude_games(all_games_new_cols_df)
    selected_games_df = select_columns(selected_games_df)

    print("selected_df shape:", selected_games_df.shape)

    #save this df to file
    save_file(selected_games_df, prefix="select_games",suffix= "select_cols")

if __name__ == "__main__":
    main()
