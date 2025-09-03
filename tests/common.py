from mpu import haversine_distance
from asmac import ASMAC
import time
import csv
import threading
import numpy as np
from datetime import datetime, timezone, timedelta
class PoissonTraceGenerator:
    def __init__(self, rate: float, count: int, seed: int = None, aliases=None):
        self.rate = rate
        self.count = count
        self.rng = np.random.default_rng(seed)
        self.aliases = aliases or ["default"]

    def generate_trace(self, out_file="trace.txt"):
        inter_arrivals = self.rng.exponential(scale=1.0 / self.rate, size=self.count)
        t_rel = np.cumsum(inter_arrivals)

        with open(out_file, "w", encoding="utf-8") as f:
            f.write("id,alias,t_rel_s,inter_arrival_s\n")
            for i, (t, ia) in enumerate(zip(t_rel, inter_arrivals)):
                alias = self.aliases[i % len(self.aliases)]
                f.write(f"{i},{alias},{t:.6f},{ia:.6f}\n")

        print(f"Traza guardada en {out_file}")
        
class ConcurrentExecutor:
    def __init__(self, csv_out="execution_log.csv"):
        self.registry = {}
        self.csv_out = csv_out
        self.lock = threading.Lock()
        self.results = []

    def register(self, alias: str, func):
        """Asocia alias → función ejecutable."""
        self.registry[alias] = func

    def _run_event(self, ev, realtime):
        alias = ev["alias"]
        wait = ev["inter_arrival_s"] if realtime else 0

        if wait > 0:
            time.sleep(wait)

        start_exec = datetime.now(timezone.utc)
        print(f"[{start_exec.isoformat()}] Lanzando evento {ev['id']} ({alias})")

        if alias in self.registry:
            t0 = time.perf_counter()
            self.registry[alias]()
            t1 = time.perf_counter()
        else:
            print(f"⚠ Alias '{alias}' no tiene acción registrada.")
            t0 = t1 = time.perf_counter()

        end_exec = datetime.now(timezone.utc)
        duration = t1 - t0

        with self.lock:
            self.results.append({
                "id": ev["id"],
                "alias": alias,
                "start_time": start_exec.isoformat(),
                "end_time": end_exec.isoformat(),
                "duration_s": round(duration, 6)
            })

    def run_from_file(self, trace_file, realtime=True):
        # Leer traza desde TXT
        events = []
        with open(trace_file, "r", encoding="utf-8") as f:
            next(f)  # saltar cabecera
            for line in f:
                id_str, alias, t_rel, ia = line.strip().split(",")
                events.append({
                    "id": int(id_str),
                    "alias": alias,
                    "t_rel_s": float(t_rel),
                    "inter_arrival_s": float(ia)
                })

        # Lanzar hilos
        threads = []
        for ev in events:
            t = threading.Thread(target=self._run_event, args=(ev, realtime))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Guardar resultados
        with open(self.csv_out, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "alias", "start_time", "end_time", "duration_s"])
            writer.writeheader()
            for row in self.results:
                writer.writerow(row)

        print(f"Resultados guardados en {self.csv_out}")