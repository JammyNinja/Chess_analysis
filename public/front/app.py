import streamlit as st
import requests
import os
from dotenv import load_dotenv

#load env variables
load_dotenv()

def make_api_request_streamlit(username):
    """
        gets summary stats for given username
        makes the request internally
        just to get things up and running
    """
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

    mvp_url = f"https://api.chess.com/pub/player/{username}/stats"
    headers = {"User-Agent" : f'username: {ADMIN_USERNAME},  email: {ADMIN_EMAIL}'}

    response = requests.get(mvp_url, headers=headers)
    # print(response.url)

    return response.json()


def make_api_request_uvicorn(endpoint, params = {}, port = 8000):
    """
        uses api endpoint at localhost to get user stats
    """

    url = f"http://localhost:{port}/{endpoint}"#user_stats"

    # params = {
    #     "username" : username
    # }

    response = requests.get(url, params=params)
    print(response.url)

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

def display_mvp_analysis(avg_opponent):
    #thanks to username_input button in main()
    username = st.session_state['username']
    st.markdown(f"The average opponent rating of {username} is: {round(avg_opponent)}")


def display_results_by_rating():
    # endpoint = "results_by_rating"
    # response = make_api_request_uvicorn(endpoint,
    #                                     params={},
    #                                     port = os.getenv("BACK_END_PORT", 8000))
    # print(response.url)

    # rating_range_fig = response['fig']
    # image=response.content
    # st.pyplot(rating_range_fig)
    
    endpoint = "test_image"
    port = os.getenv("BACK_END_PORT", 8000)
    image_url = f"http://localhost:{port}/{endpoint}"

    with st.session_state['output_display']:
        st.image(image_url)


def on_enter_show_user_ratings():
    #thanks to username_input button in main()
    username = st.session_state['username']
    endpoint="user_stats"
    params = {"username" : username}
    response = make_api_request_uvicorn(endpoint,
                                        params,
                                        port = os.getenv("BACK_END_PORT", 8000))

    with st.session_state['output_display']:
        display_user_stats(response, username)

def on_enter_show_mvp_analysis():

    port = os.getenv("BACK_END_PORT", 8000)
    endpoint="mvp"
    params={}

    #uncomment to enable
    response = make_api_request_uvicorn(endpoint,params,port)

    # avg_opponent=1069
    with st.session_state['output_display']:
        # display_user_stats(response, username)
        display_mvp_analysis(response['avg_opponent'])

def main():
    chess_com_link = "https://www.chess.com"
    st.markdown(f'Welcome to my app, where you can see some analysis of your [Chess.com]({chess_com_link}) games')

    username_input = st.text_input(
        label="Please enter your chess.com username:",
        key = "username",
        # on_change=on_enter_show_user_ratings
        # on_change=on_enter_show_mvp_analysis
        on_change=display_results_by_rating
    )

    #initialise container with empty to actually hold the place
    st.session_state['output_display'] = st.container()
    with st.session_state['output_display']:
        st.empty()


#begin
main()

#run with: streamlit run app.py
