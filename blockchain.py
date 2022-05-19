import hashutils
from block import Block

import datetime

class Blockchain:

    def __init__(self):
        self.chain = [genesis_block]

    def generate_next_block (self, block_data: str) -> Block:
        previous_block: Block = self.get_latest_block()
        next_index: int = previous_block.index + 1
        next_timestamp: int = int(datetime.datetime.now().timestamp())
        next_hash: str = hashutils.calculate_hash(next_index, previous_block.hash, next_timestamp, block_data)
        new_block: Block = Block(next_index, next_hash, previous_block.hash, next_timestamp, block_data)
        self.add_block(new_block)
        return new_block

    def add_block(self, new_block):
        try:
            validate_new_block(new_block, self.get_latest_block())
        except ValueError:
            return False

        self.chain.append(new_block)
        return True

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def replace_chain(self, new_chain: [Block]):
        validate_chain(new_chain)
        if len(new_chain) <= len(self.chain):
            raise ValueError("New chain must be longer than old chain")
        self.chain = new_chain


def validate_new_block(new_block: Block, previous_block: Block):
    if not new_block.validate_block_structure():
        raise ValueError('Block scructure is invalid')
    if previous_block.index + 1 != new_block.index:
        raise ValueError('The index of the block must be one number larger than the previous')
    if previous_block.hash != new_block.previous_hash:
        raise ValueError('The previousHash of the block match the hash of the previous block')
    if new_block.calculate_hash_for_block() != new_block.hash:
        raise ValueError("The hash of the block itself must be valid")
    return True


def validate_chain(blockchain: [Block]):
    if blockchain[0] != genesis_block:
        raise ValueError("First block in the chain doesnt match the genesisBlock")

    for i in range(1, len(blockchain)):
        validate_new_block(blockchain[i], blockchain[i - 1])
    return True

genesis_block: Block = Block(
    0, '2ed4d17ce6cca7550d4024bba70be5287ee71cc871853ccf9379e68558f4b1ca', None, 1465154705, 'my genesis block!!'
)