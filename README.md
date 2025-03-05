# Raspberry Pi CAN Monitor

A versatile tool for monitoring, sending, and managing CAN (Controller Area Network) messages. This tool supports multiple UI frameworks (PyQt6 and PySide6) with both modern and classic interfaces, as well as a command-line interface (CLI) for headless operation. It includes remote operation modes so that a client (e.g., on a Windows machine) can control a server instance (e.g., running on a Raspberry Pi with a CAN interface).

## Features

- **Multiple UI Options:**
  - Modern UI based on PyDracula theme
  - Classic functional UI
  - Support for both PyQt6 and PySide6 frameworks

- **CAN Interface:**  
  Connect directly to a CAN interface (using socketCAN on Linux) to send and receive messages.
  
- **Filter Management:**  
  Add, update, remove, and clear CAN message filters.

- **Message Management:**  
  Define, send, and manage CAN messages.

- **Remote Operation:**  
  - **Server Mode:** Run on the CAN device to broadcast messages to connected clients
  - **Client Mode:** Connect remotely to monitor and control the CAN interface

- **Dual Mode:**  
  Use either the GUI for interactive use or the CLI for headless operation.

## Directory Structure

```
rpi-can-monitor/
├── app.py                     # Unified entry point for both CLI and GUI modes
├── core/                      # Core business logic
│   ├── can_interface.py       # Manages connection to the CAN interface
│   ├── filter_manager.py      # Manages CAN message filters
│   ├── message_manager.py     # Manages CAN messages
│   └── utils.py               # Utility functions (e.g., parse_value)
├── controllers/               # Controller logic
│   └── frameworks/            # Framework-specific controllers
│       ├── pyqt/              # PyQt6 controllers
│       │   ├── can_controller.py
│       │   ├── filter_controller.py
│       │   ├── message_controller.py
│       │   ├── monitor_controller.py
│       │   └── remote_controller.py
│       └── pyside/            # PySide6 controllers
│           ├── can_controller.py
│           ├── filter_controller.py
│           ├── message_controller.py
│           ├── monitor_controller.py
│           └── remote_controller.py
├── ui/                        # User interface components
│   ├── assets/                # UI assets (images, themes)
│   ├── designs/               # UI design files
│   │   ├── main_window.ui     # Classic UI design file
│   │   └── pydracula_main.ui  # PyDracula UI design file
│   └── frameworks/            # Framework-specific UI implementations
│       ├── pyqt/              # PyQt6 UI implementations
│       │   ├── main_window.py # Classic UI main window
│       │   └── pydracula_window.py # Modern UI main window
│       └── pyside/            # PySide6 UI implementations
│           └── pydracula_window.py # Modern UI main window
└── README.md                  # This file
```

## Requirements

- **Python 3.x**
- **PyQt6**: For the classic UI and PyQt-based modern UI
- **PySide6**: For the PySide-based modern UI (optional)
- **python-can**: For CAN bus communication

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/rpi-can-monitor.git
    cd rpi-can-monitor
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

## Usage

### GUI Mode

The application now supports multiple UI options:

```bash
# Default launch (modern UI with auto-detected framework)
python app.py

# Launch with specific UI options
python app.py --ui pyqt --modern    # Modern PyQt6 UI
python app.py --ui pyqt --classic   # Classic PyQt6 UI
python app.py --ui pyside --modern  # Modern PySide6 UI

# Legacy options for backward compatibility
python app.py --pydracula           # Same as --modern
```

The graphical interface allows you to:
- **Connect** to the CAN interface (enter the channel and bitrate)
- **Manage Filters** (add, remove, or clear filters)
- **Manage Messages** (define and send CAN messages)
- **Monitor** CAN messages in real time
- Use the **Remote Tab** to switch between Local, Server, and Client modes

### CLI Mode

You can run the application in CLI mode by providing an action:

```bash
python app.py --cli --action add_filter --details "id=0x123;mask=0xFF 0x00 0x00 0x00 0x00 0x00 0x00 0x00" --channel can0 --bitrate 500000
```

#### Available CLI Actions:

- **Add a filter:**
  ```bash
  python app.py --cli --action add_filter --details "id=0x123;mask=0xFF 0x00 0x00 0x00 0x00 0x00 0x00 0x00" --channel can0
  ```

- **Remove a filter:**
  ```bash
  python app.py --cli --action remove_filter --details "id=0x123;mask=0xFF 0x00 0x00 0x00 0x00 0x00 0x00 0x00" --channel can0
  ```

- **Send a message:**
  ```bash
  python app.py --cli --action send_message --message "id=0x123;data=0x01 0x02 0x03" --channel can0
  ```

- **Start a Remote Server:**
  ```bash
  python app.py --cli --action start_server --details "port=5000" --channel can0
  ```

- **Connect as a Remote Client:**
  ```bash
  python app.py --cli --action connect_client --details "ip=192.168.1.100;port=5000"
  ```

## Remote Operation Overview

- **Local Mode:**  
  The application interacts directly with the CAN interface.

- **Server Mode:**  
  The application runs as a server on the CAN device, broadcasting incoming CAN messages to all connected remote clients and accepting remote commands (such as sending messages).

- **Client Mode:**  
  The application connects to a server and displays the broadcast messages. It can also send remote commands to control the server.

## UI Framework Information

### PyQt6 vs PySide6

This project supports both PyQt6 and PySide6 UI frameworks:

- **PyQt6**: The original framework used for the classic UI
- **PySide6**: Added to support the PyDracula modern UI (which was built for PySide6)

Both frameworks provide Python bindings for Qt6, but have different licensing models:
- PyQt6: GPL or commercial license
- PySide6: LGPL license

### UI Design Approach

The project uses a flexible architecture:

1. **Core Logic**: Framework-agnostic code in the `core/` directory
2. **Controllers**: Framework-specific controllers in `controllers/pyqt/` and `controllers/pyside/`
3. **UI Implementations**: Different UI versions in `ui/pyqt/` and `ui/pyside/`

This allows us to:
- Support multiple UI frameworks
- Provide both modern and classic interfaces
- Maintain separation of concerns

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/YourFeature`
3. Make your changes and commit them: `git commit -am 'Add new feature'`
4. Push your changes: `git push origin feature/YourFeature`
5. Open a Pull Request describing your changes

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
