from typing import Dict
import time as T
from nanoid import generate as nanoid
import humanfriendly as HF
import string
import os
from queue import Queue
from threading import Thread
from abc import ABC
from typing import List

ALPHABET = string.ascii_lowercase + string.digits

class Task:
    def __init__(self,operation:str,executed_at:float = -1,metadata:Dict[str,str]={}) -> None:
        self.id = nanoid(alphabet=ALPHABET)
        self.created_at = T.time()
        if executed_at < self.created_at :
            self.executes_at = self.created_at
        else:
            self.executes_at  = self.created_at if executed_at < 0 else executed_at
        self.wainting_time = 0
        self.operation= operation
        self.metadata = metadata
        self.max_waiting_time = HF.parse_timespan("1m")
    def __str__(self) -> str:
        return "Task(id={}, operation={})".format(self.id,self.operation)
    

class Scheduler(ABC,Thread):
    def __init__(self,
                 runtime_q:Queue,
                 scheduler_name:str="activex-scheduler",
                 tasks:List[Task]=[],
                 maxsize:int=100
    ) -> None:
        Thread.__init__(self,daemon=True)
        self.setName(scheduler_name)
        self.runtime_queue = runtime_q
        self.q = Queue(maxsize=maxsize)
        self.tasks=tasks
        self.is_running = True
        self.heartbeat = 1
        self.start()

    def schedule(self,task:Task):
        self.q.put(task)
    def run(self) -> None:
        while self.is_running:
            task:Task = self.q.get()
            current_time = T.time()

            if task.executes_at <= current_time:
                if task.operation == "PUT":
                    path = task.metadata.get("path",None)
                    if os.path.exists(path=path) :
                        self.runtime_queue.put(
                            Task(
                                operation="PUT", 
                                metadata={
                                    "task_id": task.id,
                                    "path":path
                                }
                            )
                        )

                    else:
                        T.sleep(self.heartbeat)
                        task.wainting_time = current_time - task.created_at
                        self.q.put(task)

            else:
                T.sleep(self.heartbeat)
                task.wainting_time = current_time - task.created_at
                if task.wainting_time >= task.max_waiting_time:
                    self.runtime_queue.put(Task(operation="DROP", metadata={"task_id": task.id}))
                else:
                    self.q.put(task)