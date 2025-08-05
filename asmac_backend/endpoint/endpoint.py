from abc import ABC, abstractmethod

class Endpoint(ABC):
    def __init__(self,protocol:str="tcp", hostname:str= "127.0.0.1", req_res_port:int = 46501, pubsub_port:int=46500,encoding:str ="utf-8",endpoint_id:str="asmac-endpoint-0",is_local:bool=True):
        self.endpoint_id  = endpoint_id
        self.protocol = protocol
        self.hostname = hostname
        self.req_res_port=req_res_port
        self.pubsub_port= pubsub_port
        self.encoding=encoding
        self.is_local:bool = is_local