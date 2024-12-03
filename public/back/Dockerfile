FROM python:3.10.14-slim-bookworm

WORKDIR project

COPY api api

COPY requirements_api.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

#install make as slim version doesn't come with it
RUN apt-get update && apt-get install make
# COPY Makefile Makefile
# COPY .env .env
#.envrc??

#--port $BACK_END_PORT
CMD uvicorn api.root:app --host 0.0.0.0 --port $PORT
