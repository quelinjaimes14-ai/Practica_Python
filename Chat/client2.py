import socket
import threading
import sys
import requests   # ← necesario para llamar a la API

HOST = '127.0.0.1'
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

    # Recibir prompt inicial
    prompt = sock.recv(1024).decode('utf-8')
    print(prompt, end='')
    name = input().strip()
    sock.sendall((name + "\n").encode('utf-8'))

    # ================================
    #   CARGAR HISTORIAL AUTOMÁTICO
    # ================================
    try:
        response = requests.get("http://127.0.0.1:8000/api/mensajes")
        mensajes = response.json()
        print(mensajes)
        print("\n===== MENSAJES ANTERIORES =====")
        for m in mensajes:
            print(f"[{m['fecha_hora']}] {m['usuario']}: {m['mensaje']}")
        print("================================\n")

    except Exception as e:
        print(f"[Error] No se pudo cargar historial: {e}\n")
    # ================================

    # Hilo para escuchar mensajes
    threading.Thread(target=listen, args=(sock,), daemon=True).start()

    try:
        while True:
            msg = input()

            # comando para ver historial (lo mantengo tal cual tú lo usas)
            if msg.lower() == "/historial":
                try:
                    response = requests.get("http://127.0.0.1:8000/api/mensajes")
                    mensajes = response.json()
                    print(mensajes)
                    print("\n===== HISTORIAL DE MENSAJES =====")
                    for m in mensajes:
                        print(f"[{m['fecha_hora']}] {m['usuario']}: {m['mensaje']}")
                    print("=================================\n")

                except Exception as e:
                    print(f"[Error] No se pudo obtener historial: {e}\n")

                continue

            sock.sendall((msg + "\n").encode('utf-8'))

            if msg.lower() in ('/quit', '/exit'):
                break

    except KeyboardInterrupt:
        pass
    finally:
        sock.close()


if __name__ == "__main__":
    main()

