from axo import Axo
import string
import os
import re
from nanoid import generate as nanoid 
import inspect
from typing import Any, Dict, List, Optional, Tuple, Type, Union


ALPHABET = string.ascii_lowercase+string.digits
ASMAC_ID_SIZE =int(os.environ.get("ASMAC_ID_SIZE","16"))


def generate_id_size(size:int=ASMAC_ID_SIZE):
    def __in(v:str)->str:
        if v == None or v == "":
            return nanoid(alphabet=ALPHABET, size=size)
        return re.sub(r'[^a-z0-9_]', '', v)
    return __in

class BindingObject:
    key: str
    alias: str
    bucket_id: str
    user_id: str
    is_public: bool
    is_binding:bool
    graf = []
    def __init__(self, alias: str = ""):
        self.alias = alias
        self.key = nanoid(alphabet=ALPHABET, size=ASMAC_ID_SIZE)
        self.bucket_id = nanoid(alphabet=ALPHABET,size=ASMAC_ID_SIZE*2)
        self.sink_bucket_id = nanoid(alphabet=ALPHABET,size=ASMAC_ID_SIZE*2)
        self.source_bucket_id = nanoid(alphabet=ALPHABET,size=ASMAC_ID_SIZE*2)
        self.is_public = False
        self.is_binding = True
        
    def add(self, obj: Axo, method: callable):
        self.graf.append({
            "key": obj.key,
            "alias": obj.alias,
            "method": method.__name__,
            "args": inspect.getfullargspec(method).args,
            "*args": inspect.getfullargspec(method).varargs,
            "**kwargs": inspect.getfullargspec(method).varkw
        })
        
    def run(self):
        pass
    
    def to_json(self):
        return {
            "key": self.key,
            "alias": self.alias,
            "bucket_id": self.bucket_id,
            "user_id": self.user_id,
            "is_public": self.is_public,
            "is_binding": self.is_binding,
            "graf": self.graf
        }