import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox
import time
import queue

# /c:/xampp/Ejemplo de python/InterfazGrafica.py
# GitHub Copilot
# Interfaz gráfica tipo chat cliente (tkinter + sockets)
# Ajusta HOST y PORT según tu servidor.


HOST = '127.0.0.1'   # cambiar por la IP del servidor
PORT = 12345         # cambiar por el puerto del servidor
RECONNECT_DELAY = 3  # segundos entre intentos de reconexión

class ChatClientGUI:
    def __init__(self, master):
        self.master = master
        master.title("Chat Cliente")
        master.geometry("600x500")

        self.sock = None
        self.connected = False
        self.recv_queue = queue.Queue()
        self.username_sent = False

        # Top: estado de conexión
        self.status_var = tk.StringVar(value="Desconectado")
        status_frame = tk.Frame(master)
        status_frame.pack(fill='x', padx=5, pady=3)
        tk.Label(status_frame, text="Estado:").pack(side='left')
        tk.Label(status_frame, textvariable=self.status_var).pack(side='left')

        # Centro: área de mensajes (scrollable)
        self.canvas = tk.Canvas(master, bg="#f0f0f0")
        self.scrollbar = tk.Scrollbar(master, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)
        self.msg_frame = tk.Frame(self.canvas, bg="#f0f0f0")
        self.canvas.create_window((0,0), window=self.msg_frame, anchor='nw')
        self.msg_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Abajo: entrada y botón enviar
        entry_frame = tk.Frame(master)
        entry_frame.pack(fill='x', padx=5, pady=5)
        self.entry = tk.Entry(entry_frame)
        self.entry.pack(side='left', fill='x', expand=True, padx=(0,5))
        self.entry.bind("<Return>", lambda e: self.send_message())
        tk.Button(entry_frame, text="Enviar", command=self.send_message).pack(side='left')

        # Forzar reconexión manual
        tk.Button(status_frame, text="Conectar", command=lambda: threading.Thread(target=self.connect_loop, daemon=True).start()).pack(side='right')

        master.protocol("WM_DELETE_WINDOW", self.on_close)

        # iniciar intento de conexión
        threading.Thread(target=self.connect_loop, daemon=True).start()
        # ciclo que procesa mensajes recibidos por hilo de red
        self.master.after(100, self.process_recv_queue)

    def add_message_widget(self, text, kind='other'):
        # kind: 'me' o 'other' (alineación y colores distintos)
        c = "#DCF8C6" if kind == 'me' else "#FFFFFF"
        anchor = 'e' if kind == 'me' else 'w'
        padx = (60, 5) if kind == 'other' else (5, 60)
        w = tk.Label(self.msg_frame, text=text, bg=c, wraplength=380, justify='left', anchor='w', padx=8, pady=4, bd=0, relief='solid')
        w.pack(anchor=anchor, pady=3, padx=padx)
        # desplazar scroll al final
        self.master.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def connect_loop(self):
        # intenta conectar repetidamente; mantiene ventana responsiva
        if self.connected:
            return
        self.status_var.set("Conectando...")
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)
                s.connect((HOST, PORT))
                s.settimeout(None)
                self.sock = s
                self.connected = True
                self.status_var.set(f"Conectado a {HOST}:{PORT}")
                threading.Thread(target=self.recv_thread, daemon=True).start()
                return
            except Exception as e:
                self.connected = False
                self.status_var.set(f"Reintentando en {RECONNECT_DELAY}s...")
                time.sleep(RECONNECT_DELAY)

    def recv_thread(self):
        # recibe datos del servidor y los pone en cola
        try:
            while self.connected:
                data = self.sock.recv(4096)
                if not data:
                    break
                text = data.decode(errors='ignore')
                # encolar para procesar en hilo principal
                self.recv_queue.put(text)
        except Exception:
            pass
        finally:
            self.connected = False
            self.status_var.set("Desconectado")
            # cerrar socket
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None

    def process_recv_queue(self):
        # procesar mensajes de red en hilo principal (GUI)
        try:
            while not self.recv_queue.empty():
                text = self.recv_queue.get_nowait()
                # detectar petición de nombre de usuario (heurística)
                lower = text.lower()
                if (not self.username_sent) and ("name" in lower or "usuario" in lower or "nombre" in lower):
                    # pedir al usuario su nombre mediante diálogo modal
                    name = simpledialog.askstring("Nombre de usuario", "Introduce tu nombre de usuario:", parent=self.master)
                    if name:
                        try:
                            self.sock.sendall(name.encode())
                            self.username_sent = True
                            self.add_message_widget(f"Tú te uniste como: {name}", kind='me')
                        except Exception:
                            messagebox.showerror("Error", "No se pudo enviar el nombre al servidor.")
                    else:
                        # si no ingresa nombre, enviar cadena vacía para que el servidor lo gestione
                        try:
                            self.sock.sendall(b'')
                        except Exception:
                            pass
                else:
                    # mostrar mensajes normales; el servidor puede indicar remitente en el texto
                    # intentamos identificar si es un mensaje propio (si el servidor lo marca)
                    # por defecto se muestran como 'other'
                    self.add_message_widget(text.strip(), kind='other')
        except queue.Empty:
            pass
        finally:
            self.master.after(100, self.process_recv_queue)

    def send_message(self):
        msg = self.entry.get().strip()
        if not msg or not self.connected:
            return
        try:
            self.sock.sendall(msg.encode())
            self.add_message_widget(msg, kind='me')
            self.entry.delete(0, tk.END)
        except Exception:
            messagebox.showerror("Error", "No se pudo enviar el mensaje. Está desconectado.")
            self.connected = False
            self.status_var.set("Desconectado")

    def on_close(self):
        try:
            if self.sock:
                try:
                    self.sock.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                self.sock.close()
        finally:
            self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClientGUI(root)
    root.mainloop()