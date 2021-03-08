FROM python:3.6-alpine

RUN adduser -D botic
RUN apk update
RUN apk add --no-cache binutils
RUN apk add --no-cache gcc
RUN apk add --no-cache musl-dev
RUN apk add --no-cache postgresql-dev
RUN apk add --no-cache libpq
WORKDIR /home/botic

COPY app/requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn
RUN venv/bin/pip install psycopg2

RUN apk del binutils gcc musl-dev postgresql-dev

COPY app app
COPY api api
COPY migrations migrations
COPY botic-app.py app/boot.sh ./
COPY botic-api.py api/boot-api.sh ./
COPY boot-scheduler.sh botic-scheduler.py ./
COPY util.py models.py exceptions.py constants.py ./
COPY README.md ./
RUN chmod +x boot.sh
RUN chmod +x boot-scheduler.sh
RUN chmod +x boot-api.sh

ENV FLASK_APP botic-app.py

RUN chown -R botic:botic ./
USER botic

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]