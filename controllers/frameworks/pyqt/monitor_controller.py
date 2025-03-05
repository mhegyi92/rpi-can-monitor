import logging
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QTableView
from queue import Empty

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
        """Polls for new messages from both RX and TX queues and updates the monitor table."""
        can_interface = self.main_window.can_controller.can_interface

        # Process any transmitted (Tx) messages.
        while True:
            try:
                tx_msg = can_interface.tx_queue.get_nowait()
            except Empty:
                break  # Queue is empty
            message_dict = {
                "timestamp": self.main_window.get_current_timestamp(),
                "type": "Tx",
                "id": hex(tx_msg.arbitration_id),
                "data": [hex(byte) for byte in tx_msg.data]
            }
            self.append_message(message_dict)

        # Process received (Rx) messages.
        while True:
            rx_msg = can_interface.get_received_message()
            if not rx_msg:
                break
            message_dict = {
                "timestamp": self.main_window.get_current_timestamp(),
                "type": "Rx",
                "id": hex(rx_msg.arbitration_id),
                "data": [hex(byte) for byte in rx_msg.data]
            }
            self.append_message(message_dict)

    def append_message(self, message_dict):
        """Helper method to append a message row to the monitor table."""
        timestamp_item = QStandardItem(message_dict.get("timestamp", ""))
        type_item = QStandardItem(message_dict.get("type", ""))
        id_item = QStandardItem(message_dict.get("id", ""))
        data_items = [QStandardItem(byte) for byte in message_dict.get("data", [])]
        row = [timestamp_item, type_item, id_item] + data_items
        self.monitor_model.appendRow(row)
        # Check if the vertical scroll bar is at its maximum
        vertical_scroll_bar = self.monitor_table.verticalScrollBar()
        if vertical_scroll_bar.value() == vertical_scroll_bar.maximum():
            self.monitor_table.scrollToBottom()
        # If running in server mode, you may also choose to broadcast the message.
        remote_ctrl = getattr(self.main_window, "remote_controller", None)
        if remote_ctrl and remote_ctrl.mode == "server" and remote_ctrl.server:
            remote_ctrl.server.broadcast_message(message_dict)
