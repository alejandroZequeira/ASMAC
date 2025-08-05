from mpu import haversine_distance
from asmac import ASMAC

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