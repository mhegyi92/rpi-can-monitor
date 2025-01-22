import can
import logging
import threading
from queue import Queue
from can import Bus, Message

class CANInterface:
    """
    Manages the CAN interface connection and communication.
    """

    def __init__(self):
        self.channel = None
        self.bitrate = None
        self.connected = False
        self.bus = None
        self.receive_thread = None
        self.receive_queue = Queue()

    def connect(self, channel, bitrate):
        """
        Connects to the specified CAN channel with the given bitrate.
        """
        try:
            self.channel = channel
            self.bitrate = bitrate
            self.bus = Bus(interface="socketcan", channel=self.channel, bitrate=self.bitrate)
            self.connected = True
            logging.info(f"Connected to CAN channel '{channel}' at {bitrate} bitrate.")
            return True
        except Exception as e:
            logging.error(f"Failed to connect to CAN channel '{channel}': {e}")
            self.connected = False
            return False

    def disconnect(self):
        """
        Disconnects from the CAN interface.
        """
        try:
            if self.bus:
                self.bus.shutdown()
            self.connected = False
            self.channel = None
            self.bitrate = None
            logging.info("Disconnected from CAN channel.")
            return True
        except Exception as e:
            logging.error(f"Failed to disconnect: {e}")
            return False

    def is_connected(self):
        """
        Checks the connection status.
        """
        return self.connected

    def send_message(self, message_id, data):
        """
        Sends a CAN message.
        Args:
            message_id (int): The message ID.
            data (list[int]): The message data as a list of bytes.
        """
        if not self.connected or not self.bus:
            raise ConnectionError("CAN interface is not connected.")
        try:
            msg = Message(arbitration_id=message_id, data=data, is_extended_id=False)
            self.bus.send(msg)
            logging.info(f"Message sent: ID={hex(message_id)}, Data={data}")
        except Exception as e:
            logging.error(f"Failed to send message: {e}")
            raise

    def start_receiving(self):
        """
        Starts receiving messages in a separate thread.
        """
        if not self.connected or not self.bus:
            raise ConnectionError("CAN interface is not connected.")
        if self.receive_thread and self.receive_thread.is_alive():
            logging.info("Receive thread is already running.")
            return
        self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.receive_thread.start()
        logging.info("Started CAN message reception.")

    def _receive_loop(self):
        """
        Receives messages and puts them in the queue.
        """
        try:
            for msg in self.bus:
                self.receive_queue.put(msg)
        except Exception as e:
            logging.error(f"Error in receive loop: {e}")

    def stop_receiving(self):
        """
        Stops the receiving thread.
        """
        if self.receive_thread:
            self.receive_thread = None
            logging.info("Stopped CAN message reception.")

    def get_received_message(self):
        """
        Retrieves a message from the receive queue.
        Returns:
            Message: A CAN message object.
        """
        if not self.receive_queue.empty():
            return self.receive_queue.get()
        return None
