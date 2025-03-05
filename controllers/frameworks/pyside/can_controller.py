import logging
from PySide6.QtWidgets import QLineEdit, QPushButton
from core.can_interface import CANInterface

class PySideCANController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.can_interface = CANInterface()
        self.init_widgets()

    def init_widgets(self):
        """Initialize CAN interface-related widgets and connect signals."""
        # In the PyDracula UI, we need to adapt to use appropriate widget names
        # For demo purposes, we use placeholders that will need to be updated
        self.channel_input = self.main_window.findChild(QLineEdit, "lineEdit_channel")  # Replace with actual name
        self.bitrate_input = self.main_window.findChild(QLineEdit, "lineEdit_bitrate")  # Replace with actual name
        self.connect_button = self.main_window.findChild(QPushButton, "pushButton_connect")  # Replace with actual name
        self.monitor_toggle_button = self.main_window.findChild(QPushButton, "pushButton_monitor")  # Replace with actual name

        # Connect signals if widgets exist
        if self.connect_button:
            self.connect_button.clicked.connect(self.handle_connect)
        if self.monitor_toggle_button:
            self.monitor_toggle_button.clicked.connect(self.handle_monitor_toggle)

    def is_connected(self) -> bool:
        return self.can_interface.is_connected()

    def disconnect(self) -> bool:
        return self.can_interface.disconnect()

    def handle_connect(self):
        """Handles connecting/disconnecting to the CAN interface."""
        if self.is_connected():
            if self.disconnect():
                self.main_window.update_status_indicator(False)
                if self.connect_button:
                    self.connect_button.setText("Connect")
                logging.info("Disconnected from CAN channel.")
            else:
                self.main_window.show_error("Failed to disconnect from the CAN interface.")
        else:
            if not self.channel_input or not self.bitrate_input:
                self.main_window.show_error("Channel and bitrate inputs not found in UI.")
                return
                
            channel = self.channel_input.text().strip()
            bitrate_str = self.bitrate_input.text().strip()
            if not channel or not bitrate_str:
                self.main_window.show_error("Channel and bitrate are required to connect.")
                return
            try:
                bitrate = int(bitrate_str)
                if self.can_interface.connect(channel, bitrate):
                    self.main_window.update_status_indicator(True)
                    if self.connect_button:
                        self.connect_button.setText("Disconnect")
                    self.can_interface.start_receiving()
                    logging.info(f"Connected to CAN channel '{channel}' at {bitrate} bitrate.")
                else:
                    self.main_window.show_error("Failed to connect to the CAN interface.")
            except ValueError:
                self.main_window.show_error("Invalid bitrate. Please enter a valid number.")

    def handle_monitor_toggle(self):
        """Handles toggling CAN message monitoring."""
        if not self.is_connected():
            self.main_window.show_error("Please connect to the CAN interface first.")
            return

        if not self.monitor_toggle_button:
            self.main_window.show_error("Monitor toggle button not found in UI.")
            return
            
        if self.monitor_toggle_button.text() == "Start":
            self.can_interface.start_receiving()
            self.monitor_toggle_button.setText("Stop")
            logging.info("CAN monitoring started.")
        else:
            self.can_interface.stop_receiving()
            self.monitor_toggle_button.setText("Start")
            logging.info("CAN monitoring stopped.")