FROM python:3.10-alpine

ARG ALERTA_URL=https://alerta.com/auth/login
ARG CURRENT_ENV=production
ARG PORT=9999

# Added ENV DB

ENV ALERTA_URL=$ALERTA_URL\
    PATH="/home/hera/.local/bin:${PATH}" \
    FLASK_APP=app \
    FLASK_ENV=$CURRENT_ENV \
    PORT=$PORT


WORKDIR /app

RUN adduser --disabled-password hera && \
    chown -R hera:hera /app && \
    apk --no-cache add gcc g++ musl-dev


COPY --chown=hera:hera . .

USER hera

RUN pip install -r requirements.txt && \
    python3 db_create.py && python3 db_migrate.py

ENTRYPOINT gunicorn -b 0.0.0.0:$PORT 'wsgi:app'
