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
            self.stop_receiving()  # Ensure the receiving thread is stopped before disconnecting
            if self.bus:
                self.bus.shutdown()
            self.connected = False
            self.channel = None
            self.bitrate = None
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
        except Exception as e:
            logging.error(f"Failed to send message: {e}")
            raise

    def start_receiving(self):
        """
        Starts receiving messages in a separate thread.
        """
        if not self.connected or not self.bus:
            raise ConnectionError("CAN interface is not connected.")
        if not self.receive_thread or not self.receive_thread.is_alive():
            # Initialize and start the receive thread
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            logging.info("Started CAN message reception.")
        else:
            logging.info("Receive thread is already running.")

    def stop_receiving(self):
        """
        Stops the receiving thread by terminating the loop and clearing the thread reference.
        """
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_queue.put(None)  # Insert a sentinel value to break the receive loop
            self.receive_thread = None
            logging.info("Stopped CAN message reception.")

    def _receive_loop(self):
        """
        Receives messages and puts them in the queue.
        """
        try:
            for msg in self.bus:
                if not self.receive_thread:  # Stop if the thread reference is cleared
                    break
                self.receive_queue.put(msg)  # Add messages to the queue
        except Exception as e:
            logging.error(f"Error in receive loop: {e}")

    def get_received_message(self):
        """
        Retrieves a message from the receive queue.
        Returns:
            Message: A CAN message object.
        """
        if not self.receive_queue.empty():
            return self.receive_queue.get()
        return None

    def disconnect(self):
        """Disconnects from the CAN interface."""
        try:
            self.stop_receiving()
            if self.bus:
                self.bus.shutdown()
            self.connected = False
            self.channel = None
            self.bitrate = None
            return True
        except Exception as e:
            logging.error(f"Failed to disconnect: {e}")
            return False