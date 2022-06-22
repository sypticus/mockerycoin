from functools import reduce
import operator
import hashutils
from block import Block

import datetime

from transactionpool import TransactionPool
from transactions import UnspentTxOut, Transaction
import transactions
from wallet import Wallet


class Blockchain:

    # in seconds
    BLOCK_GENERATION_INTERVAL: int = 10

    # in blocks
    DIFFICULTY_ADJUSTMENT_INTERVAL: int = 10

    def __init__(self):
        self.chain = [genesis_block]
        self.unspent_tx_outs: [UnspentTxOut] = []
        self.transaction_pool = TransactionPool()



    def send_transaction(self, address: str, amount: float, wallet) -> Transaction:
        tx: Transaction = wallet.create_transaction(address, amount, self.unspent_tx_outs, self.transaction_pool.get_transactions())
        self.transaction_pool.add_to_transaction_pool(tx, self.unspent_tx_outs)
        return tx

    def handle_received_transaction(self, transaction: Transaction):
        self.transaction_pool.add_to_transaction_pool(transaction, self.unspent_tx_outs)



    def mine_next_block_transaction(self, receiver_address, amount, wallet: Wallet) -> Block:
        tx: Transaction = wallet.create_transaction(receiver_address, amount, self.unspent_tx_outs, self.transaction_pool.get_transactions())
        coinbase_tx: Transaction = transactions.generate_coinbase_transaction(wallet.pub_key,
                                                                              self.get_latest_block().index + 1)
        block_data: [Transaction] = [coinbase_tx, tx]
        return self.generate_next_block(block_data)

    def mine_next_block(self, wallet: Wallet) -> Block:
        coinbase_tx: Transaction = transactions.generate_coinbase_transaction(wallet.pub_key,
                                                                              self.get_latest_block().index + 1)

        block_data: [Transaction] = [coinbase_tx]
        block_data.extend(self.transaction_pool.get_transactions())
        return self.generate_next_block(block_data)

    def generate_next_block(self, block_data: [Transaction]) -> Block:
        previous_block: Block = self.get_latest_block()
        next_index: int = previous_block.index + 1
        next_timestamp: int = get_current_timestamp()
        difficulty = self.get_difficulty()
        new_block: Block = self.find_block(next_index, previous_block.hash, next_timestamp, block_data, difficulty)
        self.add_block(new_block)
        return new_block

    def add_block(self, new_block: Block):  # Todo: Handle failures
        validate_new_block(new_block, self.get_latest_block())
        updated_unspent_tx_outs: [UnspentTxOut] = transactions.process_transactions(new_block.data,
                                                                                    self.unspent_tx_outs,
                                                                                    new_block.index)
        self.unspent_tx_outs = updated_unspent_tx_outs
        self.transaction_pool.update_transaction_pool(self.unspent_tx_outs)
        self.chain.append(new_block)

    def find_block(self, next_index, previous_hash, next_timestamp, block_data, difficulty) -> Block:
        nonce = 0
        while True:
            next_hash: str = hashutils.calculate_hash(next_index, previous_hash, next_timestamp, block_data, nonce, difficulty)

            if hashutils.hash_matches_difficulty(next_hash, difficulty):
                new_block: Block = Block(next_index, next_hash, previous_hash, next_timestamp, block_data, nonce, difficulty)
                return new_block
            nonce += 1



    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def replace_chain(self, new_chain: [Block]):
        validate_chain(new_chain)
        if get_accumulated_difficulty(new_chain) <= get_accumulated_difficulty(self.chain):
            raise ValueError("New chain must have higher accumulated difficulty than the old")
        self.chain = new_chain

    def get_difficulty(self) -> int:
        latest_block: Block = self.get_latest_block()
        if latest_block.index % self.DIFFICULTY_ADJUSTMENT_INTERVAL == 0 and latest_block.index != 0:
            return self.get_adjusted_difficulty()
        else:
            return latest_block.difficulty

    def get_wallet_balance(self, wallet: Wallet):
        return wallet.get_balance(self.unspent_tx_outs)

    def get_adjusted_difficulty(self) -> int:
        latest_block: Block = self.get_latest_block()
        prev_adjustment_block: Block = self.chain[-self.DIFFICULTY_ADJUSTMENT_INTERVAL]
        time_expected: int = self.BLOCK_GENERATION_INTERVAL * self.DIFFICULTY_ADJUSTMENT_INTERVAL
        time_taken: int = latest_block.timestamp - prev_adjustment_block.timestamp
        if time_taken < time_expected / 2:
            return prev_adjustment_block.difficulty + 1
        elif time_taken > time_expected * 2:
            return prev_adjustment_block.difficulty - 1
        else:
            return prev_adjustment_block.difficulty


def get_accumulated_difficulty(chain: [Block]) -> int:
    return reduce(operator.add, map(lambda block: 2**block.difficulty, chain))


def validate_new_block(new_block: Block, previous_block: Block):
    if not new_block.validate_block_structure():
        print("Validation Failed: Block scructure is invalid")
        raise ValueError('Block scructure is invalid')
    if previous_block.index + 1 != new_block.index:
        print("Validation Failed: The index of the block must be one number larger than the previous")
        raise ValueError('The index of the block must be one number larger than the previous')
    if previous_block.hash != new_block.previous_hash:
        print("Validation Failed: The previousHash of the block match the hash of the previous block")
        raise ValueError('The previousHash of the block match the hash of the previous block')
    if new_block.calculate_hash_for_block() != new_block.hash:
        print("Validation Failed: The hash of the block itself must be valid")
        raise ValueError("The hash of the block itself must be valid")
    if new_block.timestamp > get_current_timestamp() + 60:
        print("Validation Failed: The new block's timestamp is more than 60s in the future")
        raise ValueError("The new block's timestamp is more than 60s in the future")
    if new_block.timestamp < previous_block.timestamp - 60:
        print("Validation Failed: The new block's timestamp is more than 60s behind the previous block")
        raise ValueError("Validation Failed: The new block's timestamp is more than 60s behind the previous block")

    return True




def get_current_timestamp():
    return int(datetime.datetime.now().timestamp())

def validate_chain(blockchain: [Block]):
    if blockchain[0] != genesis_block:
        raise ValueError("First block in the chain doesnt match the genesisBlock")

    for i in range(1, len(blockchain)):
        validate_new_block(blockchain[i], blockchain[i - 1])
    return True

genesis_block: Block = Block(
    0, '2ed4d17ce6cca7550d4024bba70be5287ee71cc871853ccf9379e68558f4b1ca', None, 1465154705, 'my genesis block!!', 0, 0
)