import socket
import threading
import json
import logging
from queue import Queue

class CANClient:
    """Client that connects to a CAN server to send and receive messages."""
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = None
        self.running = False
        self.receive_queue = Queue()

    def connect(self):
        """Connects to the CAN server."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_ip, self.server_port))
            self.running = True
            logging.info(f"Connected to CAN Server at {self.server_ip}:{self.server_port}")
            threading.Thread(target=self.receive_messages, daemon=True).start()
            return True
        except Exception as e:
            logging.error(f"Failed to connect to CAN Server: {e}")
            return False

    def send_message(self, message_id, data):
        """Sends a CAN message to the server."""
        if not self.running:
            logging.error("Cannot send message, client is not connected.")
            return

        message = json.dumps({
            "type": "tx",
            "id": message_id,
            "data": data
        })
        try:
            self.client_socket.send(message.encode())
            logging.info(f"Sent message to server: ID={hex(message_id)}, Data={data}")
        except Exception as e:
            logging.error(f"Error sending message: {e}")

    def receive_messages(self):
        """Receives messages from the CAN server."""
        try:
            while self.running:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                message = json.loads(data.decode())
                if message['type'] == 'rx':
                    self.receive_queue.put(message)
                    logging.info(f"Received message from server: ID={hex(message['id'])}, Data={message['data']}")
        except Exception as e:
            logging.error(f"Error receiving message: {e}")
        finally:
            self.disconnect()

    def get_received_message(self):
        """Retrieves a message from the receive queue."""
        if not self.receive_queue.empty():
            return self.receive_queue.get()
        return None

    def disconnect(self):
        """Disconnects from the CAN server."""
        self.running = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except Exception:
                pass
        logging.info("Disconnected from CAN Server.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    client = CANClient("127.0.0.1", 5000)
    if client.connect():
        client.send_message(0x123, [1, 2, 3, 4, 5, 6, 7, 8])
