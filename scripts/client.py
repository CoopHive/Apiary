"""A simple client program that connects to a server running on localhost at port 1234.

It allows sending messages to the server and receiving messages from the server.
"""

import logging
import socket
import threading


def handle_input(client_socket):
    """Continuously prompts the user to enter a message and sends it to the server.

    Args:
        client_socket (socket.socket): The socket object connected to the server.

    Raises:
        BrokenPipeError: If the connection to the server is lost while sending a message.
    """
    while True:
        try:
            message = input("Enter your message: ")
            client_socket.send(message.encode("utf-8"))
        except BrokenPipeError:
            logging.error("Connection to server lost. Exiting.")
            client_socket.close()
            break


def start_client():
    """Start Client.

    Connects to a server running on localhost at port 1234 using TCP/IP socket.
    Starts a thread to handle user input and continuously receives messages from the server.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 1234))
    logging.info("Connected to server")

    threading.Thread(target=handle_input, args=(client_socket,)).start()

    while True:
        message = client_socket.recv(1024)
        if not message:
            break
        logging.info(f"Received message from server: {message.decode('utf-8')}")


if __name__ == "__main__":
    start_client()
