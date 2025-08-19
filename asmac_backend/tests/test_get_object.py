from axo import Axo,axo_method
from asmac_backend.asmac_backend.v0 import ASMaC_Backend
import asyncio
import time as T
import pandas as pd
import inspect

class dog(Axo):
    
    @axo_method
    def set_name(self, name: str,**kwargs):
        self.name = name
        return f"Dog's name set to {self.name}"
    
    @axo_method
    def bark(self,**kwargs):
        return f"{self.name} says: Woof!"

async def create_object():
    obj= dog(axo_endpoint_id = "axo-endpoint-0")
    obj.set_name(name="Rex")
    user=ASMaC_Backend.login_user(user_name="alejandro", password="test_password")
    res=await ASMaC_Backend.set_object(obj=obj, alias="my_dog1", user_id=user["user_id"])
    print(res)
    
async def get_object():
    user=ASMaC_Backend.login_user(user_name="alejandro", password="test_password")
    obj= await ASMaC_Backend.get_object_by_alias(alias="my_dog1", user_id=user["user_id"])
    obj= obj.unwrap() if obj.is_ok else None
    print("type:",type(obj))
    print(vars(obj))
    obj.persistify()
    print(obj.bark())
    
    
if __name__ == "__main__":
    asyncio.run(create_object())
    asyncio.run(get_object())