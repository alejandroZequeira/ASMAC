from axo import Axo, axo_method
from axo.endpoint.manager import DistributedEndpointManager
from axo.contextmanager.contextmanager import AxoContextManager
from axo.storage.data import MictlanXStorageService
import axo.storage.data as axo_data 

axo_data.Axo = Axo
axo_data.axo_method = axo_method

from .common import User,Object,service,Mesh,ASMACMeta,BindingObject
from .storage import StorageService, MongoDBStorageService
from option import Result, Ok, Err
import os
import time as T
from .log import get_logger
AXO_ENDPOINT_ID           = os.environ.get("AXO_ENDPOINT_ID","activex-endpoint-0")
AXO_ENDPOINT_PROTOCOL     = os.environ.get("AXO_ENDPOINT_PROTOCOL","tcp")
AXO_ENDPOINT_HOSTNAME     = os.environ.get("AXO_ENDPOINT_HOSTNAME","localhost")
AXO_ENDPOINT_PUBSUB_PORT  = int(os.environ.get("AXO_ENDPOINT_PUBSUB_PORT","16000"))
AXO_ENDPOINT_REQ_RES_PORT = int(os.environ.get("AXO_ENDPOINT_REQ_RES_PORT","16667"))

logger = get_logger(name=__name__, ltype="json")
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
        start=T.time()
        user = User(name=name, password=password, user_name=user_name)
        if storage_service:
            comprobation = storage_service.get(collection_name="users", condition={"user_name": user.user_name})
            if comprobation.is_ok:
                logger.error({
                    "event": "CREATE.USER",
                    "mode":"DISTRIBUTED",
                    "mensage": "User already exists",
                    "response_time": T.time() - start,  
                })
                print(f"Usuario {user.user_name} ya existe.")
                return None
            else:
                print(f"Usuario {user.user_name} no existe, creando nuevo usuario.")
            result = storage_service.put(collection="users", key=user.user_id, obj=user)
            if result.is_ok:
                logger.info({
                    "event": "CREATE.USER",
                    "mode":"DISTRIBUTED",
                    "user_id": user.user_id,
                    "mensage": "User created successfully",
                    "response_time": T.time() - start,  
                })
                print(f"Usuario {user.name} creado correctamente.")
                return user.to_json()
            else:
                logger.error({
                    "event": "CREATE.USER",
                    "mode":"DISTRIBUTED",
                    "mensage": "User already exists",
                    "response_time": T.time() - start,  
                })
                print(f"Error al crear usuario")
                return None

    def login_user(user_name:str, password:str, storage_service:StorageService=default_storage_service) -> User:
        start=T.time()
        if storage_service:
            result = storage_service.get(collection_name="users",condition={"user_name": user_name})
            #print(f"Resultado de la búsqueda: {result}")
            if result.is_ok:
                #print(f"Usuario {user_name} encontrado.")
                user_data = result.unwrap()
                #print(f"Datos del usuario: {user_data}")
                if user_data["password"] == password:
                    logger.info({ 
                    "event": "LOGIN.USER",
                    "mode":"DISTRIBUTED",
                    "mensage": "User logged in successfully",
                    "response_time": T.time() - start,})
                    return user_data
                else:
                    logger.info({
                    "event": "LOGIN.USER",
                    "mode":"DISTRIBUTED",
                    "mensage": "password incorrect",
                    "response_time": T.time() - start,  
                })
                    print("Contraseña incorrecta.")
                    return None
            else:
                logger.info({
                    "event": "LOGIN.USER",
                    "mode":"DISTRIBUTED",
                    "mensage": "User not found",
                    "response_time": T.time() - start,  
                })                
                print(f"Error al recuperar usuario")
                return None
        else:
            logger.error({
                    "event": "LOGIN.USER",
                    "mode":"DISTRIBUTED",
                    "mensage": "Storage service not available",
                    "response_time": T.time() - start,  
                })
            print("Servicio de almacenamiento no disponible.")
            return None
        
    def get_user(user_name:str,storage_service: StorageService=default_storage_service)->User:
        start=T.time()
        if storage_service:
            result = storage_service.get(collection_name="users",condition={"user_name": user_name})
            if result.is_ok:
                logger.info({
                    "event": "GET.USER",
                    "mode":"DISTRIBUTED",
                    "mensage": "User retrieved successfully",
                    "response_time": T.time() - start,  
                })
                return result.unwrap()
            else:
                logger.error({
                    "event": "GET.USER",
                    "mode":"DISTRIBUTED",
                    "mensage": "Error retrieving user",
                    "response_time": T.time() - start,  
                })
                print(f"Error al recuperar usuario")
                return None
        else:
            logger.error({
                    "event": "GET.USER",
                    "mode":"DISTRIBUTED",
                    "mensage": "Storage service not available",
                    "response_time": T.time() - start,  
                })
            print("Servicio de almacenamiento no disponible.")
            return None
        
    # funciones para manejo de objetos
    async def set_object(obj:Axo,alias:str="",is_public: bool=False,user_id:str="",storage_service:StorageService=default_storage_service):
        start=T.time()
        new_object = Object()
        exist_object =  storage_service.get("objects", condition={"user_id": user_id, "alias": alias})
        if exist_object.is_ok:
            logger.info({
                    "event": "SET.OBJECT",
                    "mode":"DISTRIBUTED",
                    "mensage": f"Object with alias '{alias}' already exists for user {user_id}",
                    "response_time": T.time() - start,  
                })
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
                    logger.info({
                        "event": "SET.OBJECT",
                        "mode":"DISTRIBUTED",
                        "object_key": new_object.key,
                        "user_id": user_id,
                        "mensage": f"Object '{alias}' published successfully",
                        "response_time": T.time() - start,  
                    })
                    #print(f"Objeto {new_object} publicado correctamente.")
                    return Ok(new_object)
                else:
                    logger.error({
                        "event": "SET.OBJECT",
                        "mode":"DISTRIBUTED",
                        "mensage": f"Error publishing object '{alias}'",
                        "response_time": T.time() - start,  
                    })
                    #print(f"Error al publicar objeto: {result}")
                    return Err(f"Error al publicar objeto: {result}")
            else:
                logger.error({
                        "event": "SET.OBJECT",
                        "mode":"DISTRIBUTED",
                        "mensage": f"Error preparing object '{alias}'",
                        "response_time": T.time() - start,  
                    })
                #print(f"Error al preparar objeto: {res}")
                return Err(f"Error al preparar objeto: {res}")

    async def get_object_by_alias(alias: str,user_id:str, storage_service:StorageService=default_storage_service):
        start=T.time()
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
                    logger.info({
                        "event": "GET.OBJECT",
                        "mode":"DISTRIBUTED",
                        "object_key": result["key"],
                        "user_id": user_id,
                        "mensage": f"Object '{alias}' retrieved successfully",
                        "response_time": T.time() - start,  
                    })
                    return data
                else:
                    logger.error({
                        "event": "GET.OBJECT",
                        "mode":"DISTRIBUTED",
                        "mensage": f"Error retrieving object '{alias}'",
                        "response_time": T.time() - start,  
                    })
                    #print(f"Error al recuperar objeto por alias: {data}")
                    return Err(f"Error al recuperar objeto por alias '{alias}': {data}")
        else:
            #print(f"Error al buscar objeto por alias: {result}")
            logger.error({
                        "event": "GET.OBJECT",
                        "mode":"DISTRIBUTED",
                        "mensage": f"Error finding object '{alias}'",
                        "response_time": T.time() - start,  
                    })
            return Err(f"Error al buscar objeto por alias '{alias}': {result}")
    
    #funciones para manejo de las mallas
    def create_mesh(mesh_name:str, description:str, user_id:str, storage_service:StorageService=default_storage_service):
        start=T.time()
        mesh = Mesh(name=mesh_name, description=description, user_id=user_id)
        exist= storage_service.get("meshes", condition={"name": mesh.name})
        if exist.is_ok:
            logger.error({
                "event": "CREATE.MESH",
                "mode":"DISTRIBUTED",
                "mensage": f"Mesh with id '{mesh.mesh_id}' already exists",
                "response_time": T.time() - start,})
            print(f"La malla con id '{mesh.mesh_id}' ya existe.")
            return None
        else:
            res = storage_service.put("meshes", mesh.mesh_id, mesh)
            if res.is_ok:
                logger.info({
                    "event": "CREATE.MESH",
                    "mode":"DISTRIBUTED",
                    "mesh_id": mesh.mesh_id,
                    "user_id": user_id,
                    "mensage": f"Mesh '{mesh_name}' created successfully",
                    "response_time": T.time() - start,})
                print(f"Malla '{mesh_name}' creada correctamente.")
                return mesh 
            else:
                logger.error({
                    "event": "CREATE.MESH",
                    "mode":"DISTRIBUTED",
                    "mensage": f"Error creating mesh '{mesh_name}'",
                    "response_time": T.time() - start,})
                print(f"Error al crear malla: {res}")
                return None

    def publish_object_to_mesh(category:str, object_key:str, user_id:str, storage_service:StorageService=default_storage_service):
        start=T.time()
        res=storage_service.get("meshes", condition={"category": category})
        if res.is_ok:
            mesh_data=res.unwrap()
            mesh=Mesh.from_json(mesh_data)
            obj=storage_service.get("objects", condition={"key": object_key})
            if obj.is_ok:
                obj_data=obj.unwrap()
                obj=Object.from_json(obj_data)
                res=storage_service.update("meshes", mesh.mesh_id, mesh)
                if res.is_ok:
                    logger.info({
                        "event": "PUBLISH.OBJECT.TO.MESH",
                        "mode":"DISTRIBUTED",
                        "mesh_id": mesh.mesh_id,
                        "object_key": object_key,
                        "user_id": user_id,
                        "mensage": f"Object '{object_key}' published to mesh '{mesh.mesh_id}' successfully",
                        "response_time": T.time() - start,})
                    print(f"Objeto {object_key} publicado en la malla {mesh.mesh_id} correctamente.")
                    return mesh
                else:
                    logger.error({
                        "event": "PUBLISH.OBJECT.TO.MESH",
                        "mode":"DISTRIBUTED",
                        "mensage": f"Error publishing object '{object_key}' to mesh '{mesh.mesh_id}'",
                        "response_time": T.time() - start,})    
                    print(f"Error al actualizar la malla: {res}")
                    return None
            else:
                logger.error({
                    "event": "PUBLISH.OBJECT.TO.MESH",
                    "mode":"DISTRIBUTED",
                    "mensage": f"Error retrieving mesh '{mesh.mesh_id}'",
                    "response_time": T.time() - start,})
                print(f"Error al recuperar la malla: {res}")
                return None
        else:
            logger.error({
                    "event": "PUBLISH.OBJECT.TO.MESH",
                    "mode":"DISTRIBUTED",
                    "mensage": f"Error the object not exists",
                    "response_time": T.time() - start,})
            print(f"Error al buscar la malla: {obj}")
            return None

    async def get_object_to_mesh(category:str, alias:str, storage_service:StorageService=default_storage_service):
        start=T.time()
        res=storage_service.get("meshes", condition={"category": category})
        if res.is_ok:
            mesh_data=res.unwrap()
            mesh=Mesh.from_json(mesh_data)
            objects=mesh.get_objects()
            objs=[obj for obj in objects if obj.alias == alias]
            if objs:
                logger.info({
                    "event": "GET.OBJECT.FROM.MESH",
                    "mode":"DISTRIBUTED",
                    "mesh_id": mesh.mesh_id,
                    "object_key": objs.key,
                    "mensage": f"Object '{objs.key}' retrieved from mesh '{mesh.mesh_id}' successfully",
                    "response_time": T.time() - start,})
                print(f"Objeto {objs.key} recuperado de la malla {mesh.mesh_id} correctamente.")
                act_obj=await Axo.get_by_key(bucket_id=objs[0].bucket_id, key=objs[0].key)
                if act_obj.is_ok:
                    act_obj=act_obj.unwrap()
                    logger.info({
                        "event": "GET.OBJECT.FROM.MESH",
                        "mode":"DISTRIBUTED",
                        "mesh_id": mesh.mesh_id,
                        "object_key": act_obj.get_axo_key(),
                        "mensage": f"Object '{act_obj.get_axo_key()}' retrieved successfully",
                        "response_time": T.time() - start,})
                    return act_obj
                else:
                    logger.error({
                        "event": "GET.OBJECT.FROM.MESH",
                        "mode":"DISTRIBUTED",
                        "mensage": f"Error retrieving object '{objs.key}' from mesh '{mesh.mesh_id}'",
                        "response_time": T.time() - start,})
                    print(f"Error al recuperar el objeto: {act_obj}")
                    return None
                
            else:
                logger.error({
                    "event": "GET.OBJECT.FROM.MESH",
                    "mode":"DISTRIBUTED",
                    "mensage": f"Object '{objs.key}' not found in mesh '{mesh.mesh_id}'",
                    "response_time": T.time() - start,})
                print(f"El objeto {objs.key} no se encuentra en la malla {mesh.mesh_id}.")
                return None
        else:
            logger.error({
                    "event": "GET.OBJECT.FROM.MESH",
                    "mode":"DISTRIBUTED",
                    "mensage": f"Error retrieving mesh with category '{category}'",
                    "response_time": T.time() - start,})
            print(f"Error al buscar la malla: {res}")
            return None

    def get_objects_to_mesh(category:str, storage_service:StorageService=default_storage_service):
        start=T.time()
        res=storage_service.get("meshes", condition={"category": category})
        if res.is_ok:
            mesh_data=res.unwrap()
            mesh=Mesh.from_json(mesh_data)
            objects=mesh.get_objects()
            logger.info({
                "event": "GET.OBJECTS.FROM.MESH",
                "mode":"DISTRIBUTED",
                "mesh_id": mesh.mesh_id,
                "mensage": f"Objects retrieved from mesh '{mesh.mesh_id}' successfully",
                "response_time": T.time() - start,})
            print(f"Objetos recuperados de la malla {mesh.mesh_id} correctamente.")
            return objects
        else:
            logger.error({
                "event": "GET.OBJECTS.FROM.MESH",
                "mode":"DISTRIBUTED",
                "mensage": f"Error retrieving mesh with category '{category}'",
                "response_time": T.time() - start,})
            print(f"Error al buscar la malla: {res}")
            return None

    # funciones para el manejo de los servicios
    def create_service():
        pass
        """en desarrollo"""

    def get_meshes():
        pass
        """en desarrollo"""

    # binding objects
    def create_binding_object(binding_object:BindingObject, user_id:str, storage_service:StorageService=default_storage_service):
        start=T.time()
        exist_object =  storage_service.get("binding_objects", condition={"user_id": user_id, "alias": binding_object.alias})
        if exist_object.is_ok:
            logger.info({
                    "event": "CREATE.BINDING.OBJECT",
                    "mode":"DISTRIBUTED",
                    "mensage": f"Binding object with alias '{binding_object.alias}' already exists for user {user_id}",
                    "response_time": T.time() - start,  
                })
            return Err(f"El objeto de enlace con alias '{binding_object.alias}' ya existe para el usuario {user_id}.")
        else:
            res= storage_service.put("objects", binding_object.key, binding_object)
            if res.is_ok:
                logger.info({
                    "event": "CREATE.BINDING.OBJECT",
                    "mode":"DISTRIBUTED",
                    "binding_object_key": binding_object.key,
                    "user_id": user_id,
                    "mensage": f"Binding object '{binding_object.alias}' created successfully",
                    "response_time": T.time() - start,  
                })
                print(f"Objeto de enlace '{binding_object.alias}' creado correctamente.")
                return Ok(binding_object)
            else:
                logger.error({
                    "event": "CREATE.BINDING.OBJECT",
                    "mode":"DISTRIBUTED",
                    "mensage": f"Error creating binding object '{binding_object.alias}'",
                    "response_time": T.time() - start,  
                })
                print(f"Error al crear objeto de enlace: {res}")
                return Err(f"Error al crear objeto de enlace: {res}")

    def execute_binding_object():
        pass