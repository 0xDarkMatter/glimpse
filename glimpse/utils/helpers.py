"""Helper utilities for Glimpse CLI"""

import os


def get_data_dir() -> str:
    """
    Get the data directory path

    Returns:
        Absolute path to the data directory
    """
    return os.path.join(os.getcwd(), 'data')
