import socket
import threading
import sys

HOST = '127.0.0.1'  # Cambia a la IP del servidor si es remoto
PORT = 5000

def listen(sock):
    """Hilo para escuchar mensajes del servidor."""
    try:
        while True:
            data = sock.recv(4096)
            if not data:
                print("\n[Conexión cerrada por el servidor]")
                break
            print(data.decode('utf-8'), end='')
    except:
        pass
    finally:
        sock.close()
        sys.exit(0)

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    # Recibir prompt inicial (nombre)
    prompt = sock.recv(1024).decode('utf-8')
    print(prompt, end='')
    name = input().strip()
    sock.sendall((name + "\n").encode('utf-8'))

    # Hilo para escuchar mensajes
    threading.Thread(target=listen, args=(sock,), daemon=True).start()

    try:
        while True:
            msg = input()
            sock.sendall((msg + "\n").encode('utf-8'))
            if msg.lower() in ('/quit', '/exit'):
                break
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()

if __name__ == "__main__":
    main()
