# IUM – Lab 5: konteneryzacja pipeline'u ML

Pipeline z lab. 3 (zbiór wine, `StandardScaler` + `LogisticRegression`) w kontenerze, uruchamiany
przez Docker Compose razem z drugą usługą, która serwuje wyniki treningu.

```
Dockerfile           # obraz train: python:3.11-slim, zależności przez uv (multi-stage)
docker-compose.yml   # usługi train i visualize, wolumeny, limity, depends_on
.env.train           # konfiguracja usługi train (env_file)
.env.visualize       # konfiguracja usługi visualize (env_file)
.dockerignore        # .venv, .git, data/, models/ poza kontekstem budowania
src/pipeline.py      # data_prep -> train -> evaluate + endpoint /status na porcie 5000
src/data_prep.py, src/train.py, src/evaluate.py   # moduły z lab. 3
visualize/           # serwer HTTP z katalogiem models/, przy starcie sprawdza http://train:5000/status
```

```bash
docker build -t ium-lab05-train .            # sam obraz (zad. 1)
docker compose up --build                    # trening + serwer wyników
open http://localhost:8080                   # models/model.joblib, models/wyniki.txt
docker stats                                 # limit 512 MiB i 1,5 CPU usługi train
docker compose run --rm --no-deps train pytest -q
docker compose down
```
