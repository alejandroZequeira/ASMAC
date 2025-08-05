from typing import Union, TYPE_CHECKING
import contextvars

from asmac.runtime.localRuntime import LocalRuntime
from asmac.runtime.distributedRuntime import DistributedRuntime
from asmac.runtime.runtime import Runtime

context_var = contextvars.ContextVar("current_session")
current_runtime: Union['LocalRuntime','DistributedRuntime', None] = None

def get_runtime()-> Union['LocalRuntime','DistributedRuntime',None]:
    return current_runtime


def set_runtime(runtime:Union['LocalRuntime','DistributedRuntime']) :
    global current_runtime
    current_runtime = runtime