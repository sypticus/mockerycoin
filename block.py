import json

from flask import jsonify

import hashutils


class Block:
    def __init__(self, index: int, hash: str, previous_hash, timestamp: int, data: str, nonce: int, difficulty: int):
        self.index = index
        self.previous_hash = previous_hash
        self.data = data
        self.timestamp = timestamp
        self.hash = hash
        self.nonce = nonce
        self.difficulty = difficulty

    @classmethod
    def from_dict(cls, dict):
        return cls(dict['index'], dict['hash'], dict['previous_hash'], dict['timestamp'], dict['data'], dict['nonce'], dict['difficulty'])

    @classmethod
    def partial(cls, dict): #For unit testing only
        return cls(dict.get('index'),
                   dict.get('hash'),
                   dict.get('previous_hash'),
                   dict.get('timestamp'),
                   dict.get('data'),
                   dict.get('nonce'),
                   dict.get('difficulty'))

    def calculate_hash_for_block(self) -> str:
        return hashutils.calculate_hash(self.index, self.previous_hash, self.timestamp, self.data, self.nonce, self.difficulty)

    def validate_block_structure(self) -> bool:
        return (
                type(self.index) == int
                and type(self.data) == str
                and type(self.timestamp) == int
                and type(self.hash) == str
                and type(self.previous_hash) == str
        )

    def __eq__(self, other):
        return (
                self.index == other.index
                and self.previous_hash == other.previous_hash
                and self.data == other.data
                and self.timestamp == other.timestamp
                and self.hash == other.hash
        )

    def toJson(self):
        return jsonify(self.__dict__)

    def __str__(self):
        return 'Block {}:\n-data: {}\n-timestamp: {}\n-hash: {}\n-previous_hash: {}\n'.format(
            self.index,
            self.data,
            self.timestamp,
            self.hash,
            self.previous_hash
        )
