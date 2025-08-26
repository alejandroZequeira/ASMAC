import zmq

def send(data, host="localhost", puerto=5555):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://{host}:{puerto}")

    socket.send_json(data)
    respuesta = socket.recv_json()

    socket.close()
    context.term()

    return respuesta
