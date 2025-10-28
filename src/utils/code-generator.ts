/**
 * Crockford's Base32 implementation for generating RV session codes
 * Format: XXXX-XXXX (8 characters with dash separator)
 */

const CROCKFORD_ALPHABET = '0123456789ABCDEFGHJKMNPQRSTVWXYZ';

/**
 * Generates a random Crockford Base32 code
 * @param length Total number of characters (default: 8)
 * @param separator Separator character (default: '-')
 * @param separatorPosition Position to insert separator (default: 4)
 * @returns Formatted code (e.g., "XXXX-XXXX")
 */
export function generateCode(
  length: number = 8,
  separator: string = '-',
  separatorPosition: number = 4
): string {
  const bytes = new Uint8Array(length);

  // Generate random bytes using crypto
  if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
    crypto.getRandomValues(bytes);
  } else {
    // Fallback for Node.js
    const nodeCrypto = require('crypto');
    const randomBytes = nodeCrypto.randomBytes(length);
    for (let i = 0; i < length; i++) {
      bytes[i] = randomBytes[i];
    }
  }

  let code = '';
  for (let i = 0; i < length; i++) {
    const index = bytes[i] % CROCKFORD_ALPHABET.length;
    code += CROCKFORD_ALPHABET[index];

    // Insert separator at specified position
    if (i === separatorPosition - 1 && i < length - 1) {
      code += separator;
    }
  }

  return code;
}

/**
 * Validates a Crockford Base32 code
 * @param code Code to validate
 * @returns true if valid, false otherwise
 */
export function validateCode(code: string): boolean {
  // Remove separator and convert to uppercase
  const cleanCode = code.replace(/-/g, '').toUpperCase();

  // Check if all characters are valid Crockford Base32
  return cleanCode.split('').every((char) => CROCKFORD_ALPHABET.includes(char));
}

/**
 * Normalizes a code (removes separators, converts to uppercase)
 * @param code Code to normalize
 * @returns Normalized code
 */
export function normalizeCode(code: string): string {
  return code.replace(/-/g, '').toUpperCase();
}
