import socket
import threading

# Script del servidor de chat usando sockets
# Guarda esto en: C:/xampp/Ejemplo de python/Script del servidor.py
# Ejecutar: python "C:/xampp/Ejemplo de python/Script del servidor.py"


HOST = '0.0.0.0'   # escuchar en todas las interfaces
PORT = 12345       # puerto (puedes cambiarlo)

clients = {}       # socket -> nickname
clients_lock = threading.Lock()

def broadcast(message, exclude_sock=None):
    """Enviar message (bytes) a todos los clientes salvo exclude_sock."""
    with clients_lock:
        for sock in list(clients.keys()):
            if sock is exclude_sock:
                continue
            try:
                sock.sendall(message)
            except Exception:
                # Si falla enviar, cerrar y limpiar
                try:
                    sock.close()
                except Exception:
                    pass
                del clients[sock]

def handle_client(conn, addr):
    """Manejar un cliente conectado: pedir nickname, reenviar mensajes."""
    try:
        conn.sendall("NICK\n".encode('utf-8'))  # solicitar nickname al cliente
        nick = conn.recv(1024).decode('utf-8').strip()
        if not nick:
            conn.close()
            return

        with clients_lock:
            clients[conn] = nick

        join_msg = f"*** {nick} se ha unido al chat\n".encode('utf-8')
        broadcast(join_msg)

        # Recibir mensajes del cliente y retransmitirlos
        while True:
            data = conn.recv(4096)
            if not data:
                break
            text = data.decode('utf-8', errors='ignore').strip()
            if not text:
                continue
            # Si el cliente envía '/quit' cierra su conexión
            if text.lower() == '/quit':
                break
            msg = f"{nick}: {text}\n".encode('utf-8')
            broadcast(msg, exclude_sock=None)
    except Exception:
        pass
    finally:
        # limpieza al desconectar
        with clients_lock:
            if conn in clients:
                left_nick = clients.pop(conn)
            else:
                left_nick = None
        try:
            conn.close()
        except Exception:
            pass
        if left_nick:
            leave_msg = f"*** {left_nick} ha dejado el chat\n".encode('utf-8')
            broadcast(leave_msg)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(10)
    print(f"Servidor escuchando en {HOST}:{PORT}")
    try:
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\nServidor detenido por usuario.")
    finally:
        with clients_lock:
            for sock in list(clients.keys()):
                try:
                    sock.close()
                except Exception:
                    pass
            clients.clear()
        try:
            server.close()
        except Exception:
            pass

if __name__ == '__main__':
    start_server()