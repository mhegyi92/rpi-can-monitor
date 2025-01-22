import can
import logging

class CANInterface:
    """
    Manages the CAN interface connection and communication.
    """
    def __init__(self):
        self.channel = None
        self.bitrate = None
        self.bus = None  # This will hold the CAN bus object
        self.connected = False

    def connect(self, channel, bitrate):
        """
        Connects to the specified CAN channel with the given bitrate.
        """
        try:
            # Connect to the CAN interface using python-can
            self.channel = channel
            self.bitrate = bitrate
            self.bus = can.interface.Bus(channel=channel, bustype='socketcan', bitrate=bitrate)
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
            # Close the CAN bus connection
            if self.bus:
                self.bus.shutdown()
                self.bus = None
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
            message_id (int): The CAN ID of the message.
            data (list[int]): A list of data bytes (max 8 bytes).

        Returns:
            bool: True if the message was sent successfully, False otherwise.
        """
        if not self.connected or not self.bus:
            logging.error("Cannot send message: Not connected to a CAN interface.")
            return False

        try:
            # Create a CAN message
            msg = can.Message(arbitration_id=message_id, data=data, is_extended_id=False)
            self.bus.send(msg)
            logging.info(f"Message sent: ID={hex(message_id)}, Data={data}")
            return True
        except Exception as e:
            logging.error(f"Failed to send message: {e}")
            return False

    def receive_message(self, timeout=1.0):
        """
        Receives a CAN message (blocking).

        Args:
            timeout (float): The time (in seconds) to wait for a message.

        Returns:
            can.Message: The received CAN message, or None if no message is received.
        """
        if not self.connected or not self.bus:
            logging.error("Cannot receive message: Not connected to a CAN interface.")
            return None

        try:
            msg = self.bus.recv(timeout=timeout)
            if msg:
                logging.info(f"Message received: ID={hex(msg.arbitration_id)}, Data={list(msg.data)}")
            return msg
        except Exception as e:
            logging.error(f"Failed to receive message: {e}")
            return None
