#data cleaning
import pandas as pd
import re #extracting from pgn string

#file manips
import pickle
import os

#pipelines
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer

from public.back.api.src.data import load_pickle, save_pickle, load_sample_raw_data

#fixed filepaths
path_to_data = os.path.join(os.path.dirname(__file__), "..", "data")
clean_pipe_fname = "clean_pipeline.pkl"
clean_pipe_path = os.path.join(path_to_data, "pipes", clean_pipe_fname)

def clean_raw_data(raw_data, save=True):
    print("cleaning raw data...")
    # raw_data = load_raw_data_from_file()
    clean_pipe = pickle.load(open(clean_pipe_path,"rb"))
    clean_data = clean_pipe.transform(raw_data)

    clean_path = os.path.join(path_to_data, "sample_clean.pkl")

    if save:
        save_pickle(clean_data, clean_path)
    else:
        print("NOT saving clean data")

    return clean_data

def create_clean_sample_data():
    #grab raw pickle file
    raw_data = load_sample_raw_data()

    #clean games + save clean
    clean_data = clean_raw_data(raw_data, save=True)

    # return clean_games
    return clean_data

#PIPELINE FUNCS
def type_conversion(df):
    """converts date columns to datetime"""
    dt_cols = ["date"]
    for col in dt_cols:
        df[col] = pd.to_datetime(df[col], format='%d/%m/%Y')
    return df

def extract_game_data(game, USERNAME = "JammyNinja"):
    """
        Used in clean_pipe
        converts a game as received from chess.com API JSON to pandas Series

        try out the raw form at:
            https://api.chess.com/pub/player/jammyninja/games/2023/01
    """
    # display(game)
    game_dict = {}

    game_pgn = game["pgn"]
    game_dict["result"] = game_pgn.split("}")[-1].strip()
    game_dict['time_control'] = game["time_control"]
    game_dict['time_class'] = game["time_class"]
    game_dict['rules'] = game["rules"] #to exclude any chess960 or other that may have been played

    #extract date from pgn 'date' field
    date_pattern = r'\[Date\s+"(\d{4}.\d{2}.\d{2})"\]'
    date_str = re.search(date_pattern, game_pgn).group(1)
    game_dict['date'] = pd.to_datetime(date_str).strftime('%d/%m/%Y')

    user_colour = "white" if game["white"]["username"] == USERNAME else "black"
    opp_colour = "black" if user_colour == "white" else "white" #used to save time below

    game_dict["user_colour"] = user_colour
    game_dict['opp_username'] = game[opp_colour]["username"]

    game_dict['user_rating'] = game[user_colour]["rating"]
    game_dict['opp_rating'] = game[opp_colour]["rating"]

    game_dict['user_result'] = game[user_colour]["result"]
    game_dict['opp_result'] = game[opp_colour]["result"]

    return game_dict

def games_to_pandas(raw_games_list):
    clean_list = [extract_game_data(game) for game in raw_games_list]
    return pd.DataFrame(clean_list)

def create_clean_pipe():
    clean_pipe = Pipeline([
        ("raw list to df" , FunctionTransformer(games_to_pandas)),
        ("dtypes", FunctionTransformer(type_conversion))
    ])

    #save clean pipe as pickle
    # pickle.dump(clean_pipe, open(clean_pipe_path, "wb"))
    save_pickle(clean_pipe, clean_pipe_path)

    #saved clean pipe
    print("saved clean pipe to", clean_pipe_path)


def load_clean_pipe():
    clean_pipe = pickle.load(open(clean_pipe_path,"rb"))
    return clean_pipe

if __name__ == "__main__":
    # create_clean_pipe()
    print(clean_raw_data())
