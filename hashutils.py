import hashlib


def calculate_hash(index: int, previous_hash: str, timestamp: int, data: str) -> str:
    body = str(index) + str(previous_hash) + str(timestamp) + str(data)
    return hashlib.sha256(body.encode('utf-8')).hexdigest()

