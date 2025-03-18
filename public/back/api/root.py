from fastapi import FastAPI
import os
import requests
from dotenv import load_dotenv

from fastapi.responses import FileResponse #returning image

from public.back.api.src.analysis import mvp_analysis, get_results_by_rating_fig

#load env variables
load_dotenv()
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

app = FastAPI()

@app.get('/')
def root():
    return {
        "working" : "oui"
    }

@app.get("/test/")
def test_endpoint():
    return {
        "testing" : True
    }

@app.get("/test/arg/{arg_one}")
def test_arg(arg_one, arg_two="no arguments here"):
    """"
        Example:
        http://localhost:8000/test/arg/hello?arg_two=bonjour
    """
    return {
        "arg1" : arg_one,
        "arg2" : arg_two
    }


@app.get("/user_stats")
def get_user_stats(username):
    """
        Example usage:
        http://localhost:8000/user_stats?username=JammyNinja
    """

    mvp_url = f"https://api.chess.com/pub/player/{username}/stats"
    headers = {"User-Agent" : f'username: {ADMIN_USERNAME},  email: {ADMIN_EMAIL}'}

    response = requests.get(mvp_url, headers=headers)

    return response.json()

@app.get("/mvp")
def show_mvp_analysis():
    return mvp_analysis()

@app.get("/results_by_rating")
def results_by_rating():
    return {
        "fig" : get_results_by_rating_fig()
    }

@app.get("/test_image")
def rating_results_img():
    path_to_data = os.path.join(os.path.dirname(__file__), "data")
    test_image_filename = "test_fig.jpg"
    test_image_path = os.path.join(path_to_data, test_image_filename)
    return FileResponse(test_image_path)



#http://localhost:8000/
