FROM ubuntu:20.04

RUN apt update && apt upgrade -y
RUN apt install python3 python3-pip gcc g++ libffi-dev -y

WORKDIR /api

# install python requirement
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# copy fastapi app
COPY ./app ./app

WORKDIR /api/app

CMD [ "uvicorn", "main:app", "--host=0.0.0.0"]