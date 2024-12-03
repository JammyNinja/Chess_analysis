# Chess_analysis

## Welcome
My name is Louis, and I studied Data Science at Le Wagon, where I have now been teaching Data Science and Analytics for over a year!.

I like to play chess in my spare time, where I oscillate between 1200-1400 bullet. That's 1 minute chess.

As my rating fluctuates, I have naturally been wondering if there are any patterns to be found in games that I win or lose.

Enter: this product, (name_tbd)

## Quick Start
Log on to website_incoming.com and provide your Chess.com username to receive a page of analysis of your games
### Just Looking?
Have a read through one of [the Jupyter notebooks](https://github.com/JammyNinja/Chess_analysis/tree/main/explore/notebooks) to see some sample analyses without leaving github

## What's the big idea?
I want to make a product where a user can see some general trends in their own play.
I am thinking of simple questions like:
- When I castle, and my opponent does not, do I tend to win?
  - Do I tend to win games where I castle after move 10?
- Do I win more of my games in the morning, or on Tuesdays?
- Do I tend to win my games on time,resignation or checkmate?
  - Does that differ against higher/lower rated opponents?
- The list goes on, and I would appreciate any ideas you may like to suggest!

### What it isn't
It isn't as good as [Chess.com's insights page](https://www.chess.com/insights) - they have done this much better than I could hope to...
They are able to go into more depth thanks to Stockfish (A chess engine, better than the best humans) and £9/month from the users who get access to it!
Plus, you know... It's kind of their job :p

## Why
What started as genuine curiosity about my own chess games, has turned a way to flex my data analysis/science/engineering muscles.
Primarily this is to be something I am proud of, a look-I-made-that to show others and myself what I can do!
Certainly wouldn't hurt if any prospective employers were looking at this 👀

## How
For the back end, I am running a FastAPI out of a docker container hosted on Google Cloud Platform.
I am currently using Streamlit for the front end, although I would like to try Django in the future.

I am massively leaning on data made available by [Chess.com's API](https://www.chess.com/news/view/published-data-api) - thank you to the dev community over there!.

## Who
Me 😇 Louis, a long-time chess enthusiast and short-time data professional.

- [Email](mailto:louis.auger.pro@gmail.com)
- [LinkedIn](https://www.linkedin.com/in/louis-auger-data-london/)

## In the future:
- Integrate Lichess games
- Use stockfish to analyse final positions?
