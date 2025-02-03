import socket
import threading
import json
import logging
from core.can_interface import CANInterface

# Constants
BUFFER_SIZE = 1024

class CANServer:
    """
    A server that forwards CAN messages between clients and a local CAN interface.
    """
    def __init__(self, host='0.0.0.0', port=5000, can_channel='can0', bitrate=500000):
        self.host = host
        self.port = port
        self.clients = []  # List of connected clients
        self.running = False
        self.can_interface = CANInterface()
        self.can_channel = can_channel
        self.bitrate = bitrate

    def start(self):
        """Starts the server."""
        self.running = True
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        logging.info(f"Server started on {self.host}:{self.port}")
        
        # Start CAN monitoring
        if self.can_interface.connect(self.can_channel, self.bitrate):
            self.can_interface.start_receiving()
            threading.Thread(target=self.monitor_can, daemon=True).start()
        else:
            logging.error("Failed to connect CAN interface")
        
        while self.running:
            client_socket, addr = server_socket.accept()
            self.clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
            logging.info(f"Client connected: {addr}")
    
    def monitor_can(self):
        """Reads messages from the CAN interface and forwards them to clients."""
        while self.running:
            message = self.can_interface.get_received_message()
            if message:
                self.broadcast(json.dumps({
                    'type': 'can_message',
                    'id': message.arbitration_id,
                    'data': list(message.data)
                }))
    
    def handle_client(self, client_socket):
        """Handles client commands."""
        try:
            while self.running:
                data = client_socket.recv(BUFFER_SIZE).decode('utf-8')
                if not data:
                    break
                message = json.loads(data)
                
                if message['type'] == 'send_message':
                    self.can_interface.send_message(message['id'], message['data'])
                elif message['type'] == 'change_can':
                    self.can_interface.disconnect()
                    self.can_interface.connect(message['channel'], message['bitrate'])
                    logging.info(f"Changed CAN interface to {message['channel']} at {message['bitrate']} bitrate")
        except Exception as e:
            logging.error(f"Client error: {e}")
        finally:
            self.clients.remove(client_socket)
            client_socket.close()
            logging.info("Client disconnected")
    
    def broadcast(self, message):
        """Sends a message to all connected clients."""
        for client in self.clients:
            try:
                client.send(message.encode('utf-8'))
            except:
                self.clients.remove(client)

class CANClient:
    """
    A client that connects to a CAN server and forwards messages.
    """
    def __init__(self, server_ip, port=5000):
        self.server_ip = server_ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def connect(self):
        """Connects to the CAN server."""
        self.socket.connect((self.server_ip, self.port))
        logging.info(f"Connected to CAN server at {self.server_ip}:{self.port}")
        threading.Thread(target=self.listen_for_messages, daemon=True).start()
    
    def listen_for_messages(self):
        """Listens for messages from the server."""
        while True:
            data = self.socket.recv(BUFFER_SIZE).decode('utf-8')
            if not data:
                break
            message = json.loads(data)
            
            if message['type'] == 'can_message':
                logging.info(f"Received CAN message: ID={hex(message['id'])}, Data={message['data']}")
    
    def send_can_message(self, message_id, data):
        """Sends a CAN message to the server."""
        message = json.dumps({'type': 'send_message', 'id': message_id, 'data': data})
        self.socket.send(message.encode('utf-8'))
    
    def change_can_interface(self, channel, bitrate):
        """Requests the server to change its CAN interface."""
        message = json.dumps({'type': 'change_can', 'channel': channel, 'bitrate': bitrate})
        self.socket.send(message.encode('utf-8'))
