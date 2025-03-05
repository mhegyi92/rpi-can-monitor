import logging
from PySide6.QtWidgets import QLineEdit, QPushButton
from core.message_manager import MessageManager

class PySideMessageController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.message_manager = MessageManager()
        self.init_widgets()

    def init_widgets(self):
        """Initialize message-related widgets and connect signals."""
        # In the PyDracula UI, we need to adapt to use appropriate widget names
        # For demo purposes, we use placeholders that will need to be updated
        self.message_id_input = self.main_window.findChild(QLineEdit, "lineEdit_messageId")  # Replace with actual name
        self.message_data_input = self.main_window.findChild(QLineEdit, "lineEdit_messageData")  # Replace with actual name
        self.send_message_button = self.main_window.findChild(QPushButton, "pushButton_sendMessage")  # Replace with actual name

        # Connect signals if widgets exist
        if self.send_message_button:
            self.send_message_button.clicked.connect(self.handle_send_message)

    def handle_send_message(self):
        """Handles sending a CAN message."""
        # Check if widgets exist
        if not self.message_id_input or not self.message_data_input:
            self.main_window.show_error("Message input fields not found in UI.")
            return
            
        # Get input values
        message_id = self.message_id_input.text().strip()
        message_data = self.message_data_input.text().strip()
        
        if not message_id or not message_data:
            self.main_window.show_error("Message ID and data are required.")
            return
        
        # Get CAN interface from CAN controller
        can_interface = self.main_window.can_controller.can_interface
        
        if not can_interface.is_connected():
            self.main_window.show_error("Please connect to the CAN interface first.")
            return
        
        # Add message to message manager
        timestamp = self.main_window.get_current_timestamp()
        if self.message_manager.add_message("user", message_id, message_data, timestamp):
            # Send message via CAN interface
            can_interface.send_message(message_id, message_data)
            logging.info(f"Sent message: ID={message_id}, Data={message_data}")
            
            # Clear input fields
            self.message_id_input.clear()
            self.message_data_input.clear()
        else:
            self.main_window.show_error("Failed to send message (invalid format).")