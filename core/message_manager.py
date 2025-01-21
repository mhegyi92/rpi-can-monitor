import logging


class MessageManager:
    """
    Manages CAN messages, allowing addition, removal, and validation with names.
    """

    def __init__(self):
        self.messages = []  # Stores messages as dictionaries: {'id': int, 'data': list[int], 'name': str}

    def add_message(self, name, message_id, data):
        """
        Adds a message to the list.

        Args:
            name (str): The name of the message.
            message_id (str): The message ID in hex, binary, or decimal format.
            data (str): The data bytes in hex format.

        Returns:
            bool: True if successfully added, False if invalid or duplicate.
        """
        try:
            # Normalize the input
            parsed_id = int(message_id, 16)
            parsed_data = [int(byte, 16) for byte in data.split()]

            # Validate the data length
            if len(parsed_data) > 8:
                logging.warning("Message data exceeds 8 bytes.")
                return False

            # Check for duplicate name or message
            for msg in self.messages:
                if msg['name'] == name:
                    logging.warning(f"Duplicate message name detected: {name}")
                    return False  # Duplicate name
                if msg['id'] == parsed_id and msg['data'] == parsed_data:
                    logging.warning(f"Duplicate message detected: {msg}")
                    return False  # Duplicate message

            # Add the message
            self.messages.append({'name': name, 'id': parsed_id, 'data': parsed_data})
            logging.info(f"Message added: Name={name}, ID={parsed_id}, Data={parsed_data}")
            return True
        except ValueError as e:
            logging.error(f"Error parsing message: {e}")
            return False

    def remove_message(self, name):
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

    def update_message(self, name, message_id, data):
        """
        Updates a message with new data.

        Args:
            name (str): The name of the message.
            message_id (int): The new message ID.
            data (list[int]): The new data.
        """
        for msg in self.messages:
            if msg['name'] == name:
                msg['id'] = message_id
                msg['data'] = data
                logging.info(f"Message updated: Name={name}, ID={message_id}, Data={data}")
                return
        logging.warning(f"Message with Name={name} not found. Adding as new.")
        self.add_message(name, hex(message_id), " ".join(hex(b) for b in data))

    def get_messages(self):
        """Returns the list of messages."""
        return self.messages

    def clear_messages(self):
        """Clears all messages."""
        self.messages.clear()
        logging.info("All messages cleared.")
