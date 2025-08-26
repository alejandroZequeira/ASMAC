from axo import Axo,axo_method
from asmac_backend.asmac_backend.v0 import ASMaC_Backend
import asyncio
import time as T
import pandas as pd
import inspect
import pandas as pd
import time as T
data=[]
class dog(Axo):
    
    @axo_method
    def set_name(self, name: str,**kwargs):
        self.name = name
        return f"Dog's name set to {self.name}"
    
    @axo_method
    def bark(self,**kwargs):
        return f"{self.name} says: Woof!"

async def create_object():
    for i in range(1,100):
        start=T.time()
        print("Creating object...")
        obj= dog(axo_endpoint_id = "axo-endpoint-0")
        obj.set_name(name="Rex")
        user=ASMaC_Backend.login_user(user_name="alejandro", password="test_password")
        res=await ASMaC_Backend.set_object(obj=obj, alias="my_dog"+str(i), user_id=user["user_id"])
        res=obj.bark()
        print(res)
        end=T.time()
        data.append({
            "object": obj.get_axo_key(),
            "alias": "my_dog"+str(i),
            "user_id": user["user_id"],
            "time": end-start,
            "result": res
        })
    
async def get_object():
    for i in range(1,100):
        start=T.time()
        print("Getting object...")
        user=ASMaC_Backend.login_user(user_name="alejandro", password="test_password")
        obj= await ASMaC_Backend.get_object_by_alias(alias="my_dog"+str(i), user_id=user["user_id"])
        obj:Axo= obj.unwrap() if obj.is_ok else None
        print("type:",type(obj))
        #print(vars(obj))
        end=T.time()
        data.append({
            "object": obj.get_axo_key() if obj else None,
            "alias": "my_dog"+str(i),
            "user_id": user["user_id"],
            "time": end-start,
        })
    
    
if __name__ == "__main__":
    asyncio.run(create_object())
    asyncio.run(get_object())
    df=pd.DataFrame(data)
    df.to_csv("test_get_object.csv", index=False)