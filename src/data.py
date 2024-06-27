import pandas as pd
import numpy as np
import os
import requests
import re #regex for extracting info from pgn string

def make_api_request(month, year, username="JammyNinja"):
    """ gets all user games from that month
        calls chess.com API endpoint below
        eg: https://api.chess.com/pub/player/jammyninja/games/2024/05
    """

    #weird params, thanks to
    #https://www.chess.com/clubs/forum/view/error-403-in-member-profile?page=2
    params = {"User-Agent" : f'username: {username},  email: jammyninja95@gmail.com'}

    url = f'https://api.chess.com/pub/player/jammyninja/games/{year}/{month}'
    response_json = requests.get(url,headers=params).json()

    #json object contains only one key, which is games
    return response_json["games"]

def get_all_games_list(start_date="2023-01-01", end_date="2024-06-01"):
    """
        Calls Chess.com API to get all games that the user played in each month for the period specified
        Returns list of all raw games found
    """

    def make_api_dates(start_date="2023-01-01", end_date="2024-06-01"):
        """ returns list of tuples where the sub dicts contain year and month
            eg: [('06', 2023), ('07', '2023')]
        """
        out_dates = []
        month_map = {1: '01', 2: '02', 3: '03', 4: '04', 5: '05', 6: '06',
                    7: '07', 8: '08', 9: '09', 10: '10', 11: '11', 12: '12' }

        for date in pd.date_range(start=start_date, end=end_date,freq='M'):
            month = month_map[date.month]
            year  = str(date.year)
            out_dates.append((month, year))

        return out_dates

    months_to_loop = make_api_dates(start_date, end_date)
    all_games = []

    for month, year in months_to_loop:
        print(f"getting month {year}-{month}")
        games = make_api_request(month,year)
        all_games += games

    print(f"Downloaded a total of {len(all_games)} games.")

    return all_games

def clean_game(game):
    """
        Cleans one raw game as received from API
        Mostly extracting information from the pgn string
        output clean dictionary made from most of the local variables in locals()
    """
    #get the moves
    game_pgn = game["pgn"]
    moves = "".join(game_pgn.split("\n\n")[1].split("}")[:-1])
    result = game_pgn.split("}")[-1].strip()

    #opening (eco = Encyclopaedia of Chess Openings)
    eco_pattern = r'\[ECO\s+"[^"]*"\]'
    opening_exists = True if len(re.findall(eco_pattern, game_pgn)) >= 1 else False
    if opening_exists:
        eco_url_pattern = r'\[ECOUrl\s+"[^"]*"\]' #[ECOUrl xyz]
        opening_code = re.search(r'"[^"]*"',re.search(eco_pattern, game_pgn)[0])[0].strip('"')
        opening_name = re.search(eco_url_pattern, game_pgn)[0].split('/')[-1][:-2]
    else:
        opening_code = np.nan
        opening_name = np.nan
    del opening_exists #refactor

    #get meta/admin
    url = game["url"]
    final_position_fen = game["fen"]
    rated = game["rated"]
    time_control = game["time_control"]
    time_class = game["time_class"]
    rules = game["rules"] #to exclude any chess960 or other that may have been played

    #extract start/end datetime
    end_time = pd.to_datetime(game["end_time"], unit="s")
    date = end_time.date()
    time_pattern = r'\[StartTime\s+"(\d{2}:\d{2}:\d{2})"\]'
    start_time = re.search(time_pattern, game_pgn)[1]
    #wrong date for daily games #refactor
    start_time = pd.to_datetime(str(date) + " " + start_time)

    #extract players info
    white_rating = game["white"]["rating"]
    white_result = game["white"]["result"]
    white_username = game["white"]["username"]

    black_rating = game["black"]["rating"]
    black_result = game["black"]["result"]
    black_username = game["black"]["username"]

    #wrap it up for output
    game_dict = {}
    vars_to_loop = [var for var in locals()
                    if not (var.startswith("game") or var.endswith("pattern"))]

    for variable in vars_to_loop:
        game_dict[variable] = locals()[variable]

    return game_dict

def all_games_list_to_df(all_games_list):
    """
        Cleans each game in the list.
        Returns dataframe of clean games
    """
    clean_games = []
    for game in all_games_list:
        clean = clean_game(game)
        clean_games.append(clean)
    clean_games_df = pd.DataFrame.from_dict(clean_games)

    col_order = ['date','start_time','end_time',
                 'time_class', 'time_control', 'rated', 'rules', 'url',
                 'moves', 'final_position_fen',
                 'opening_code', 'opening_name',
                 'white_username', 'black_username',
                 'result',
                 'white_rating', 'black_rating',
                 'white_result', 'black_result']

    return clean_games_df[col_order]

def get_filepath(start_date, end_date):
    #2024-01-01 -> 2024-01
    filename = f"all_games_{start_date[:7]}_to_{end_date[:7]}_raw.csv"

    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    filepath = os.path.join(data_dir,filename)

    return filepath

def save_file(df, start_date, end_date):

    filepath = get_filepath(start_date,end_date)
    df.to_csv(filepath, index=False)
    print(f"File saved in {filepath}")

def get_data():

    start_date="2023-01-01"
    end_date  ="2024-06-01"
    username = "JammyNinja"

    print(f"Looking for all games of chess played on Chess.com by {username} between {start_date} and {end_date}")

    #check if file already exists
    filepath = get_filepath(start_date, end_date)
    if os.path.exists(filepath):
        print(f"file {filepath} already exists!")

    else:
        all_games_list = get_all_games_list(start_date=start_date, end_date=end_date)
        all_games_df = all_games_list_to_df(all_games_list)
        save_file(all_games_df, start_date, end_date)

if __name__ == "__main__":
    get_data()
