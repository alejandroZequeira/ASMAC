from abc import ABC, abstractmethod
from threading import Thread
from queue import Queue
from typing import Optional
from weakref import WeakKeyDictionary
from nanoid import generate as nanoid
from option import Result, Ok, Err
import time as T

import cloudpickle as pickle
from asmac.endpoint.endpoint import EndpointManager
#from asmac.runtime import get_runtime, set_runtime
from asmac.storage.storage import StorageService
from asmac.import_manager import  DefaultImportManager
from asmac.common.metaclass import AsmacMetaClass
from asmac.scheduler import Task

class Runtime(ABC,Thread):
    """
    Base class for all runtimes.
    """
    def __init__(self, runtime_id: str,queue:Queue, endpoint_manager: EndpointManager,storage_service: StorageService,is_distributed: bool = False):
        Thread.__init__(self,daemon=True, name="ASMAC-runtime")
        self.runtime_id = runtime_id
        self.queue = queue
        self.endpoint_manager = endpoint_manager
        self.storage_service = storage_service
        self.is_distributed = is_distributed
        self.is_running = True
        self.in_memory_objects = WeakKeyDictionary()
        self.remote_objects = set()
        self.import_manager= DefaultImportManager()
        self.start()

    def get_active_object(self,bucket_id:str,key:str)->Result[AsmacMetaClass,Exception]:
        return self.storage_service._get_active_object(key=key,bucket_id=bucket_id)
    
    def persistify(
            self,
            instance:AsmacMetaClass ,
            bucket_id:Optional[str] = None,
            key:Optional[str] = None,
    )->Result[str,Exception]:
        
        try:
            instance_endpoint_id = instance.get_endpoint_id()
            endpoint             = self.endpoint_manager.get_endpoint(endpoint_id=instance_endpoint_id )
            m_result = endpoint.put(
                key=key,
                metadata=instance._acx_metadata
            )
            if m_result.is_err:
                return Err(Exception("Active object storage metadata failed: {}".format(str(m_result.unwrap_err()))))
            class_def_put_result = self.storage_service.put(
                bucket_id=bucket_id,
                key="{}_class_def".format(key),
                tags={
                    "module":instance._acx_metadata.module,
                    "class_name":instance._acx_metadata.class_name
                },
                data= pickle.dumps(self.__class__)
            )
            class_def_key = class_def_put_result.unwrap()

            tags = instance._acx_metadata.to_json_with_string_values()
            tags["class_def_key"] = class_def_key
            s_result = self.storage_service.put(
                # obj=instance,
                bucket_id=bucket_id,
                key=key,
                data= instance.to_bytes(),
                tags=tags
            )

            if s_result.is_err:
                return Err(Exception("Active object storage failed: {}".format(str(s_result.unwrap_err()))))
            return Ok(key)
        except Exception as e:
            return Err(e)
            
        # logger.debug("%s persistify",key)

    @abstractmethod
    def stop(self):
        pass
    def run(self) -> None:
        while self.is_running:
            task:Task = self.q.get()
            current_time = T.time()
            if current_time >= task.executes_at:
                path       = task.metadata.get("path","")
                bucket_id  = task.metadata.get("bucket_id","activex")
                chunk_size = task.metadata.get("chunk_size","1MB")
                
                if task.operation == "PUT" and not path =="" and not path in self.remote_files:
                    result = self.storage_service.put_data_from_file(
                        bucket_id=bucket_id,
                        key="",
                        source_path=path,
                        tags={},
                        chunk_size=chunk_size
                    )
                    if result.is_ok:
                        self.remote_files.add(path)
                    else:
                        print("Error: {}".format(result.unwrap_err()))
                elif task.operation == "DROP":
                    print("DROP")