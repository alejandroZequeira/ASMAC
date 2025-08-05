from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Type, Union
import string
import os
from nanoid import generate as nanoid 
import re
import struct
import types
from option import Result,Ok,Err
from activex import Axo


ALPHABET = string.ascii_lowercase+string.digits
ASMAC_ID_SIZE =int(os.environ.get("ASMAC_ID_SIZE","16"))


def generate_id_size(size:int=ASMAC_ID_SIZE):
    def __in(v:str)->str:
        if v == None or v == "":
            return nanoid(alphabet=ALPHABET, size=size)
        return re.sub(r'[^a-z0-9_]', '', v)
    return __in


class ASMACMeta(ABC):
    
    @abstractmethod
    def to_json(self):
        pass
    
    
class User(ASMACMeta):
    name:str
    user_id:str
    password:str
    user_name:str
    
    def __init__(self,name:str,password:str,user_name:str=None):
        self.name = name
        self.user_id = nanoid(alphabet=ALPHABET, size=ASMAC_ID_SIZE)
        self.password = password
        self.user_name = user_name if user_name else name
        
    def get_user(self):
        return {
            "name": self.name,
            "user_id": self.user_id,
            "password": self.password,
            "user_name": self.user_name
        }
        
    def to_json(self):
        return self.get_user()
    
    def set_password(self, password:str):
        self.password = password
        
    def set_user_name(self, user_name:str):
        self.user_name = user_name

class Object:
    key: str
    alias: str
    bucket_id: str
    user_id: str
    is_public: bool
    
    def to_json(self):
        return {
            "key": self.key,
            "alias": self.alias,
            "bucket_id": self.bucket_id,
            "user_id": self.user_id,
            "is_public": str(self.is_public)
        }
    def set_public(self):
        self.is_public = True
    
    def get_object_by_alias(self) ->Result[Axo]:
        return Axo.get_by_key(key=self.key,bucket_id=self.bucket_id)
    
    def set_object(self, obj:Axo, alias:str=None, is_public:bool=False, user_id:str=None):
        self.key = obj.key
        self.alias = alias
        self.bucket_id = obj.bucket_id
        self.user_id = user_id
        self.is_public = is_public
        res=obj.persistify()
        return Ok(res) if res else Err("Error persisting object")
    
class Mesh(ASMACMeta):
    objects:List[object]
    mesh_id: str
    category: str
    description: str
    def __init__(self,category:str="default", mesh_id:str=None, description:str=""):
        self.objects = []
        self.mesh_id = mesh_id
        self.category = category
        self.description = description
    
    def add_object(self,obj:object):
        self.objects.append(obj)
    
    def remove_object(self,obj:object):
        self.objects = [o for o in self.objects if o.key != obj.key]
    
    def get_objects(self)->List[object]:
        return self.objects
    
    def get_mesh(self):
        return {
            "mesh_id": self.mesh_id,
            "category": self.category,
            "description": self.description,
            "objects": [obj.to_json() for obj in self.objects]
        }
    def to_json(self):
        return self.get_mesh()
    
class service(ASMACMeta):
    service_id: str
    description: str
    meshes:list[Mesh]
    
    def __init__(self,service_id:str=None, description:str=""):
        self.service_id = service_id if service_id else nanoid(alphabet=ALPHABET, size=ASMAC_ID_SIZE)
        self.description = description
        self.meshes = []
    
    def create_mesh(self,category:str="default", description:str="",objects: List[object]=[]) -> Mesh:
        mesh_id=nanoid(alphabet=ALPHABET, size=ASMAC_ID_SIZE)
        mesh = Mesh(category=category, mesh_id=mesh_id, description=description)
        self.mesh_id = mesh.mesh_id   
        self.meshes.append(mesh)
        return mesh
    
    def drop_mesh(self,mesh:Mesh):
        self.meshes = [m for m in self.meshes if m.mesh_id != mesh.mesh_id]
        
    def get_service(self):
        return {
            "service_id": self.service_id,
            "description": self.description,
            "meshes": [mesh.get_mesh() for mesh in self.meshes]
        }
        
    def to_json(self):
        return self.get_service()