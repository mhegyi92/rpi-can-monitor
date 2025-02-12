import sys
import argparse
import logging
from PyQt6.QtWidgets import QApplication, QStyleFactory
from main_window import MainWindow

# Import core modules for CLI mode
from core.can_interface import CANInterface
from core.filter_manager import FilterManager
from core.message_manager import MessageManager
from core.utils import parse_value
# Import remote classes from your controllers
from controllers.remote_controller import RemoteServer, RemoteClient
from PyQt6.QtCore import QCoreApplication

# Optional custom stylesheet for GUI mode
stylesheet = """
QFrame {
    border: none;
}
"""

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def run_cli(args):
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


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="CAN Monitor Tool (CLI + GUI)")
    parser.add_argument("--action", type=str,
                        help="Action to perform (e.g., add_filter, remove_filter, send_message, start_server, connect_client)")
    parser.add_argument("--details", type=str,
                        help="Details for the action (e.g., for filters: 'id=0x123;mask=0xFF 0x00 ...'; for remote: 'port=5000' or 'ip=192.168.1.100;port=5000')")
    parser.add_argument("--message", type=str,
                        help="Message to be sent (e.g., 'id=0x123;data=0x01 0x02')")
    parser.add_argument("--channel", type=str, help="CAN channel (CLI mode)", default="can0")
    parser.add_argument("--bitrate", type=str, help="CAN bitrate (CLI mode)", default="500000")
    args = parser.parse_args()

    if args.action:
        run_cli(args)
    else:
        app = QApplication(sys.argv)
        app.setStyle(QStyleFactory.create("Fusion"))
        app.setStyleSheet(stylesheet)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())


if __name__ == "__main__":
    main()
