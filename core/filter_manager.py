import logging


class FilterManager:
    """
    Manages CAN message filters, allowing addition, removal, and validation.
    """

    def __init__(self):
        self.filters = []  # Stores filters as dictionaries: {'id': int, 'mask': list[int]}

    def add_filter(self, filter_id, mask):
        """
        Adds a filter to the list.

        Args:
            filter_id (str): The filter ID in hex format.
            mask (str): The mask in hex format.

        Returns:
            bool: True if successfully added, False if invalid or duplicate.
        """
        try:
            # Normalize the input to ensure consistency
            parsed_id = int(filter_id, 16)
            parsed_mask = [int(byte, 16) for byte in mask.split()]

            # Check for duplicates
            for f in self.filters:
                if f['id'] == parsed_id and f['mask'] == parsed_mask:
                    logging.warning(f"Duplicate filter detected: {f}")
                    return False  # Duplicate filter

            # Add the filter
            self.filters.append({'id': parsed_id, 'mask': parsed_mask})
            logging.info(f"Filter added: ID={parsed_id}, Mask={parsed_mask}")
            return True
        except ValueError as e:
            logging.error(f"Error parsing filter: {e}")
            return False

    def remove_filter(self, filter_id, mask):
        """
        Removes a filter from the list.

        Args:
            filter_id (str): The filter ID in hex, binary, or decimal format.
            mask (list[int]): The mask as a list of integers.

        Returns:
            bool: True if successfully removed, False otherwise.
        """
        try:
            parsed_id = int(filter_id, 16)

            for f in self.filters:
                if f['id'] == parsed_id and f['mask'] == mask:
                    self.filters.remove(f)
                    logging.info(f"Filter removed: ID={parsed_id}, Mask={mask}")
                    return True

            logging.warning(f"Filter not found: ID={parsed_id}, Mask={mask}")
            return False
        except ValueError as e:
            logging.error(f"Error removing filter: {e}")
            return False

    def update_filter(self, filter_id, mask):
        """
        Updates a filter with a new mask.

        Args:
            filter_id (int): The filter ID.
            mask (list[int]): The new mask.
        """
        for f in self.filters:
            if f['id'] == filter_id:
                f['mask'] = mask
                logging.info(f"Filter updated: ID={filter_id}, Mask={mask}")
                return
        logging.warning(f"Filter ID {filter_id} not found. Adding as new.")
        self.add_filter(hex(filter_id), " ".join(hex(b) for b in mask))

    def get_filters(self):
        """Returns the list of filters."""
        return self.filters

    def clear_filters(self):
        """Clears all filters."""
        self.filters.clear()
        logging.info("All filters cleared.")
