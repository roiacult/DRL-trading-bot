FROM ubuntu:20.04

RUN apt update && apt upgrade -y
RUN apt install python3 python3-pip gcc g++ libffi-dev -y

WORKDIR /api

COPY requirements.txt .
# COPY ./app ./app

RUN pip install --upgrade pip && pip install -r requirements.txt


RUN pip install gym==0.21

WORKDIR /api/app

CMD [ "uvicorn", "main:app", "--host=0.0.0.0", "--reload"]