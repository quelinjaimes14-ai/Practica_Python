import socket
import threading

def receive_messages(sock):
    while True:
        try:
            message = sock.recv(1024).decode('utf-8')
            print(message)
        except:
            print("Error receiving message")
            break

# Create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
HOST = '127.0.0.1'  # localhost
PORT = 5000       # same port as server

try:
    client.connect((HOST, PORT))
    print("Connected to server!")

    # Get username from user
    username = input("Enter your username: ")
    client.send(username.encode('utf-8'))

    # Create thread to receive messages
    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()

    # Main loop to send messages
    while True:
        message = input("")
        if message.lower() == 'quit':
            break
        client.send(f"{message}".encode('utf-8'))

except ConnectionRefusedError:
    print("Could not connect to server")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    client.close()