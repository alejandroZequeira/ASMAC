from abc import ABC, abstractmethod
from threading import Thread
from typing import Dict, Any,TypeVar, Callable,Set
import random
import humanfriendly as HF
import zmq
import time as T
import json as J
import pickle as CP
from pydantic import BaseModel
from option import Result,Err,Ok

from asmac.common.metaclass import  ASMACMeta, AsmacMetaClass
#from asmac import ASMAC

TV = TypeVar("TV")
GenericFunction = Callable[[TV],TV]

class Endpoint(ABC):
    def __init__(self,protocol:str="tcp", hostname:str= "127.0.0.1", req_res_port:int = 46501, pubsub_port:int=46500,encoding:str ="utf-8",endpoint_id:str="asmac-endpoint-0",is_local:bool=True):
        self.endpoint_id  = endpoint_id
        self.protocol = protocol
        self.hostname = hostname
        self.req_res_port=req_res_port
        self.pubsub_port= pubsub_port
        self.encoding=encoding
        self.is_local:bool = is_local
        
    @abstractmethod
    def put(self, key:str, value:ASMACMeta)->Result[str, Exception]:
        return Err(Exception("No implemented yet."))

    @abstractmethod
    def get(self, key:str)->Result[ASMACMeta, Exception]:
        return Err(Exception("No implemented yet."))

    @abstractmethod
    def method_execution(self,key:str,fname:str,ao:AsmacMetaClass,f:GenericFunction = None, fargs:list=[],fkwargs:dict={})->Result[Any,Exception]:
        return Err(Exception("No implemented yet."))
    
    @abstractmethod
    def add_code(self,ao:AsmacMetaClass)->Result[bool, Exception]:
        return Err(Exception("No implemented yet."))
    

class LocalEndpoint(Endpoint):
    def __init__(self, endpoint_id:str="ASMAC-endpoint-0"):
        super().__init__(
            endpoint_id=endpoint_id
        )
        self.__db  = {}

    def put(self, key: str, metadata: ASMACMeta) -> Result[str, Exception]:
        try:
            if not key in self.__db:
                self.__db[key] = metadata
            return Ok(key)
        except Exception as e:
            return Err(e)
        
    def get(self, key: str) -> Result[ASMACMeta, Exception]:
        if key in self.__db:
            return Ok(self.__db[key])
        return Err(Exception("Not found: {}".format(key)))
   
    def method_execution(self,key:str,fname:str,ao:AsmacMetaClass,f:GenericFunction = None,fargs:list=[],fkwargs:dict={}) -> Result[Any, Exception]:
        try:
            return Ok(f(ao,*fargs, **fkwargs))
        except Exception as e:
            return Err(e)
   
    def add_code(self, ao: AsmacMetaClass) -> Result[bool, Exception]:
        try:
            return Ok(False)
        except Exception as e:
            return Err(e)
        # return Err(Exception("No implemented yet."))
    
