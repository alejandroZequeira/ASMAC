import zmq
import json
import os
import time as T
import logger 
from asmac_backend.asmac_backend.v0 import ASMaC_Backend

# crear variables de entorno
ASMAC_BACKEND_PORT = os.getenv("ASMAC_BACKEND_PORT", "4555")
ASMAC_BACKEND_PROTOCOL = os.getenv("ASMAC_BACKEND_PROTOCOL", "tcp")

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind(ASMAC_BACKEND_PROTOCOL+"://*:" + ASMAC_BACKEND_PORT)

print("Servidor ZeroMQ escuchando en puerto 5555...")

while True:
    # Recibir JSON
    mensaje = socket.recv_json()
    print(f"Mensaje recibido: {mensaje}")

    action = mensaje.get("action")
    data = mensaje.get("data")

    if action == "PUT.USER":
        response=ASMaC_Backend.create_user(
            name=data.get("name"), 
            password=data.get("password"),
            user_name=data.get("user_name")
        )
        if response != None:
            response = response.unwrap()
    elif action == "GET.OBJECT.BY.ALIAS":
        user=ASMaC_Backend.login_user(
            user_name=data.get("user_name"),
            password=data.get("password")
        )
        response = ASMaC_Backend.get_object_by_alias(
            alias=data.get("alias"),
            user_id=user["user_id"]
        )
        if response != None:
            response = response.unwrap()
    elif action == "PUT.MESH": 
        user=ASMaC_Backend.login_user(user_name=data.get("user_name"),password=data.get("password"))
        response=ASMaC_Backend.create_mesh(mesh_name=data.get("mesh_name"), description=data.get("description"), user_id=user["user_id"])
        if response == None:
            response=f"create mesh not found"
    elif action == "GET.MESHES":
        pass
    elif action == "GET.OBJECTS.BY.MESH":
        pass
    elif action == "PUT.OBJECT":
        user=ASMaC_Backend.login_user(user_name=data.get("user_name"),password=data.get("password"))
        if user!=None:
            response=ASMaC_Backend.set_object(obj=data.get("obj"),alias=data.get("alias"),is_public=data.get("is_public"),user_id=user["user_id"])
            if response.is_ok:
                response=response.unwrap()
    elif action == "PUT.OBJECT.MESH":
        pass
    else:
        response = {"status": "error", "mensaje": "Acción no reconocida"}

    # Enviar respuesta como JSON
    socket.send_json(response)