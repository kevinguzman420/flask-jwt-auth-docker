FROM python:3.10.7-slim-buster

RUN useradd flaskauth

WORKDIR /home/flaskauth

COPY requirements.txt requirements.txt
RUN python -m pip install --upgrade pip
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY migrations migrations
COPY tests tests
COPY config config
COPY entrypoint.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP entrypoint.py
ENV APP_SETTINGS_MODULE config.dev

RUN chown -R flaskauth:flaskauth ./
USER flaskauth

EXPOSE 5000
ENTRYPOINT [ "./boot.sh" ]
