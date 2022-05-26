import unittest
import block
import blockchain
import hashutils
from blockchain import Blockchain

class BlockchainTestCase(unittest.TestCase):
    def test_validate_chain(self):
        new_block = block.Block(1,
                                "1eae5f6c30c0db442a35c2930a1a04a51c3d7365c9051f0e5c63f3f778a86e95",
                                "2ed4d17ce6cca7550d4024bba70be5287ee71cc871853ccf9379e68558f4b1ca",
                                1465154705,
                                "Some Block Data",
                                0,
                                0)

        self.assertTrue(blockchain.validate_chain([blockchain.genesis_block, new_block]))


    def test_generate_next_block(self):

        new_blockchain = Blockchain()

        #Create a new block. Should be added to the chain along with the genesis
        first_block = new_blockchain.generate_next_block("This is the first block added")

        self.assertTrue(blockchain.genesis_block, new_blockchain.chain[0])
        self.assertTrue(first_block, new_blockchain.chain[1])

        self.assertEqual(first_block.data, "This is the first block added")
        self.assertEqual(first_block.previous_hash, blockchain.genesis_block.hash)

        #Create another block. Should get added to the chain.
        next_block = new_blockchain.generate_next_block("This is the 3rd block in the chain")

        self.assertTrue(blockchain.genesis_block, new_blockchain.chain[0])
        self.assertTrue(first_block, new_blockchain.chain[1])
        self.assertTrue(next_block, new_blockchain.chain[2])

        self.assertEqual(next_block.data, "This is the 3rd block in the chain")
        self.assertEqual(next_block.previous_hash, first_block.hash)


    def test_find_block(self):
        new_blockchain = Blockchain()
        block = new_blockchain.find_block(1, '2ed4d17ce6cca7550d4024bba70be5287ee71cc871853ccf9379e68558f4b1ca', 123, 'test2', 1)
        self.assertEqual(block.nonce, 1)
        self.assertTrue(hashutils.hex_to_bin(block.hash).startswith('0'))


    def test_find_block_more_difficult(self):
        new_blockchain = Blockchain()
        block = new_blockchain.find_block(1, '2ed4d17ce6cca7550d4024bba70be5287ee71cc871853ccf9379e68558f4b1ca', 123, 'test_again', 4)
        self.assertEqual(block.nonce, 9)
        print(hashutils.hex_to_bin(block.hash))
        self.assertTrue(hashutils.hex_to_bin(block.hash).startswith('0000'))


    def test_get_accumulated_difficulty(self):
        block0 = block.Block.partial({'difficulty': 0})
        block1 = block.Block.partial({'difficulty': 2})
        block2 = block.Block.partial({'difficulty': 5})
        block3 = block.Block.partial({'difficulty': 3})
        total = blockchain.get_accumulated_difficulty([block0, block1, block2, block3])
        self.assertEqual(total, 45)


if __name__ == '__main__':
    unittest.main()
