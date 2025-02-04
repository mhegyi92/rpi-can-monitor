# filter_controller.py
import logging
from PyQt6.QtWidgets import QTableWidgetItem, QLineEdit, QPushButton, QTableWidget
from core.filter_manager import FilterManager
from core.utils import parse_value

class FilterController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.filter_manager = FilterManager()
        self.init_widgets()
        self.setup_table()

    def init_widgets(self):
        """Initialize filter-related widgets and connect signals."""
        self.filters_table: QTableWidget = self.main_window.findChild(QTableWidget, "tableFilters")
        self.filter_id_input: QLineEdit = self.main_window.findChild(QLineEdit, "inputFilterId")
        self.filter_byte_inputs = [self.main_window.findChild(QLineEdit, f"inputFilterByte{i}") for i in range(8)]
        self.add_filter_button: QPushButton = self.main_window.findChild(QPushButton, "buttonAddFilter")
        self.remove_filter_button: QPushButton = self.main_window.findChild(QPushButton, "buttonRemoveFilter")
        self.clear_filters_button: QPushButton = self.main_window.findChild(QPushButton, "buttonClearFilters")

        # Connect filter buttons to handlers
        self.add_filter_button.clicked.connect(self.handle_add_filter)
        self.remove_filter_button.clicked.connect(self.handle_remove_filter)
        self.clear_filters_button.clicked.connect(self.handle_clear_filters)
        self.filters_table.itemChanged.connect(self.handle_edit_filter)

    def setup_table(self):
        """Set up the filters table for in-place editing."""
        self.filters_table.setColumnCount(9)  # One for ID and eight for data bytes
        self.filters_table.setHorizontalHeaderLabels(["Filter ID"] + [f"Byte {i}" for i in range(8)])
        self.filters_table.setEditTriggers(self.filters_table.EditTrigger.AllEditTriggers)

    def update_filters_table(self):
        """Updates the filters table with the latest filters."""
        self.filters_table.blockSignals(True)
        self.filters_table.setRowCount(0)
        filters = self.filter_manager.get_filters()

        for row_index, f in enumerate(filters):
            self.filters_table.insertRow(row_index)
            self.filters_table.setItem(row_index, 0, QTableWidgetItem(hex(f['id'])))
            for col_index, byte_value in enumerate(f['mask']):
                self.filters_table.setItem(row_index, col_index + 1, QTableWidgetItem(hex(byte_value)))

        self.filters_table.blockSignals(False)
        logging.info("Filters table updated.")

    def handle_add_filter(self):
        """Handles adding a new filter."""
        filter_id = self.filter_id_input.text().strip()
        filter_bytes = [input_field.text().strip() for input_field in self.filter_byte_inputs]

        if not filter_id:
            self.main_window.show_error("Filter ID is required.")
            return

        try:
            parsed_id = parse_value(filter_id)
            if not (0 <= parsed_id <= 0x7FF):
                raise ValueError(f"Invalid Filter ID: {parsed_id}")
            # Parse each byte; empty fields become 0
            parsed_bytes = []
            for i, byte in enumerate(filter_bytes):
                if byte:
                    parsed_byte = parse_value(byte)
                    if not (0 <= parsed_byte <= 255):
                        raise ValueError(f"Invalid Byte {i}: {parsed_byte}")
                    parsed_bytes.append(parsed_byte)
                else:
                    parsed_bytes.append(0)

            mask = " ".join(hex(b) for b in parsed_bytes)
            if self.filter_manager.add_filter(hex(parsed_id), mask):
                logging.info("Filter added successfully.")
                self.update_filters_table()
                self.filter_id_input.clear()
                for input_field in self.filter_byte_inputs:
                    input_field.clear()
            else:
                self.main_window.show_error("Duplicate filter detected.")
        except ValueError as e:
            self.main_window.show_error(str(e))

    def handle_remove_filter(self):
        """Handles removing selected filters."""
        selected_rows = sorted({index.row() for index in self.filters_table.selectedIndexes()}, reverse=True)
        if not selected_rows:
            self.main_window.show_error("Please select one or more filters to remove.")
            return

        removed_successfully = True
        for row in selected_rows:
            filter_id = self.filters_table.item(row, 0).text()
            mask = [parse_value(self.filters_table.item(row, col).text()) for col in range(1, 9)]
            if not self.filter_manager.remove_filter(filter_id, mask):
                logging.warning(f"Failed to remove filter: ID={filter_id}, Mask={mask}")
                removed_successfully = False

        if removed_successfully:
            self.update_filters_table()
        else:
            self.main_window.show_error("Failed to remove one or more filters.")

    def handle_clear_filters(self):
        """Clears all filters."""
        self.filter_manager.clear_filters()
        self.update_filters_table()

    def handle_edit_filter(self, item):
        """Handles editing a filter directly in the table.
        (For brevity, detailed editing logic is omitted. You can refactor the code here similar to the add/remove routines.)
        """
        # You would retrieve the row, re-parse the updated values,
        # remove the old filter, and add the new filter.
        pass
