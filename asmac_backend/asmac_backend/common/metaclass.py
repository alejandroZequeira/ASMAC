from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Type, Union
import string
import os
from nanoid import generate as nanoid 
import re
import struct
import types
from option import Result,Ok,Err
from axo import Axo
from axo.contextmanager.contextmanager import AxoContextManager
from axo.endpoint.manager import DistributedEndpointManager

ALPHABET = string.ascii_lowercase+string.digits
ASMAC_ID_SIZE =int(os.environ.get("ASMAC_ID_SIZE","16"))

AXO_ENDPOINT_ID           = os.environ.get("AXO_ENDPOINT_ID","activex-endpoint-0")
AXO_ENDPOINT_PROTOCOL     = os.environ.get("AXO_ENDPOINT_PROTOCOL","tcp")
AXO_ENDPOINT_HOSTNAME     = os.environ.get("AXO_ENDPOINT_HOSTNAME","localhost")
AXO_ENDPOINT_PUBSUB_PORT  = int(os.environ.get("AXO_ENDPOINT_PUBSUB_PORT","16000"))
AXO_ENDPOINT_REQ_RES_PORT = int(os.environ.get("AXO_ENDPOINT_REQ_RES_PORT","16667"))

def init_axo():
        endpoint = DistributedEndpointManager()
        endpoint.add_endpoint(
            endpoint_id=AXO_ENDPOINT_ID,
            protocol=AXO_ENDPOINT_PROTOCOL,
            hostname=AXO_ENDPOINT_HOSTNAME,
            pubsub_port=AXO_ENDPOINT_PUBSUB_PORT,
            req_res_port=AXO_ENDPOINT_REQ_RES_PORT
        )
        return endpoint

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
    is_binding:bool
    class_code:str
    
    def __init__(self,key:str="",alias:str="",bucket_id:str="",class_code:str="",user_id:str="",is_public: bool=False,is_binding:bool=False):
        self.key=key
        self.alias=alias
        self.bucket_id=bucket_id
        self.user_id=user_id
        self.is_public=is_public
        self.is_binding=is_binding  
        self.class_code=class_code
    
    def to_json(self):
        return {
            "key": self.key,
            "alias": self.alias,
            "bucket_id": self.bucket_id,
            "user_id": self.user_id,
            "is_public": str(self.is_public),
            "class_code":self.class_code
        }
    def set_public(self):
        self.is_public = True
    
    async def get_object_by_alias(self) ->Result[Axo,Any]:
        return await Axo.get_by_key(key=self.key,bucket_id=self.bucket_id)
    
    async def set_object(self,class_code:str="", obj_key:str="",bucket_id:str="", alias:str=None, is_public:bool=False, user_id:str=None) -> Result[Axo, Any]:        
        self.key = obj_key
        self.alias = alias
        self.bucket_id =bucket_id
        self.user_id = user_id
        self.is_public = is_public
        self.class_code=class_code
        return Ok("object created") 
    
class BindingObject(Object):
    graf:list[Dict]
    
    def __init__(self,key:str,alias:str,graf):
        super().__init__(key=key,alias=alias,is_binding=True)
        self.graf=graf
        
    def to_json(self):
        return {"key":self.key,
                "alias":self.alias,
                "graf":self.graf}
        
    async def execute(self):
        for g in self.graf:
            with AxoContextManager.distributed(endpoint_manager=init_axo()) as cx:
                obj=await Axo.get_by_key(g["key"],g["bucket_id"])
                if obj.is_ok:
                    obj=obj.unwrap()
                    method=obj.call(obj,g.method_name,args=g.args,kwargs=g.kwargs)
                    if method.is_ok:
                        res = DistributedEndpointManager.method_execution(
                        key=obj.get_axo_key(),
                        fname=obj.__name__,
                        ao=obj,
                        f= method,
                        fargs=g.args,
                        fkwargs=g.kwargs
                    )



class Mesh(ASMACMeta):
    objects:List[object]
    mesh_id: str
    name: str
    description: str
    def __init__(self,name:str="default", description:str="", user_id: str=""):
        self.objects = []
        key=generate_id_size()
        self.mesh_id = key("")
        self.name = name
        self.description = description
        self.user_id=user_id
    
    def add_object(self,obj:object):
        self.objects.append(obj)
    
    def from_json(data:Dict)->'Mesh':
        mesh=Mesh(name=data.get("name","default"), description=data.get("description",""),user_id=data.get("user_id",""))
        mesh.mesh_id=data.get("mesh_id", generate_id_size())
        objects=data.get("objects",[])
        for obj in objects:
            mesh.add_object(Object(
                key=obj.get("key",""),
                alias=obj.get("alias",""),
                bucket_id=obj.get("bucket_id",""),
                user_id=obj.get("user_id",""),
                is_public=obj.get("is_public",True)
            ))
        return mesh
    
    def remove_object(self,obj:object):
        self.objects = [o for o in self.objects if o.key != obj.key]
    
    def get_objects(self)->List[object]:
        return self.objects
    
    def get_mesh(self):
        return {
            "mesh_id": self.mesh_id,
            "category": self.name,
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
    
    def create_mesh(self,category:str="default", description:str="") -> Mesh:
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