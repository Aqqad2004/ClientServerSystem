import signal
import socket
import sys
import threading
import json
import logging

# Setup logging

logging.basicConfig(filename="logs/server_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# Server data

clients = {}

def handle_client(conn, addr):

    try:

        data = conn.recv(1024).decode() #Decodes data from client

        client_data = json.loads(data) #Parses it as JSON
        
        # Register client

        if not register_client(client_data, conn):

            conn.send(b"Error: Registration failed.")

            return

        conn.send(b"Registration successful.")
        
        # Process actions until session ends
        while True:

            action_data = conn.recv(1024).decode()

            if not action_data:

                break

            action, amount = action_data.split()

            amount = int(amount)

            new_value = process_action(client_data['id'], action, amount)

            log_activity(client_data['id'], new_value)

            conn.send(f"Counter updated: {new_value}".encode())

    finally:

        # Cleanup and close connection

        conn.close()

        if client_data['id'] in clients:

            del clients[client_data['id']]

from threading import Lock

clients_lock = Lock()

def register_client(client_data, conn):
    client_id = client_data['id']
    password = client_data['password']

    with clients_lock:
        if client_id in clients and clients[client_id]['password'] != password:
            return False

        clients[client_id] = {"password": password, "counter": 0, "connection": conn}

    return True

def process_action(client_id, action, amount):
    if client_id not in clients:
        return 0

    if action not in ["INCREASE", "DECREASE"]:
        return clients[client_id]["counter"]

    try:
        amount = int(amount)
    except ValueError:
        return clients[client_id]["counter"]

    if action == "INCREASE":
        clients[client_id]["counter"] += amount
    elif action == "DECREASE":
        clients[client_id]["counter"] -= amount

    return clients[client_id]["counter"]

def log_activity(client_id, counter_value):

    logging.info(f"Client {client_id} updated counter to {counter_value}")

def start_server(ip, port):

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.bind((ip, port))

    server_socket.listen()

    server_socket.settimeout(1)  

    print(f"Server listening on {ip}:{port}")

    running = True

    def shutdown_server(signal, frame):

        nonlocal running

        print("\nShutting down the server...")

        running = False

        server_socket.close()

        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_server)

    while running:

        try:

            conn, addr = server_socket.accept()

            thread = threading.Thread(target=handle_client, args=(conn, addr))

            thread.start()

        except socket.timeout:
            
            continue

        except OSError:
           
            break

if __name__ == "__main__":
    start_server("127.0.0.1", 65432)