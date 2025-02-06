import logging
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QLabel
from PyQt6.uic import loadUi
from PyQt6.QtCore import QTimer

# Import the separated controllers
from controllers.filter_controller import FilterController
from controllers.message_controller import MessageController
from controllers.can_controller import CANController
from controllers.monitor_controller import MonitorController
from controllers.remote_controller import RemoteController

class MainWindow(QMainWindow):
    """
    Main application window for the CAN Monitor Tool.
    """
    def __init__(self):
        super().__init__()
        loadUi("ui/main_window.ui", self)

        # Instantiate controllers
        self.filter_controller = FilterController(self)
        self.message_controller = MessageController(self)
        self.can_controller = CANController(self)
        self.monitor_controller = MonitorController(self)
        self.remote_controller = RemoteController(self, self.can_controller.can_interface, self.monitor_controller)
        
        # Set up a timer for polling received messages
        self.message_poll_timer = QTimer(self)
        self.message_poll_timer.timeout.connect(self.monitor_controller.update_monitor_table)
        self.message_poll_timer.start(100)
        
        # Set initial CAN connection status
        self.update_status_indicator(False)

        logging.info("MainWindow initialized.")

    def update_status_indicator(self, connected: bool):
        """Updates the status indicator based on the connection state."""
        # Look up the widget by its known type (QLabel) and object name ("ledCanStatus")
        status_indicator: QLabel = self.findChild(QLabel, "ledCanStatus")
        if not status_indicator:
            # Optionally, log or raise an error if the widget isn’t found.
            logging.error("Status indicator widget 'ledCanStatus' not found in UI.")
            return

        if connected:
            status_indicator.setStyleSheet("background-color: green; border-radius: 8px;")
        else:
            status_indicator.setStyleSheet("background-color: red; border-radius: 8px;")

    def show_error(self, message: str):
        """Displays an error message to the user."""
        logging.error(message)
        QMessageBox.critical(self, "Error", message)

    def get_current_timestamp(self) -> str:
        """Returns the current timestamp as a string."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    def closeEvent(self, event):
        """Clean up when the application is closed."""
        if self.can_controller.is_connected():
            self.can_controller.disconnect()
            logging.info("CAN interface disconnected on application close.")
        logging.info("Application closed.")
        event.accept()
