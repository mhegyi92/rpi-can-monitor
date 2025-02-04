import logging
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QTableView

class MonitorController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.monitor_table: QTableView = self.main_window.findChild(QTableView, "tableMonitor")
        if not self.monitor_table:
            raise ValueError("Monitor table not found in the UI.")
        self.setup_table()

    def setup_table(self):
        """Set up the monitor table for displaying CAN messages."""
        self.monitor_model = QStandardItemModel(0, 11, self.main_window)
        self.monitor_model.setHorizontalHeaderLabels(
            ["Timestamp", "Type", "Message ID"] + [f"Byte {i}" for i in range(8)]
        )
        self.monitor_table.setModel(self.monitor_model)

    def update_monitor_table(self):
        """Polls for new messages and updates the monitor table."""
        can_interface = self.main_window.can_controller.can_interface
        while True:
            message = can_interface.get_received_message()
            if not message:
                break

            # Create a message dictionary
            message_dict = {
                "timestamp": self.main_window.get_current_timestamp(),
                "type": "Rx",
                "id": hex(message.arbitration_id),
                "data": [hex(byte) for byte in message.data]
            }

            # Add the message to the monitor table
            timestamp_item = QStandardItem(message_dict["timestamp"])
            type_item = QStandardItem(message_dict["type"])
            id_item = QStandardItem(message_dict["id"])
            data_items = [QStandardItem(byte) for byte in message_dict["data"]]
            row = [timestamp_item, type_item, id_item] + data_items
            self.monitor_model.appendRow(row)

            # Auto-scroll to bottom
            self.monitor_table.scrollToBottom()

            # If the RemoteController is in server mode, broadcast this message.
            remote_ctrl = getattr(self.main_window, "remote_controller", None)
            if remote_ctrl and remote_ctrl.mode == "server" and remote_ctrl.server:
                remote_ctrl.server.broadcast_message(message_dict)

    def append_remote_message(self, message):
        # Create QStandardItems from the remote message dictionary.
        # Assume message contains keys: "timestamp", "type", "id", and "data" (list of hex strings)
        from PyQt6.QtGui import QStandardItem
        timestamp = QStandardItem(message.get("timestamp", ""))
        message_type = QStandardItem(message.get("type", ""))
        msg_id = QStandardItem(message.get("id", ""))
        data_items = [QStandardItem(byte) for byte in message.get("data", [])]
        row = [timestamp, message_type, msg_id] + data_items
        self.monitor_model.appendRow(row)
        # Optionally scroll to bottom.
        self.monitor_table.scrollToBottom()