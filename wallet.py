from os.path import exists

import hashutils
from transactions import UnspentTxOut, TxIn, TxOut, Transaction

WALLET_LOCATION = 'wallet_file.txt'  #TODO encrypt this


class Wallet:
    def __init__(self):
        if not exists(WALLET_LOCATION):
            _private_key = hashutils.generate_private_key()
            f = open(WALLET_LOCATION, "w")
            f.write(_private_key)
            f.close()
        else:
            f = open(WALLET_LOCATION, "r")
            _private_key: str = f.read()
            f.close()
        self.private_key = _private_key
        self.pub_key = self.get_pub_key()

    def get_pub_key(self):
        return hashutils.get_public_key_from_private(self.private_key)

    def get_balance(self, unspent_tx_outs: [UnspentTxOut]) -> float:
        balance = 0
        for ustxo in unspent_tx_outs:
            if ustxo.address == self.pub_key:
                ustxo: UnspentTxOut = ustxo
                balance += ustxo.amount
        return balance

    def get_unspent_tx_outs(self, unspent_tx_outs: [UnspentTxOut]) -> [UnspentTxOut]:
        return [unspent_tx_out for unspent_tx_out in unspent_tx_outs if unspent_tx_out.address  == self.pub_key]

    def create_transaction(self, receiving_address: str, amount_to_send: float, unspent_tx_outs: [UnspentTxOut], transaction_pool: [Transaction]) -> Transaction:
        my_utxos = self.get_unspent_tx_outs(unspent_tx_outs)
        my_utxos = filter_tx_pool_transactions(my_utxos, transaction_pool)

        unspent_tx_outs_to_spend, extra_amount = find_tx_outs_for_amount(amount_to_send, my_utxos)
        unsigned_tx_ins: [TxIn] = []
        for utxo in unspent_tx_outs_to_spend:
            unsigned_tx_ins.append(TxIn(utxo.tx_out_id, utxo.tx_out_index))



        tx_outs = [TxOut(amount_to_send, receiving_address)]
        if extra_amount != 0: #When summing up the totals from utxos, there was some left over. It needs to be a new TXO back to our own wallet
            tx_outs.append(TxOut(extra_amount, self.pub_key))



        tx: Transaction = Transaction(unsigned_tx_ins, tx_outs)
        tx.id = tx.get_id()

        for idx, tx_in in enumerate(tx.tx_ins):
            tx_in: TxIn = tx_in
            tx_in.signature = tx.sign_tx_in(idx, self.private_key, my_utxos)

        return tx



#Filter out any tx's that have a tx_in that are in the tx pool.
def filter_tx_pool_transactions(unspent_tx_outs: [UnspentTxOut], transaction_pool: [Transaction]) -> [UnspentTxOut]:
    tx_ins = []
    for transaction in transaction_pool:
        tx_ins.extend(transaction.tx_ins)

    to_keep: [UnspentTxOut] = []
    for utxo in unspent_tx_outs:
        if not next((tx_in for tx_in in tx_ins if
                     tx_in.tx_out_index == utxo.tx_out_index and tx_in.tx_out_id == utxo.tx_out_id),
                    None):
            to_keep.append(utxo)
    return to_keep

def find_tx_outs_for_amount (amount: float, unspent_tx_outs: [UnspentTxOut]):
    cumulative_amount = 0
    included_unspent_tx_outs: [UnspentTxOut] = []
    for unspent_tx_out in unspent_tx_outs:
        included_unspent_tx_outs.append(unspent_tx_out)
        cumulative_amount = cumulative_amount + unspent_tx_out.amount
        if cumulative_amount >= amount:
            extra_amount = cumulative_amount - amount
            return unspent_tx_outs, extra_amount

    raise ValueError("Not enough amount in wallet to cover: {}".format(amount))

