import socket
import threading

class ServidorChat:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor.bind((self.host, self.port))
        self.servidor.listen(5)
        self.clientes = []
        print(f"Servidor iniciado en {self.host}:{self.port}")

    def broadcast(self, mensaje, remitente=None):
        for cliente in self.clientes:
            if cliente != remitente:
                try:
                    cliente.send(mensaje.encode('utf-8'))
                except:
                    self.clientes.remove(cliente)

    def manejar_cliente(self, cliente_socket, direccion):
        self.clientes.append(cliente_socket)
        mensaje = f"¡Nuevo cliente conectado desde {direccion[0]}:{direccion[1]}!"
        print(mensaje)
        self.broadcast(mensaje, cliente_socket)

        while True:
            try:
                mensaje = cliente_socket.recv(1024).decode('utf-8')
                if not mensaje:
                    break
                print(f"Mensaje de {direccion}: {mensaje}")
            except:
                break

        cliente_socket.close()
        self.clientes.remove(cliente_socket)
        self.broadcast(f"Cliente {direccion[0]}:{direccion[1]} se ha desconectado")

    def iniciar(self):
        while True:
            cliente_socket, direccion = self.servidor.accept()
            thread = threading.Thread(target=self.manejar_cliente, 
                                   args=(cliente_socket, direccion))
            thread.start()

if __name__ == "__main__":
    servidor = ServidorChat()
    servidor.iniciar()