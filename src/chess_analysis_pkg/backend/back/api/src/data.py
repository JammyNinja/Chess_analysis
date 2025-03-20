#this file contains functions to get raw games from chess.com api
#also also cleans the

#imports
import os
import pickle

path_to_data = os.path.join(os.path.dirname(__file__), "..", "data")
sample_clean_filename = "sample_clean.pkl"
sample_raw_filename = "sample_raw.pkl"

def load_pickle(fname = "sample_raw.pkl"):
    with open(os.path.join(path_to_data, fname), "rb") as file:
        raw_data = pickle.load(file)
    return raw_data

def save_pickle(py_obj, filename):
    filepath = os.path.join(path_to_data, filename)
    with open(filepath, "wb") as file:
        pickle.dump(py_obj, file)

    print(f"saved {filename} to {filepath}")

def load_sample_raw_data():
    return load_pickle(sample_raw_filename)

def load_sample_clean_data():
    return load_pickle(sample_clean_filename)
