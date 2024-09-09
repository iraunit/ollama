FROM python:3.11.9-alpine3.20

WORKDIR /app

COPY . .

RUN pip3 install -r /app/requirements.txt

CMD fastapi run --reload