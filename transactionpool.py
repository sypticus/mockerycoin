from transactions import Transaction, UnspentTxOut, TxIn
import transactions


class TransactionPool:

    def __init__(self):
        self.transaction_pool: [Transaction] = []

    def get_transactions(self):
        return self.transaction_pool

    def add_to_transaction_pool(self, transaction: Transaction, unspent_tx_outs: [UnspentTxOut]):
        transactions.validate_transaction(transaction, unspent_tx_outs)
        self.is_valid_tx_for_pool(transaction)
        self.transaction_pool.append(transaction)

    def is_valid_tx_for_pool(self, transaction: Transaction):
        p_tx_ins = []
        for transaction in self.transaction_pool:
            p_tx_ins.extend(transaction.tx_ins)

        for t_tx_in in transaction.tx_ins:
            if next((p_tx_in for p_tx_in in p_tx_ins
                     if t_tx_in.tx_out_index == p_tx_in.tx_out_index and t_tx_in.tx_out_id == p_tx_in.tx_out_id), None):
                raise ValueError("Transaction contains a tx_in which is already in transaction pool")

    def update_transaction_pool(self, unspent_tx_outs: [UnspentTxOut]):
        invalid_txs = []
        for tx in self.transaction_pool:
            for tx_in in tx.tx_ins:
                if not has_tx_in(tx_in, unspent_tx_outs):
                    invalid_txs.append(tx)
                    break
        return [tx for tx in unspent_tx_outs if tx not in invalid_txs]

def has_tx_in(tx_in: TxIn, unspent_tx_outs: [UnspentTxOut]):
    if any(utxo.tx_out_id == tx_in.tx_out_id and utxo.tx_out_index == tx_in.tx_out_index for utxo in unspent_tx_outs):
        return True
    return False
