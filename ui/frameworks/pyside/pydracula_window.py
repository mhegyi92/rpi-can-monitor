import sys
import os
import logging
from PySide6.QtWidgets import QMainWindow, QApplication, QHeaderView, QMessageBox
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QIcon

# Import the UI modules - adjust paths to match the new structure
from ui.assets.modules.ui_functions import UIFunctions
from ui.assets.modules.app_functions import AppFunctions
from ui.assets.modules.ui_main import Ui_MainWindow
from ui.assets.modules.app_settings import Settings

# Import controllers - these will need to be adapted for PySide6
from controllers.frameworks.pyside.filter_controller import PySideFilterController
from controllers.frameworks.pyside.message_controller import PySideMessageController
from controllers.frameworks.pyside.can_controller import PySideCANController
from controllers.frameworks.pyside.monitor_controller import PySideMonitorController
from controllers.frameworks.pyside.remote_controller import PySideRemoteController

# SET AS GLOBAL WIDGETS
widgets = None

class PyDraculaWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # SET UP UI
        # ///////////////////////////////////////////////////////////////
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        global widgets
        widgets = self.ui

        # USE CUSTOM TITLE BAR
        # ///////////////////////////////////////////////////////////////
        Settings.ENABLE_CUSTOM_TITLE_BAR = True

        # APP NAME
        # ///////////////////////////////////////////////////////////////
        title = "CAN Monitor - Modern GUI"
        description = "Raspberry Pi CAN Monitor Tool"
        # APPLY TEXTS
        self.setWindowTitle(title)
        widgets.titleRightInfo.setText(description)

        # TOGGLE MENU
        # ///////////////////////////////////////////////////////////////
        widgets.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))

        # SET UI DEFINITIONS
        # ///////////////////////////////////////////////////////////////
        UIFunctions.uiDefinitions(self)

        # INITIALIZE CONTROLLERS
        # ///////////////////////////////////////////////////////////////
        self.filter_controller = PySideFilterController(self)
        self.message_controller = PySideMessageController(self)
        self.can_controller = PySideCANController(self)
        self.monitor_controller = PySideMonitorController(self)
        self.remote_controller = PySideRemoteController(self, self.can_controller.can_interface, self.monitor_controller)
        
        # Set up a timer for polling received messages
        self.message_poll_timer = QTimer(self)
        self.message_poll_timer.timeout.connect(self.monitor_controller.update_monitor_table)
        self.message_poll_timer.start(100)
        
        # Set initial CAN connection status
        self.update_status_indicator(False)

        # BUTTONS CLICK CONNECTIONS
        # ///////////////////////////////////////////////////////////////
        # LEFT MENU
        widgets.btn_home.clicked.connect(self.buttonClick)
        widgets.btn_widgets.clicked.connect(self.buttonClick)
        widgets.btn_new.clicked.connect(self.buttonClick)
        widgets.btn_save.clicked.connect(self.buttonClick)

        # EXTRA LEFT BOX
        def openCloseLeftBox():
            UIFunctions.toggleLeftBox(self, True)
        widgets.toggleLeftBox.clicked.connect(openCloseLeftBox)
        widgets.extraCloseColumnBtn.clicked.connect(openCloseLeftBox)

        # EXTRA RIGHT BOX
        def openCloseRightBox():
            UIFunctions.toggleRightBox(self, True)
        widgets.settingsTopBtn.clicked.connect(openCloseRightBox)

        # SHOW APP
        # ///////////////////////////////////////////////////////////////
        self.show()

        # SET CUSTOM THEME
        # ///////////////////////////////////////////////////////////////
        themeFile = "ui/assets/themes/py_dracula_dark.qss"
        UIFunctions.theme(self, themeFile, True)
        # Initialize with our modified AppFunctions
        app_functions = AppFunctions()
        app_functions.setThemeHack(self)

        # SET HOME PAGE AND SELECT MENU
        # ///////////////////////////////////////////////////////////////
        widgets.stackedWidget.setCurrentWidget(widgets.home)
        widgets.btn_home.setStyleSheet(UIFunctions.selectMenu(widgets.btn_home.styleSheet()))

        logging.info("PyDraculaWindow initialized.")

    # BUTTONS CLICK
    # ///////////////////////////////////////////////////////////////
    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        # SHOW HOME PAGE - Monitor Page
        if btnName == "btn_home":
            widgets.stackedWidget.setCurrentWidget(widgets.home)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW WIDGETS PAGE - Remote Page
        if btnName == "btn_widgets":
            widgets.stackedWidget.setCurrentWidget(widgets.widgets)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW NEW PAGE - CAN Settings
        if btnName == "btn_new":
            widgets.stackedWidget.setCurrentWidget(widgets.new_page)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # PRINT BTN NAME
        print(f'Button "{btnName}" pressed!')

    def update_status_indicator(self, connected: bool):
        """Updates the status indicator based on the connection state."""
        # We'll use one of the existing UI elements for status indication
        # This can be customized based on actual UI elements available
        if connected:
            status_color = "background-color: #2ecc71; border-radius: 8px;"  # Green color
        else:
            status_color = "background-color: #e74c3c; border-radius: 8px;"  # Red color
            
        # Update a label in the UI to show connection status
        # This will need to be adjusted based on the actual UI elements
        if hasattr(widgets, "circularBg"):
            widgets.circularBg.setStyleSheet(status_color)

    def show_error(self, message: str):
        """Displays an error message to the user."""
        logging.error(message)
        QMessageBox.critical(self, "Error", message)

    def get_current_timestamp(self) -> str:
        """Returns the current timestamp as a string."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    # RESIZE EVENTS
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        # Update Size Grips
        UIFunctions.resize_grips(self)

    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPosition()  # PySide6 uses globalPosition() instead of globalPos()

    def closeEvent(self, event):
        """Clean up when the application is closed."""
        if self.can_controller.is_connected():
            self.can_controller.disconnect()
            logging.info("CAN interface disconnected on application close.")
        logging.info("Application closed.")
        event.accept()