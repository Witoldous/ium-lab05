"""Zadania 3 i 6: uruchamia po kolei etapy z lab. 3 (data_prep -> train -> evaluate).

Każdy etap to osobny skrypt uruchamiany jak lokalnie (python src/<etap>.py), więc log
w kontenerze jest taki sam jak przy uruchomieniu z terminala w lab. 3.
Zadanie 6: w tle działa serwer HTTP z endpointem /status, z którego usługa visualize
odczytuje bieżący etap, łącząc się po nazwie usługi (http://train:5000/status).
"""
import json
import os
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

STAGES = ["data_prep", "train", "evaluate"]
STATUS_PORT = int(os.getenv("STATUS_PORT", 5000))
KEEP_ALIVE = int(os.getenv("KEEP_ALIVE", 0))   # ile sekund serwować status po zakończeniu

status = {"stage": "start", "finished": []}


class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/status":
            self.send_error(404)
            return
        body = json.dumps(status).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        # kto pyta o status: adres IP kontenera visualize w sieci compose
        print(f"[status] {self.client_address[0]} {self.requestline} -> {status['stage']}", flush=True)


def start_status_server():
    server = ThreadingHTTPServer(("0.0.0.0", STATUS_PORT), StatusHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"Status pipeline'u: http://0.0.0.0:{STATUS_PORT}/status", flush=True)


def run_stage(name):
    status["stage"] = name
    print(f"=== Etap: {name} ===", flush=True)
    t0 = time.time()
    subprocess.run([sys.executable, f"src/{name}.py"], check=True)   # błąd etapu przerywa pipeline
    status["finished"].append(name)
    print(f"=== {name}: OK ({time.time() - t0:.1f} s) ===", flush=True)


if __name__ == "__main__":
    start_status_server()
    try:
        for stage in STAGES:
            run_stage(stage)
    except subprocess.CalledProcessError:
        status["stage"] = "error"
        raise
    status["stage"] = "done"
    print("Pipeline zakończony", flush=True)
    if KEEP_ALIVE > 0:
        print(f"Status dostępny jeszcze przez {KEEP_ALIVE} s", flush=True)
        time.sleep(KEEP_ALIVE)
