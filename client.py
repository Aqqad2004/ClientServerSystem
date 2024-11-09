import socket
import json
import time

def load_config(config_path):
    with open(config_path, 'r') as file:
        return json.load(file)

def register_with_server(client_socket, client_id, password):
    client_data = json.dumps({"id": client_id, "password": password})
    client_socket.send(client_data.encode())
    response = client_socket.recv(1024).decode()
    print("Server response:", response)

def execute_actions(client_socket, actions):
    delay = actions['delay']
    for action in actions['steps']:
        print(f"Performing action: {action}")
        client_socket.send(action.encode())
        response = client_socket.recv(1024).decode()
        print("Server response:", response)
        time.sleep(delay)

if __name__ == "__main__":
    config = load_config("config.json")
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((config['server']['ip'], config['server']['port']))
    
    register_with_server(client_socket, config['id'], config['password'])
    execute_actions(client_socket, config['actions'])
    
    client_socket.close()
