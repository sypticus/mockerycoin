import unittest
import block


class MyTestCase(unittest.TestCase):

    def test_create_block(self):
        new_block = block.Block(1,
                                "67c18b4716799348311c3f94a3d15ef3520dc991ab84b7844679b4cf224bf66b",
                                "2ed4d17ce6cca7550d4024bba70be5287ee71cc871853ccf9379e68558f4b1ca",
                                1465154705,
                                "Some Block Data")

        self.assertTrue(new_block.validate_block_structure())
        self.assertEqual(new_block.calculate_hash_for_block(), new_block.hash)



if __name__ == '__main__':
    unittest.main()
