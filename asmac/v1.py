import inspect
from typing import List, Dict, Any
from functools import wraps
from option import Result,Ok,Err
from typing import TypeVar
import cloudpickle as CP
import struct
import types 
import time as T
import importlib.util, sys, inspect
import ast, sys, importlib.util
from typing import List, Set
import os

from asmac.runtime import get_runtime


from asmac.common.metaclass import metaclient, ASMACMeta, generate_id_size

R = TypeVar('R')


def active_method(f):
    @wraps(f)
    def __active_method(self:ASMAC, *args, **kwargs):
        try:
            runtime = get_runtime()
            self.set_endpoint_id(endpoint_id=runtime.endpoint_manager.get_endpoint().endpoint_id)
            endpoint= runtime.endpoint_manager.get_endpoint(endpoint_id= kwargs.get("endpoint_id",""))
            if not runtime.is_distributed:
                kwargs["storage"]= runtime.storage_service
            
            if runtime.is_distributed and self.local:
                self.persistent()
            
            res=endpoint.method_execution(key=self.metadata.key,fname=f.__name__,ao=self,f=f,fargs=args,fkwargs=kwargs)
            return res
        except Exception as e:
            print("Error in method {}: {}".format(f.__name__, str(e)))
            raise RuntimeError(f"Error in method {f.__name__}: {str(e)}")
    return __active_method




