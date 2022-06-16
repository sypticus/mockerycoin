import unittest

import hashutils


class HashutilsTestCase(unittest.TestCase):

    def test_generate_private_key(self):
        pk = hashutils.generate_private_key()
        print(pk)
        self.assertEqual(len(pk), 64)

    def test_get_public_key_from_private(self):
        pub_key = hashutils.get_public_key_from_private("e2b3157838803983fdc5eed680f6312069f0fa5199c2c02d80c74fc2212880cf")
        self.assertEqual(pub_key, "00045ac146da77da2c9590cc3fd344405b3d808dba6ab76d872415e1e0505c2ed311afea3a71870bf48d746ae355b9deb145b0acb4b0986dc4d269b37334f935e8bc")
