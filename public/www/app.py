import streamlit as st
import requests
import os
from dotenv import load_dotenv

#load env variables
load_dotenv()
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

def make_api_request(username):
    """
        gets summary stats for given username
    """
    mvp_url = f"https://api.chess.com/pub/player/{username}/stats"
    headers = {"User-Agent" : f'username: {ADMIN_USERNAME},  email: {ADMIN_EMAIL}'}

    response = requests.get(mvp_url, headers=headers)
    # print(response.url)

    return response.json()

def display_user_stats(response, username):
    """
        displays summary stats for given username
    """
    #output intro line
    chesscom_user_url = f"https://www.chess.com/member/{username}"
    st.markdown(f"[{username}'s]({chesscom_user_url}) stats:")

    for key,value in response.items():
        if key.startswith("chess"):
            time_control = key.split("_")[-1]
            best_rating = value['best']['rating']
            report = f"Your best {time_control} rating is {best_rating}"
            st.write(report)

def on_enter():
    username = st.session_state['username']
    # st.session_state["username"] = username
    response = make_api_request(username)

    with st.session_state['stats_output']:
        display_user_stats(response, username)

def main():
    chess_com_link = "https://www.chess.com"
    st.markdown(f'Welcome to my app, where you can see some analysis of your [Chess.com]({chess_com_link}) games')

    st.text_input(
        label="Please enter your chess.com username:",
        key = "username",
        on_change=on_enter
    )

    #initialise container with empty to actually hold the place
    st.session_state['stats_output'] = st.container()
    with st.session_state['stats_output']:
        st.empty()


#begin
main()
#run with: streamlit run app.py
