from json import dumps

from flask import jsonify

import hashutils

COINBASE_AMOUNT: int = 50

class TxIn:  #unlocks the coins
    def __init__(self, tx_out_id: str, tx_out_index: int):
        self.tx_out_id: str = tx_out_id
        self.tx_out_index: int = tx_out_index
        self.signature = None

    @classmethod
    def from_dict(cls, dict):
        new_tx_in = cls(dict['tx_out_id'], dict['tx_out_index'])
        new_tx_in.signature = dict.get('signature')
        return new_tx_in

    def __str__(self):
        return str(self.__dict__)
    def __repr__(self):
        return str(self.__dict__)

    def toJson(self):
        return self.__dict__

class TxOut: #locks the coin to an address
    def __init__(self, amount: float, address: str):
        self.amount: float = amount
        self.address: str = address #this is a pubkey

    @classmethod
    def from_dict(cls, dict):
        return cls(dict['amount'], dict['address'])

    def toJson(self):
        return self.__dict__


    def __str__(self):
        return str(self.__dict__)
    def __repr__(self):
        return str(self.__dict__)

class UnspentTxOut:
    def __init__(self, tx_out_id: str, tx_out_index: int, address: str, amount: float):
        self.tx_out_id: str = tx_out_id
        self.tx_out_index: int = tx_out_index
        self.address: str = address
        self.amount: float = amount

    def __str__(self):
        return str(self.__dict__)
    def __repr__(self):
        return str(self.__dict__)

class Transaction:
    def __init__(self, tx_ins: [TxIn], tx_outs:[TxOut]):
        self.tx_ins: [TxIn] = tx_ins
        self.tx_outs: [TxOut] = tx_outs
        self.id = None

    def toJson(self):
        return self.__dict__

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    @classmethod
    def from_dict(cls, dict):
        tx_ins = [TxIn.from_dict(tx_in) for tx_in in dict.get('tx_ins')]
        tx_outs = [TxOut.from_dict(tx_out) for tx_out in dict.get('tx_outs')]
        new_tx = cls(tx_ins, tx_outs)
        new_tx.id = dict.get('id')
        return new_tx

    def get_id(self) -> str:
        tx_in_content: str = ''.join([tx_in.tx_out_id + str(tx_in.tx_out_index) for tx_in in self.tx_ins])
        tx_out_content: str = ''.join([tx_out.address + str(tx_out.amount) for tx_out in self.tx_outs])
        return hashutils.sha256(tx_in_content + tx_out_content)

    def get_tx_in(self, index) -> TxIn:
        return self.tx_ins[index]

    def sign_tx_in(self,  tx_in_index: int, private_key_string: str, unspent_tx_outs: [UnspentTxOut]) -> str:
        tx_in: TxIn = self.get_tx_in(tx_in_index)
        data_to_sign = self.id

        referenced_unspent_tx_out: UnspentTxOut = find_unspent_tx_out(tx_in.tx_out_id, tx_in.tx_out_index, unspent_tx_outs)
        if not referenced_unspent_tx_out:
            print('tx_in.tx_out_id, tx_in.tx_out_index did not point to a valid tx_out in UnspentTXOuts')
            raise ValueError('tx_in.tx_out_id, tx_in.tx_out_index did not point to a valid tx_out in UnspentTXOuts')

        referenced_address = referenced_unspent_tx_out.address

        if hashutils.get_public_key_from_private(private_key_string) != referenced_address:
            print('Trying to sign an input with private key that does not match the address that is referenced in txIn')
            raise ValueError('Trying to sign an input with private key that does not match the address that is referenced in txIn')


        return hashutils.get_signature_string(private_key_string, data_to_sign)



def get_unspent_tx_outs_from_transactions(transactions: [Transaction]) -> [UnspentTxOut]:
    unspent_txs = []
    for transaction in transactions:
        for index, tx_out in enumerate(transaction.tx_outs):
            tx_out: TxOut = tx_out
            unspent_txs.append(UnspentTxOut(transaction.id, index, tx_out.address, tx_out.amount))
    return unspent_txs


def get_consumed_tx_outs_from_transactions(transactions: [Transaction]) ->  [UnspentTxOut]:
    consumed_unspent_txs = []
    for transaction in transactions:
        for tx_in in transaction.tx_ins:
            tx_in: TxIn = tx_in
            consumed_unspent_txs.append(UnspentTxOut(tx_in.tx_out_id, tx_in.tx_out_index, "", 0))
    return consumed_unspent_txs


def find_unspent_tx_out(transaction_id: str, index: int, unspent_tx_outs: [UnspentTxOut])-> UnspentTxOut:
    return next((tx for tx in unspent_tx_outs if tx.tx_out_id == transaction_id and tx.tx_out_index == index), None)


def updated_unspent_tx_outs(transactions: [Transaction], unspent_tx_outs: [UnspentTxOut]) -> [UnspentTxOut]:
    new_unspent_tx_outs = get_unspent_tx_outs_from_transactions(transactions)
    consumed_tx_outs = get_consumed_tx_outs_from_transactions(transactions)

    for unspent_tx_out in unspent_tx_outs:
        unspent_tx_out: UnspentTxOut = unspent_tx_out
        if not find_unspent_tx_out(unspent_tx_out.tx_out_id, unspent_tx_out.tx_out_index, consumed_tx_outs):
            # This unspent tx out was not in the consumed, so its still unspent
            new_unspent_tx_outs.append(unspent_tx_out)

    return new_unspent_tx_outs


