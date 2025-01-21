import sys
import argparse
import logging
from PyQt6.QtWidgets import QApplication, QStyleFactory
from gui.main_window import MainWindow

# Optional custom stylesheet
stylesheet = """
QFrame {
    border: none;
}
"""

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def run_cli(args):
    """Handles CLI actions."""
    try:
        if args.action == "add_filter":
            logging.info(f"CLI: Adding a filter with details: {args.details}")
        elif args.action == "remove_filter":
            logging.info("CLI: Removing a filter")
        elif args.action == "send_message":
            logging.info(f"CLI: Sending message: {args.message}")
        else:
            logging.error("CLI: Invalid action specified.")
            sys.exit(1)
    except Exception as e:
        logging.error(f"Error in CLI mode: {e}")


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="CAN Monitor Tool (CLI + GUI)")
    parser.add_argument("--action", type=str, help="Action to perform (e.g., add_filter, remove_filter, send_message)")
    parser.add_argument("--details", type=str, help="Details for the action (e.g., CAN ID or filter data)")
    parser.add_argument("--message", type=str, help="Message to be sent")
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
