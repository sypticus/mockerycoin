import unittest
import node, block


class MyTestCase(unittest.TestCase):

    def test_generate_next_block(self):
        new_node = node.Node()

        #Create a new block. Should be added to the chain along with the genesis
        first_block = new_node.generate_next_block("This is the first block added")

        self.assertTrue(block.genesis_block, new_node.blockchain[0])
        self.assertTrue(first_block, new_node.blockchain[1])

        self.assertEqual(first_block.data, "This is the first block added")
        self.assertEqual(first_block.previous_hash, block.genesis_block.hash)

        #Create another block. Should get added to the chain.
        next_block = new_node.generate_next_block("This is the 3rd block in the chain")

        self.assertTrue(block.genesis_block, new_node.blockchain[0])
        self.assertTrue(first_block, new_node.blockchain[1])
        self.assertTrue(next_block, new_node.blockchain[2])

        self.assertEqual(next_block.data, "This is the 3rd block in the chain")
        self.assertEqual(next_block.previous_hash, first_block.hash)


if __name__ == '__main__':
    unittest.main()
