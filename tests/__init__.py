from asmac import ASMAC,active_method
from asmac.endpoint.endpoint import EndpointManager
from asmac.contextManager import ContextManager
from  common import Proximidad
import random
class example(ASMAC):
    
    def __init__(self):
        self.name = "example"
        self.value = 42
  
    def method(self):
        return random.randint(1, 100)    

#endpoint=EndpointManager()
#ax=ContextManager.local()
obj = Proximidad()
print(obj.metadata)
print(obj.get_dependencies())
print(obj.get_source_code())
obj.get_file_code()