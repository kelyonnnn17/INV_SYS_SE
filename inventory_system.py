#!/usr/bin/env python3

"""
A simple JSON-based inventory management system.

This module provides functions to add, remove, and query
stock levels for items, and persists the data to a JSON file.
"""

import json
import logging
import sys

# Global variable to hold stock data.
# It is loaded from a file at runtime.
stock_data = {}


def setup_logging():
    """Configure basic logging."""
    # Configure logging to output to standard error
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)]
    )


def add_item(item: str, qty: int):
    """
    Add a specified quantity of an item to the stock.

    Args:
        item: The name of the item (str).
        qty: The quantity to add (int). Must be non-negative.
    """
    if not isinstance(item, str) or not item:
        # Use lazy logging (W1203)
        logging.error(
            "Invalid item name: '%s'. Must be non-empty string.", item
        )
        return
    if not isinstance(qty, int):
        logging.error("Invalid quantity: '%s'. Must be an integer.", qty)
        return
    # LOGICAL FIX: Prevent adding negative numbers
    if qty < 0:
        # FIX E501: Break long line
        logging.warning(
            "Invalid quantity: %d. Cannot add negative amount.", qty
        )
        return

    stock_data[item] = stock_data.get(item, 0) + qty
    # FIX E501: Break long line
    logging.info(
        "Added %d of '%s'. New total: %d", qty, item, stock_data[item]
    )


def remove_item(item: str, qty: int):
    """
    Remove a specified quantity of an item from the stock.

    If the item's stock goes to 0 or below, it is removed.

    Args:
        item: The name of the item to remove (str).
        qty: The quantity to remove (int). Must be non-negative.
    """
    if not isinstance(item, str) or not item:
        logging.error(
            "Invalid item name: '%s'. Must be non-empty string.", item
        )
        return
    if not isinstance(qty, int):
        logging.error("Invalid quantity: '%s'. Must be an integer.", qty)
        return
    # LOGICAL FIX: Prevent removing negative numbers
    if qty < 0:
        # FIX E501: Break long line
        logging.warning(
            "Invalid quantity: %d. Cannot remove negative amount.", qty
        )
        return

    try:
        stock_data[item] -= qty
        # FIX E501: Break long line
        logging.info(
            "Removed %d of '%s'. New total: %d", qty, item, stock_data[item]
        )
        if stock_data[item] <= 0:
            del stock_data[item]
            logging.info("Item '%s' removed from stock (quantity <= 0).", item)
    except KeyError:
        # Specified exception instead of bare 'except'
        logging.warning("Item '%s' not in stock, cannot remove.", item)


def get_qty(item: str) -> int:
    """
    Get the current quantity of a specific item.

    Args:
        item: The name of the item (str).

    Returns:
        The quantity of the item (int), or 0 if not found.
    """
    if not isinstance(item, str):
        logging.error("Invalid item name: '%s'. Must be a string.", item)
        return 0
    return stock_data.get(item, 0)


def load_data(file: str = "inventory.json") -> dict:
    """
    Load stock data from a JSON file.

    Args:
        file: The file to load from.

    Returns:
        A dictionary containing the stock data.
    """
    try:
        # Use 'with' for resource management and 'encoding'
        with open(file, "r", encoding="utf-8") as f:
            data = json.loads(f.read())
            logging.info("Successfully loaded data from %s", file)
            return data
    except FileNotFoundError:
        logging.warning("File '%s' not found. Starting empty stock.", file)
    except json.JSONDecodeError:
        logging.error("JSON decode error in '%s'. Starting empty stock.", file)
    # FIX W0718: Catch more specific exceptions than 'Exception'
    except (IOError, OSError) as e:
        logging.error("Error loading data from %s: %s", file, e)
    return {}


def save_data(file: str = "inventory.json"):
    """
    Save the current stock data to a JSON file.

    Args:
        file: The file to save to.
    """
    try:
        # Use 'with' for resource management and 'encoding'
        with open(file, "w", encoding="utf-8") as f:
            # Use indent=4 for readable JSON
            f.write(json.dumps(stock_data, indent=4))
            logging.info("Successfully saved data to %s", file)
    except (IOError, OSError) as e:
        logging.error("Could not write to file '%s': %s", file, e)


def print_data():
    """Print a formatted report of all items in stock."""
    print("\n--- Items Report ---")
    if not stock_data:
        print("  Stock is empty.")
    else:
        # Use .items() for cleaner iteration
        for item, quantity in stock_data.items():
            # Use f-string for cleaner output
            print(f"  {item}: {quantity}")
    print("--------------------\n")


def check_low_items(threshold: int = 5) -> list:
    """
    Get a list of all items at or below a given threshold.

    Args:
        threshold: The stock level to check against.

    Returns:
        A list of item names (str) that are low in stock.
    """
    result = []
    for item, quantity in stock_data.items():
        if quantity <= threshold:
            result.append(item)
    return result


def main():
    """Main function to run the inventory system."""

    # Configure logging
    setup_logging()

    # Load data and assign to global variable
    # FIX W0603: The 'global' keyword is required here for this design.
    # We disable the pylint warning for this specific, intentional line.
    # FIX E261: Added two spaces before inline comment
    global stock_data  # pylint: disable=global-statement
    stock_data = load_data()

    # Use snake_case function names
    add_item("apple", 10)
    add_item("banana", 8)

    # These invalid calls will now be caught by input validation
    add_item(123, "ten")
    add_item("pear", -2)  # LOGICAL FIX: This will now be blocked

    remove_item("apple", 3)
    remove_item("orange", 1)  # Will log a warning (KeyError)
    remove_item("banana", -1)

    print(f"Apple stock: {get_qty('apple')}")
    print(f"Orange stock: {get_qty('orange')}")

    # 'pear' will not be in the list, as it was never added.
    print(f"Low items: {check_low_items()}")

    print_data()
    save_data()

    # The insecure 'eval' call has been removed.


# Standard Python entry point guard
if __name__ == "__main__":
    main()
