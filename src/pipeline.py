"""Zadanie 3: uruchamia po kolei etapy z lab. 3 (data_prep -> train -> evaluate).

Każdy etap to osobny skrypt uruchamiany jak lokalnie (python src/<etap>.py), więc log
w kontenerze jest taki sam jak przy uruchomieniu z terminala w lab. 3.
"""
import subprocess
import sys
import time

STAGES = ["data_prep", "train", "evaluate"]


def run_stage(name):
    print(f"=== Etap: {name} ===", flush=True)
    t0 = time.time()
    subprocess.run([sys.executable, f"src/{name}.py"], check=True)   # błąd etapu przerywa pipeline
    print(f"=== {name}: OK ({time.time() - t0:.1f} s) ===", flush=True)


if __name__ == "__main__":
    for stage in STAGES:
        run_stage(stage)
    print("Pipeline zakończony", flush=True)
