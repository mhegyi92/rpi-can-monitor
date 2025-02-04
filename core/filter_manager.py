import logging
from core.utils import parse_value

class FilterManager:
    """
    Manages CAN message filters, allowing addition, removal, and validation.
    All numeric inputs are accepted as strings (hex, binary, or decimal).
    """

    def __init__(self):
        # Each filter is stored as a dictionary: {'id': int, 'mask': list[int]}
        self.filters = []

    def add_filter(self, filter_id: str, mask: str) -> bool:
        """
        Adds a filter to the list.

        Args:
            filter_id (str): The filter ID in hex, binary, or decimal format.
            mask (str): The mask bytes as a space-separated string (e.g., "0xFF 0x0F").

        Returns:
            bool: True if successfully added, False if invalid or duplicate.
        """
        try:
            parsed_id = parse_value(filter_id)
            parsed_mask = [parse_value(byte) for byte in mask.split()]

            # Check for duplicates
            for f in self.filters:
                if f['id'] == parsed_id and f['mask'] == parsed_mask:
                    logging.warning(f"Duplicate filter detected: {f}")
                    return False  # Duplicate filter

            self.filters.append({'id': parsed_id, 'mask': parsed_mask})
            logging.info(f"Filter added: ID={parsed_id}, Mask={parsed_mask}")
            return True
        except ValueError as e:
            logging.error(f"Error parsing filter: {e}")
            return False

    def remove_filter(self, filter_id: str, mask: str) -> bool:
        """
        Removes a filter from the list.

        Args:
            filter_id (str): The filter ID in hex, binary, or decimal format.
            mask (str): The mask as a space-separated string.

        Returns:
            bool: True if successfully removed, False otherwise.
        """
        try:
            parsed_id = parse_value(filter_id)
            parsed_mask = [parse_value(byte) for byte in mask.split()]

            for f in self.filters:
                if f['id'] == parsed_id and f['mask'] == parsed_mask:
                    self.filters.remove(f)
                    logging.info(f"Filter removed: ID={parsed_id}, Mask={parsed_mask}")
                    return True

            logging.warning(f"Filter not found: ID={parsed_id}, Mask={parsed_mask}")
            return False
        except ValueError as e:
            logging.error(f"Error removing filter: {e}")
            return False

    def update_filter(self, filter_id: str, mask: str) -> None:
        """
        Updates a filter with a new mask.

        Args:
            filter_id (str): The filter ID in hex, binary, or decimal format.
            mask (str): The new mask as a space-separated string.
        """
        try:
            parsed_id = parse_value(filter_id)
            parsed_mask = [parse_value(byte) for byte in mask.split()]
            
            for f in self.filters:
                if f['id'] == parsed_id:
                    f['mask'] = parsed_mask
                    logging.info(f"Filter updated: ID={parsed_id}, Mask={parsed_mask}")
                    return
            logging.warning(f"Filter ID {parsed_id} not found. Adding as new.")
            self.add_filter(filter_id, mask)
        except ValueError as e:
            logging.error(f"Error updating filter: {e}")

    def get_filters(self):
        """Returns the list of filters."""
        return self.filters

    def clear_filters(self):
        """Clears all filters."""
        self.filters.clear()
        logging.info("All filters cleared.")
