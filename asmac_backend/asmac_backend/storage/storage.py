from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Iterator
from option import Result, Ok, Err
import os
import string
from nanoid import generate as nanoid
import time as T
from ..common import ASMACMeta
#dependencias de mongo 
from pymongo import MongoClient

from option import Result,Err,Ok,Some,NONE,Option


class StorageService:
    def __init__(self,storage_service_id:str):
        self.storage_service_id = storage_service_id
    
    @abstractmethod
    def put(self,bd:str,key:str,data:ASMACMeta)->Result[str,Exception]:
        pass
    @abstractmethod
    def get(self,collection_name: str,condition:str)->Result[bytes,Exception]:
        pass
    @abstractmethod
    def gets(self,collection_name: str,condition:str)->Result[bytes,Exception]:
        pass
    @abstractmethod
    def update(self,bd:str,key:str,condition:str,new_values:Dict[str,Any])->Result[str,Exception]:
        pass
class MongoDBStorageService(StorageService):
    def __init__(self, storage_service_id: str = "ASMAC-Mongo", db: str = "ASMAC"):
        super().__init__(storage_service_id)
        host = os.environ.get("MONGO_HOST", "localhost")
        port = int(os.environ.get("MONGO_PORT", 27017))
        username = os.environ.get("MONGO_USERNAME", "admin")
        password = os.environ.get("MONGO_PASSWORD", "admin")
        authSource = os.environ.get("MONGO_AUTH_DB", "admin")

        self.client = MongoClient(
            host=host,
            port=port,
            username=username,
            password=password,
            authSource=authSource
        )
        self.db = self.client[db]
        
    def put(self,collection:str,key:str,obj:Any)->Result[str,Exception]:
        try:
            col = self.db[collection]
            col.insert_one(obj.to_json())
            print(f"Objeto con clave '{key}' subido correctamente.")
            return Ok(f"Objeto con clave '{key}' subido correctamente.")
        except Exception as e:
            print(f"Error al subir datos: {e}")
            return Err(e)
        
    def get(self, collection_name: str, condition: Dict[str, Any]) -> Result[Dict[str, Any], Exception]:
        try:
            #print(condition)
            #print(collection_name)
            collection = self.db[collection_name]
            result = collection.find_one(condition)
            #print(f"Resultado de la búsqueda en '{collection_name}': {result}")
            
            if not result:
                return Err(Exception(f"No se encontró ningún documento en '{collection_name}' con la condición: {condition}"))
            
            return Ok(result)  # devuelve todo el documento como dict
        except Exception as e:
            return Err(e)
    def gets(self, collection_name: str, condition: Dict[str, Any]) -> Result[Dict[str, Any], Exception]:
        try:
            #print(condition)
            #print(collection_name)
            collection = self.db[collection_name]
            result = collection.find(condition)
            #print(f"Resultado de la búsqueda en '{collection_name}': {result}")
            
            if not result:
                return Err(Exception(f"No se encontró ningún documento en '{collection_name}' con la condición: {condition}"))
            
            return Ok(result)  # devuelve todo el documento como dict
        
        except Exception as e:
            return Err(e)
    
    def update(
        self,
        collection_name: str,
        condition: Dict[str, Any],
        new_values: Dict[str, Any]
    ) -> Result[Dict[str, Any], Exception]:
        """
        Actualiza un documento en la colección.
        condition -> filtro de búsqueda
        new_values -> valores a actualizar (sin $set, ya lo añadimos aquí)
        """
        try:
            collection = self.db[collection_name]
            result = collection.update_one(condition, {"$set": new_values})
            
            if result.matched_count == 0:
                return Err(Exception(
                    f"No se encontró ningún documento en '{collection_name}' con la condición: {condition}"
                ))
            
            return Ok({
                "matched_count": result.matched_count,
                "modified_count": result.modified_count
            })
        except Exception as e:
            return Err(e)