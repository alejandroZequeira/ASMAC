from axo import Axo, axo_method
from axo.endpoint.manager import DistributedEndpointManager
from axo.contextmanager.contextmanager import AxoContextManager
from axo.storage.data import MictlanXStorageService
import axo.storage.data as axo_data 

axo_data.Axo = Axo
axo_data.axo_method = axo_method

from .common import User,Object,service,Mesh,ASMACMeta
from .storage import StorageService, MongoDBStorageService
from option import Result, Ok, Err
import os
AXO_ENDPOINT_ID           = os.environ.get("AXO_ENDPOINT_ID","activex-endpoint-0")
AXO_ENDPOINT_PROTOCOL     = os.environ.get("AXO_ENDPOINT_PROTOCOL","tcp")
AXO_ENDPOINT_HOSTNAME     = os.environ.get("AXO_ENDPOINT_HOSTNAME","localhost")
AXO_ENDPOINT_PUBSUB_PORT  = int(os.environ.get("AXO_ENDPOINT_PUBSUB_PORT","16000"))
AXO_ENDPOINT_REQ_RES_PORT = int(os.environ.get("AXO_ENDPOINT_REQ_RES_PORT","16667"))

def init_axo():
        endpoint = DistributedEndpointManager()
        endpoint.add_endpoint(
            endpoint_id=AXO_ENDPOINT_ID,
            protocol=AXO_ENDPOINT_PROTOCOL,
            hostname=AXO_ENDPOINT_HOSTNAME,
            pubsub_port=AXO_ENDPOINT_PUBSUB_PORT,
            req_res_port=AXO_ENDPOINT_REQ_RES_PORT
        )
        return endpoint

default_storage_service = MongoDBStorageService()
class ASMaC_Backend:
    # funciones de control de usuario
    def create_user(name:str, password:str, user_name:str=None, storage_service:StorageService=default_storage_service) -> User:
        user = User(name=name, password=password, user_name=user_name)
        if storage_service:
            comprobation = storage_service.get(collection_name="users", condition={"user_name": user.user_name})
            if comprobation.is_ok:
                print(f"Usuario {user.user_name} ya existe.")
                return None
            else:
                print(f"Usuario {user.user_name} no existe, creando nuevo usuario.")
            result = storage_service.put(collection="users", key=user.user_id, obj=user)
            if result.is_ok:
                print(f"Usuario {user.name} creado correctamente.")
                return user.to_json()
            else:
                print(f"Error al crear usuario")
                return None

    def login_user(user_name:str, password:str, storage_service:StorageService=default_storage_service) -> User:
        if storage_service:
            result = storage_service.get(collection_name="users",condition={"user_name": user_name})
            #print(f"Resultado de la búsqueda: {result}")
            if result.is_ok:
                #print(f"Usuario {user_name} encontrado.")
                user_data = result.unwrap()
                #print(f"Datos del usuario: {user_data}")
                if user_data["password"] == password:
                    return user_data
                else:
                    print("Contraseña incorrecta.")
                    return None
            else:
                print(f"Error al recuperar usuario")
                return None
        else:
            print("Servicio de almacenamiento no disponible.")
            return None

    # funciones para manejo de objetos
    async def set_object(obj:Axo,alias:str="",is_public: bool=False,user_id:str="",storage_service:StorageService=default_storage_service):
        new_object = Object()
        exist_object =  storage_service.get("objects", condition={"user_id": user_id, "alias": alias})
        if exist_object.is_ok:
            return Err(f"El objeto con alias '{alias}' ya existe para el usuario {user_id}.")
        else:
            res= await new_object.set_object(obj=obj, alias=alias, is_public=is_public, user_id=user_id)
            #print(res)
            if res.is_ok:
                print(new_object)
                res=res.unwrap()
                #print(f"Objeto {obj.get_axo_key()} preparado para publicación.")
                result =  storage_service.put("objects", new_object.key, new_object)
                if result.is_ok:
                    #print(f"Objeto {new_object} publicado correctamente.")
                    return Ok(new_object)
                else:
                    #print(f"Error al publicar objeto: {result}")
                    return Err(f"Error al publicar objeto: {result}")
            else:
                #print(f"Error al preparar objeto: {res}")
                return Err(f"Error al preparar objeto: {res}")

    async def get_object_by_alias(alias: str,user_id:str, storage_service:StorageService=default_storage_service):
        result=storage_service.get("objects", condition={"user_id":user_id, "alias":alias})
        #print(f"Resultado de la búsqueda por alias '{alias}': {result}")
        if result.is_ok:
            result=result.unwrap()
            #print(f"Objeto encontrado: {result}")
            with AxoContextManager.distributed(endpoint_manager=init_axo()) as cx:
                #print(result["key"], result["bucket_id"])
                data= await Axo.get_by_key( bucket_id=result["bucket_id"],key=result["key"])
                #print(f"Objeto recuperado por alias '{alias}': {data}")
                if data.is_ok:
                    return data
                else:
                    #print(f"Error al recuperar objeto por alias: {data}")
                    return Err(f"Error al recuperar objeto por alias '{alias}': {data}")
        else:
            #print(f"Error al buscar objeto por alias: {result}")
            return Err(f"Error al buscar objeto por alias '{alias}': {result}")
    
    #funciones para manejo de las mallas
    def create_mesh(name:str, description:str, user_id:str, storage_service:StorageService=default_storage_service):
        pass

    def publish_object_to_mesh():
        pass

    def get_object_to_mesh():
        pass

    def get_objects_to_mesh():
        pass

    # funciones para el manejo de los servicios
    def create_service():
        pass

    def get_meshes():
        pass

    # binding objects
    def create_binding_object():
        pass

    def execute_binding_object():
        pass