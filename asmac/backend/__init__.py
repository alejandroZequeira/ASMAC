import zmq

def send(data, host="localhost", puerto=5555):
    """
    Envía un JSON al servidor ZeroMQ y recibe la respuesta.

    Args:
        data (dict): Datos a enviar (se convertirán a JSON).
        host (str): Host del servidor.
        puerto (int): Puerto TCP del servidor.
    """
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://{host}:{puerto}")

    socket.send_json(data)
    respuesta = socket.recv_json()

    socket.close()
    context.term()

    return respuesta
