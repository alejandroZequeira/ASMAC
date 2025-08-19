import inspect
from typing import List, Dict, Any
from functools import wraps
from option import Result,Ok,Err
from typing import TypeVar
import cloudpickle as CP
import struct
import types 
import time as T
import importlib.util, sys, inspect
import ast, sys, importlib.util
from typing import List, Set
import os

from asmac.backend import send

from axo import Axo
from axo.endpoint.manager import DistributedEndpointManager,LocalEndpointManager
from asmac.runtime import get_runtime


from asmac.common.metaclass import metaclient, ASMACMeta, generate_id_size

    
class ASMaC:
    def __init__(self, host: str = "localhost", port: int = 45001):
        self.host = host
        self.port = port
        
    def user(self, password: str, user_name: str = None):
        self.user_name= user_name
        self.password = password
    
    def create_user(self, user_name: str, password: str, name:str):
        result=send(data={"action": "PUT.USER","data": {"user_name": user_name, "password": password, "name": name}}, host=self.host, puerto=self.port)
        if result["status"] == "OK":
            return Ok(result["data"])
        else:
            return Err(result["message"])
    
    def get_object_by_alias(self, alias: str, from_: str) :
        data={
            "user_name":self.user_name,
            "password":self.password,
            "alias": alias, 
            "from": from_} 
        result= send(data={"action": "GET.OBJECT.BY.ALIAS", "data":data}, host=self.host, puerto=self.port)
    
    def create_mesh(self, mesh_name: str, description: str = None):
        data={
            "user_name":self.user_name,
            "password":self.password,
            "mesh_name": mesh_name, 
            "description": description}
        
        result=send(data={"action": "PUT.MESH", "data":data }, host=self.host, puerto=self.port)
        if result["status"] == "OK":
            return Ok(result["data"])
        else:
            return Err(result["message"])
        
    def get_meshes(self):
        data={"user_name":self.user_name,"password":self.password} 
        result= send(data={"action": "GET.MESHES", "data": data}, host=self.host, puerto=self.port)
        return result
    
    def get_objects_by_mesh(self, mesh_name: str):
        data={
            "user_name":self.user_name,
            "password":self.password,
            "mesh_name": mesh_name}
        
        result=send(data={"action": "GET.OBJECTS.BY.MESH", "data": data }, host=self.host, puerto=self.port)
        return result
    
    def endpoint(self, endpoint_id: str = "axo-endpoint-0", protocol: str = "tcp", hostname: str = "localhost", pubsub_port: int = 16000, req_res_port: int = 16667):
        if hostname == "localhost" or hostname == "0.0.0.0":
            self._endpoint = LocalEndpointManager()
            self._endpoint.add_endpoint(
                endpoint_id=endpoint_id,
                protocol=protocol,
                hostname=hostname,
                pubsub_port=pubsub_port,
                req_res_port=req_res_port
            )
        else:
            self._endpoint = DistributedEndpointManager()
            self._endpoint.add_endpoint(
                endpoint_id=endpoint_id,
                protocol=protocol,
                hostname=hostname,
                pubsub_port=pubsub_port,
                req_res_port=req_res_port
            )
    
    def perstisify(self, obj: Axo, alias: str = None, mesh_name: str = None):
        
        if not alias:
            alias = obj.__class__.__name__
        
        data = {
            "user_name": self.user_name,
            "password": self.password,
            "alias": alias,
            "object": CP.dumps(obj)
        }
        
        result = send(data={"action": "PUT.OBJECT", "data": data}, host=self.host, puerto=self.port)
        
        if result["status"] == "OK":
            return Ok(result["data"])
        else:
            return Err(result["message"])
        
    def publish_to_mesh(self, mesh_name: str, object_alias: str): 
        data={"user_name": self.user_name,
              "password": self.password,
              "mesh_name": mesh_name,
              "alias": object_alias}
        
        result = send(data={"action": "PUT.MESH.DATA", "data": data}, host=self.host, puerto=self.port)
        
        if result["status"] == "OK":
            return Ok(result["data"])
        else:
            return Err(result["message"])
        