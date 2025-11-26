import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
import requests
import sys

HOST = '127.0.0.1'
PORT = 5000

API_URL = "http://127.0.0.1:8000/api/mensajes"   # GET historial completo


class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("💬 Chat Bonito")
        self.master.geometry("650x500")
        self.master.configure(bg="#f0f4f7")

        # ===========================================
        #   SECCIÓN PARA INGRESAR NOMBRE (MISMA VENTANA)
        # ===========================================
        self.name_frame = tk.Frame(master, bg="#f0f4f7")
        self.name_frame.pack(fill=tk.X, pady=(15, 10))

        tk.Label(
            self.name_frame, text="Ingresa tu nombre:",
            font=("Arial", 12, "bold"), bg="#f0f4f7", fg="#333"
        ).pack(anchor="w", padx=20)

        self.name_entry = tk.Entry(
            self.name_frame, font=("Arial", 12),
            bg="#ffffff", fg="#111"
        )
        self.name_entry.pack(fill=tk.X, padx=20, pady=(5, 8))
        self.name_entry.focus()

        self.name_button = tk.Button(
            self.name_frame, text="Aceptar",
            bg="#4CAF50", fg="white",
            font=("Arial", 11, "bold"),
            relief=tk.FLAT, command=self.send_name
        )
        self.name_button.pack(pady=(0, 5))

        # ===========================================
        #   ÁREA DE CHAT
        # ===========================================
        self.chat_area = scrolledtext.ScrolledText(
            master, wrap=tk.WORD, state='disabled',
            bg="#ffffff", fg="#333333", font=("Arial", 11)
        )
        self.chat_area.pack(padx=12, pady=(0, 8), fill=tk.BOTH, expand=True)

        # Colores
        self.chat_area.tag_config("system", foreground="#6b7280")
        self.chat_area.tag_config("me", foreground="#2563eb")
        self.chat_area.tag_config("other", foreground="#111827")
        self.chat_area.tag_config("history", foreground="#10b981")

        # ===========================================
        #   INPUT + ENVIAR
        # ===========================================
        self.input_frame = tk.Frame(master, bg="#f0f4f7")
        self.input_frame.pack(fill=tk.X, padx=12, pady=(0, 12))

        tk.Label(
            self.input_frame, text="Escribe tu mensaje:",
            font=("Arial", 10), bg="#f0f4f7", fg="#374151"
        ).pack(anchor="w", pady=(0, 4))

        self.input_box = tk.Text(
            self.input_frame, height=2, wrap=tk.WORD,
            font=("Arial", 11), bg="#e8eef2", fg="#333333",
            insertbackground="#333333", relief=tk.FLAT
        )
        self.input_box.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.send_button = tk.Button(
            self.input_frame, text="➤", font=("Arial", 16, "bold"),
            bg="#4CAF50", fg="white", width=3, relief=tk.FLAT,
            command=self.send_message
        )
        self.send_button.pack(side=tk.RIGHT, padx=(8, 0))

        self.input_box.bind("<Control-Return>", self.send_message)

        # ===========================================
        #   CONEXIÓN AL SERVIDOR
        # ===========================================
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((HOST, PORT))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar al servidor: {e}")
            sys.exit(0)

        # Recibir prompt de nombre del servidor
        try:
            prompt = self.sock.recv(1024).decode('utf-8')
            self.add_message(prompt, tag="system")
        except:
            messagebox.showerror("Error", "No se recibió prompt de servidor.")
            self.master.quit()

        # Hilo de escucha
        threading.Thread(target=self.listen, daemon=True).start()

    # ===========================================
    #  ENVÍA NOMBRE + CARGA AUTOMÁTICAMENTE HISTORIAL
    # ===========================================
    def send_name(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Atención", "Escribe un nombre.")
            return

        try:
            self.sock.sendall((name + "\n").encode('utf-8'))
        except:
            messagebox.showerror("Error", "No se pudo enviar el nombre.")
            self.master.quit()
            return

        # Oculta el frame
        self.name_frame.pack_forget()
        self.input_box.focus_set()

        # Cargar historial automáticamente
        self.load_history()

    # ===========================================
    #  MOSTRAR MENSAJE EN CHAT
    # ===========================================
    def add_message(self, message, tag=None):
        self.chat_area.config(state='normal')
        if tag:
            self.chat_area.insert(tk.END, message + "\n", tag)
        else:
            self.chat_area.insert(tk.END, message + "\n")
        self.chat_area.yview(tk.END)
        self.chat_area.config(state='disabled')

    # ===========================================
    #  ENVIAR MENSAJE AL SERVIDOR
    # ===========================================
    def send_message(self, event=None):
        msg = self.input_box.get("1.0", tk.END).strip()
        if not msg:
            return

        try:
            self.sock.sendall((msg + "\n").encode('utf-8'))
        except:
            messagebox.showerror("Error", "Conexión perdida con el servidor.")
            self.master.quit()

        self.input_box.delete("1.0", tk.END)

    # ===========================================
    #   ESCUCHAR MENSAJES DEL SERVIDOR
    # ===========================================
    def listen(self):
        try:
            while True:
                data = self.sock.recv(4096)
                if not data:
                    self.add_message("[Conexión cerrada por el servidor]", tag="system")
                    break

                text = data.decode("utf-8")

                if text.startswith("[Sistema]"):
                    self.add_message(text, tag="system")
                else:
                    self.add_message(text, tag="other")

        except:
            self.add_message("[Error de conexión]", tag="system")

        finally:
            self.sock.close()
            self.master.quit()

    # ===========================================
    #   CARGAR HISTORIAL AUTOMÁTICAMENTE
    # ===========================================
    def load_history(self):
        try:
            response = requests.get(API_URL)
            data = response.json()
        except Exception as e:
            self.add_message(f"[Error historial] {e}", tag="system")
            return

        self.add_message("----- HISTORIAL DE MENSAJES -----", tag="history")

        for msg in data:
            fecha = msg['fecha_hora']
            usuario = msg['usuario']
            texto = msg['mensaje']

            line = f"[{fecha}] {usuario}: {texto}"
            self.add_message(line, tag="history")


if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()
