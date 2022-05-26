import hashlib


def calculate_hash(index: int, previous_hash: str, timestamp: int, data: str, nonce: int, difficulty: int) -> str:
    body = str(index) + str(previous_hash) + str(timestamp) + str(data) + str(nonce) + str(difficulty)
    return hashlib.sha256(body.encode('utf-8')).hexdigest()


def hash_matches_difficulty(hash: str, difficulty: int) -> bool:
    hash_bin: str = hex_to_bin(hash)
    required_prefix = '0' * difficulty
    print("a")
    passes = hash_bin.startswith(required_prefix)
    print("hash_bin: {}, required_prefix: {}, passes: {}".format(hash_bin, required_prefix, passes))
    return passes


def hex_to_bin(hash: str) -> str:
    ret = ''
    lookup_table = {
        '0': '0000', '1': '0001', '2': '0010', '3': '0011', '4': '0100',
        '5': '0101', '6': '0110', '7': '0111', '8': '1000', '9': '1001',
        'a': '1010', 'b': '1011', 'c': '1100', 'd': '1101',
        'e': '1110', 'f': '1111'
    }
    for i in hash:
        ret += lookup_table[i]
    return ret
