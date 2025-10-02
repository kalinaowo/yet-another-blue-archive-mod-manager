import binascii
from pathlib import Path

def bytes_to_u32_be(b):
    return int.from_bytes(b, 'big')

def u32_to_bytes_be(i):
    return i.to_bytes(4, 'big')

def reverse_bits_in_bytes(b):
    # b is 4 bytes
    num = bytes_to_u32_be(b)
    rev = 0
    for i in range(32):
        if (num >> i) & 1:
            rev |= 1 << (31 - i)
    return u32_to_bytes_be(rev)

def hex_string_to_bytes(hexstr):
    if len(hexstr) % 2 != 0:
        raise ValueError("Hex string length must be even")
    return bytes.fromhex(hexstr)

def gf_multiply(a, b):
    result = 0
    while b:
        if b & 1:
            result ^= a
        a <<= 1
        b >>= 1
    return result

def gf_divide(dividend, divisor):
    if divisor == 0:
        return 0
    quotient = 0
    remainder = dividend
    divisor_bits = divisor.bit_length()
    while remainder.bit_length() >= divisor_bits and remainder != 0:
        shift = remainder.bit_length() - divisor_bits
        quotient |= 1 << shift
        remainder ^= divisor << shift
    return quotient

def gf_mod(dividend, divisor, n):
    if divisor == 0:
        return dividend
    dividend_bits = dividend.bit_length()
    divisor_bits = divisor.bit_length()
    while dividend != 0 and dividend.bit_length() >= divisor_bits:
        shift = dividend.bit_length() - divisor_bits
        dividend ^= divisor << shift
    mask = (1 << n) - 1 if n < 64 else 0xFFFFFFFFFFFFFFFF
    return dividend & mask

def gf_multiply_modular(a, b, modulus, n):
    product = gf_multiply(a, b)
    return gf_mod(product, modulus, n)

def gf_modular_inverse(a, m):
    if a == 0:
        raise ValueError("Inverse of zero does not exist")
    old_r, r = m, a
    old_s, s = 0, 1
    while r != 0:
        q = gf_divide(old_r, r)
        old_r, r = r, old_r ^ gf_multiply(q, r)
        old_s, s = s, old_s ^ gf_multiply(q, s)
    if old_r != 1:
        raise ValueError("Modular inverse does not exist")
    return old_s

def gf_inverse(k, poly):
    x32 = 0x100000000
    inverse = gf_modular_inverse(x32, poly)
    result = gf_multiply_modular(k, inverse, poly, 32)
    return result

def compute_crc32(data: bytes):
    # Standard CRC32 (IEEE)
    return binascii.crc32(data) & 0xFFFFFFFF

def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))

def manipulate_crc(original_path, modified_path):
    with open(original_path, "rb") as f:
        original_data = f.read()
    with open(modified_path, "rb") as f:
        modified_data = f.read()

    original_crc = compute_crc32(original_data)
    # Append 4 zero bytes to modified_data before hashing (matches rust code)
    modified_crc = compute_crc32(modified_data + b'\x00\x00\x00\x00')

    # Convert CRCs to 4-byte big-endian bytes
    original_bytes = u32_to_bytes_be(original_crc)
    modified_bytes = u32_to_bytes_be(modified_crc)

    xor_result = xor_bytes(original_bytes, modified_bytes)
    reversed_bytes = reverse_bits_in_bytes(xor_result)
    k = bytes_to_u32_be(reversed_bytes)

    crc32_poly = 0x104C11DB7  # CRC-32 polynomial + implicit 33rd bit

    correction_value = gf_inverse(k, crc32_poly)

    # Prepare correction bytes (reverse bits of each byte in BE order)
    correction_bytes_raw = u32_to_bytes_be(correction_value)
    correction_bytes = bytes(b[::-1] for b in correction_bytes_raw.to_bytes(4, 'big')) if False else bytes((int('{:08b}'.format(b)[::-1], 2) for b in correction_bytes_raw))

    # In Python, just reverse bits of each byte:
    def reverse_byte_bits(byte):
        return int('{:08b}'.format(byte)[::-1], 2)
    correction_bytes = bytes(reverse_byte_bits(b) for b in correction_bytes_raw)

    # Append correction bytes to modified data
    final_data = modified_data + correction_bytes

    final_crc = compute_crc32(final_data)
    is_crc_match = (final_crc == original_crc)

    if is_crc_match:
        # Overwrite modified file with corrected data
        with open(modified_path, "wb") as f:
            f.write(final_data)

    return is_crc_match

# Example usage:
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python crc_correction.py <original_file> <modified_file>")
        sys.exit(1)

    original_file = Path(sys.argv[1])
    modified_file = Path(sys.argv[2])

    success = manipulate_crc(original_file, modified_file)
    print("CRC correction successful:", success)
