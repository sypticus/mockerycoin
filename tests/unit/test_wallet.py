import os
import unittest
from os.path import exists

import hashutils
import wallet
from transactions import UnspentTxOut, TxOut
from wallet import Wallet


class WalletTestCase(unittest.TestCase):
    wallet.WALLET_LOCATION = "test_wallet_file.txt"
    def setUp(self):
        if os.path.exists(wallet.WALLET_LOCATION):
            os.remove(wallet.WALLET_LOCATION)

    def test_create_wallet(self):
        my_wallet = Wallet()

        self.assertTrue(exists(wallet.WALLET_LOCATION))
        self.assertEqual(my_wallet.pub_key, hashutils.get_public_key_from_private(my_wallet.private_key))

    def test_get_balance(self):
        my_wallet = Wallet()
        utxo_1 = UnspentTxOut('tx_out1', 0, my_wallet.pub_key, 5)
        utxo_2 = UnspentTxOut('tx_out2', 0, '', 3)
        utxo_3 = UnspentTxOut('tx_out3', 0, my_wallet.pub_key, 2)

        # balance should only include amount belonging to this wallet
        balance = my_wallet.get_balance([utxo_1, utxo_2, utxo_3])

        self.assertEqual(balance, 7)


    def test_create_transaction(self):
        my_wallet = Wallet()

        utxo_1 = UnspentTxOut('tx_out1', 0, my_wallet.pub_key, 5)
        utxo_2 = UnspentTxOut('tx_out2', 0, my_wallet.pub_key, 3)

        tx = my_wallet.create_transaction('some_pub_key', 6, [utxo_1, utxo_2])

        self.assertEqual(len(tx.tx_outs), 2)
        tx_out1: TxOut = tx.tx_outs[0]
        tx_out2: TxOut = tx.tx_outs[1]

        self.assertEqual(tx_out1.amount, 6)
        self.assertEqual(tx_out1.address, 'some_pub_key')
        self.assertEqual(tx_out2.amount, 2)
        self.assertEqual(tx_out2.address, my_wallet.pub_key)


    def test_create_transaction_2(self):
        my_wallet = Wallet()

        utxo_1 = UnspentTxOut('tx_out1', 0, my_wallet.pub_key, 5)
        utxo_2 = UnspentTxOut('tx_out2', 0, my_wallet.pub_key, 3)

        tx = my_wallet.create_transaction('some_pub_key', 4, [utxo_1, utxo_2])

        self.assertEqual(len(tx.tx_outs), 2)
        tx_out1: TxOut = tx.tx_outs[0]
        tx_out2: TxOut = tx.tx_outs[1]

        self.assertEqual(tx_out1.amount, 4)
        self.assertEqual(tx_out1.address, 'some_pub_key')
        self.assertEqual(tx_out2.amount, 1)
        self.assertEqual(tx_out2.address, my_wallet.pub_key)