class DistributedEndpoint(Endpoint):
    def __init__(self, endpoint_id:str="", protocol:str="tcp", hostname: str = "127.0.0.1", publisher_hostname:str = "*", pubsub_port: int = 16666, req_res_port:int = 16667, max_health_ping_time:str = "1h", max_recv_timeout:str = "120s", max_retries:int=10):
        super().__init__(protocol=protocol,hostname=hostname, req_res_port=req_res_port,endpoint_id=endpoint_id,pubsub_port=pubsub_port,is_local=False)
        self.pubsub_uri = f"{self.protocol}://{publisher_hostname}:{pubsub_port+1}" if pubsub_port != -1 else f"{self.protocol}://{publisher_hostname}"
        
        self.reqres_full_uri = f"{self.protocol}://{hostname}:{req_res_port}" if req_res_port != -1 else f"{self.protocol}://{hostname}"
        self.pubsub_socket = None
        self.reqres_socket = None
        self.last_ping_at = -1
        self.max_health_tick_time = HF.parse_timespan(max_health_ping_time)
        self.max_retries = max_retries
        self.is_connected = False
        self.max_recv_timeout = int(HF.parse_timespan(max_recv_timeout)*1000)

    
    def start(self)->int:
        current_tries = 0
        # current_time = T.time()
        # diff = current_time - self.last_ping_at
        while not self.is_connected and current_tries < self.max_retries:
            try:
                if current_tries > 0:
                    print("Retrying to connect to {}...".format(self.reqres_full_uri))
                    
                if self.pubsub_socket == None or self.reqres_socket == None:
                    self.context = zmq.Context()

                if self.reqres_socket==None:
                    self.reqres_socket = self.context.socket(zmq.REQ)
                    self.reqres_socket.setsockopt(zmq.RCVTIMEO, self.max_recv_timeout)
                    self.reqres_socket.connect(self.reqres_full_uri)
                current_time = T.time()
                diff = current_time - self.last_ping_at
                
                if not self.reqres_socket  == None and ( self.last_ping_at ==-1 or  diff >= self.max_health_tick_time ):
                    T.sleep(1)
                    try:
                        x = self.reqres_socket.send_multipart([b"activex",b"PING",b"{}"],track=True)
                        y = self.reqres_socket.recv_multipart()
                        self.last_ping_at = T.time()   
                        self.is_connected = True
                        return 0
                    
                    except Exception as e:
                        if not self.reqres_socket == None:
                            self.reqres_socket.close(linger=1)
                        # if not self.pubsub_socket == None:
                            # self.pubsub_socket.close(linger=1)
                        if not self.context == None:
                            self.context.destroy()
                        self.context=None
                        self.reqres_socket= None 
                        self.pubsub_socket = None
                        print("Failed to connect to {}: {}".format(self.reqres_full_uri, str(e)))
            except Exception as e:
                print("Failed to connect to {}: {}".format(self.reqres_full_uri, str(e)))
            finally:
                current_tries+=1
        return 0 if self.is_connected else -1

    def put(self, key: str, metadata: ASMACMeta)->Result[str,Exception]:
        try:
            
            status = self.start()
            start_time = T.time()
            json_metadata =metadata.model_dump().copy()
            json_metadata_str = J.dumps(json_metadata)
            json_metadata_bytes = json_metadata_str.encode(encoding="utf-8")
            request_tracker = self.reqres_socket.send_multipart([b"activex",b"PUT.METADATA", json_metadata_bytes])
            response = self.reqres_socket.recv_multipart()
            print("PUT.METADATA %s %s", key, T.time() - start_time)
            return Ok(key)
        except Exception as e:
            return Err(e)

    def get(self, key: str)->Result[ASMACMeta,Exception]:
        try:
            print("GET.METADATA %s", key)
            return Ok(key)
        except Exception as e:
            return Err(Exception("Not implemented yet."))

    def __deserialize(self,x:bytes)->Any:
        try:
            return CP.loads(x)
        except Exception as e:
            return J.loads(x)
        
    def method_execution(self,key:str,fname:str,ao:AsmacMetaClass,f:GenericFunction,fargs:list=[],fkwargs:dict={}) -> Result[Any, Exception]:
        start_time = T.time()
        try:
            payload = {
                "key":key,
                "fname":fname
            }
            payload_bytes = J.dumps(payload).encode(self.encoding)

            f_bytes = CP.dumps(f)
            self.reqres_socket.send_multipart([b"ASMAC",b"METHOD.EXEC", payload_bytes, f_bytes,CP.dumps(fargs[1:]), CP.dumps(fkwargs)])
            response_multipart = self.reqres_socket.recv_multipart()
            if len(response_multipart) == 5:
                topic_bytes,operation_bytes,status_bytes,metadata_bytes, result_bytes  = response_multipart
                
                topic           = topic_bytes.decode()
                operation       = operation_bytes.decode()
                status          = int.from_bytes(bytes=status_bytes, byteorder="little",signed=True )
                result          = self.__deserialize(x= result_bytes)
                result_metadata = J.loads(metadata_bytes)
                
                return Ok(result)
            else:
                return Err(Exception("Not expected response: {}".format(len(response_multipart))))
        except Exception as e:
            return Err(e)
    
    def add_code(self, ao: AsmacMetaClass) -> Result[bool, Exception]:
        start_time = T.time()
        try:
            payload = {
                "module":ao._acx_metadata.class_name, 
                "class_name":ao._acx_metadata.class_name,
                "axo_bucket_id": ao._acx_metadata.axo_bucket_id,
                "class_def_key":"{}_class_def".format(ao._acx_metadata.axo_key)
            }
            payload_bytes = J.dumps(payload).encode(self.encoding)
            self.reqres_socket.send_multipart([b"ASMAC",b"ADD.CODE",payload_bytes])
            
            return Ok(False)
        except Exception as e:
            return Err(e)

    def to_string(self):
        return "{}:{}:{}:{}:{}".format(self.endpoint_id,self.protocol,self.hostname,self.req_res_port,self.pubsub_port)
    
    @staticmethod
    def from_str(endpoint_str:str)->'DistributedEndpoint':
        x = endpoint_str.split(":")
        return DistributedEndpoint(
            endpoint_id=x[0],
            protocol=x[1],
            hostname=x[2],
            req_res_port=x[3],
            pubsub_port=x[4],
        )

    
class EndpointManager(ABC):
    def __init__(self,endpoints:Dict[str,DistributedEndpoint]={},endpoint_id:str=""):
        self.endpoints = endpoints
        self.endpoint_id = endpoint_id
        self.counter =0 
        
    def exists(self,endpoint_id:str)->bool:
        return endpoint_id in self.endpoints
        # eids = self.endpoints.values(
    def get_endpoint(self,endpoint_id:str="")->DistributedEndpoint:
        if not endpoint_id  in self.endpoints:
            i = self.counter%len(self.endpoints)
            self.counter+=1
            return list(self.endpoints.values())[i]
        self.counter+=1
        return self.endpoints.get(endpoint_id)
    
    def add_endpoint(self,endpoint_id:str,hostname:str, pubsub_port:int, req_res_port:int,protocol:str="tcp"):
        x= DistributedEndpoint(protocol=protocol,hostname=hostname,endpoint_id=endpoint_id, req_res_port=req_res_port,pubsub_port=pubsub_port)
        if not self.endpoint_id== endpoint_id:
            status = x.start()
            if status == -1:
                raise Exception("Failed to start the endpoint: {}".format(endpoint_id))
        self.endpoints[endpoint_id] = x

    def del_endpoint(self,endpoint_id):
        return self.endpoints.pop(endpoint_id)
    
    def get_available_port(self,ports:Set[int], low:int=16000,high:int = 65000)->int:
        while True:
            port = random.randint(low, high)
            if port not in ports:
                return port
            
    def get_available_req_res_port(self)->int:
        return self.get_available_port(
            ports=  set(list(map(lambda x: x.req_res_port,self.endpoints.values())))
        )
        
    def get_available_pubsub_port(self)->int:
        return self.get_available_port(
            ports=  set(list(map(lambda x: x.pubsub_port,self.endpoints.values())))
        )