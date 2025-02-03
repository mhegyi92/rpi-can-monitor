import socket
import threading
import json
import logging
from core.can_interface import CANInterface

class CANServer:
    """Server that relays CAN messages between a remote client and a local CAN bus."""
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = []
        self.running = False
        self.can_interface = CANInterface()

    def start(self):
        """Starts the server and listens for incoming connections."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True
        logging.info(f"CAN Server started on {self.host}:{self.port}")

        threading.Thread(target=self.accept_clients, daemon=True).start()
        threading.Thread(target=self.forward_can_messages, daemon=True).start()

    def accept_clients(self):
        """Handles incoming client connections."""
        while self.running:
            client_socket, addr = self.server_socket.accept()
            self.clients.append(client_socket)
            logging.info(f"New client connected: {addr}")
            threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()

    def handle_client(self, client_socket):
        """Handles communication with a connected client."""
        try:
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                message = json.loads(data.decode())
                
                if message['type'] == 'tx':
                    self.can_interface.send_message(message['id'], message['data'])
        except Exception as e:
            logging.error(f"Client error: {e}")
        finally:
            self.clients.remove(client_socket)
            client_socket.close()

    def forward_can_messages(self):
        """Sends received CAN messages to all connected clients."""
        self.can_interface.start_receiving()
        while self.running:
            message = self.can_interface.get_received_message()
            if message:
                msg_json = json.dumps({
                    "type": "rx",
                    "id": message.arbitration_id,
                    "data": list(message.data)
                })
                self.broadcast(msg_json)

    def broadcast(self, msg_json):
        """Sends a message to all connected clients."""
        for client in self.clients:
            try:
                client.send(msg_json.encode())
            except Exception:
                self.clients.remove(client)

    def stop(self):
        """Stops the server and disconnects all clients."""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        for client in self.clients:
            client.close()
        self.clients.clear()
        logging.info("CAN Server stopped.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = CANServer()
    server.start()
