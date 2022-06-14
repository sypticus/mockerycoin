import unittest
from unittest.mock import patch
from ecdsa import ellipticcurve
from ellipticcurve import PrivateKey, Ecdsa, Signature

import block
import hashutils
import transactions
from transactions import Transaction, TxIn, TxOut, UnspentTxOut


class TransactionTestCase(unittest.TestCase):

    def test_create_validate_transaction(self):
        pub_key = "00048ef1ddedf42ca1d0461149cdc7d50502da8eb2f5976296b0752a0771ff8c023bfb8dd8b13880d6eb210141844fe06c0cac357222081d4e4709fb9224ea00fc21"
        priv_key = "5af128debc1b9122da06359c4498b208b829879cf13b3d6cac5d1260c0fd967a"
        utxo1 = UnspentTxOut('tx_out_4', 0, pub_key, 15)

        tx_out1 = TxOut(15, pub_key)
        tx_in1 = TxIn('tx_out_4', 0)
        transaction = Transaction([tx_in1], [tx_out1])
        transaction.id = transaction.get_id()
        tx_in1.signature = transaction.sign_tx_in(0, priv_key, [utxo1])


        transactions.validate_transaction_structure(transaction)

        transactions.validate_transaction(transaction, [utxo1])

        self.assertEqual('305c8a0ee6601aee1dfe09d41a1cbf7f1fec9599e543f73f808d2d74917e86f9', transaction.id)

    def test_updated_unspent_tx_outs_none_consumed(self):
        utxo1 = UnspentTxOut('tx_out_4', 1, 'some_key', 15)
        utxo2 = UnspentTxOut('tx_out_5', 1, 'some_key', 6)


        tx_out1 = TxOut(2, 'address_1')
        tx_in1 = TxIn('tx_out_1', 1)
        tx1 = Transaction([tx_in1], [tx_out1])

        tx_out2 = TxOut(3, 'address_2')
        tx_in2 = TxIn('tx_out_2', 2)
        tx2 = Transaction([tx_in2], [tx_out2])

        tx_out3 = TxOut(7, 'address_3')
        tx_in3 = TxIn('tx_out_3', 3)
        tx3 = Transaction([tx_in3], [tx_out3])


        utxos: [UnspentTxOut] = transactions.updated_unspent_tx_outs([tx1, tx2, tx3], [utxo1, utxo2])

        self.assertEqual(len(utxos), 5)


    def test_updated_unspent_tx_outs_one_consumed(self):
        utxo1 = UnspentTxOut('tx_out_4', 1, 'some_key', 15) #This will be consumed by tx2
        utxo2 = UnspentTxOut('tx_out_5', 1, 'some_key', 6)


        tx_out1 = TxOut(2, 'address_1')
        tx_in1 = TxIn('tx_out_1', 1)
        tx1 = Transaction([tx_in1], [tx_out1])

        tx_out2 = TxOut(3, 'address_2')
        tx_in2 = TxIn('tx_out_4', 1) #This consumes the existing unspent utxo1
        tx2 = Transaction([tx_in2], [tx_out2])

        tx_out3 = TxOut(7, 'address_3')
        tx_in3 = TxIn('tx_out_3', 3)
        tx3 = Transaction([tx_in3], [tx_out3])


        utxos: [UnspentTxOut] = transactions.updated_unspent_tx_outs([tx1, tx2, tx3], [utxo1, utxo2])

        self.assertEqual(len(utxos), 4) # We removed the spent utxo1

    def test_sign_tx_in(self):
        pub_key = "00048ef1ddedf42ca1d0461149cdc7d50502da8eb2f5976296b0752a0771ff8c023bfb8dd8b13880d6eb210141844fe06c0cac357222081d4e4709fb9224ea00fc21"
        priv_key = "5af128debc1b9122da06359c4498b208b829879cf13b3d6cac5d1260c0fd967a"
        tx_out1 = TxOut(12, 'abc')
        tx_in1 = TxIn('abc', 12)
        transaction = Transaction([tx_in1], [tx_out1])
        transaction.id = transaction.get_id()
        self.assertEqual(transaction.id, "3bc4c8559f042da2bf48aff6822a597e319da30f3661c87eea3fc74b2fd06e56")

        ustxo = UnspentTxOut('abc', 12, pub_key, 123.0)
        signature_str = transaction.sign_tx_in(0, priv_key, [ustxo])

        signature = hashutils.signature_from_string(signature_str)

        self.assertTrue(Ecdsa.verify(transaction.id, signature, PrivateKey.fromString(priv_key).publicKey()))


if __name__ == '__main__':
    unittest.main()
