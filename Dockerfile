FROM python:3.10-alpine

ARG ALERTA_URL=https://alerta.io/auth/login
ARG CURRENT_ENV=production
ARG PORT=9999
ARG DATABASE_URL=sqlite
ARG SECRET_URL=https://raw.githubusercontent.com/Hera-system/HTTPSecret/main/HTTPSecret
ARG SECRET_TOKEN=VeryStrongString
ARG HTTPUser=User
ARG HTTPassword=Password

EXPOSE $PORT

ENV ALERTA_URL=$ALERTA_URL\
    PATH="/home/hera/.local/bin:${PATH}" \
    FLASK_APP=app \
    FLASK_ENV=$CURRENT_ENV \
    PORT=$PORT \
    DATABASE_URL=$DATABASE_URL \
    SECRET_URL=$SECRET_URL \
    SECRET_TOKEN=$SECRET_TOKEN


WORKDIR /app

RUN adduser --disabled-password hera && \
    chown -R hera:hera /app && \
    apk --no-cache add gcc g++ musl-dev curl


COPY --chown=hera:hera . .

USER hera

RUN pip install -r requirements.txt

ENTRYPOINT python3 db_create.py || python3 db_migrate.py && gunicorn -b 0.0.0.0:$PORT 'wsgi:app'
