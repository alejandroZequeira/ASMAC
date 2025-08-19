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
socket.bind("tcp://*:5555")

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
        pass
    elif action == "PUT.MESH": 
        pass
    elif action == "GET.MESHES":
        pass
    elif action == "GET.OBJECTS.BY.MESH":
        pass
    elif action == "PUT.OBJECT":
        pass
    elif action == "GET.OBJECT.BY.ID":
        pass
    else:
        response = {"status": "error", "mensaje": "Acción no reconocida"}

    # Enviar respuesta como JSON
    socket.send_json(response)