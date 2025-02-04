# CAN Monitor Tool

A Python-based application for monitoring, sending, and managing CAN (Controller Area Network) messages. The tool supports both a graphical user interface (GUI) (using PyQt6) and a command-line interface (CLI) for headless operation. It also includes remote operation modes so that a client (e.g., on a Windows machine) can control a server instance (e.g., running on a Raspberry Pi with a CAN interface).

## Features

- **Local Mode:**  
  Connect directly to a CAN interface (using socketCAN on Linux) to send and receive messages.
  
- **Filter Management:**  
  Add, update, remove, and clear CAN message filters.

- **Message Management:**  
  Define, send, and manage CAN messages.

- **Remote Operation:**  
  - **Server Mode:**  
    Run the application as a server on the CAN device (e.g., Raspberry Pi) that broadcasts CAN messages to connected clients and accepts remote commands.
  - **Client Mode:**  
    Connect from a remote machine to the server to monitor and control the CAN interface as if running locally.

- **Dual Mode:**  
  Use either the GUI for interactive use or the CLI for headless operation.

## Directory Structure

```
CAN_Monitor_Tool/
├── core/
│   ├── __init__.py
│   ├── can_interface.py       # Manages connection to the CAN interface
│   ├── filter_manager.py      # Manages CAN message filters
│   ├── message_manager.py     # Manages CAN messages
│   └── utils.py               # Utility functions (e.g., parse_value)
├── controllers/
│   ├── __init__.py
│   ├── can_controller.py      # Handles CAN interface logic and UI integration
│   ├── filter_controller.py   # Handles filter management UI and logic
│   ├── message_controller.py  # Handles message management UI and logic
│   ├── monitor_controller.py  # Updates the monitor table with CAN messages
│   └── remote_controller.py   # Implements remote server/client functionality
├── ui/
│   └── main_window.ui         # UI file created with Qt Designer
├── main_window.py             # Main application window tying all controllers together
├── main.py                    # Application entry point (CLI and GUI modes)
└── README.md                  # This file
```

## Requirements

- **Python 3.x**
- **PyQt6**
- **python-can**

You can install the required Python packages using pip:

```bash
pip install PyQt6 python-can
```

(Alternatively, if you have a `requirements.txt` file, run `pip install -r requirements.txt`.)

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/CAN_Monitor_Tool.git
    cd CAN_Monitor_Tool
    ```

2. **Create and activate a virtual environment:**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

    If no `requirements.txt` is provided, simply install the required packages as mentioned above.

## Usage

### GUI Mode

Run the application without any CLI arguments:

```bash
python main.py
```

This launches the graphical interface where you can:
- **Connect** to the CAN interface (enter the channel and bitrate).
- **Manage Filters** (add, remove, or clear filters).
- **Manage Messages** (define and send CAN messages).
- **Monitor** CAN messages in real time.
- Use the **Remote Tab** to switch between Local, Server, and Client modes.

### CLI Mode

You can also run the application in CLI mode by providing an action:

#### Local Actions

- **Add a filter:**

    ```bash
    python main.py --action add_filter --details "id=0x123;mask=0xFF 0x00 0x00 0x00 0x00 0x00 0x00 0x00" --channel can0 --bitrate 500000
    ```

- **Remove a filter:**

    ```bash
    python main.py --action remove_filter --details "id=0x123;mask=0xFF 0x00 0x00 0x00 0x00 0x00 0x00 0x00" --channel can0 --bitrate 500000
    ```

- **Send a message:**

    ```bash
    python main.py --action send_message --message "id=0x123;data=0x01 0x02 0x03" --channel can0 --bitrate 500000
    ```

#### Remote Operations

- **Start a Remote Server:**

    This will run the application in server mode, connecting to the CAN interface and listening for remote client connections.

    ```bash
    python main.py --action start_server --details "port=5000" --channel can0 --bitrate 500000
    ```

    The server will run until interrupted (Ctrl+C).

- **Connect as a Remote Client:**

    Connect to a remote server (e.g., on your Raspberry Pi) from a client machine.

    ```bash
    python main.py --action connect_client --details "ip=192.168.1.100;port=5000"
    ```

    This mode will start a minimal event loop and print received remote messages to the console.

## Remote Operation Overview

- **Local Mode:**  
  The application interacts directly with the CAN interface.

- **Server Mode:**  
  The application runs as a server on the CAN device, broadcasting incoming CAN messages to all connected remote clients and accepting remote commands (such as sending messages).

- **Client Mode:**  
  The application connects to a server and displays the broadcast messages. It can also send remote commands to control the server.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch:  
   ```bash
   git checkout -b feature/YourFeature
   ```
3. Make your changes and commit them:  
   ```bash
   git commit -am 'Add new feature'
   ```
4. Push your changes:  
   ```bash
   git push origin feature/YourFeature
   ```
5. Open a Pull Request describing your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or issues, please open an issue in the repository or email [your-email@example.com](mailto:your-email@example.com).
