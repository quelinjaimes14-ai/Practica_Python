import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
import sys

HOST = '127.0.0.1'   # Cambia a la IP del servidor si es remoto
PORT = 5000

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("💬 Chat Bonito")
        self.master.geometry("600x450")
        self.master.configure(bg="#f0f4f7")

        # ====== Área de chat (lectura) ======
        self.chat_area = scrolledtext.ScrolledText(
            master, wrap=tk.WORD, state='disabled',
            bg="#ffffff", fg="#333333", font=("Arial", 11)
        )
        self.chat_area.pack(padx=12, pady=(12, 8), fill=tk.BOTH, expand=True)

        # Configuración de tags para colores
        self.chat_area.tag_config("system", foreground="#6b7280")  # gris
        self.chat_area.tag_config("me", foreground="#2563eb")      # azul
        self.chat_area.tag_config("other", foreground="#111827")   # casi negro

        # ====== Frame de entrada ======
        input_frame = tk.Frame(master, bg="#f0f4f7")
        input_frame.pack(fill=tk.X, padx=12, pady=(0, 12))

        # Etiqueta de ayuda
        tk.Label(
            input_frame, text="Escribe tu mensaje:",
            font=("Arial", 10), bg="#f0f4f7", fg="#374151"
        ).pack(anchor="w", pady=(0, 4))

        # Caja de texto de entrada (multilínea suave)
        self.input_box = tk.Text(
            input_frame, height=2, wrap=tk.WORD,
            font=("Arial", 11), bg="#e8eef2", fg="#333333",
            insertbackground="#333333", relief=tk.FLAT
        )
        self.input_box.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Botón enviar con flechita
        self.send_button = tk.Button(
            input_frame, text="➤", font=("Arial", 16, "bold"),
            bg="#4CAF50", fg="white", width=3, relief=tk.FLAT,
            command=self.send_message
        )
        self.send_button.pack(side=tk.RIGHT, padx=(8, 0))

        # Atajo: Ctrl+Enter envía, Enter hace nueva línea
        self.input_box.bind("<Control-Return>", self.send_message)
        # Foco inicial
        self.input_box.focus_set()

        # ====== Conexión al servidor ======
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((HOST, PORT))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar al servidor: {e}")
            sys.exit(0)

        # Recibir prompt inicial (nombre)
        try:
            prompt = self.sock.recv(1024).decode('utf-8')
        except Exception as e:
            messagebox.showerror("Error", f"No se recibió el prompt del servidor: {e}")
            self.master.destroy()
            return
        self.add_message(prompt, tag="system")

        # Ventana de nombre
        self.name_window()

        # Hilo para escuchar mensajes
        threading.Thread(target=self.listen, daemon=True).start()

    # ====== Ventana para ingresar nombre ======
    def name_window(self):
        def set_name():
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("Atención", "Ingresa un nombre.")
                return
            try:
                self.sock.sendall((name + "\n").encode('utf-8'))
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo enviar el nombre: {e}")
                self.master.quit()
            name_win.destroy()
            self.input_box.focus_set()

        name_win = tk.Toplevel(self.master)
        name_win.title("Ingresa tu nombre")
        name_win.geometry("320x140")
        name_win.configure(bg="#f0f4f7")
        name_win.grab_set()  # Bloquear interacción hasta que se ingrese el nombre

        tk.Label(name_win, text="Tu nombre:", font=("Arial", 11), bg="#f0f4f7").pack(pady=(14, 6))
        name_entry = tk.Entry(name_win, font=("Arial", 11), bg="#ffffff")
        name_entry.pack(pady=(0, 8), padx=12, fill=tk.X)
        tk.Button(name_win, text="Aceptar", bg="#4CAF50", fg="white",
                  font=("Arial", 10, "bold"), relief=tk.FLAT, command=set_name).pack()
        name_entry.focus()

    # ====== Utilidades de UI ======
    def add_message(self, message, tag=None):
        self.chat_area.config(state='normal')
        if tag:
            self.chat_area.insert(tk.END, message + "\n", tag)
        else:
            self.chat_area.insert(tk.END, message + "\n")
        self.chat_area.yview(tk.END)
        self.chat_area.config(state='disabled')

    def send_message(self, event=None):
        msg = self.input_box.get("1.0", tk.END).strip()
        if not msg:
            return
        try:
            self.sock.sendall((msg + "\n").encode('utf-8'))
        except Exception:
            messagebox.showerror("Error", "Conexión perdida con el servidor.")
            self.master.quit()
            return
        # Mostrar tu propio mensaje con color "me" (opcional, el servidor también lo devolverá)
        # self.add_message(f"Tú: {msg}", tag="me")
        self.input_box.delete("1.0", tk.END)
        self.input_box.focus_set()

    # ====== Red ======
    def listen(self):
        try:
            while True:
                data = self.sock.recv(4096)
                if not data:
                    self.add_message("[Conexión cerrada por el servidor]", tag="system")
                    break
                text = data.decode('utf-8')
                # Colorear según tipo básico
                if text.startswith("[Sistema]"):
                    self.add_message(text, tag="system")
                elif text.startswith("Tú:"):
                    self.add_message(text, tag="me")
                else:
                    self.add_message(text, tag="other")
        except:
            self.add_message("[Error de conexión]", tag="system")
        finally:
            try:
                self.sock.close()
            except:
                pass
            self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()
