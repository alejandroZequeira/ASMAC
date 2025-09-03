import zmq
import json
import os
import asyncio
import base64
import cloudpickle as CP
import pickle
from asmac_backend.asmac_backend.v0 import ASMaC_Backend
from axo import Axo
import socket
import socket as pysocket
# Configuración de entorno
ASMAC_BACKEND_PORT = os.getenv("ASMAC_BACKEND_PORT", "4555")
ASMAC_BACKEND_PROTOCOL = os.getenv("ASMAC_BACKEND_PROTOCOL", "tcp")
AXO_ENDPOINT_PROTOCOL     = os.environ.get("AXO_ENDPOINT_PROTOCOL","tcp")
AXO_ENDPOINT_HOSTNAME     = os.environ.get("AXO_ENDPOINT_HOSTNAME","localhost")
AXO_ENDPOINT_PUBSUB_PORT  = int(os.environ.get("AXO_ENDPOINT_PUBSUB_PORT","16000"))
AXO_ENDPOINT_REQ_RES_PORT = int(os.environ.get("AXO_ENDPOINT_REQ_RES_PORT","16667"))
AXO_ENDPOINT_ID           = os.environ.get("AXO_ENDPOINT_ID","activex-endpoint-0")
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind(f"{ASMAC_BACKEND_PROTOCOL}://*:{ASMAC_BACKEND_PORT}")

print(f"Servidor ZeroMQ escuchando en {ASMAC_BACKEND_PROTOCOL} puerto {ASMAC_BACKEND_PORT}...")


# Función para obtener la IP real del host
def get_real_ip():
    s = pysocket.socket(pysocket.AF_INET, pysocket.SOCK_DGRAM)  # <-- usar pysocket
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

while True:
    mensaje = socket.recv_json()
    action = mensaje.get("action")
    data = mensaje.get("data")
    response = {"status": "error", "msg": "Acción no reconocida"}
    
    if action == "GET.ENDPOINT.INFO":
        # Obtenemos la IP real del host
        host_real = get_real_ip()
        response = {
            "status": "OK",
            "host": host_real,
            "protocol": AXO_ENDPOINT_PROTOCOL,        # Ej: "tcp"
            "pubsub_port": AXO_ENDPOINT_PUBSUB_PORT,  # puerto Pub/Sub
            "req_res_port": AXO_ENDPOINT_REQ_RES_PORT,
            "endpoint_id":AXO_ENDPOINT_ID,
        }
    # Crear usuario
    if action == "PUT.USER":
        res = ASMaC_Backend.create_user(
            name=data.get("name"),
            password=data.get("password"),
            user_name=data.get("user_name")
        )
        if res is not None:
            response = {"status": "OK", "data": res}
        else:
            response={"status":"Error","msg":"user exist"}

    # Obtener objeto por alias
    elif action == "GET.OBJECT.BY.ALIAS":
        user = ASMaC_Backend.login_user(
            user_name=data.get("user_name"),
            password=data.get("password")
        )
        if user is not None:
            res = ASMaC_Backend.get_object_by_alias(
                alias=data.get("alias"),
                user_name=data.get("from")
            )
            if res.is_ok :
                print("entro a la condicion")
                res=res.unwrap()
                response = {"status": "OK", "data":{"key":res["key"],"bucket_id":res["bucket_id"]}}
            else:
                response ={"status":"Error","msg": res.unwrap()}
        else:
            response={"status":"Error","msg":"The user could not be logged in"}
    elif action=="GET.OBJECTS":
        user = ASMaC_Backend.login_user(
            user_name=data.get("user_name"),
            password=data.get("password")
        )
        if user is not None:
            res = ASMaC_Backend.get_objects(user["user_id"])
            if res.is_ok:
                res=res.unwrap()
                response={"status":"OK","data":[r["alias"] for r in res ]}
            else:
                response={"status":"Error","msg":res.unwrap()}
        else:
            response={"status":"Error","msg":"The user could not be logged in"}
    # Crear mesh
    elif action == "PUT.MESH":
        user = ASMaC_Backend.login_user(
            user_name=data.get("user_name"),
            password=data.get("password")
        )
        res = ASMaC_Backend.create_mesh(
            mesh_name=data.get("mesh_name"),
            description=data.get("description"),
            user_id=user["user_id"]
        )
        if res is not None:
            response = {"status": "OK", "data": res.unwrap()}
        else:
            response = {"status": "Error", "msg": "No se pudo crear mesh"}

    # Guardar objeto serializado
    elif action == "PUT.OBJECT":
        user = ASMaC_Backend.login_user(
            user_name=data.get("user_name"),
            password=data.get("password")
        )
        if user is not None:
                # Guardar el objeto Axo con el backend
                #print(data.get("class_code"))
                res = asyncio.run(
                    ASMaC_Backend.set_object(
                        obj_key=data.get("obj_key"),
                        bucket_id=data.get("bucket_id"),
                        alias=data.get("alias"),
                        is_public=data.get("is_public"),
                        class_code=data.get("class_code"),   # no necesitamos class_code
                        user_id=user["user_id"]
                    )
                )
                if res.is_ok:
                    response = {"status": "OK", "data":"successfully created"}
                else:
                    response = {"status": "Error", "msg": "Error guardando objeto"}

    socket.send_json(response)
