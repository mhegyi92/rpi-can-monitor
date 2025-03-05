import sys
import os
import logging
from PyQt6.QtWidgets import QMainWindow, QApplication, QHeaderView, QMessageBox, QTableWidget, QTableWidgetItem, QLineEdit, QPushButton, QLabel
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QColor, QIcon

# Import controllers using existing PyQt6 controllers
from controllers.frameworks.pyqt.filter_controller import FilterController
from controllers.frameworks.pyqt.message_controller import MessageController
from controllers.frameworks.pyqt.can_controller import CANController
from controllers.frameworks.pyqt.monitor_controller import MonitorController
from controllers.frameworks.pyqt.remote_controller import RemoteController

class PyQtPyDraculaWindow(QMainWindow):
    """
    A PyQt6-compatible implementation of the PyDracula UI.
    Used as a fallback when PySide6 cannot be loaded.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAN Monitor - PyQt6 Modern UI")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create a central widget
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget for main functionality
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create Monitor tab
        self.monitor_tab = QWidget()
        self.tab_widget.addTab(self.monitor_tab, "Monitor")
        
        # Create Remote tab
        self.remote_tab = QWidget()
        self.tab_widget.addTab(self.remote_tab, "Remote")
        
        # Create CAN tab
        self.can_tab = QWidget()
        self.tab_widget.addTab(self.can_tab, "CAN Settings")
        
        # Create UI components for each tab
        self.setup_monitor_tab()
        self.setup_remote_tab()
        self.setup_can_tab()
        
        # Initialize controllers after UI setup
        # We'll set up stub controllers without initializing widgets since we have a different UI
        self.filter_controller = self.create_stub_filter_controller()
        self.message_controller = self.create_stub_message_controller()
        self.can_controller = self.create_stub_can_controller() 
        self.monitor_controller = self.create_stub_monitor_controller()
        self.remote_controller = RemoteController(self, self.can_controller.can_interface, self.monitor_controller)
        
        # Set up a timer for polling received messages
        self.message_poll_timer = QTimer(self)
        self.message_poll_timer.timeout.connect(self.monitor_controller.update_monitor_table)
        self.message_poll_timer.start(100)
        
        # Set initial CAN connection status
        self.update_status_indicator(False)
        
        logging.info("PyQt PyDracula Window initialized.")
        
    def update_status_indicator(self, connected: bool):
        """Updates the status indicator based on the connection state."""
        # This method is required by the controllers
        status_text = "Connected" if connected else "Disconnected"
        self.setWindowTitle(f"CAN Monitor - {status_text}")
        
    def show_error(self, message: str):
        """Displays an error message to the user."""
        logging.error(message)
        QMessageBox.critical(self, "Error", message)
        
    def get_current_timestamp(self) -> str:
        """Returns the current timestamp as a string."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
    def setup_monitor_tab(self):
        """Set up the monitor tab with necessary widgets."""
        from PyQt6.QtWidgets import QVBoxLayout, QTableWidget, QHeaderView
        
        # Create layout
        layout = QVBoxLayout(self.monitor_tab)
        
        # Create and add monitor table
        self.table_monitor = QTableWidget()
        self.table_monitor.setObjectName("tableMonitor")
        self.table_monitor.setColumnCount(5)
        self.table_monitor.setHorizontalHeaderLabels(["Timestamp", "Source", "ID", "Data", "Count"])
        self.table_monitor.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_monitor)
    
    def setup_remote_tab(self):
        """Set up the remote tab with necessary widgets."""
        from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
        
        # Create layout
        layout = QVBoxLayout(self.remote_tab)
        
        # Create and add IP/port inputs
        ip_layout = QHBoxLayout()
        ip_layout.addWidget(QLabel("IP:"))
        self.input_ip = QLineEdit()
        self.input_ip.setObjectName("inputIp")
        ip_layout.addWidget(self.input_ip)
        ip_layout.addWidget(QLabel("Port:"))
        self.input_port = QLineEdit("5000")
        self.input_port.setObjectName("inputPort")
        ip_layout.addWidget(self.input_port)
        layout.addLayout(ip_layout)
        
        # Create and add buttons
        button_layout = QHBoxLayout()
        self.button_start_server = QPushButton("Start Server")
        self.button_start_server.setObjectName("buttonStartServer")
        button_layout.addWidget(self.button_start_server)
        self.button_connect_client = QPushButton("Connect as Client")
        self.button_connect_client.setObjectName("buttonConnectClient")
        button_layout.addWidget(self.button_connect_client)
        layout.addLayout(button_layout)
    
    def setup_can_tab(self):
        """Set up the CAN tab with necessary widgets."""
        from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QHeaderView
        
        # Create layout
        layout = QVBoxLayout(self.can_tab)
        
        # Create and add connection settings
        conn_layout = QHBoxLayout()
        conn_layout.addWidget(QLabel("Channel:"))
        self.input_channel = QLineEdit("can0")
        self.input_channel.setObjectName("inputCanChannel")
        conn_layout.addWidget(self.input_channel)
        conn_layout.addWidget(QLabel("Bitrate:"))
        self.input_bitrate = QLineEdit("500000")
        self.input_bitrate.setObjectName("inputCanBitrate")
        conn_layout.addWidget(self.input_bitrate)
        self.button_connect = QPushButton("Connect")
        self.button_connect.setObjectName("buttonCanConnect")
        conn_layout.addWidget(self.button_connect)
        layout.addLayout(conn_layout)
        
        # Create and add filter section
        filter_layout = QVBoxLayout()
        filter_layout.addWidget(QLabel("Filters:"))
        self.table_filters = QTableWidget()
        self.table_filters.setObjectName("tableFilters")
        self.table_filters.setColumnCount(9)
        self.table_filters.setHorizontalHeaderLabels(["ID", "B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7"])
        self.table_filters.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        filter_layout.addWidget(self.table_filters)
        
        # Filter input and buttons
        filter_input_layout = QHBoxLayout()
        filter_input_layout.addWidget(QLabel("ID:"))
        self.input_filter_id = QLineEdit()
        self.input_filter_id.setObjectName("inputFilterId")
        filter_input_layout.addWidget(self.input_filter_id)
        
        for i in range(8):
            filter_input_layout.addWidget(QLabel(f"B{i}:"))
            input_byte = QLineEdit()
            input_byte.setObjectName(f"inputFilterByte{i}")
            input_byte.setMaximumWidth(40)
            filter_input_layout.addWidget(input_byte)
            setattr(self, f"input_filter_byte{i}", input_byte)
        
        filter_layout.addLayout(filter_input_layout)
        
        # Filter buttons
        filter_button_layout = QHBoxLayout()
        self.button_add_filter = QPushButton("Add Filter")
        self.button_add_filter.setObjectName("buttonAddFilter")
        filter_button_layout.addWidget(self.button_add_filter)
        self.button_remove_filter = QPushButton("Remove Filter")
        self.button_remove_filter.setObjectName("buttonRemoveFilter")
        filter_button_layout.addWidget(self.button_remove_filter)
        self.button_clear_filters = QPushButton("Clear Filters")
        self.button_clear_filters.setObjectName("buttonClearFilters")
        filter_button_layout.addWidget(self.button_clear_filters)
        filter_layout.addLayout(filter_button_layout)
        
        layout.addLayout(filter_layout)
    
    def create_stub_filter_controller(self):
        """Create a stub filter controller with basic functionality."""
        from core.filter_manager import FilterManager
        
        class StubFilterController:
            def __init__(self, window):
                self.main_window = window
                self.filter_manager = FilterManager()
                
                # Connect buttons
                if hasattr(window, 'button_add_filter'):
                    window.button_add_filter.clicked.connect(self.handle_add_filter)
                if hasattr(window, 'button_remove_filter'):
                    window.button_remove_filter.clicked.connect(self.handle_remove_filter)
                if hasattr(window, 'button_clear_filters'):
                    window.button_clear_filters.clicked.connect(self.handle_clear_filters)
                
            def handle_add_filter(self):
                """Add a filter using values from the UI inputs."""
                if not hasattr(self.main_window, 'input_filter_id'):
                    return
                    
                # Get filter ID
                filter_id = self.main_window.input_filter_id.text().strip()
                if not filter_id:
                    self.main_window.show_error("Filter ID is required.")
                    return
                
                # Create mask from byte inputs
                mask = []
                for i in range(8):
                    byte_input = getattr(self.main_window, f'input_filter_byte{i}', None)
                    if byte_input and byte_input.text().strip():
                        try:
                            mask.append(byte_input.text().strip())
                        except:
                            mask.append("0")
                    else:
                        mask.append("0")
                
                # Join mask into a space-separated string
                mask_str = " ".join(mask)
                
                # Add the filter
                if self.filter_manager.add_filter(filter_id, mask_str):
                    logging.info(f"Filter added: ID={filter_id}, Mask={mask_str}")
                    self.update_filters_table()
                    
                    # Clear inputs
                    self.main_window.input_filter_id.clear()
                    for i in range(8):
                        byte_input = getattr(self.main_window, f'input_filter_byte{i}', None)
                        if byte_input:
                            byte_input.clear()
                else:
                    self.main_window.show_error("Failed to add filter (invalid format or duplicate)")
                
            def handle_remove_filter(self):
                pass  # Implement filter removal later
                
            def handle_clear_filters(self):
                self.filter_manager.clear_filters()
                logging.info("All filters cleared.")
                
            def update_filters_table(self):
                """Update the filters table with current filters."""
                if not hasattr(self.main_window, 'table_filters'):
                    return
                    
                table = self.main_window.table_filters
                table.setRowCount(0)
                
                # Add current filters to the table
                for i, f in enumerate(self.filter_manager.get_filters()):
                    table.insertRow(i)
                    
                    # Add filter ID
                    table.setItem(i, 0, QTableWidgetItem(str(f["id"])))
                    
                    # Add mask bytes
                    for j, byte in enumerate(f["mask"]):
                        if j < 8:  # Ensure we don't go out of bounds
                            table.setItem(i, j+1, QTableWidgetItem(str(byte)))
        
        return StubFilterController(self)
    
    def create_stub_message_controller(self):
        """Create a stub message controller with basic functionality."""
        from core.message_manager import MessageManager
        
        class StubMessageController:
            def __init__(self, window):
                self.main_window = window
                self.message_manager = MessageManager()
                
            def handle_send_message(self):
                pass  # Implement message sending later
        
        return StubMessageController(self)
    
    def create_stub_can_controller(self):
        """Create a stub CAN controller with basic functionality."""
        from core.can_interface import CANInterface
        
        class StubCANController:
            def __init__(self, window):
                self.main_window = window
                self.can_interface = CANInterface()
                
                # Connect buttons
                if hasattr(window, 'button_connect'):
                    window.button_connect.clicked.connect(self.handle_connect)
                
            def is_connected(self):
                return self.can_interface.is_connected()
                
            def disconnect(self):
                return self.can_interface.disconnect()
                
            def handle_connect(self):
                pass  # Implement connection handling later
        
        return StubCANController(self)
    
    def create_stub_monitor_controller(self):
        """Create a stub monitor controller with basic functionality."""
        from core.message_manager import MessageManager
        
        class StubMonitorController:
            def __init__(self, window):
                self.main_window = window
                self.message_manager = MessageManager()
                self.last_message_count = 0
                self.monitor_table = window.table_monitor if hasattr(window, 'table_monitor') else None
                
            def update_monitor_table(self):
                # Simple implementation that can be improved later
                if not self.monitor_table:
                    return
                    
                messages = self.message_manager.get_messages()
                if self.last_message_count != len(messages):
                    self.monitor_table.setRowCount(0)
                    for i, msg in enumerate(messages):
                        self.monitor_table.insertRow(i)
                        self.monitor_table.setItem(i, 0, QTableWidgetItem(msg["timestamp"]))
                        self.monitor_table.setItem(i, 1, QTableWidgetItem(msg["source"]))
                        self.monitor_table.setItem(i, 2, QTableWidgetItem(msg["id"]))
                        self.monitor_table.setItem(i, 3, QTableWidgetItem(" ".join(msg["data"])))
                        self.monitor_table.setItem(i, 4, QTableWidgetItem(str(msg["count"])))
                    
                    self.last_message_count = len(messages)
                
                # Mark messages as old - Since this method doesn't exist in MessageManager yet
                # We'll skip it for now
                pass
                
            def add_message(self, source, can_id, data):
                timestamp = self.main_window.get_current_timestamp()
                return self.message_manager.add_message(source, can_id, data, timestamp)
        
        return StubMonitorController(self)