def process_transactions(transactions: [Transaction], unspent_tx_outs: [UnspentTxOut], block_index: int):
    for transaction in transactions:
        validate_transaction_structure(transaction)

    validate_block_of_transactions(transactions, unspent_tx_outs, block_index)

    return updated_unspent_tx_outs(transactions, unspent_tx_outs)


def validate_transaction_structure(transaction: Transaction):
    if not transaction.id or type(transaction.id) != str:
        print("Transaction Validation Failed: TransactionId is missing")
        raise ValueError('Transaction Validation Failed: TransactionId is missing')

    for tx_in in transaction.tx_ins:
        validate_tx_in_structure(tx_in)

    for tx_out in transaction.tx_outs:
        is_valid_tx_out_structure(tx_out)


def validate_tx_in_structure(tx_in: TxIn):
    if not tx_in:
        raise ValueError('TXIn Validation Failed: txin is missing')
    if type(tx_in.signature) != str:
        raise ValueError('invalid signature type in txIn')
    if type(tx_in.tx_out_id) != str:
        raise ValueError('invalid tx_out_id type in txIn')
    if type(tx_in.tx_out_index) != int:
        raise ValueError('invalid txOutIndex type in txIn')

def is_valid_tx_out_structure(tx_out: TxOut):
    if not tx_out:
        raise ValueError('TXOut Validation Failed: txout is missing')
    if type(tx_out.address) != str:
        raise ValueError('invalid address type in txOut')
    if type(tx_out.amount) not in (float, int):
        raise ValueError('invalid amount type in txOut')

    validate_address(tx_out.address)


#valid address is a valid ecdsa public key in the 0004 + X-coordinate + Y-coordinate format
def validate_address(address: str):
    if len(address) != 132:
        print('invalid public key length for address')
        raise ValueError('invalid public key length for address')

    int(address, 16) #This will throw a ValueError if address is not hex
    if not address.startswith('0004'):
        raise ValueError('public key must start with 0004')


def validate_block_of_transactions(transactions: [Transaction], unspent_tx_outs: [UnspentTxOut], block_index: int):
    validate_coinbase_tx(transactions[0], block_index)

    for transaction in transactions[1:]:
        validate_transaction(transaction, unspent_tx_outs)


def validate_coinbase_tx(tx: Transaction, index):
    if not tx:
        raise ValueError("Coinbase tx has to exist.")

    if tx.id != tx.get_id():
        raise ValueError("Coinbase tx has an invalid id")

    if len(tx.tx_ins) != 1:
        raise ValueError("Coinbase tx must have only 1 txin")

    if tx.tx_ins[0].tx_out_index != index:
        raise ValueError("TxIn in coinbase must match block height")

    if len(tx.tx_outs) != 1:
        raise ValueError("invalid number of txOuts in coinbase transaction")

    if tx.tx_outs[0].amount != COINBASE_AMOUNT:
        raise ValueError("Invalid coinbase amount in coinbase transaction")


def validate_transaction(transaction: Transaction, unspent_tx_outs: [UnspentTxOut]):
    print("TXUs: {}".format(unspent_tx_outs))
    print("tx: {}".format(transaction))
    if transaction.get_id() != transaction.id:
        print("Transaction Id for transaction {} is not current.".format(transaction.id))
        raise ValueError("Transaction Id for transaction {} is not current.".format(transaction.id))

    total_tx_in_vals: float = 0
    total_tx_out_vals: float = 0

    for tx_in in transaction.tx_ins:
        validate_tx_in(tx_in, transaction, unspent_tx_outs)
        total_tx_in_vals += find_unspent_tx_out(tx_in.tx_out_id, tx_in.tx_out_index, unspent_tx_outs).amount

    for tx_out in transaction.tx_outs:
        total_tx_out_vals += tx_out.amount

    if total_tx_in_vals != total_tx_out_vals:
        print("Total tx_in amounts and tx_out amounts do not match for transaction {}".format(transaction.id))
        raise ValueError("Total tx_in amounts and tx_out amounts do not match for transaction {}".format(transaction.id))



def validate_tx_in(tx_in: TxIn, transaction: Transaction, unspent_tx_outs: [UnspentTxOut]):

    referenced_utxo: UnspentTxOut = find_unspent_tx_out(tx_in.tx_out_id, tx_in.tx_out_index, unspent_tx_outs)
    if not referenced_utxo:
        print("tx_in references a utxo which doesnt exist in the given list")
        raise ValueError("tx_in references a utxo which doesnt exist in the given list")

    address = referenced_utxo.address

    valid = hashutils.verify_signature(address, tx_in.signature, transaction.id)
    if not valid:
        print("Signature could not be verified")
        raise ValueError("Signature could not be verified")


def generate_coinbase_transaction(address: str, block_index: int) -> Transaction:

    tx_in: TxIn = TxIn('', block_index)
    tx_in.signature = ''

    coinbase_tx = Transaction([tx_in], [TxOut(COINBASE_AMOUNT, address)])
    coinbase_tx.id = coinbase_tx.get_id()
    return coinbase_tx