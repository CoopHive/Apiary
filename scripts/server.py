"""This module implements a simple multithreaded server that can handle client input and output.

The server listens on localhost and port 1234, and it creates a new thread for each connected client
to handle input and output separately.
"""

import logging
import socket
import threading


def handle_client_input(client_socket):
    """Handle input from the client.

    This function continuously prompts the user for input and sends it to the connected client
    until the connection is broken.
    """
    while True:
        try:
            message = input("Enter your message: ")
            client_socket.send(message.encode("utf-8"))
        except BrokenPipeError:
            logging.info("Connection to client lost. Exiting.")
            client_socket.close()
            break


def handle_client_output(client_socket):
    """Handle output to the client.

    This function continuously receives messages from the connected client and logs them
    until the connection is reset.
    """
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break
            logging.info(f"Received message from client: {message.decode('utf-8')}")
        except ConnectionResetError:
            logging.info("Connection lost. Closing connection.")
            client_socket.close()
            break


def start_server():
    """Start the server.

    This function sets up the server to listen for incoming connections on localhost and port 1234.
    For each client connection, it creates two threads to handle input and output separately.

    The server runs indefinitely until manually stopped.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", 1234))
    server_socket.listen(5)
    logging.info("Server listening on port 1234")

    while True:
        client_socket, addr = server_socket.accept()
        logging.info(f"Connection established with {addr}")

        threading.Thread(target=handle_client_output, args=(client_socket,)).start()
        threading.Thread(target=handle_client_input, args=(client_socket,)).start()


if __name__ == "__main__":
    start_server()
