from pydantic import BaseModel
from typing import Any, Dict, List, Optional, Tuple, Type, Union
import string
import os
from nanoid import generate as nanoid 
import re


ALPHABET = string.ascii_lowercase+string.digits
ASMAC_ID_SIZE =int(os.environ.get("ASMAC_ID_SIZE","16"))


def generate_id_size(size:int=ASMAC_ID_SIZE):
    def __in(v:str)->str:
        if v == None or v == "":
            return nanoid(alphabet=ALPHABET, size=size)
        return re.sub(r'[^a-z0-9_]', '', v)
    return __in

class metaclient(BaseModel):
   pass


class ASMACMeta(BaseModel):
    module: str=""
    alias: str=""
    key: str=""
    name: str=""
    class_name: str=""
    version: str="v0"
    dependencies:List[str]=[]
    bucket_id: str=""
    source_bucket_id: str=""
    sink_bucket_id: str=""
    code:str=""
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.key = nanoid(alphabet=ALPHABET, size=ASMAC_ID_SIZE)
        self.bucket_id = nanoid(alphabet=ALPHABET,size=ASMAC_ID_SIZE*2)
        self.sink_bucket_id = nanoid(alphabet=ALPHABET,size=ASMAC_ID_SIZE*2)
        self.source_bucket_id = nanoid(alphabet=ALPHABET,size=ASMAC_ID_SIZE*2)
    
    def to_json_with_string_values(self)->Dict[str,str]:
        json_data = self.model_dump()
        # Convert all values to strings
        for key, value in json_data.items():
            # if key == "replica_nodes"
            if isinstance(value, list):
                json_data[key] = ";".join(value)
            else:
                json_data[key] = str(value)

        return json_data
    
    
class AsmacMetaClass(BaseModel):
    pass