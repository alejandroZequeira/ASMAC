from queue import Queue
from option import Option, NONE

from asmac.scheduler import Scheduler
from asmac.storage import  StorageService
#from asmac.endpoint import EndpointManager, LocalEndpoint

class LocalRuntime:
    def __init__(self, runtime_id: str="",  is_distributed: bool = False, maxsize:int=100, storage_service:Option[StorageService] = NONE):
        q= Queue(maxsize= maxsize)
        # default_ss =  (lambda _:  )
        super().__init__(
            q=q,
            scheduler= Scheduler(
                tasks=[], 
                runtime_q=q
            ),
            runtime_id=runtime_id,
            is_distributed=is_distributed, 
        )

    def stop(self):
        print("Stopping the local runtime %s", self.runtime_id)