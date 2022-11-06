# Hera

Ready to run on Heroku. [Demo](https://hera-system.herokuapp.com)

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://dashboard.heroku.com/new?template=https://github.com/Hera-system/Hera)

## How to start

___

#### Install [Alerta](https://github.com/alerta/alerta) and follow next steps

---

### Docker

```bash
$ git clone https://github.com/Hera-system/Hera.git
$ cd Hera
$ nano docker-compose.yml  # Edit ALERTA_URL to your address
$ sudo docker-compose up
```

---

### Native

```bash
$ pip install -r requirements.txt
$ export ALERTA_URL=https://alerta.com/auth/login  # URL to auth endpoint your Alerta
$ python3 db_create.py
$ python3 wsgi.py
```

---

## What is it

This is a server management system. It works only after installing the [Webhook](https://github.com/Hera-system/webhook) on your server.

## How it works

1. You are login in [Hera](https://github.com/Hera-system/Hera) using password and email from [alerta](https://github.com/alerta/alerta).
2. Create template on endpoint `/addTemplate`.
3. Confirm template from other account on endpoint `/confirmTemplate` or skip for admin.
4. Send execute template to webhook from endpoint `/execCommand`.
5. Wait until execute command.
6. View result on endpoint `/commands`.
