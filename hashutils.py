import hashlib

import ellipticcurve
from ellipticcurve import Signature, PublicKey
from ellipticcurve.ecdsa import Ecdsa
from ellipticcurve.privateKey import PrivateKey

def calculate_hash(index: int, previous_hash: str, timestamp: int, data: str, nonce: int, difficulty: int) -> str:
    body = str(index) + str(previous_hash) + str(timestamp) + str(data) + str(nonce) + str(difficulty)
    return sha256(body)


def sha256(body: str) -> str:
    return hashlib.sha256(body.encode('utf-8')).hexdigest()


def byte_array_to_hex(body: [bytes]) -> str:
    return bytes(body).hex()


def hex_to_byte_array(body: str) -> [bytes]:
    return bytes.fromhex(body)


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


def get_public_key_from_private(private_key_str: str) -> str:
    return PrivateKey.fromString(private_key_str).publicKey().toString(True)


def get_signature_string(private_key_string: str, data_to_sign) -> str:
    key = PrivateKey.fromString(private_key_string)
    signature: str = byte_array_to_hex(Ecdsa.sign(data_to_sign, key).toDer())
    return signature


def verify_signature(pub_key_str, signature_str, message) -> bool:
    signature: Signature = signature_from_string(signature_str)
    key = PublicKey.fromString(pub_key_str)
    return Ecdsa.verify(message, signature, key)


def signature_from_string(signature_str: str) -> Signature:
    return Signature.fromDer(hex_to_byte_array(signature_str))


def generate_private_key() -> str:
    private_key = PrivateKey()
    return private_key.toString()
