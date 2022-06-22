import os
import unittest
from os.path import exists

import hashutils
import wallet
from transactionpool import TransactionPool
from transactions import UnspentTxOut, TxOut, TxIn, Transaction
from wallet import Wallet


class TransactionPoolTestCase(unittest.TestCase):
    wallet.WALLET_LOCATION = "test_wallet_file.txt"

    def setUp(self):
        if os.path.exists(wallet.WALLET_LOCATION):
            os.remove(wallet.WALLET_LOCATION)

    def test_create(self):
        tx_in = TxIn('id', 1)
        utxo = UnspentTxOut('id', 1, '00045ac146da77da2c9590cc3fd344405b3d808dba6ab76d872415e1e0505c2ed311afea3a71870bf48d746ae355b9deb145b0acb4b0986dc4d269b37334f935e8bc', 10)

        tx_out = TxOut(10, '00045ac146da77da2c9590cc3fd344405b3d808dba6ab76d872415e1e0505c2ed311afea3a71870bf48d746ae355b9deb145b0acb4b0986dc4d269b37334f935e8bc')
        tx = Transaction([tx_in], [tx_out])
        tx.id = tx.get_id()
        tx_in.signature = tx.sign_tx_in(0, 'e2b3157838803983fdc5eed680f6312069f0fa5199c2c02d80c74fc2212880cf', [utxo])



        tp = TransactionPool()
        tp.add_to_transaction_pool(tx, [utxo])

        transactions = tp.get_transactions()
        self.assertEqual(len(transactions), 1)

