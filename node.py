import json
from types import SimpleNamespace

from werkzeug.exceptions import HTTPException, BadRequest
from flask import Flask, g, request, jsonify

import utils
from block import Block
from blockchain import Blockchain
from p2p import P2P, NodeAddress

from argparse import ArgumentParser

from transactions import Transaction
from wallet import Wallet




app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.json_encoder = utils.ComplexEncoder

@app.route('/status')
def test():
    return jsonify({"host": p2p.my_host, "port": p2p.my_port}), 200


@app.route('/latest-block')
def get_latest_block():
    return blockchain.get_latest_block().toJson()


@app.route('/balance')
def get_wallet_balance():
    return jsonify(blockchain.get_wallet_balance(wallet))


@app.route('/blocks')
def get_full_chain():
    return jsonify([block.__dict__ for block in blockchain.chain])


@app.route('/transaction-pool')
def get_transaction_pool():
    return jsonify(blockchain.transaction_pool.get_transactions())


@app.route('/mine-block', methods=['POST'])
def mine_block():
    new_block: Block = blockchain.mine_next_block(wallet)
    p2p.broadcast_block(new_block)
    return jsonify(new_block), 200


@app.route('/mine-transaction', methods=['POST'])
def mine_transaction():
    req = request.get_json()
    address = get_or_raise(req, 'address')
    amount = get_or_raise(req, 'amount')
    new_block: Block = blockchain.mine_next_block_transaction(address, amount, wallet)
    p2p.broadcast_block(new_block)
    return new_block.toJson(), 200


@app.route('/send-transaction', methods=['POST'])
def send_transaction():
    req = request.get_json()
    address = get_or_raise(req, 'address')
    amount = get_or_raise(req, 'amount')
    new_transaction: Transaction = blockchain.send_transaction(address, amount, wallet)
    p2p.broadcast_transaction_pool(blockchain.transaction_pool.get_transactions())
    return jsonify(new_transaction), 200


@app.route('/receive-transactions', methods=['POST'])
def receive_transaction():
    req = request.get_json()
    pool = get_or_raise(req, 'pool')
    host = get_or_raise(req, 'host')
    port = get_or_raise(req, 'port')
    peer = NodeAddress(host, port)

    print("Peer {} is sending me its transaction pool".format(peer))
    txs: [Transaction] = json.loads(pool, object_hook=lambda d: SimpleNamespace(**d))
    handle_transaction_from_peer(txs)
    return jsonify({"status": "ok"}), 200


def handle_transaction_from_peer(tx_dicts):
    for tx in tx_dicts:
        try:
            tx = Transaction.from_dict(tx)
            blockchain.handle_received_transaction(tx)
            p2p.broadcast_transaction_pool(blockchain.transaction_pool.get_transactions())
        except ValueError as e:
            print("Adding received transaction threw an error. Ignoring and moving on.")
            return


@app.route('/peers')
def get_peers():
    return jsonify([peer.__dict__ for peer in p2p.peers]), 200


@app.route('/peer', methods=['POST'])
def add_peer():
    req = request.get_json()

    host = get_or_raise(req, 'host')
    port = get_or_raise(req, 'port')
    new_peer = NodeAddress(host, port)

    if p2p.add_peer(new_peer):
        print("New peer {} added, getting its latest block".format(new_peer))
        peers_latest_block: Block = p2p.query_lastest_block(new_peer)
        handle_block_from_peer(peers_latest_block, new_peer)

        print("Peer {} was new to me, going to ensure I am registered with it.".format(new_peer))
        p2p.register_with_peer(new_peer)

    # TODO: What if peer already exists?
    return jsonify({"status": "ok"}), 200


@app.route('/receive-block', methods=['POST'])
def receive_block():
    req = request.get_json()
    block = get_or_raise(req, 'block')
    host = get_or_raise(req, 'host')
    port = get_or_raise(req, 'port')
    peer = NodeAddress(host, port)

    print("Peer {} is sending me its latest block.".format(peer))

    handle_block_from_peer(Block.from_dict(block), peer)
    return jsonify({"status": "ok"}), 200


def handle_block_from_peer(new_block: Block, peer: NodeAddress):
    my_latest_block = blockchain.get_latest_block()
    if new_block.index > my_latest_block.index:
        print("Block from node, {} has a later index, I may be behind.".format(peer))

        if my_latest_block.hash == new_block.previous_hash:
            print("New nodes latest block is 1 block ahead, adding it to my chain")

            if blockchain.add_block(new_block):
                print("Block added to chain, broadcasting new block to all peers")
                p2p.broadcast_block(new_block)

        else:
            print("My chain is shorter than the change of the latest block, pulling entire chaing from peer.")
            new_chain = p2p.query_entire_chain(peer)
            blockchain.replace_chain(new_chain)
    else:
        print("Received block is not ahead of my current block, doing nothing.")


def get_or_raise(values: [], key: str):
    if key not in values:
        raise BadRequest("{} is a required field.".format(key))
    return values[key]


@app.errorhandler(BadRequest)
def handle_400_error(e: BadRequest):
    return {'message': e.description}, 400


# todo: this is ugly, fix this later
host = 'localhost'
port = 8001
p2p = P2P(host, port)
blockchain = Blockchain()
wallet = Wallet()

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=8001)
    args = parser.parse_args()
    port = args.port
    p2p = P2P(host, port)
    app.run(host=host, port=port)
