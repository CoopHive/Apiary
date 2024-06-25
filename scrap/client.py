import socket
import threading

def handle_input(client_socket):
    while True:
        try:
            message = input("Enter your message: ")
            client_socket.send(message.encode('utf-8'))
        except BrokenPipeError:
            print("Connection to server lost. Exiting.")
            client_socket.close()
            break

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 1234))
    print("Connected to server")

    threading.Thread(target=handle_input, args=(client_socket,)).start()

    while True:
        message = client_socket.recv(1024)
        if not message:
            break
        print(f"Received message from server: {message.decode('utf-8')}")

if __name__ == "__main__":
    start_client()
