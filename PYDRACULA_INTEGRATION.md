# PyDracula UI Integration for CAN Monitor

This project integrates the modern PyDracula UI framework with the existing CAN Monitor tool.

## Latest Development Status (Updated)

### Initial Assessment and Strategy
- **Task**: Integrate PyDracula's modern UI with the existing CAN monitoring tool
- **Approaches**:
  1. Complete UI replacement (chosen approach)
  2. Hybrid approach
  3. Component integration

### Implementation Steps Taken
1. **Directory Organization**:
   - Restructured project into framework-specific directories:
     - `controllers/frameworks/{pyqt,pyside}/`
     - `ui/frameworks/{pyqt,pyside}/`
   - Created `ui/assets/` for shared resources
   - Added `ui/designs/` for UI definition files

2. **Controller Adaptation**:
   - Adapted PyQt controllers to maintain original functionality
   - Created PySide controllers for PyDracula compatibility

3. **UI Components**:
   - Created modern UI implementations for both frameworks
   - Maintained the classic UI for backward compatibility

4. **Entry Point**:
   - `app.py`: Unified entry point with comprehensive UI selection options and CLI support

5. **Documentation**:
   - Updated README with new structure and usage instructions
   - Added setup.py for package management
   - Enhanced .gitignore for better project maintenance

### Current Status
- **Working Components**:
  - Classic PyQt UI (`python app.py --ui pyqt --classic`)
  - Path structure and controller organization
  - Framework-specific implementation architecture

- **Pending Fixes**:
  - PyDracula UI integration has interdependency issues
  - PySide implementation needs additional work

### Next Steps
1. **Fix PyDracula Integration**:
   - Resolve module import issues in ui_functions.py
   - Update path references to match the new structure
   - Adapt PyDracula components to work with the CAN monitoring tool

2. **Implement UI Features**:
   - Add CAN monitoring tables to PyDracula UI
   - Connect filter management UI to existing controllers
   - Implement message handling in the new UI

3. **UI Design Customization**:
   - Customize PyDracula for CAN monitor requirements
   - Ensure theme consistency across components

## Overview

The CAN Monitor tool now offers two UI options:
1. The original PyQt6-based UI (default)
2. The modern PyDracula UI based on PySide6

## How to Use

First, make sure to install PySide6:

```bash
pip install pyside6
```

To use the PyDracula UI, run:

```bash
python app.py --modern
# or use legacy option
python app.py --pydracula
```

To use the original UI, run:

```bash
python app.py --classic
# or for default UI
python app.py
```

Note: If there are PySide6 compatibility issues with your system, the application will automatically fall back to the original PyQt6 UI.

## Implementation Details

### UI Framework

The PyDracula UI is based on PySide6, while the original UI uses PyQt6. This required creating separate controller implementations for each UI framework.

### Directory Structure

- `ui/pydracula/` - Contains the PyDracula UI files
- `controllers/` - Original PyQt6 controllers
- `controllers/pyside_*.py` - PySide6 versions of controllers for PyDracula UI

### Integration Approach

1. **Framework Compatibility**: The PyDracula UI is kept with its original PySide6 framework
2. **Controller Adaptation**: Separate PySide6 versions of controllers were created
3. **UI Adjustment**: The PyDracula UI components were customized for CAN Monitor functionality
4. **Widget Mapping**: Controllers reference PyDracula widget names

## Customization

To further customize the PyDracula UI:

1. Edit the `ui/pydracula/main.ui` file using Qt Designer
2. Update widget names in the controller classes to match your UI design
3. Add additional functionality by extending the controller classes

## Theme Configuration

The PyDracula UI supports two themes:
- Dark theme (default): `ui/pydracula/themes/py_dracula_dark.qss`
- Light theme: `ui/pydracula/themes/py_dracula_light.qss`

To change the theme, modify the `themeFile` variable in `pydracula_window.py`.

## Previous Status

This integration is a work in progress. The following components are functional:

- [x] Basic PyDracula UI structure
- [x] Controller architecture for PySide6
- [x] Menu navigation
- [x] Dark/light theme support
- [x] PyQt6 fallback UI for environments with PySide6 compatibility issues
- [x] Basic CAN connection UI (PyQt fallback)
- [x] Basic CAN monitor UI (PyQt fallback)
- [x] Basic filter management UI (PyQt fallback)
- [ ] Complete PySide6 UI design customization
- [ ] Complete remote functionality UI

## Original Next Steps

1. Complete the UI design for all CAN Monitor functionality
2. Update widget references in controller classes to match final UI design
3. Implement missing functionality
4. Add theme toggle in settings
5. Add configuration saving/loading