# It works. Tested it!

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

# What's done

* Progress list view in endpoint `/index`
