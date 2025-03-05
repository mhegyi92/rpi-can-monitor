import logging
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtGui import QColor
from core.message_manager import MessageManager
from datetime import datetime

class PySideMonitorController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.message_manager = MessageManager()
        self.init_widgets()
        self.last_message_count = 0

    def init_widgets(self):
        """Initialize monitor-related widgets."""
        # In the PyDracula UI, we need to adapt to use appropriate widget names
        # For demo purposes, we use a placeholder that will need to be updated
        self.monitor_table = self.main_window.findChild(QTableWidget, "tableWidget")  # Use the default table from PyDracula

        # Configure table if it exists
        if self.monitor_table:
            self.monitor_table.setColumnCount(5)
            self.monitor_table.setHorizontalHeaderLabels(["Timestamp", "Source", "ID", "Data", "Count"])
            self.monitor_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)  # Make data column expandable
            self.monitor_table.setSelectionBehavior(QTableWidget.SelectRows)
            self.monitor_table.setEditTriggers(QTableWidget.NoEditTriggers)

    def update_monitor_table(self):
        """
        Updates the monitor table with received CAN messages.
        This method is called periodically by a timer.
        """
        if not self.monitor_table:
            return

        # Get messages from the message manager
        messages = self.message_manager.get_messages()
        
        # Clear previous content
        # Optimization: only clear and repopulate if the number of messages has changed
        if self.last_message_count != len(messages):
            self.monitor_table.setRowCount(0)
            
            # Add each message
            for i, msg in enumerate(messages):
                self.monitor_table.insertRow(i)
                
                # Set timestamp
                timestamp_item = QTableWidgetItem(msg["timestamp"])
                self.monitor_table.setItem(i, 0, timestamp_item)
                
                # Set source
                source_item = QTableWidgetItem(msg["source"])
                self.monitor_table.setItem(i, 1, source_item)
                
                # Set ID
                id_item = QTableWidgetItem(msg["id"])
                self.monitor_table.setItem(i, 2, id_item)
                
                # Set data
                data_item = QTableWidgetItem(" ".join(msg["data"]))
                self.monitor_table.setItem(i, 3, data_item)
                
                # Set count
                count_item = QTableWidgetItem(str(msg["count"]))
                self.monitor_table.setItem(i, 4, count_item)
                
                # Highlight new messages
                if msg["new"]:
                    for col in range(5):
                        item = self.monitor_table.item(i, col)
                        item.setBackground(QColor(200, 255, 200))  # Light green
            
            self.last_message_count = len(messages)
            
        # Update "new" flag in message manager
        self.message_manager.mark_all_as_old()

    def clear_monitor(self):
        """Clears the monitor table."""
        if self.monitor_table:
            self.monitor_table.setRowCount(0)
        self.message_manager.clear_messages()
        self.last_message_count = 0

    def add_message(self, source, can_id, data):
        """
        Adds a message to the message manager.
        This is used by the remote controller to add messages.
        """
        timestamp = self.main_window.get_current_timestamp()
        return self.message_manager.add_message(source, can_id, data, timestamp)