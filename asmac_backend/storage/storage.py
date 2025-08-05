from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Iterator
from option import Result, Ok, Err
import os
import string
from nanoid import generate as nanoid
import time as T
from asmac_backend.common import ASMACMeta
#dependencias de mongo 
from pymongo import MongoClient

#dependencias a mictlanx
from option import Result,Err,Ok,Some,NONE,Option
from mictlanx.utils.index import Utils
from mictlanx.v4.client import Client
from mictlanx.logger.tezcanalyticx.tezcanalyticx import TezcanalyticXHttpHandler,TezcanalyticXParams
import mictlanx.v4.interfaces as InterfaceX

class StorageService:
    def __init__(self,storage_service_id:str):
        self.storage_service_id = storage_service_id
    
    @abstractmethod
    def put(self,bd:str,key:str,data:ASMACMeta)->Result[str,Exception]:
        pass
    @abstractmethod
    def get(self,bd:str,key:str,condition:str)->Result[bytes,Exception]:
        pass

class MongoDBStorageService(StorageService):
    def __init__(self,storage_service_id:str="ASMAC-Mongo",db:str="ASMAC"):
        super().__init__(storage_service_id)
        self.client=MongoClient(os.environ("Mongo_host","localhost"),os.environ("Mongo_port",27017))
        self.db = db
        
    def put(self,collection:str,key:str,obj:ASMACMeta)->Result[str,Exception]:
        try:
            db = self.client[self.db]
            col = db[collection]
            col.insert_one(obj.to_json())
        except Exception as e:
            print(f"Error al subir datos: {e}")
        
    def get(self, bd: str, key: str,condition: str) -> Result[bytes, Exception]:
        try:
            result = self.db[bd].find_one({"key": key})
            if not result:
                return Err(Exception(f"No se encontró el objeto con clave '{key}'"))
            return Ok(result["data"].encode('utf-8'))  # Devuelve como bytes
        except Exception as e:
            return Err(e)