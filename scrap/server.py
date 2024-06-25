import socket
import threading

def handle_client_input(client_socket):
    while True:
        try:
            message = input("Enter your message: ")
            client_socket.send(message.encode('utf-8'))
        except BrokenPipeError:
            print("Connection to client lost. Exiting.")
            client_socket.close()
            break

def handle_client_output(client_socket):
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break
            print(f"Received message from client: {message.decode('utf-8')}")
        except ConnectionResetError:
            print("Connection lost. Closing connection.")
            client_socket.close()
            break

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 1234))
    server_socket.listen(5)
    print("Server listening on port 1234")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection established with {addr}")
        
        threading.Thread(target=handle_client_output, args=(client_socket,)).start()
        threading.Thread(target=handle_client_input, args=(client_socket,)).start()

if __name__ == "__main__":
    start_server()
