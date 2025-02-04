import logging
from PyQt6.QtWidgets import QTableWidgetItem, QLineEdit, QPushButton, QTableWidget
from core.message_manager import MessageManager
from core.utils import parse_value

class MessageController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.message_manager = MessageManager()
        self.init_widgets()
        self.setup_table()

    def init_widgets(self):
        """Initialize message-related widgets and connect signals."""
        self.messages_table: QTableWidget = self.main_window.findChild(QTableWidget, "tableMessages")
        self.message_name_input: QLineEdit = self.main_window.findChild(QLineEdit, "inputMessageName")
        self.message_id_input: QLineEdit = self.main_window.findChild(QLineEdit, "inputMessageId")
        self.message_byte_inputs = [self.main_window.findChild(QLineEdit, f"inputMessageByte{i}") for i in range(8)]
        self.add_message_button: QPushButton = self.main_window.findChild(QPushButton, "buttonAddMessage")
        self.remove_message_button: QPushButton = self.main_window.findChild(QPushButton, "buttonRemoveMessage")
        self.clear_messages_button: QPushButton = self.main_window.findChild(QPushButton, "buttonClearMessages")
        self.send_message_button: QPushButton = self.main_window.findChild(QPushButton, "buttonSendMessage")
        self.send_selected_button: QPushButton = self.main_window.findChild(QPushButton, "buttonSendSelected")

        # Connect message buttons to handlers
        self.add_message_button.clicked.connect(self.handle_add_message)
        self.remove_message_button.clicked.connect(self.handle_remove_message)
        self.clear_messages_button.clicked.connect(self.handle_clear_messages)
        self.send_message_button.clicked.connect(self.handle_send_message)
        self.send_selected_button.clicked.connect(self.handle_send_selected_message)
        self.messages_table.itemChanged.connect(self.handle_edit_message)

    def setup_table(self):
        """Set up the messages table for in-place editing."""
        self.messages_table.setColumnCount(10)
        self.messages_table.setHorizontalHeaderLabels(
            ["Message Name", "Message ID"] + [f"Byte {i}" for i in range(8)]
        )
        self.messages_table.setEditTriggers(self.messages_table.EditTrigger.AllEditTriggers)

    def update_messages_table(self):
        """Updates the messages table with the latest messages."""
        self.messages_table.blockSignals(True)
        self.messages_table.setRowCount(0)
        messages = self.message_manager.get_messages()

        for row_index, msg in enumerate(messages):
            self.messages_table.insertRow(row_index)
            self.messages_table.setItem(row_index, 0, QTableWidgetItem(msg['name']))
            self.messages_table.setItem(row_index, 1, QTableWidgetItem(hex(msg['id'])))
            for col_index, byte_value in enumerate(msg['data']):
                self.messages_table.setItem(row_index, col_index + 2, QTableWidgetItem(hex(byte_value)))

        self.messages_table.blockSignals(False)

    def handle_add_message(self):
        """Handles adding a new message."""
        name = self.message_name_input.text().strip()
        message_id = self.message_id_input.text().strip()
        message_bytes = [input_field.text().strip() for input_field in self.message_byte_inputs]

        if not name:
            self.main_window.show_error("Message Name is required.")
            return
        if not message_id:
            self.main_window.show_error("Message ID is required.")
            return

        try:
            parsed_id = parse_value(message_id)
            if not (0 <= parsed_id <= 0x7FF):
                raise ValueError(f"Invalid Message ID: {parsed_id}")
            parsed_bytes = []
            for i, byte in enumerate(message_bytes):
                if byte:
                    parsed_byte = parse_value(byte)
                    if not (0 <= parsed_byte <= 255):
                        raise ValueError(f"Invalid Byte {i}: {parsed_byte}")
                    parsed_bytes.append(parsed_byte)
                else:
                    parsed_bytes.append(0)
            data = " ".join(hex(b) for b in parsed_bytes)
            if self.message_manager.add_message(name, hex(parsed_id), data):
                self.update_messages_table()
                self.message_name_input.clear()
                self.message_id_input.clear()
                for input_field in self.message_byte_inputs:
                    input_field.clear()
            else:
                self.main_window.show_error(f"Duplicate message detected for '{name}'.")
        except ValueError as e:
            self.main_window.show_error(str(e))

    def handle_remove_message(self):
        """Handles removing selected messages."""
        selected_rows = sorted({index.row() for index in self.messages_table.selectedIndexes()}, reverse=True)
        if not selected_rows:
            self.main_window.show_error("Please select one or more messages to remove.")
            return

        for row in selected_rows:
            name = self.messages_table.item(row, 0).text()
            if not self.message_manager.remove_message(name):
                self.main_window.show_error(f"Failed to remove message: {name}")

        self.update_messages_table()

    def handle_clear_messages(self):
        """Clears all messages."""
        self.message_manager.clear_messages()
        self.update_messages_table()

    def handle_edit_message(self, item):
        """Handles editing a message directly in the table.
        (Detailed editing logic would be similar to the filter editing method.)
        """
        pass

    def handle_send_message(self):
        """Handles sending a single message.
        (You might call the CAN controller’s send functionality here.)
        """
        pass

    def handle_send_selected_message(self):
        """Handles sending selected messages.
        (You might loop through selected rows and trigger sending.)
        """
        pass
