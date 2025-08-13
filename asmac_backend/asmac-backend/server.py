import zmq
import os
import time as T
import logger 

# crear variables de entorno
ASMAC_BACKEND_PORT = os.getenv("ASMAC_BACKEND_PORT", "4555")
ASMAC_BACKEND_PROTOCOL = os.getenv("ASMAC_BACKEND_PROTOCOL", "tcp")
# Crear el contexto
context = zmq.Context()

# Crear un socket tipo REP (respuesta)
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")  # Escucha en el puerto 5555

print("Servidor ZeroMQ escuchando en puerto 5555...")

while True:
    # Espera un mensaje del cliente
    mensaje = socket.recv_string()
    print(f"Mensaje recibido: {mensaje}")
    # Clasificar la solicitud
    if mensaje.startswith("put.data"):
        datos = mensaje[len("put.data "):]
        print(f"Solicitud PUT recibida con datos: {datos}")
        respuesta = "Datos almacenados correctamente"

    elif mensaje.startswith("get.data"):
        clave = mensaje[len("get.data "):]
        print(f"Solicitud GET recibida para clave: {clave}")
        respuesta = f"Datos solicitados para: {clave}"


    # Procesa y responde
    respuesta = f"Recibido: {mensaje}"
    socket.send_string(respuesta)
