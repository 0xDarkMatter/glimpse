"""Helper utilities for Glimpse CLI"""

import os
from datetime import datetime


def get_data_dir() -> str:
    """
    Get the data directory path

    Returns:
        Absolute path to the data directory
    """
    return os.path.join(os.getcwd(), 'data')


def format_capture_date(date_str: str) -> str:
    """
    Format Street View capture date from YYYY-MM to readable format

    Args:
        date_str: Date string in format "YYYY-MM" (e.g., "2025-06")

    Returns:
        Formatted date string (e.g., "June 2025")
    """
    if not date_str:
        return date_str

    try:
        # Parse YYYY-MM format
        if '-' in date_str and len(date_str.split('-')) == 2:
            year, month = date_str.split('-')
            date_obj = datetime(int(year), int(month), 1)
            return date_obj.strftime('%B %Y')
        else:
            # If it's just a year or other format, return as-is
            return date_str
    except (ValueError, AttributeError):
        return date_str
