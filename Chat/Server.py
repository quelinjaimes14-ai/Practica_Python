import socket
import threading

HOST = '0.0.0.0'
PORT = 5000

clients = {}  # socket -> nombre
clients_lock = threading.Lock()

def broadcast(message, exclude_sock=None):
    """Enviar mensaje a todos los clientes conectados."""
    with clients_lock:
        for sock in list(clients.keys()):
            if sock is exclude_sock:
                continue
            try:
                sock.sendall(message.encode('utf-8'))
            except:
                # Si falla, eliminar cliente
                name = clients.pop(sock, None)
                sock.close()
                if name:
                    broadcast(f"[Sistema] {name} salió del chat.\n")

def handle_client(conn, addr):
    try:
        conn.sendall("Bienvenido. Ingresa tu nombre: ".encode('utf-8'))
        while True:
            name = conn.recv(1024).decode('utf-8').strip()
            if not name:
                name = f"Usuario_{addr[1]}"
            with clients_lock:
                if name not in clients.values():
                    clients[conn] = name
                    break
            conn.sendall("Ese nombre ya está en uso, intenta otro: ".encode('utf-8'))

        conn.sendall(f"[Sistema] Te has unido como '{name}'.\n".encode('utf-8'))
        broadcast(f"[Sistema] {name} se unió al chat.\n", exclude_sock=conn)

        while True:
            data = conn.recv(4096)
            if not data:
                break
            msg = data.decode('utf-8').strip()
            if not msg:
                continue

            # Comandos especiales
            if msg.lower() == "/users":
                with clients_lock:
                    users_list = ", ".join(clients.values())
                conn.sendall(f"[Sistema] Usuarios conectados: {users_list}\n".encode('utf-8'))
            elif msg.lower().startswith("/nick "):
                new_name = msg[6:].strip()
                if new_name and new_name not in clients.values():
                    old_name = clients[conn]
                    clients[conn] = new_name
                    broadcast(f"[Sistema] {old_name} ahora es {new_name}\n")
                else:
                    conn.sendall("[Sistema] Nombre inválido o ya en uso.\n".encode('utf-8'))
            elif msg.lower() in ("/quit", "/exit"):
                break
            else:
                broadcast(f"{clients[conn]}: {msg}\n")

    finally:
        with clients_lock:
            name = clients.pop(conn, None)
        conn.close()
        if name:
            broadcast(f"[Sistema] {name} salió del chat.\n")

def start_server():
    print(f"Servidor iniciando en {HOST}:{PORT}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print("Servidor escuchando. Esperando clientes...")

        while True:
            conn, addr = s.accept()
            print(f"Conexión de {addr}")
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()


