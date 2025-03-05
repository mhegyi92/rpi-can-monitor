#!/usr/bin/env python3
"""
RPI CAN Monitor - Main Entry Point
A tool for monitoring CAN bus communications with different UI options.
This is the unified entry point for both CLI and GUI modes.
"""

import sys
import logging
import argparse
from typing import Optional

def setup_logging(level: int = logging.INFO) -> None:
    """Set up logging for the application."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.getLogger('can').setLevel(logging.WARNING)

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="CAN Monitor Tool with multiple UI options")
    
    # UI selection arguments
    ui_group = parser.add_argument_group('UI Selection')
    ui_group.add_argument('--ui', choices=['pyqt', 'pyside', 'auto'], default='auto',
                         help='UI framework to use (default: auto)')
    ui_group.add_argument('--modern', action='store_true',
                         help='Use modern UI (PyDracula based)')
    ui_group.add_argument('--classic', action='store_true',
                         help='Use classic UI')
    # Legacy compatibility - map --pydracula to --modern
    ui_group.add_argument('--pydracula', action='store_true', dest='modern',
                         help='Use modern UI (alias for --modern, for backward compatibility)')
    
    # CLI mode arguments
    cli_group = parser.add_argument_group('CLI Mode')
    cli_group.add_argument('--cli', action='store_true',
                         help='Run in CLI mode (no GUI)')
    cli_group.add_argument('--action', type=str,
                        help='CLI action (add_filter, remove_filter, send_message, etc.)')
    cli_group.add_argument('--details', type=str,
                        help='Details for CLI action')
    cli_group.add_argument('--message', type=str,
                        help='Message to send (for send_message action)')
    cli_group.add_argument('--channel', type=str, default='can0',
                        help='CAN channel to use (default: can0)')
    cli_group.add_argument('--bitrate', type=str, default='500000',
                        help='CAN bitrate (default: 500000)')
    
    # Debug options
    debug_group = parser.add_argument_group('Debug Options')
    debug_group.add_argument('--debug', action='store_true',
                           help='Enable debug logging')
    
    return parser.parse_args()

def run_cli_mode(args: argparse.Namespace) -> None:
    """Run the application in CLI mode."""
    # Import core modules for CLI mode
    from core.can_interface import CANInterface
    from core.filter_manager import FilterManager
    from core.message_manager import MessageManager
    from core.utils import parse_value
    # Import remote classes from controllers
    from controllers.frameworks.pyqt.remote_controller import RemoteServer, RemoteClient
    from PyQt6.QtCore import QCoreApplication
    
    """Handles CLI actions."""
    # Local actions: add_filter, remove_filter, send_message
    if args.action in ["add_filter", "remove_filter", "send_message"]:
        # Instantiate and connect the CAN interface using CLI options
        can_interface = CANInterface()
        channel = args.channel if args.channel else "can0"
        try:
            bitrate = int(args.bitrate) if args.bitrate else 500000
        except ValueError:
            logging.error("Invalid bitrate specified.")
            sys.exit(1)
        if not can_interface.connect(channel, bitrate):
            logging.error("Failed to connect to CAN interface.")
            sys.exit(1)
        # Instantiate managers for filters and messages
        filter_manager = FilterManager()
        message_manager = MessageManager()

        if args.action == "add_filter":
            try:
                details_dict = {}
                for part in args.details.split(";"):
                    key, value = part.split("=")
                    details_dict[key.strip()] = value.strip()
                filter_id = details_dict["id"]
                mask = details_dict["mask"]
                if filter_manager.add_filter(filter_id, mask):
                    logging.info("Filter added successfully via CLI.")
                else:
                    logging.error("Failed to add filter (duplicate or invalid).")
            except Exception as e:
                logging.error(f"Error parsing details for add_filter: {e}")

        elif args.action == "remove_filter":
            try:
                details_dict = {}
                for part in args.details.split(";"):
                    key, value = part.split("=")
                    details_dict[key.strip()] = value.strip()
                filter_id = details_dict["id"]
                mask_str = details_dict["mask"]
                # Convert the mask string to a list of integers
                mask_list = [parse_value(b) for b in mask_str.split()]
                if filter_manager.remove_filter(filter_id, mask_list):
                    logging.info("Filter removed successfully via CLI.")
                else:
                    logging.error("Failed to remove filter.")
            except Exception as e:
                logging.error(f"Error parsing details for remove_filter: {e}")

        elif args.action == "send_message":
            try:
                msg_dict = {}
                for part in args.message.split(";"):
                    key, value = part.split("=")
                    msg_dict[key.strip()] = value.strip()
                message_id = msg_dict["id"]
                data_str = msg_dict["data"]
                if message_manager.add_message("cli", message_id, data_str):
                    # Get the newly added message and send it
                    msg = message_manager.get_messages()[-1]
                    can_interface.send_message(msg["id"], msg["data"])
                    logging.info(f"Message sent: ID={message_id}, Data={data_str}")
                else:
                    logging.error("Failed to add/send message (duplicate or invalid).")
            except Exception as e:
                logging.error(f"Error parsing message for send_message: {e}")

        can_interface.disconnect()

    # Remote server mode: start a server that listens for client commands and broadcasts CAN messages
    elif args.action == "start_server":
        try:
            details_dict = {}
            for part in args.details.split(";"):
                key, value = part.split("=")
                details_dict[key.strip()] = value.strip()
            port = int(details_dict.get("port", 5000))
            can_interface = CANInterface()
            channel = args.channel if args.channel else "can0"
            try:
                bitrate = int(args.bitrate) if args.bitrate else 500000
            except ValueError:
                logging.error("Invalid bitrate specified.")
                sys.exit(1)
            if not can_interface.connect(channel, bitrate):
                logging.error("Failed to connect to CAN interface.")
                sys.exit(1)
            server = RemoteServer(port, can_interface)
            server.start()
            logging.info("Remote server started. Press Ctrl+C to stop.")
            try:
                # In a real implementation you would integrate CAN message polling and broadcasting here.
                # For now, simply sleep until interrupted.
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logging.info("Shutting down server...")
            server.stop()
            can_interface.disconnect()
        except Exception as e:
            logging.error(f"Error starting server: {e}")

    # Remote client mode: connect to a remote server and print received messages
    elif args.action == "connect_client":
        try:
            details_dict = {}
            for part in args.details.split(";"):
                key, value = part.split("=")
                details_dict[key.strip()] = value.strip()
            ip = details_dict.get("ip")
            port = int(details_dict.get("port", 5000))
            # QCoreApplication is used here for a minimal event loop to run QThread-based RemoteClient
            app = QCoreApplication([])
            client = RemoteClient(ip, port)

            def print_message(msg):
                print("Received remote message:", msg)

            client.message_received.connect(print_message)
            client.start()
            logging.info("Remote client connected. Press Ctrl+C to exit.")
            app.exec()
        except Exception as e:
            logging.error(f"Error connecting as client: {e}")
    else:
        logging.error("CLI: Invalid action specified.")
        sys.exit(1)

def run_gui_mode(args: argparse.Namespace) -> None:
    """Run the application in GUI mode."""
    # Fix for high DPI displays
    import os
    os.environ["QT_FONT_DPI"] = "96"
    
    # Determine which UI to use based on arguments and availability
    ui_framework = args.ui
    use_modern = args.modern
    
    # If neither modern nor classic is specified, default to modern
    if not args.modern and not args.classic:
        use_modern = True
    
    # Auto-detect UI framework if needed
    if ui_framework == 'auto':
        try:
            import PySide6
            ui_framework = 'pyside'
        except ImportError:
            ui_framework = 'pyqt'
    
    # Import the appropriate UI modules and start the application
    if ui_framework == 'pyside':
        try:
            from PySide6.QtWidgets import QApplication
            from PySide6.QtGui import QIcon
            
            app = QApplication(sys.argv)
            app.setWindowIcon(QIcon("ui/assets/images/images/PyDracula.png"))
            
            if use_modern:
                from ui.frameworks.pyside.pydracula_window import PyDraculaWindow
                window = PyDraculaWindow()
            else:
                # We don't have a classic PySide UI yet
                logging.warning("Classic UI not available for PySide6, using PyQt6")
                raise ImportError("No classic PySide UI")
                
        except ImportError as e:
            logging.warning(f"Error loading PySide6: {e}")
            logging.warning("Falling back to PyQt6...")
            ui_framework = 'pyqt'
    
    if ui_framework == 'pyqt':
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QIcon
        
        app = QApplication(sys.argv)
        
        if use_modern:
            app.setWindowIcon(QIcon("ui/assets/images/images/PyDracula.png"))
            from ui.frameworks.pyqt.pydracula_window import PyQtPyDraculaWindow
            window = PyQtPyDraculaWindow()
        else:
            from PyQt6.QtWidgets import QStyleFactory
            app.setStyle(QStyleFactory.create("Fusion"))
            
            # Apply basic stylesheet
            stylesheet = """
            QFrame {
                border: none;
            }
            """
            app.setStyleSheet(stylesheet)
            
            from ui.frameworks.pyqt.main_window import MainWindow
            window = MainWindow()
    
    window.show()
    sys.exit(app.exec())

def main() -> None:
    """Main entry point for the application."""
    args = parse_arguments()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(log_level)
    
    # Run in CLI or GUI mode
    if args.cli or args.action:
        run_cli_mode(args)
    else:
        run_gui_mode(args)

if __name__ == "__main__":
    main()