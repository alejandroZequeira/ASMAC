from activex import Axo
from activex.endpoint import XoloEndpointManager
from common import User,Object,service,Mesh,ASMACMeta
from storage import StorageService, MongoDBStorageService
import os

AXO_ENDPOINT_ID           = os.environ.get("AXO_ENDPOINT_ID","activex-endpoint-0")
AXO_ENDPOINT_PROTOCOL     = os.environ.get("AXO_ENDPOINT_PROTOCOL","tcp")
AXO_ENDPOINT_HOSTNAME     = os.environ.get("AXO_ENDPOINT_HOSTNAME","localhost")
AXO_ENDPOINT_PUBSUB_PORT  = int(os.environ.get("AXO_ENDPOINT_PUBSUB_PORT","16000"))
AXO_ENDPOINT_REQ_RES_PORT = int(os.environ.get("AXO_ENDPOINT_REQ_RES_PORT","16667"))

def init_axo():
    endporint = XoloEndpointManager(
        endpoint_id=AXO_ENDPOINT_ID,
        protocol=AXO_ENDPOINT_PROTOCOL,
        hostname=AXO_ENDPOINT_HOSTNAME,
        pubsub_port=AXO_ENDPOINT_PUBSUB_PORT,
        req_res_port=AXO_ENDPOINT_REQ_RES_PORT
    )
    return endporint

# funciones de control de usuario
def create_user(name:str, password:str, user_name:str=None, storage_service:StorageService=None) -> User:
    user = User(name=name, password=password, user_name=user_name)
    if storage_service:
        result = storage_service.put("users", user.user_id, user)
        if result.is_ok():
            print(f"Usuario {user.name} creado correctamente.")
        else:
            print(f"Error al crear usuario: {result.error}")
    return user

def login_user(user_id:str, password:str, storage_service:StorageService=None) -> User:
    if storage_service:
        result = storage_service.get("users", user_id)
        if result.is_ok():
            user_data = result.value
            if user_data.password == password:
                print(f"Usuario {user_data.name} autenticado correctamente.")
                return user_data
            else:
                print("Contraseña incorrecta.")
                return None
        else:
            print(f"Error al recuperar usuario: {result.error}")
            return None
    else:
        print("Servicio de almacenamiento no disponible.")
        return None

# funciones para manejo de objetos
def set_object(obj:Axo,alias:str,is_public: bool,user_id:str,storage_service:StorageService):
    if isinstance(storage_service, MongoDBStorageService):
        res= Object.set_object(obj=obj, alias=alias, is_public=is_public, user_id=user_id)
        if res.is_ok():
            print(f"Objeto {obj.key} preparado para publicación.")
            result = storage_service.put("objects", obj.key, obj)
            if result.is_ok():
                print(f"Objeto {obj.key} publicado correctamente.")
            else:
                print(f"Error al publicar objeto: {result.error}")
    else:
        print("Servicio de almacenamiento no soportado.")
        

def get_object_by_alias():
    pass


#funciones para manejo de las mallas
def create_mesh():
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


# binding objects
def create_binding_object():
    pass

def execute_binding_object():
    pass