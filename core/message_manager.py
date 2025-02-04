import logging
from core.utils import parse_value

class MessageManager:
    """
    Manages CAN messages, allowing addition, removal, and validation with names.
    All numeric inputs are accepted as strings (hex, binary, or decimal).
    """

    def __init__(self):
        # Each message is stored as a dictionary: {'id': int, 'data': list[int], 'name': str}
        self.messages = []

    def add_message(self, name: str, message_id: str, data: str) -> bool:
        """
        Adds a message to the list.

        Args:
            name (str): The name of the message.
            message_id (str): The message ID in hex, binary, or decimal format.
            data (str): The data bytes as a space-separated string (e.g., "0x01 0x02").

        Returns:
            bool: True if successfully added, False if invalid or duplicate.
        """
        try:
            parsed_id = parse_value(message_id)
            parsed_data = [parse_value(byte) for byte in data.split()]

            # Validate the message ID (for standard 11-bit CAN IDs)
            if not (0 <= parsed_id <= 0x7FF):
                logging.warning(f"Invalid Message ID: {parsed_id}. Must be in range 0-0x7FF.")
                return False

            # Validate the data length
            if len(parsed_data) > 8:
                logging.warning("Message data exceeds 8 bytes.")
                return False

            # Check for duplicate name or duplicate message (ID and data)
            for msg in self.messages:
                if msg['name'] == name:
                    logging.warning(f"Duplicate message name detected: {name}")
                    return False  # Duplicate name
                if msg['id'] == parsed_id and msg['data'] == parsed_data:
                    logging.warning(f"Duplicate message detected: {msg}")
                    return False  # Duplicate message

            self.messages.append({'name': name, 'id': parsed_id, 'data': parsed_data})
            logging.info(f"Message added: Name={name}, ID={parsed_id}, Data={parsed_data}")
            return True
        except ValueError as e:
            logging.error(f"Error parsing message: {e}")
            return False

    def remove_message(self, name: str) -> bool:
        """
        Removes a message by its name.

        Args:
            name (str): The name of the message.

        Returns:
            bool: True if successfully removed, False otherwise.
        """
        for msg in self.messages:
            if msg['name'] == name:
                self.messages.remove(msg)
                logging.info(f"Message removed: Name={name}")
                return True
        logging.warning(f"Message not found: Name={name}")
        return False

    def update_message(self, name: str, message_id: str, data: str) -> None:
        """
        Updates a message with new data.

        Args:
            name (str): The name of the message.
            message_id (str): The new message ID in hex, binary, or decimal format.
            data (str): The new data bytes as a space-separated string.
        """
        try:
            parsed_id = parse_value(message_id)
            parsed_data = [parse_value(byte) for byte in data.split()]

            for msg in self.messages:
                if msg['name'] == name:
                    msg['id'] = parsed_id
                    msg['data'] = parsed_data
                    logging.info(f"Message updated: Name={name}, ID={parsed_id}, Data={parsed_data}")
                    return
            logging.warning(f"Message with Name={name} not found. Adding as new.")
            self.add_message(name, message_id, data)
        except ValueError as e:
            logging.error(f"Error updating message: {e}")

    def get_messages(self):
        """Returns the list of messages."""
        return self.messages

    def clear_messages(self):
        """Clears all messages."""
        self.messages.clear()
        logging.info("All messages cleared.")
