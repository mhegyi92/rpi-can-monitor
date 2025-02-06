import socket
import threading
import json
import logging
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QRadioButton, QPushButton, QLineEdit

########################################################################
# Remote Server
########################################################################

class RemoteServer:
    def __init__(self, port, can_interface):
        """
        :param port: TCP port to listen on.
        :param can_interface: The local CAN interface object to use for sending messages.
        """
        self.port = port
        self.can_interface = can_interface
        self.clients = []
        self.server_socket = None
        self.running = False
        self.server_thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow address reuse
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('', self.port))
        self.server_socket.listen(5)
        self.server_thread = threading.Thread(target=self.accept_clients, daemon=True)
        self.server_thread.start()
        logging.info(f"Remote server started on port {self.port}.")

    def accept_clients(self):
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                logging.info(f"Client connected from {addr}.")
                self.clients.append(client_socket)
                # Start a thread to handle incoming commands from this client
                threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
            except Exception as e:
                logging.error(f"Error accepting client: {e}")

    def handle_client(self, client_socket):
        while self.running:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                try:
                    msg = json.loads(data.decode())
                    self.handle_command(msg, client_socket)
                except json.JSONDecodeError:
                    logging.error("Received invalid JSON from client.")
            except Exception as e:
                logging.error(f"Error handling client: {e}")
                break
        # Remove the client on disconnect
        if client_socket in self.clients:
            self.clients.remove(client_socket)
        client_socket.close()
        logging.info("Client disconnected.")

    def handle_command(self, command, client_socket):
        """
        Process a command sent by a remote client.
        For now, we support a 'send_message' command.
        Expected command format (JSON):
          { "cmd": "send_message", "data": { "id": "0x123", "data": "0x01 0x02 ..." } }
        """
        if command.get("cmd") == "send_message":
            msg_data = command.get("data")
            if msg_data:
                try:
                    message_id = int(msg_data.get("id"), 0)
                    # Assume the data is a space‐separated string of numbers (in hex, binary, or decimal)
                    data_str = msg_data.get("data")
                    data_bytes = [int(b, 0) for b in data_str.split()]
                    self.can_interface.send_message(message_id, data_bytes)
                    logging.info(f"Remote server sent message: ID {hex(message_id)}, Data {data_bytes}")
                except Exception as e:
                    logging.error(f"Error processing send_message command: {e}")
        else:
            logging.warning("Received unknown command from client.")

    def broadcast_message(self, message):
        """
        Broadcast a CAN message (as a dictionary) to all connected clients.
        Expected message format (for example):
           { "timestamp": "2023-05-01 12:34:56.789",
             "type": "Rx",
             "id": "0x123",
             "data": ["0x01", "0x02", ...] }
        """
        msg_json = json.dumps(message).encode()
        for client in self.clients:
            try:
                client.sendall(msg_json)
            except Exception as e:
                logging.error(f"Error broadcasting message: {e}")

    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        for client in self.clients:
            try:
                client.close()
            except Exception:
                pass
        self.clients = []
        logging.info("Remote server stopped.")

########################################################################
# Remote Client (QThread-based)
########################################################################

class RemoteClient(QThread):
    message_received = pyqtSignal(dict)

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.socket = None
        self.running = False

    def run(self):
        self.running = True
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            logging.info(f"Connected to remote server at {self.host}:{self.port}")
            while self.running:
                data = self.socket.recv(1024)
                if not data:
                    break
                try:
                    msg = json.loads(data.decode())
                    self.message_received.emit(msg)
                except json.JSONDecodeError:
                    logging.error("Received invalid JSON from server.")
        except Exception as e:
            logging.error(f"Remote client error: {e}")
        if self.socket:
            self.socket.close()
        logging.info("Remote client disconnected.")

    def send_command(self, command):
        """
        Send a command (as a dictionary) to the remote server.
        """
        if self.socket:
            try:
                msg_json = json.dumps(command).encode()
                self.socket.sendall(msg_json)
            except Exception as e:
                logging.error(f"Error sending command to server: {e}")

    def disconnect(self):
        self.running = False
        if self.socket:
            self.socket.close()

