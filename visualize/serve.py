"""Zadania 4 i 6: serwer HTTP z wynikami treningu (katalog models/ z wolumenu).

Przed startem serwera sprawdza usługę train po jej nazwie z docker-compose.yml:
rozwiązuje nazwę "train" w DNS sieci compose i odpytuje http://train:5000/status,
aż pipeline skończy pracę. Jeśli train już nie działa, sprawdza wspólny plik z wolumenu.
"""
import json
import os
import socket
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from urllib.request import urlopen

TRAIN_URL = os.getenv("TRAIN_URL", "http://train:5000/status")
WAIT_TIMEOUT = int(os.getenv("WAIT_TIMEOUT", 300))
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 3))
RESULTS_DIR = os.getenv("RESULTS_DIR", "/srv/models")
RESULTS_FILE = os.getenv("RESULTS_FILE", "wyniki.txt")
PORT = int(os.getenv("PORT", 8080))


def log(msg):
    print(f"[visualize] {msg}", flush=True)


def wait_for_train():
    """Odpytuje usługę train po nazwie, aż zgłosi stage == done (albo minie WAIT_TIMEOUT)."""
    host = urlparse(TRAIN_URL).hostname
    deadline = time.time() + WAIT_TIMEOUT
    while time.time() < deadline:
        try:
            ip = socket.gethostbyname(host)                 # DNS sieci utworzonej przez compose
            with urlopen(TRAIN_URL, timeout=3) as resp:
                st = json.load(resp)
            log(f"{host} -> {ip}, GET {TRAIN_URL}: etap={st['stage']}, ukończone={st['finished']}")
            if st["stage"] == "done":
                return True
            if st["stage"] == "error":
                log("pipeline w usłudze train zakończył się błędem")
                return False
        except socket.gaierror as e:                        # nazwy nie ma w DNS: kontener train nie działa
            log(f"{TRAIN_URL} niedostępny ({e})")
            return False
        except OSError as e:                                # np. serwer /status jeszcze nie wstał
            log(f"{TRAIN_URL}: {e}, ponawiam za {POLL_INTERVAL} s")
        time.sleep(POLL_INTERVAL)
    return False


def check_shared_file():
    """Plan B: odczyt wyników zapisanych przez train na wspólnym wolumenie."""
    path = os.path.join(RESULTS_DIR, RESULTS_FILE)
    if not os.path.exists(path):
        log(f"brak {path}: trening jeszcze nie zapisał wyników")
        return False
    with open(path, encoding="utf-8") as f:
        head = " | ".join(f.read().splitlines()[:3])
    log(f"wspólny plik {path}: {head}")
    return True


if __name__ == "__main__":
    log(f"sprawdzam usługę train: {TRAIN_URL}")
    if wait_for_train():
        log("usługa train zakończyła pipeline")
    else:
        log("usługa train nieosiągalna, sprawdzam wspólny wolumen")
    check_shared_file()

    handler = partial(SimpleHTTPRequestHandler, directory=RESULTS_DIR)
    log(f"serwuję {RESULTS_DIR} na porcie {PORT}")
    ThreadingHTTPServer(("0.0.0.0", PORT), handler).serve_forever()
