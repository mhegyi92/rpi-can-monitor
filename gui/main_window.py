import logging
from PyQt6.QtWidgets import (
    QMainWindow, QTableWidgetItem, QMessageBox, QPushButton, QLineEdit, QTableWidget, QLabel, QTableView
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.uic import loadUi
from PyQt6.QtCore import QTimer
from core.utils import parse_value
from core.filter_manager import FilterManager
from core.message_manager import MessageManager
from core.can_interface import CANInterface


class MainWindow(QMainWindow):
    """
    Main application window for the CAN Monitor Tool.
    """

    def __init__(self):
        super().__init__()
        loadUi("ui/main_window.ui", self)

        self.filter_manager = FilterManager()
        self.message_manager = MessageManager()
        self.can_interface = CANInterface()

        # Initialize GUI components
        self.init_filter_widgets()
        self.init_message_widgets()
        self.init_can_widgets()
        self.init_monitor_widgets()

        # Setup tables
        self.setup_filter_table()
        self.setup_message_table()
        self.setup_monitor_table()

        # Set up message reception polling
        self.message_poll_timer = QTimer(self)
        self.message_poll_timer.timeout.connect(self.update_monitor_table)

        # Set initial CAN connection status
        self.update_status_indicator(False)

        logging.info("MainWindow initialized.")

    def init_filter_widgets(self):
        """Initialize widgets related to filters."""
        self.filters_table = self.findChild(QTableWidget, "tableFilters")
        self.filter_id_input = self.findChild(QLineEdit, "inputFilterId")
        self.filter_byte_inputs = [self.findChild(QLineEdit, f"inputFilterByte{i}") for i in range(8)]
        self.add_filter_button = self.findChild(QPushButton, "buttonAddFilter")
        self.remove_filter_button = self.findChild(QPushButton, "buttonRemoveFilter")
        self.clear_filters_button = self.findChild(QPushButton, "buttonClearFilters")

        # Connect filter buttons to handlers
        self.add_filter_button.clicked.connect(self.handle_add_filter)
        self.remove_filter_button.clicked.connect(self.handle_remove_filter)
        self.clear_filters_button.clicked.connect(self.handle_clear_filters)
        self.filters_table.itemChanged.connect(self.handle_edit_filter)

    def init_message_widgets(self):
        """Initialize widgets related to messages."""
        self.messages_table = self.findChild(QTableWidget, "tableMessages")
        self.message_name_input = self.findChild(QLineEdit, "inputMessageName")
        self.message_id_input = self.findChild(QLineEdit, "inputMessageId")
        self.message_byte_inputs = [self.findChild(QLineEdit, f"inputMessageByte{i}") for i in range(8)]
        self.add_message_button = self.findChild(QPushButton, "buttonAddMessage")
        self.remove_message_button = self.findChild(QPushButton, "buttonRemoveMessage")
        self.clear_messages_button = self.findChild(QPushButton, "buttonClearMessages")
        self.send_message_button = self.findChild(QPushButton, "buttonSendMessage")
        self.send_selected_button = self.findChild(QPushButton, "buttonSendSelected")  # New button

        # Connect message buttons to handlers
        self.add_message_button.clicked.connect(self.handle_add_message)
        self.remove_message_button.clicked.connect(self.handle_remove_message)
        self.clear_messages_button.clicked.connect(self.handle_clear_messages)
        self.send_message_button.clicked.connect(self.handle_send_message)
        self.send_selected_button.clicked.connect(self.handle_send_selected_message)
        self.messages_table.itemChanged.connect(self.handle_edit_message)

    def init_can_widgets(self):
        """Initialize widgets related to CAN interface."""
        self.channel_input = self.findChild(QLineEdit, "inputCanChannel")
        self.bitrate_input = self.findChild(QLineEdit, "inputCanBitrate")
        self.connect_button = self.findChild(QPushButton, "buttonCanConnect")
        self.monitor_toggle_button = self.findChild(QPushButton, "buttonMonitorToggle")
        self.status_indicator = self.findChild(QLabel, "ledCanStatus")

        # Connect CAN buttons to handlers
        self.connect_button.clicked.connect(self.handle_connect)
        self.monitor_toggle_button.clicked.connect(self.handle_monitor_toggle)

    def init_monitor_widgets(self):
        """Initialize widgets related to the monitor."""
        self.monitor_table = self.findChild(QTableView, "tableMonitor")
        self.clear_monitor_button = self.findChild(QPushButton, "buttonMonitorClear")

        # Connect clear monitor button
        self.clear_monitor_button.clicked.connect(self.handle_clear_monitor)

    def setup_filter_table(self):
        """Setup the filters table with in-place editing."""
        self.filters_table.setColumnCount(9)  # One for ID and eight for data bytes
        self.filters_table.setHorizontalHeaderLabels(["Filter ID"] + [f"Byte {i}" for i in range(8)])
        self.filters_table.setEditTriggers(self.filters_table.EditTrigger.AllEditTriggers)

    def setup_message_table(self):
        """Setup the messages table with in-place editing."""
        self.messages_table.setColumnCount(10)  # One for Name, ID, and eight for data bytes
        self.messages_table.setHorizontalHeaderLabels(
            ["Message Name", "Message ID"] + [f"Byte {i}" for i in range(8)]
        )
        self.messages_table.setEditTriggers(self.messages_table.EditTrigger.AllEditTriggers)

    def setup_monitor_table(self):
        """Setup the monitor table for displaying received messages."""
        self.monitor_table = self.findChild(QTableView, "tableMonitor")
        if not self.monitor_table:
            raise ValueError("QTableView 'tableMonitor' not found in the UI file.")

        self.monitor_model = QStandardItemModel(0, 10, self)  # 0 rows, 10 columns
        self.monitor_model.setHorizontalHeaderLabels(
            ["Timestamp", "Message ID"] + [f"Byte {i}" for i in range(8)]
        )
        self.monitor_table.setModel(self.monitor_model)

    def handle_clear_monitor(self):
        """Clears all entries in the monitor table."""
        self.monitor_model.removeRows(0, self.monitor_model.rowCount())
        logging.info("Monitor table cleared.")

    def update_monitor_table(self):
        """Updates the monitor table with the latest received messages."""
        while True:
            message = self.can_interface.get_received_message()
            if not message:
                break

            row = [
                QStandardItem(str(message.timestamp)),
                QStandardItem(hex(message.arbitration_id)),
            ] + [QStandardItem(hex(byte)) for byte in message.data]

            self.monitor_model.appendRow(row)
        logging.info("Monitor table updated with received messages.")

    def handle_add_filter(self):
        """Handles adding a new filter."""
        filter_id = self.filter_id_input.text().strip()
        filter_bytes = [byte_input.text().strip() for byte_input in self.filter_byte_inputs]

        if not filter_id:
            self.show_error("Filter ID is required. Please enter a value for Filter ID.")
            return

        try:
            # Parse and validate filter ID
            parsed_id = parse_value(filter_id)
            if not (0 <= parsed_id <= 255):
                raise ValueError(f"Invalid Filter ID. Must be in range 0-255. Got: {parsed_id}")

            # Parse and validate each byte
            parsed_bytes = []
            for i, byte in enumerate(filter_bytes):
                if byte:  # Skip empty inputs
                    parsed_byte = parse_value(byte)
                    if not (0 <= parsed_byte <= 255):
                        raise ValueError(f"Invalid Byte {i}: Must be in range 0-255. Got: {parsed_byte}")
                    parsed_bytes.append(parsed_byte)
                else:
                    parsed_bytes.append(0)

            # Combine ID and byte values into a filter string
            mask = " ".join(hex(b) for b in parsed_bytes)

            logging.info(f"Attempting to add filter: ID={hex(parsed_id)}, Mask={mask}")

            if self.filter_manager.add_filter(hex(parsed_id), mask):
                logging.info("Filter added successfully.")
                self.update_filters_table()
                self.filter_id_input.clear()
                for byte_input in self.filter_byte_inputs:
                    byte_input.clear()
            else:
                self.show_error("Duplicate filter detected. A filter with the same ID and mask already exists.")
        except ValueError as e:
            self.show_error(str(e))

    def handle_remove_filter(self):
        """Handles removing selected filters."""
        selected_rows = sorted(set(index.row() for index in self.filters_table.selectedIndexes()), reverse=True)

        if not selected_rows:
            logging.warning("No filters selected for removal.")
            self.show_error("Please select one or more filters to remove.")
            return

        removed_successfully = True
        for row in selected_rows:
            filter_id = self.filters_table.item(row, 0).text()
            mask = [
                parse_value(self.filters_table.item(row, col).text()) for col in range(1, 9)
            ]

            logging.info(f"Attempting to remove filter: ID={filter_id}, Mask={mask}")
            if not self.filter_manager.remove_filter(filter_id, mask):
                logging.warning(f"Failed to remove filter: ID={filter_id}, Mask={mask}")
                removed_successfully = False

        if removed_successfully:
            logging.info("All selected filters removed successfully.")
            self.update_filters_table()
        else:
            self.show_error("Failed to remove one or more selected filters.")

    def handle_clear_filters(self):
        """Handles clearing all filters."""
        logging.info("Clearing all filters.")
        self.filter_manager.clear_filters()
        self.update_filters_table()

    def handle_edit_filter(self, item):
        """Handles editing a filter directly in the table."""
        row = item.row()
        col = item.column()

        try:
            # Get the current filter from the FilterManager
            current_filter = self.filter_manager.get_filters()[row]
            current_id = current_filter['id']
            current_mask = current_filter['mask']

            if col == 0:  # Editing the Filter ID
                new_id = parse_value(item.text())
                if not (0 <= new_id <= 255):
                    raise ValueError(f"Invalid Filter ID. Must be in range 0-255. Got: {new_id}")

                # Remove the original filter using the current ID and mask
                if not self.filter_manager.remove_filter(hex(current_id), current_mask):
                    raise ValueError(f"Failed to remove the original filter with ID {hex(current_id)}.")

                # Add the updated filter
                if not self.filter_manager.add_filter(hex(new_id), " ".join(hex(b) for b in current_mask)):
                    raise ValueError(f"Failed to update the filter to new ID {hex(new_id)}.")

            else:  # Editing the Bytes
                # Retrieve and validate the new mask values
                new_mask = [
                    parse_value(self.filters_table.item(row, c).text())
                    for c in range(1, 9)
                ]
                for i, b in enumerate(new_mask):
                    if not (0 <= b <= 255):
                        raise ValueError(f"Invalid Byte {i}: Must be in range 0-255. Got: {b}")

                # Retrieve the filter ID from the original data
                filter_id = current_id

                # Remove the original filter using the current ID and mask
                if not self.filter_manager.remove_filter(hex(filter_id), current_mask):
                    raise ValueError(f"Failed to remove the original filter with ID {hex(filter_id)}.")

                # Add the updated filter
                if not self.filter_manager.add_filter(hex(filter_id), " ".join(hex(b) for b in new_mask)):
                    raise ValueError(f"Failed to update the filter bytes for ID {hex(filter_id)}.")

            logging.info(f"Filter updated: Row={row}")
        except ValueError as e:
            logging.error(f"Error editing filter: {e}")
            self.show_error(str(e))
            self.update_filters_table()  # Revert to the previous state

    def update_filters_table(self):
        """Updates the filters table with the latest filters."""
        self.filters_table.blockSignals(True)  # Block signals to avoid triggering itemChanged
        self.filters_table.setRowCount(0)
        filters = self.filter_manager.get_filters()

        for row_index, f in enumerate(filters):
            self.filters_table.insertRow(row_index)
            self.filters_table.setItem(row_index, 0, QTableWidgetItem(hex(f['id'])))
            for col_index, byte_value in enumerate(f['mask']):
                self.filters_table.setItem(row_index, col_index + 1, QTableWidgetItem(hex(byte_value)))

        self.filters_table.blockSignals(False)  # Re-enable signals
        logging.info("Filters table updated.")

    def handle_add_message(self):
        """Handles adding a new message."""
        name = self.message_name_input.text().strip()
        message_id = self.message_id_input.text().strip()
        message_bytes = [byte_input.text().strip() for byte_input in self.message_byte_inputs]

        if not name:
            self.show_error("Message Name is required. Please enter a value for the message name.")
            return
        if not message_id:
            self.show_error("Message ID is required. Please enter a value for the message ID.")
            return

        try:
            parsed_id = parse_value(message_id)
            if not (0 <= parsed_id <= 255):
                raise ValueError(f"Invalid Message ID. Must be in range 0-255. Got: {parsed_id}")

            parsed_bytes = []
            for i, byte in enumerate(message_bytes):
                if byte:
                    parsed_byte = parse_value(byte)
                    if not (0 <= parsed_byte <= 255):
                        raise ValueError(f"Invalid Byte {i}: Must be in range 0-255. Got: {parsed_byte}")
                    parsed_bytes.append(parsed_byte)
                else:
                    parsed_bytes.append(0)

            data = " ".join(hex(b) for b in parsed_bytes)

            if self.message_manager.add_message(name, hex(parsed_id), data):
                self.update_messages_table()
                self.message_name_input.clear()
                self.message_id_input.clear()
                for byte_input in self.message_byte_inputs:
                    byte_input.clear()
            else:
                self.show_error(f"Duplicate message detected. A message with name '{name}' already exists.")
        except ValueError as e:
            self.show_error(str(e))

    def handle_remove_message(self):
        """Handles removing selected messages."""
        selected_rows = sorted(set(index.row() for index in self.messages_table.selectedIndexes()), reverse=True)

        if not selected_rows:
            self.show_error("Please select one or more messages to remove.")
            return

        for row in selected_rows:
            name = self.messages_table.item(row, 0).text()

            if not self.message_manager.remove_message(name):
                self.show_error(f"Failed to remove message with Name={name}.")

        self.update_messages_table()

    def handle_clear_messages(self):
        """Handles clearing all messages."""
        self.message_manager.clear_messages()
        self.update_messages_table()

    def handle_edit_message(self, item):
        """Handles editing a message directly in the table."""
        row = item.row()
        col = item.column()

        try:
            # Get the current message from the MessageManager
            current_message = self.message_manager.get_messages()[row]
            current_name = current_message['name']
            current_id = current_message['id']
            current_data = current_message['data']

            if col == 0:  # Editing the Message Name
                new_name = item.text().strip()
                if not new_name:
                    raise ValueError("Message Name cannot be empty.")

                # Check for duplicate name
                if any(msg['name'] == new_name for msg in self.message_manager.get_messages() if msg != current_message):
                    raise ValueError(f"A message with the name '{new_name}' already exists.")

                # Update the message name
                self.message_manager.remove_message(current_name)
                self.message_manager.add_message(new_name, hex(current_id), " ".join(hex(b) for b in current_data))

            elif col == 1:  # Editing the Message ID
                new_id = parse_value(item.text())
                if not (0 <= new_id <= 255):
                    raise ValueError(f"Invalid Message ID. Must be in range 0-255. Got: {new_id}")

                # Update the message ID
                self.message_manager.remove_message(current_name)
                self.message_manager.add_message(current_name, hex(new_id), " ".join(hex(b) for b in current_data))

            else:  # Editing the Bytes
                byte_index = col - 2
                if byte_index < 0 or byte_index >= 8:
                    raise ValueError(f"Invalid column index for data bytes: {byte_index}")

                # Update the specific byte value
                new_data = current_data[:]
                new_byte = parse_value(item.text())
                if not (0 <= new_byte <= 255):
                    raise ValueError(f"Invalid Byte {byte_index}: Must be in range 0-255. Got: {new_byte}")

                new_data[byte_index] = new_byte

                # Update the message data
                self.message_manager.remove_message(current_name)
                self.message_manager.add_message(current_name, hex(current_id), " ".join(hex(b) for b in new_data))

            logging.info(f"Message updated: Row={row}")
        except ValueError as e:
            logging.error(f"Error editing message: {e}")
            self.show_error(str(e))
            self.update_messages_table()  # Revert to the previous state if validation fails

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

    def handle_connect(self):
        """Handles connecting and disconnecting to the CAN interface."""
        if self.can_interface.is_connected():
            if self.can_interface.disconnect():
                self.update_status_indicator(False)
                self.connect_button.setText("Connect")
                self.message_poll_timer.stop()
            else:
                self.show_error("Failed to disconnect from the CAN interface.")
        else:
            channel = self.channel_input.text().strip()
            bitrate = self.bitrate_input.text().strip()
            if not channel or not bitrate:
                self.show_error("Channel and bitrate are required to connect.")
                return
            try:
                bitrate = int(bitrate)
                if self.can_interface.connect(channel, bitrate):
                    self.update_status_indicator(True)
                    self.connect_button.setText("Disconnect")
                    self.message_poll_timer.start(100)  # Poll messages every 100ms
                else:
                    self.show_error("Failed to connect to the CAN interface.")
            except ValueError:
                self.show_error("Invalid bitrate. Please enter a valid number.")

    def handle_send_message(self):
        """Handles sending a CAN message."""
        try:
            message_id = parse_value(self.message_id_input.text())
            data = [parse_value(input.text()) for input in self.message_byte_inputs if input.text().strip()]
            if not (0 <= message_id <= 0x7FF):
                raise ValueError(f"Invalid Message ID: {message_id}. Must be in range 0-0x7FF.")
            if len(data) > 8:
                raise ValueError(f"Invalid data length: {len(data)}. Must not exceed 8 bytes.")
            self.can_interface.send_message(message_id, data)
            self.show_info(f"Message sent: ID={hex(message_id)}, Data={data}")
        except Exception as e:
            self.show_error(f"Failed to send message: {e}")

    def handle_send_selected_message(self):
        """Handles sending a selected message from the table."""
        selected_rows = self.messages_table.selectionModel().selectedRows()
        if not selected_rows:
            self.show_error("Please select a message to send.")
            return

        try:
            for row in selected_rows:
                # Extract Message ID
                message_id_item = self.messages_table.item(row.row(), 1)
                if not message_id_item:
                    raise ValueError(f"Message ID is missing in row {row.row()}.")
                message_id = parse_value(message_id_item.text())

                # Extract Message Data
                data = []
                for col in range(2, 10):  # Columns 2-9 for data bytes
                    item = self.messages_table.item(row.row(), col)
                    if item and item.text().strip():
                        data.append(parse_value(item.text()))

                if not (0 <= message_id <= 0x7FF):
                    raise ValueError(f"Invalid Message ID: {message_id}. Must be in range 0-0x7FF.")
                if len(data) > 8:
                    raise ValueError(f"Invalid data length: {len(data)}. Must not exceed 8 bytes.")

                # Send the message using CAN interface
                self.can_interface.send_message(message_id, data)
                self.show_info(f"Message sent: ID={hex(message_id)}, Data={data}")
        except Exception as e:
            self.show_error(f"Failed to send selected message: {e}")

    def handle_start_listening(self):
        """Starts or stops listening for CAN messages."""
        if self.can_interface.is_connected():
            if self.connect_button.text() == "Start":
                self.can_interface.start_receiving()
                self.connect_button.setText("Stop")
            else:
                self.can_interface.stop_receiving()
                self.connect_button.setText("Start")
        else:
            self.show_error("Connect to the CAN interface first.")

    def update_received_messages(self):
        """Updates the received messages table."""
        message = self.can_interface.get_received_message()
        while message:
            row = self.messages_table.rowCount()
            self.messages_table.insertRow(row)
            self.messages_table.setItem(row, 0, QTableWidgetItem("Received"))
            self.messages_table.setItem(row, 1, QTableWidgetItem(hex(message.arbitration_id)))
            for i, byte in enumerate(message.data):
                self.messages_table.setItem(row, i + 2, QTableWidgetItem(hex(byte)))
            message = self.can_interface.get_received_message()

    def update_status_indicator(self, connected):
        """Updates the status indicator based on the connection state."""
        if connected:
            self.status_indicator.setStyleSheet("background-color: green; border-radius: 8px;")
        else:
            self.status_indicator.setStyleSheet("background-color: red; border-radius: 8px;")

    def handle_monitor_toggle(self):
        """Handles toggling the CAN message monitor."""
        if not self.can_interface.is_connected():
            self.show_error("Please connect to the CAN interface first.")
            return

        if self.monitor_toggle_button.text() == "Start":
            self.can_interface.start_receiving()
            self.monitor_toggle_button.setText("Stop")
            logging.info("CAN monitoring started.")
        else:
            self.can_interface.stop_receiving()
            self.monitor_toggle_button.setText("Start")
            logging.info("CAN monitoring stopped.")

    def show_error(self, message):
        """Displays an error message to the user."""
        logging.error(message)
        QMessageBox.critical(self, "Error", message)

    def show_info(self, message, details=None):
        """
        Displays an informational message to the user.
        Args:
            message (str): Main message to display.
            details (str): Additional details for the message.
        """
        logging.info(message)
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle("Information")
        msg_box.setText(message)
        if details:
            msg_box.setDetailedText(details)
        msg_box.exec()