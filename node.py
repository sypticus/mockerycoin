import datetime
import block
from block import Block, genesis_block


class Node:
    def __init__(self):
        self.blockchain = [genesis_block]

    def generate_next_block (self, block_data: str) -> Block:
        previous_block: Block = self.get_latest_block()
        next_index: int = previous_block.index + 1
        next_timestamp: int = int(datetime.datetime.now().timestamp())
        next_hash: str = block.calculate_hash(next_index, previous_block.hash, next_timestamp, block_data)
        new_block: Block = Block(next_index, next_hash, previous_block.hash, next_timestamp, block_data)
        self.add_block(new_block)
        return new_block

    def add_block(self, new_block):
        try:
            block.validate_new_block(new_block, self.get_latest_block())
        except ValueError:
            return False

        self.blockchain.append(new_block)
        return True

    def get_latest_block(self) -> Block:
        return self.blockchain[-1]

    def replace_chain(self, new_chain: [Block]):
        block.validate_chain(new_chain)
        if len(new_chain) <= len(self.blockchain):
            raise ValueError("New chain must be longer than old chain")
        self.blockchain = new_chain
