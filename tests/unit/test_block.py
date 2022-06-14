import unittest
import block


class BlockTestCase(unittest.TestCase):

    def test_create_block(self):
        new_block = block.Block(1,
                                "1eae5f6c30c0db442a35c2930a1a04a51c3d7365c9051f0e5c63f3f778a86e95",
                                "2ed4d17ce6cca7550d4024bba70be5287ee71cc871853ccf9379e68558f4b1ca",
                                1465154705,
                                "Some Block Data",
                                0,
                                0)

        self.assertTrue(new_block.validate_block_structure())
        self.assertEqual(new_block.calculate_hash_for_block(), new_block.hash)



if __name__ == '__main__':
    unittest.main()
