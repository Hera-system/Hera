## Useful stuf
* https://habr.ru/post/346306/

# It works. Tested it!

## How to start

### Docker

```bash
$ git clone https://github.com/Hera-system/Hera.git
$ cd Hera
$ sudo docker-compose up
```

### Native

```commandline
pip install -r requirements.txt
python3 wsgi.py
```
### Export Alerta URL auth
```bash
export ALERTA_URL=https://alerta.com/auth/login
```

### And pls don't forget create/migrations db

```commandline
python3 db_create.py
```

# What's done

* Progress list view in endpoint `/index`