########################################################################
# Remote Controller (UI Integration)
########################################################################

class RemoteController:
    """
    Manages the Remote Tab functionality.
    Based on the selected mode, it can run as:
      - Local: operate directly on the CAN interface.
      - Server: start a RemoteServer that broadcasts CAN messages and receives commands.
      - Client: connect to a remote server and receive streamed CAN messages.
    """
    def __init__(self, main_window, can_interface, monitor_controller):
        self.main_window = main_window
        self.can_interface = can_interface
        self.monitor_controller = monitor_controller
        self.server = None
        self.client = None
        self.mode = "local"  # Modes: "local", "server", "client"
        self.init_widgets()

    def init_widgets(self):
        # Obtain remote tab widgets using findChild.
        # (Make sure these names match your UI file.)
        self.radioButtonServer = self.main_window.findChild(QRadioButton, "radioButtonServer")
        self.radioButtonClient = self.main_window.findChild(QRadioButton, "radioButtonClient")
        self.radioButtonLocal  = self.main_window.findChild(QRadioButton, "radioButtonLocal")
        self.buttonClientConnect = self.main_window.findChild(QPushButton, "buttonClientConnect")
        self.inputClientIp = self.main_window.findChild(QLineEdit, "inputClientIp")
        self.inputClientPort = self.main_window.findChild(QLineEdit, "inputClientPort")
        self.buttonServerStart = self.main_window.findChild(QPushButton, "buttonServerStart")
        self.inputServerPort = self.main_window.findChild(QLineEdit, "inputServerPort")

        # Connect radio buttons to mode change.
        if self.radioButtonLocal:
            self.radioButtonLocal.toggled.connect(lambda checked: self.set_mode("local") if checked else None)
        if self.radioButtonServer:
            self.radioButtonServer.toggled.connect(lambda checked: self.set_mode("server") if checked else None)
        if self.radioButtonClient:
            self.radioButtonClient.toggled.connect(lambda checked: self.set_mode("client") if checked else None)
        # Connect buttons.
        if self.buttonClientConnect:
            self.buttonClientConnect.clicked.connect(self.handle_client_connect)
        if self.buttonServerStart:
            self.buttonServerStart.clicked.connect(self.handle_server_start)

    def set_mode(self, mode):
        self.mode = mode
        logging.info(f"Remote mode set to: {mode}")
        if mode == "local":
            self.stop_server()
            self.stop_client()
        elif mode == "server":
            self.stop_client()
        elif mode == "client":
            self.stop_server()

    def handle_server_start(self):
        try:
            port = int(self.inputServerPort.text().strip())
        except ValueError:
            logging.error("Invalid server port.")
            return
        if self.server:
            self.stop_server()
        self.server = RemoteServer(port, self.can_interface)
        self.server.start()
        logging.info("Remote server started.")

    def stop_server(self):
        if self.server:
            self.server.stop()
            self.server = None

    def handle_client_connect(self):
        ip = self.inputClientIp.text().strip()
        try:
            port = int(self.inputClientPort.text().strip())
        except ValueError:
            logging.error("Invalid client port.")
            return
        if self.client:
            self.stop_client()
        self.client = RemoteClient(ip, port)
        self.client.message_received.connect(self.handle_remote_message)
        self.client.start()
        logging.info("Remote client connecting...")

    def stop_client(self):
        if self.client:
            self.client.disconnect()
            self.client.wait()
            self.client = None

    def handle_remote_message(self, message):
        """
        Called when a remote CAN message is received.
        The 'message' is expected to be a dict with keys such as
        'timestamp', 'type', 'id', and 'data'.
        Forward it to the monitor controller for display.
        """
        self.monitor_controller.append_message(message)


    def send_remote_command(self, command):
        """
        If in client mode, send a command via the RemoteClient.
        For example, to send a message remotely.
        """
        if self.mode == "client" and self.client:
            self.client.send_command(command)
        elif self.mode == "server":
            # In server mode, you might choose to handle local commands directly.
            logging.info("Server mode: command processing is done locally.")
