import string

BASE62_ALPHABET = string.digits + string.ascii_letters


def encode_base62(num):
    if num == 0:
        return BASE62_ALPHABET[0]
    base62 = []
    while num > 0:
        num, rem = divmod(num, 62)
        base62.append(BASE62_ALPHABET[rem])
    return ''.join(reversed(base62))


def decode_base62(code):
    num = 0
    for char in code:
        num = num * 62 + BASE62_ALPHABET.index(char)
    return num
