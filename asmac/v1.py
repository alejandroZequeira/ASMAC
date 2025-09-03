import inspect
import re
import textwrap
from typing import List, Dict, Any
from functools import wraps
from option import Result,Ok,Err
from typing import TypeVar
import cloudpickle as CP

import time as T
import sys

import json

from asmac.backend import send

from axo import Axo

from axo.storage.services import StorageService
from axo.storage.services import MictlanXStorageService
from axo.endpoint.manager import DistributedEndpointManager,LocalEndpointManager
from axo.contextmanager import AxoContextManager

def init_axo(endpoint_id,protocol,hostname,pubsub_port,req_res_port):
        endpoint = DistributedEndpointManager()
        endpoint.add_endpoint(
            endpoint_id=endpoint_id,
            protocol=protocol,
            hostname=hostname,
            pubsub_port=pubsub_port,
            req_res_port=req_res_port
        )
        return endpoint

class ASMaC:
    def __init__(self, host: str = "localhost", port: int = 4555):
        self.host = host
        self.port = port
        
    def __storage_service(self):
        return MictlanXStorageService(protocol="http")
    
    def run(self,obj:Axo,method:str,*args:any, **kwargs:any):
        result = send(data={"action": "GET.ENDPOINT.INFO", "data":{}}, host=self.host, puerto=self.port)
        if result["status"]=="OK":
            with AxoContextManager.distributed(
                    endpoint_manager=init_axo(endpoint_id=result["endpoint_id"],hostname="148.247.202.72",protocol=result["protocol"],pubsub_port=result["pubsub_port"],req_res_port=result["req_res_port"]),
                    storage_service=self.__storage_service()) as cx:
                res=Axo.call(obj,method_name=method,*args, **kwargs)
                return res
    
    def user(self, password: str, user_name: str = None):
        self.user_name= user_name
        self.password = password
    
    def create_user(self, user_name: str, password: str, name:str):
        result=send(data={"action": "PUT.USER","data": {"user_name": user_name, "password": password, "name": name}}, host=self.host, puerto=self.port)
        if result["status"] == "OK":
            return Ok(result["data"])
        else:
            return Err(result["msg"])
    def get_objects(self):
        data={
            "user_name":self.user_name,
            "password":self.password,} 
        res= send(data={"action": "GET.OBJECTS", "data":data}, host=self.host, puerto=self.port)
        if res["status"]=="OK":
            print(res["data"])
        else:
            print("not objects")
    
    async def get_object_by_alias(self, alias: str="", from_: str=None) :
        result = send(data={"action": "GET.ENDPOINT.INFO", "data":{}}, host=self.host, puerto=self.port)
        print(result["status"])
        if result["status"]=="OK":
            if  from_== None:
                data={
                    "user_name":self.user_name,
                    "password": self.password,
                    "alias":alias,
                    "from": self.user_name
                }
            else:
                data={
                        "user_name":self.user_name,
                        "password":self.password,
                        "alias": alias, 
                        "from": from_} 
            res= send(data={"action": "GET.OBJECT.BY.ALIAS", "data":data}, host=self.host, puerto=self.port)
            if res["status"]=="OK":
                print(res["data"])
                with AxoContextManager.distributed(
                    endpoint_manager=init_axo(endpoint_id=result["endpoint_id"],hostname="148.247.202.72",protocol=result["protocol"],pubsub_port=result["pubsub_port"],req_res_port=result["req_res_port"]),
                    storage_service=self.__storage_service()) as cx:
                    ao_key=res["data"]["key"]
                    bucket_id=res["data"]["bucket_id"]
                    ao = await Axo.get_by_key(bucket_id=bucket_id,key=ao_key)
                    print(ao)
                    if ao.is_ok:
                        return ao.unwrap()
                    else:
                        print(ao)
                        return ao
            else:
                print(result["msg"])
                return result["msg"]
        else:
            print("endpoint unavailable")
            return "endpoint unavailable"

    
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
    def __auto_dependencies(self, obj):
        deps = set()

        # Revisa atributos de instancia
        for attr in obj.__dict__.values():
            cls = type(attr)
            if cls.__module__ != "builtins":
                deps.add(cls)

        # Revisa anotaciones de tipo
        for attr_type in getattr(obj.__class__, "__annotations__", {}).values():
            if isinstance(attr_type, type) and attr_type.__module__ != "builtins":
                deps.add(attr_type)

        # Revisa métodos y globales que usen clases
        for _, method in inspect.getmembers(obj.__class__, inspect.isfunction):
            for val in method.__globals__.values():
                if isinstance(val, type) and val.__module__ != "builtins":
                    deps.add(val)

        return list(deps)
    
    def __get_full_class_code(self, obj, dependencies=[]):
        imports = set()
        code_parts = []

        def collect_source(cls):
            src_file = inspect.getsourcefile(cls)
            if not src_file:
                return

            # Si es librería externa → solo import
            if "site-packages" in src_file:
                imports.add(f"import {cls.__module__}")
                return

            # Leer archivo completo para extraer imports
            try:
                with open(src_file, "r") as f:
                    file_content = f.read()

                # Extraer imports
                for imp in re.findall(r'^\s*(?:import|from)\s+[^\n]+', file_content, re.MULTILINE):
                    imp = imp.strip()
                    if imp.startswith("from .") or imp.startswith("from .."):
                        continue
                    imports.add(imp)

            except Exception:
                pass

            # Agregar código fuente de la clase
            try:
                src = inspect.getsource(cls)
                code_parts.append(textwrap.dedent(src))
            except OSError:
                pass

        # Primero dependencias
        for dep in dependencies:
            collect_source(dep)

        # Luego la clase principal
        collect_source(obj.__class__)

        # Concatenar imports y definiciones
        return "\n".join(sorted(imports)) + "\n\n" + "\n\n".join(code_parts)
    
    
    async def perstisify(self, obj: Axo, alias: str = None, mesh_name: str = None):
        if not alias:
            alias = obj.__class__.__name__
        result = send(data={"action": "GET.ENDPOINT.INFO", "data":{}}, host=self.host, puerto=self.port)
        print(result)
        if result["status"]=="OK":
            with AxoContextManager.distributed(
                endpoint_manager=init_axo(endpoint_id=result["endpoint_id"],hostname="148.247.202.72",protocol=result["protocol"],pubsub_port=result["pubsub_port"],req_res_port=result["req_res_port"]),
                storage_service=self.__storage_service()) as cx:
                res=await obj.persistify()
                if res.is_ok:

                    dep = self.__auto_dependencies(obj)
                    class_code = self.__get_full_class_code(obj, dep)
                data = {
                    "user_name": self.user_name,
                    "password": self.password,
                    "alias": alias,
                    "obj_key": obj.get_axo_key(),
                    "bucket_id":obj.get_axo_bucket_id(),
                    "class_code": str(class_code),
                }

                # 4. Enviar al servidor
                result = send(data={"action": "PUT.OBJECT", "data": data}, host=self.host, puerto=self.port)

                if result["status"] == "OK":
                    return Ok(result["data"])
                else:
                    return Err(result["msg"])
        else: 
            return Err("endpoint is not active")


        
    def publish_to_mesh(self, mesh_name: str, object_alias: str): 
        data={
            "user_name": self.user_name,
            "password": self.password,
            "mesh_name": mesh_name,
            "alias": object_alias}
        
        result = send(data={"action": "PUT.MESH.DATA", "data": data}, host=self.host, puerto=self.port)
        
        if result["status"] == "OK":
            return Ok(result["data"])
        else:
            return Err(result["message"])
        