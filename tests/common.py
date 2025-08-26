from mpu import haversine_distance
from asmac import ASMAC
import time
import threading
import numpy as np
from datetime import datetime, timezone, timedelta

class Proximidad(ASMAC):
    def __init__(self,proposed_radius=5):
        self.rp=proposed_radius
        
    def distance(self,c_1,c_2):
        dist = haversine_distance((float(c_1["lat"]), float(c_1["lon"])), (float(c_2["lat"]), float(c_2["lon"])))
        return dist
    
    
    def Nearby_centroids(self,c_1,centroids):
        distances=[]
        for c in centroids:
            #print(c)
            d=self.distance(c_1,c)
            if d<self.rp:
                distances.append(d)
        return distances
    
class PoissonTraceGenerator:
    def __init__(self, rate: float, count: int, seed: int = None, aliases=None):
        self.rate = rate
        self.count = count
        self.rng = np.random.default_rng(seed)
        self.aliases = aliases or ["default"]

    def generate_trace(self):
        inter_arrivals = self.rng.exponential(scale=1.0 / self.rate, size=self.count)
        t_rel = np.cumsum(inter_arrivals)

        events = []
        for i, (t, ia) in enumerate(zip(t_rel, inter_arrivals)):
            alias = self.aliases[i % len(self.aliases)]
            events.append({
                "id": i,
                "t_rel_s": float(t),
                "inter_arrival_s": float(ia),
                "alias": alias
            })
        return events