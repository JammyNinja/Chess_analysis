import pandas as pd
import numpy as np
import os
import requests
import re #regex for extracting info from pgn string

from dotenv import load_dotenv
load_dotenv()

#api call dates
START_MONTH= os.getenv("START_MONTH")
END_MONTH = pd.to_datetime('today').strftime('%Y-%m')
# END_MONTH= os.getenv("END_MONTH") #uncomment to get one year of chess games (2023)
#api call user info
USERNAME = os.getenv("USERNAME")
USER_EMAIL = os.getenv("USER_EMAIL")
#data directory for saving df as csv
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def make_api_request(api_date):
    """ gets all user games from that month
        calls chess.com API endpoint below
        username and email taken from env
        eg: https://api.chess.com/pub/player/jammyninja/games/2024/05
    """

    #weird params, thanks to
    #https://www.chess.com/clubs/forum/view/error-403-in-member-profile?page=2
    params = {"User-Agent" : f'username: {USERNAME},  email: {USER_EMAIL}'}

    # url = f'https://api.chess.com/pub/player/jammyninja/games/{year}/{month}'
    url = f'https://api.chess.com/pub/player/jammyninja/games/{api_date}'
    response_json = requests.get(url,headers=params).json()

    #json object contains only one key, which is games
    return response_json["games"]

def get_all_games_list():
    """
        Calls Chess.com API to get all games that the user played in each month in
        the period specified by START_DATE, END_DATE in env
        Returns list of all raw games found
    """

    def make_api_dates(start_date=START_MONTH, end_date=END_MONTH):
        """ returns list of tuples where the sub dicts contain year and month
            eg: [('06', '2023'), ('07', '2023')...]
        """
        api_dates = []

        date_range_loop = pd.date_range(start=start_date, end=end_date,freq='MS', inclusive="both")

        for date in date_range_loop:
            api_date = date.strftime('%Y/%m')
            api_dates.append(api_date)

        return api_dates

    api_dates = make_api_dates()
    all_games = []

    for api_date in api_dates:
        print("getting", api_date)
        games = make_api_request(api_date)
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

    #extract moves

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

def get_filepath(df_name, descriptor, start_date=START_MONTH, end_date=END_MONTH):
    #2024-01-01 -> 2024-01
    filename = f"{df_name}_{start_date}_to_{end_date}_{descriptor}.csv"

    filepath = os.path.join(DATA_DIR,filename)

    return filepath

def save_file(df, df_name="all_games", descriptor="raw"):
    filepath_out = get_filepath(df_name=df_name, descriptor=descriptor)

    #also in main()
    if os.path.exists(filepath_out):
        print(f"file {filepath_out} already exists, NOT saving!")
    else:
        df.to_csv(filepath_out, index=False)
        print("saved file as", filepath_out)


def load_file(df_name="all_games", descriptor="raw"):

    filepath_in = get_filepath(df_name=df_name, descriptor=descriptor)

    if os.path.exists(filepath_in):
        df = pd.read_csv(filepath_in)
    else:
        download = input("file {filepath_in} not found, would you like to create it?\ny/n:")
        if download.lower() == 'y':
            df = download_data()
            return df
        else:
            return

def download_data():
    all_games_list = get_all_games_list()
    all_games_df = all_games_list_to_df(all_games_list)

    save_file(all_games_df,  df_name="all_games", descriptor="raw")

    return all_games_df

def get_data(df_name="all_games", descriptor="raw"):
    """
        Usage:
            all_games_df_raw = get_data(df_name="select_games", descriptor="select_cols")
            all_games_df_raw = get_data(df_name="all_games", descriptor="raw")
    """
    print(f"""Looking for all games of chess played on Chess.com by {USERNAME}
          between {START_MONTH} and {END_MONTH}""")

    #check if file already exists
    filepath = get_filepath(df_name=df_name, descriptor=descriptor)
    if os.path.exists(filepath):
        print(f"file {filepath} already exists!")

        confirm = ''
        while confirm.lower() != 'y' and confirm.lower() != 'n':
            confirm = input("Do you want to download all games again?\n>>(Have you played more since last running this?)\ny/n:")
            # last_date = df.iloc[-1].start_time.strftime('%Y-%m')
            if confirm.lower() == 'n':
                return pd.read_csv(filepath)

    all_games_df = download_data()
    return all_games_df

if __name__ == "__main__":
    get_data()
    # get_all_games_list()
