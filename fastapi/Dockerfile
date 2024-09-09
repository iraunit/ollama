FROM python:3.8-slim

WORKDIR /app

COPY . .

RUN pip3 install -r /app/requirements.txt

CMD fastapi run --reload