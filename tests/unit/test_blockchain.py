import unittest
import block
import blockchain
from blockchain import Blockchain

class BlockchainTestCase(unittest.TestCase):
    def test_validate_chain(self):
        new_block = block.Block(1,
                                "67c18b4716799348311c3f94a3d15ef3520dc991ab84b7844679b4cf224bf66b",
                                "2ed4d17ce6cca7550d4024bba70be5287ee71cc871853ccf9379e68558f4b1ca",
                                1465154705,
                                "Some Block Data")

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


if __name__ == '__main__':
    unittest.main()
