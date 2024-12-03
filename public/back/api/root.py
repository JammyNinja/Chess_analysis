from fastapi import FastAPI
import os
import requests
from dotenv import load_dotenv

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


#http://localhost:8000/
