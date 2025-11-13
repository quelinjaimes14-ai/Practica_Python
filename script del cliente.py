import socket
import threading
import sys
import time
import os

#!/usr/bin/env python3
# cliente basado en sockets TCP
# Guarda este archivo como: C:/xampp/Ejemplo de python/script del cliente.py


#HOST = '127.0.0.1'   # Cambiar por la IP del servidor si es necesario
HOST ='192.168.137.86' #IP del servidor jacquie en pruebas
#PORT = 65432         # Debe coincidir con el puerto del servidor
PORT = 12345          # Puerto del servidor de jacquie para pruebas

ENC = 'utf-8'
BUFFER = 4096

def recibir_loop(sock):
    """Hilo que recibe datos del servidor y los imprime."""
    try:
        while True:
            data = sock.recv(BUFFER)
            if not data:
                print('\n[Conexión cerrada por el servidor]')
                break
            try:
                print('\nServidor:', data.decode(ENC))
            except Exception:
                # Si falla la decodificación, mostrar bytes crudos
                print('\nServidor (bytes):', data)
    except Exception as e:
        print('\n[Error en recepción]:', e)
    finally:
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        sock.close()
        # Forzar salida del proceso si el hilo receptor termina
        os._exit(0)

def main():
    print('Bienvenido al chat de 7mo Informatica')
    #host = input(f'Host [{HOST}]: ').strip() or HOST
    #try:
    #    port_input = input(f'Puerto [{PORT}]: ').strip()
    #    port = int(port_input) if port_input else PORT
    #except ValueError:
    #    print('Puerto inválido. Usando valor por defecto.')
    #    port = PORT

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        #Asignamos los valores por defecto directamente
        #si deseas el pregunar el host comenta estas dos lineas
        host = HOST
        port = PORT
        sock.connect((host, port))

    except Exception as e:
        print('No se pudo conectar al servidor:', e)
        return

    print(f'Conectado a {host}:{port}')
    # Lanzar hilo receptor
    receiver = threading.Thread(target=recibir_loop, args=(sock,), daemon=True)
    receiver.start()

    try:
        # Bucle principal para enviar mensajes
        while True:
            msg = input()  # el usuario escribe el mensaje
            if not msg:
                continue
            if msg.lower() in ('/salir', '/exit', '/quit'):
                print('Cerrando conexión...')
                try:
                    sock.sendall(msg.encode(ENC))
                except Exception:
                    pass
                break
            # Enviar mensaje al servidor
            try:
                sock.sendall(msg.encode(ENC))
            except BrokenPipeError:
                print('Conexión perdida.')
                break
            except Exception as e:
                print('Error enviando datos:', e)
                break
    except KeyboardInterrupt:
        print('\nInterrupción por teclado. Saliendo...')
    finally:
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        sock.close()
        # dar tiempo al hilo receptor para terminar
        time.sleep(0.2)

if __name__ == '__main__':
    # evitar import circular al usar os._exit en el hilo
    main()