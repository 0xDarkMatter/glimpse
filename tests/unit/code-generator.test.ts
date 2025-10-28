import { generateCode, validateCode, normalizeCode } from '../../src/utils/code-generator';

describe('Code Generator', () => {
  describe('generateCode', () => {
    it('should generate code with default length of 8 characters plus separator', () => {
      const code = generateCode();
      expect(code.length).toBe(9); // 8 chars + 1 separator
    });

    it('should generate code with separator at position 4', () => {
      const code = generateCode();
      expect(code.charAt(4)).toBe('-');
    });

    it('should generate unique codes', () => {
      const codes = new Set();
      for (let i = 0; i < 100; i++) {
        codes.add(generateCode());
      }
      expect(codes.size).toBe(100);
    });

    it('should only use valid Crockford Base32 characters', () => {
      const validChars = /^[0-9A-HJ-NP-Z-]+$/;
      for (let i = 0; i < 20; i++) {
        const code = generateCode();
        expect(code).toMatch(validChars);
      }
    });
  });

  describe('validateCode', () => {
    it('should validate correct codes', () => {
      expect(validateCode('AB3D-X7K2')).toBe(true);
      expect(validateCode('0000-0000')).toBe(true);
      expect(validateCode('ZZZZ-ZZZZ')).toBe(true);
    });

    it('should reject codes with invalid characters', () => {
      expect(validateCode('ILOU-1234')).toBe(false); // I, L, O, U not in Crockford
      expect(validateCode('ABCD-EFGH')).toBe(true); // All valid
    });

    it('should handle codes without separators', () => {
      expect(validateCode('AB3DX7K2')).toBe(true);
    });

    it('should be case insensitive', () => {
      expect(validateCode('ab3d-x7k2')).toBe(true);
      expect(validateCode('AB3D-X7K2')).toBe(true);
    });
  });

  describe('normalizeCode', () => {
    it('should remove separators', () => {
      expect(normalizeCode('AB3D-X7K2')).toBe('AB3DX7K2');
    });

    it('should convert to uppercase', () => {
      expect(normalizeCode('ab3d-x7k2')).toBe('AB3DX7K2');
    });

    it('should handle codes without separators', () => {
      expect(normalizeCode('AB3DX7K2')).toBe('AB3DX7K2');
    });
  });
});
