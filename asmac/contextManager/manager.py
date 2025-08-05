import string
from nanoid import generate as nanoid
from typing import Optional,Set, Dict, Any
from abc import ABC, abstractmethod
import random
from asmac.runtime import get_runtime,set_runtime, LocalRuntime, DistributedRuntime, Runtime
from asmac.endpoint.endpoint import EndpointManager

class ContextManager:
    is_running = False
    def __init__(self, runtime:Optional[Runtime] = None):
        self.prev_runtime = get_runtime()
        if runtime == None:
            self.runtime = LocalRuntime(
                runtime_id="local-{}".format(nanoid(alphabet=string.ascii_lowercase+string.digits))
            )
        else:
            self.runtime = runtime
        set_runtime(self.runtime)
        self.is_running = True

    @staticmethod
    def local()->'ContextManager':
        return ContextManager(
            runtime= LocalRuntime(
                runtime_id="local-{}".format(nanoid(alphabet=string.ascii_lowercase+string.digits)),
            )
        )
        
    @staticmethod
    def distributed(
        endpoint_manager:EndpointManager,
    )->'ContextManager':
        return ContextManager(
            runtime= DistributedRuntime(
                runtime_id="distributed-{}".format(nanoid(alphabet=string.ascii_lowercase+string.digits)),
                endpoint_manager=endpoint_manager
            )
        )
        
    def stop(self):
        if not self.is_running:
            return
        self.runtime.stop()
        set_runtime(self.prev_runtime)
        self.is_running=False

    def __del__(self):
        self.stop()
        