class ASMAC: 
    metadata: ASMACMeta
    local: bool = True
    remote: bool = False
    def __new__(cls, *args, **kwargs):
        obj= super().__new__(cls)
        class_name = cls.__name__
        module= cls.__module__
        name=cls.__name__
        deps = ASMAC._extract_external_dependencies(cls)
        obj.metadata = ASMACMeta(
            module=module,
            name=name,
            dependencies=deps,
            class_name=class_name,
        )
        obj.metadata.code= obj.get_source_code()
        return obj
    
    def __init__(cls,tags:Dict[str,str]={},version:str  = "v0"):     
        obj = super().__new__(cls)
        # obj.object_id = nanoid(ALPHABET) if object_id =="" else object_id
        obj.tags= tags
        obj.metadata.version=version

    @staticmethod
    def _extract_external_dependencies(cls) -> List[str]:
        dependencies = set()
        try:
            module = sys.modules.get(cls.__module__)
            if module is None:
                return []

            source_file = inspect.getfile(module)
            with open(source_file, 'r', encoding='utf-8') as f:
                source = f.read()
            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module = alias.name.split('.')[0]
                        if ASMAC._is_external(module):
                            dependencies.add(module)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module = node.module.split('.')[0]
                        if ASMAC._is_external(module):
                            dependencies.add(module)
        except Exception as e:
            print(f"Error al extraer dependencias: {e}")
            pass

        return list(dependencies)


    def _is_external(module_name: str) -> bool:
        try:
            spec = importlib.util.find_spec(module_name)
            return spec is not None and "site-packages" in (spec.origin or "")
        except:
            return False

    
    def get_source_code(self):
        try:
            code= inspect.getsource(self.__class__)
            return code
        except TypeError:
            return "The provided object has no source code (it can be a built-in or dynamic object)."
        except OSError:
            return "The source code (possibly defined in an interactive or compiled environment) could not be retrieved."
        
    def get_file_code(self):
        nombre_archivo="__init__.py"
        # Obtiene la ruta absoluta donde está este script
        ruta_base = os.path.dirname(os.path.abspath(__file__))
        # Crea la ruta completa a la carpeta destino
        name="dummy"
        ruta_carpeta = os.path.join(ruta_base, name)
        # Crea la carpeta si no existe
        os.makedirs(ruta_carpeta, exist_ok=True)
        # Ruta final del archivo
        ruta_archivo = os.path.join(ruta_carpeta, nombre_archivo)
        # Escribe el archivo
        code=""
        dependencies=self.get_dependencies()
        if len(dependencies)!=0:
            for d in dependencies:
                code+="import "+d+"\n"
        code+=self.metadata.code
        with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
            archivo.write(code)
    
    def get_dependencies(self)->List[str]:
        return self.metadata.dependencies
    
    def set_dependencies(self,dependcies: List[str])->List[str]:
        self.metadata.dependencies = List(set(dependcies))
        return self.metadata.dependencies
    
    def append_dependencies(self,dependencies:List[str])->List[str]:
        A = set(dependencies)
        B = set(self.metadata.dependencies)
        self.metadata.dependencies = list(A.union(B))
        return self.metadata.dependencies
    
    def get_key(self)->str:
        return self.metadata.key
    
    def get_bucket_id(self)->str:
        return self.metadata.bucket_id
    
    def set_endpoint_id(self,endpoint_id:str="")->str:
        if endpoint_id =="":
            _endpoint_id = "ASMAC-endpoint-{}".format(generate_id_size(8)(v=endpoint_id))
        else:
            _endpoint_id = endpoint_id
        
        self.metadata.endpoint_id = _endpoint_id
        return self.metadata.endpoint_id
    
    def get_endpoint_id(self)->str:
        if self.metadata.endpoint_id == "":
            return self.set_endpoint_id()
        return self.metadata.endpoint_id
    
    def to_bytes(self)->bytes:
        attrs            = self.__dict__
        methods          = dict([ (attr,getattr(self, attr) )  for attr in dir(self) if callable(getattr(self, attr))])
        attrs_bytes      = CP.dumps(attrs)
        methods_bytes    = CP.dumps(methods)
        class_def_bytes  = CP.dumps(self.__class__)
        class_code_str   = self.get_source_code()
        class_code_bytes = CP.dumps(class_code_str.encode())
        packed_data = b''
        for data in (attrs_bytes, methods_bytes, class_def_bytes, class_code_bytes):
            # Prefix each part with its length (using 4 bytes for the length)
            packed_data += struct.pack('I', len(data)) + data
        return packed_data
    
    @staticmethod
    def call(instance,method_name:str,*args,**kwargs)->Result[R,Exception]:
        # print("methods",method_name,instance)
        try:
            if hasattr(instance,method_name):
                value = getattr(instance, method_name)
                is_callable = inspect.isfunction(value) or inspect.ismethod(value)
                if is_callable:
                    output = value(*args,**kwargs)
                    return Ok(output)
                else:
                    return Ok(value)
                # if 
                # return Ok(value(*args,kwargs)) if  else Ok(value)
            return Err(Exception("{} not found in the object instance.".format(method_name)))
        except Exception as e:
            return Err(e)
        
    @staticmethod
    def from_bytes(raw_obj:bytes,original_f:bool=False):
        try:
            index = 0
            # Attrs, Methods, ClassDefinition, ClassCode
            unpacked_data = []
            while index < len(raw_obj):
                # Read length
                length = struct.unpack_from('I', raw_obj, index)[0]
                index += 4  # Move past the length field
                # Read data
                data = raw_obj[index:index+length]
                index += length
                unpacked_data.append(CP.loads(data))  # Deserialize each component
            attrs    = unpacked_data[0]
            methods = unpacked_data[1]
            class_df = unpacked_data[2]
            instance:ASMAC = class_df()
            for attr_name, attr_value in attrs.items():
                if attr_name not in ('__class__', '__dict__', '__module__', '__weakref__'):
                    setattr(instance, attr_name, attr_value)
            for method_name, func in methods.items():
                if "original" in dir(func) and original_f:
                    func = func.original
                bound_method = types.MethodType(func, instance)
                if method_name not in ('__class__', '__dict__', '__module__', '__weakref__'):
                    setattr(instance, method_name, bound_method)
            # f0       = methods["test"].original
            return Ok(instance)
        except Exception as e:
            return Err(e)
        
    def get_attrs(self):
        return self.__dict__
    @staticmethod
    def get_by_id(self, id: str):
        pass
    
    @staticmethod
    def persistent(self, buckerd_id: str="", key: str="",alias: str="")->Result[str,Exception]:
        try:
            start_time = T.time()
            _key = self.get_key() if key == "" else key
            _bucket_id = self.get_bucket_id() if buckerd_id == "" else buckerd_id
            _alias = _key if alias == "" else alias
            runtime = get_runtime()
            endpoint = runtime.endpoint_manager.get_endpoint()
            self.set_endpoint_id(endpoint_id=endpoint.endpoint_id)
            result = runtime.persistify(
                instance=self,
                bucket_id=_bucket_id,
                key=_key,
                alias=_alias
            )
            if result.is_ok:
                return result
            print("Persistify Failed {} seconds".format(T.time()-start_time))
            return result
        except Exception as e:
            return Err(e)


    
class Binding(ASMAC):
    pass