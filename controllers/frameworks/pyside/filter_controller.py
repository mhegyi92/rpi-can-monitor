import logging
from PySide6.QtWidgets import QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
from core.filter_manager import FilterManager

class PySideFilterController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.filter_manager = FilterManager()
        self.init_widgets()

    def init_widgets(self):
        """Initialize filter-related widgets and connect signals."""
        # In the PyDracula UI, we need to adapt to use appropriate widget names
        # For demo purposes, we use placeholders that will need to be updated
        self.filter_id_input = self.main_window.findChild(QLineEdit, "lineEdit_filterId")  # Replace with actual name
        self.filter_mask_input = self.main_window.findChild(QLineEdit, "lineEdit_filterMask")  # Replace with actual name
        self.add_filter_button = self.main_window.findChild(QPushButton, "pushButton_addFilter")  # Replace with actual name
        self.remove_filter_button = self.main_window.findChild(QPushButton, "pushButton_removeFilter")  # Replace with actual name
        self.filter_table = self.main_window.findChild(QTableWidget, "tableWidget_filters")  # Replace with actual name

        # Connect signals if widgets exist
        if self.add_filter_button:
            self.add_filter_button.clicked.connect(self.handle_add_filter)
        if self.remove_filter_button:
            self.remove_filter_button.clicked.connect(self.handle_remove_filter)

    def handle_add_filter(self):
        """Handles adding a new filter."""
        if not self.filter_id_input or not self.filter_mask_input:
            self.main_window.show_error("Filter input fields not found in UI.")
            return
            
        filter_id = self.filter_id_input.text().strip()
        filter_mask = self.filter_mask_input.text().strip()
        
        if not filter_id or not filter_mask:
            self.main_window.show_error("Filter ID and mask are required.")
            return
        
        # Add the filter
        if self.filter_manager.add_filter(filter_id, filter_mask):
            logging.info(f"Added filter with ID {filter_id} and mask {filter_mask}.")
            self.update_filter_table()
            # Clear input fields
            self.filter_id_input.clear()
            self.filter_mask_input.clear()
        else:
            self.main_window.show_error("Failed to add filter (invalid format or duplicate).")

    def handle_remove_filter(self):
        """Handles removing a selected filter."""
        if not self.filter_table:
            self.main_window.show_error("Filter table not found in UI.")
            return
            
        selected_rows = self.filter_table.selectedIndexes()
        if not selected_rows:
            self.main_window.show_error("Please select a filter to remove.")
            return
        
        row = selected_rows[0].row()
        filter_id = self.filter_table.item(row, 0).text()
        filter_mask = self.filter_table.item(row, 1).text()
        
        # Convert string mask to list
        mask_parts = filter_mask.split()
        
        if self.filter_manager.remove_filter(filter_id, mask_parts):
            logging.info(f"Removed filter with ID {filter_id} and mask {filter_mask}.")
            self.update_filter_table()
        else:
            self.main_window.show_error("Failed to remove filter.")

    def update_filter_table(self):
        """Updates the filter table with current filters."""
        if not self.filter_table:
            logging.error("Filter table not found in UI.")
            return
            
        # Clear the table
        self.filter_table.setRowCount(0)
        
        # Add each filter
        for i, filter_data in enumerate(self.filter_manager.get_filters()):
            self.filter_table.insertRow(i)
            
            # Set filter ID
            id_item = QTableWidgetItem(filter_data["id"])
            self.filter_table.setItem(i, 0, id_item)
            
            # Set filter mask
            mask_str = " ".join(filter_data["mask"])
            mask_item = QTableWidgetItem(mask_str)
            self.filter_table.setItem(i, 1, mask_item)