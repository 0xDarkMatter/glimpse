"""
Crockford's Base32 implementation for generating RV session codes
Format: XXXX-XXXX (8 characters with dash separator)
"""

import secrets

CROCKFORD_ALPHABET = '0123456789ABCDEFGHJKMNPQRSTVWXYZ'


def generate_code(length: int = 8, separator: str = '-', separator_position: int = 4) -> str:
    """
    Generates a random Crockford Base32 code

    Args:
        length: Total number of characters (default: 8)
        separator: Separator character (default: '-')
        separator_position: Position to insert separator (default: 4)

    Returns:
        Formatted code (e.g., "XXXX-XXXX")
    """
    code = ''
    for i in range(length):
        code += secrets.choice(CROCKFORD_ALPHABET)

        # Insert separator at specified position
        if i == separator_position - 1 and i < length - 1:
            code += separator

    return code


def validate_code(code: str) -> bool:
    """
    Validates a Crockford Base32 code

    Args:
        code: Code to validate

    Returns:
        True if valid, False otherwise
    """
    # Remove separator and convert to uppercase
    clean_code = code.replace('-', '').upper()

    # Check if all characters are valid Crockford Base32
    return all(char in CROCKFORD_ALPHABET for char in clean_code)


def normalize_code(code: str) -> str:
    """
    Normalizes a code (removes separators, converts to uppercase)

    Args:
        code: Code to normalize

    Returns:
        Normalized code
    """
    return code.replace('-', '').upper()
