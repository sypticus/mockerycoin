import hashlib


class Block:
    def __init__(self, index: int, hash: str, previous_hash, timestamp: int, data: str):
        self.index = index
        self.previous_hash = previous_hash
        self.data = data
        self.timestamp = timestamp
        self.hash = hash

    def calculate_hash_for_block(self) -> str:
        return calculate_hash(self.index, self.previous_hash, self.timestamp, self.data)

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

    def __str__(self):
        return 'Block {}:\n-data: {}\n-timestamp: {}\n-hash: {}\n-previous_hash: {}\n'.format(
            self.index,
            self.data,
            self.timestamp,
            self.hash,
            self.previous_hash
        )


def calculate_hash(index: int, previous_hash: str, timestamp: int, data: str) -> str:
    body = str(index) + str(previous_hash) + str(timestamp) + str(data)
    return hashlib.sha256(body.encode('utf-8')).hexdigest()




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