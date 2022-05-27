FROM python:3.9-alpine

WORKDIR /api

COPY requirements.txt .
# COPY ./app ./app

RUN pip install --upgrade pip && pip install -r requirements.txt

CMD [ "uvicorn", "app.main:app", "--host=0.0.0.0", "--reload"]