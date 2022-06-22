import json

import requests

from utils import ComplexEncoder
from block import Block
from transactions import Transaction


class NodeAddress:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def __str__(self):
        return "{}:{}".format(self.host, self.port)

    def __eq__(self, other):
        return isinstance(other, NodeAddress) and self.host == other.host and self.port == other.port


class P2P:
    def __init__(self, host, port):
        self.peers = []
        self.my_host = host
        self.my_port = port

    def add_peer(self, new_peer: NodeAddress):
        if new_peer in self.peers:
            print("Peer {} already exists in my nodes.".format(new_peer))
            return False
        print("Current peers are {}".format(self.peers))
        print("Peer {} is new, adding to peers".format(new_peer))
        self.peers.append(new_peer)

        return True


    def query_lastest_block(self, peer: NodeAddress):
        resp = requests.get("http://{}/latest-block".format(peer))
        block = resp.json()

        return Block.from_dict(block)

    def broadcast_block(self, block: Block):
        headers = {'Content-type': 'application/json'}
        for peer in self.peers:
            peer: NodeAddress = peer
            body = {
                'host': self.my_host,
                'port': self.my_port,
                'block': json.dumps(block, cls=ComplexEncoder)
            }

            print("Broadcasting to peer: {}".format(peer))
            resp = requests.post("http://{}/receive-block".format(peer), json=body, headers=headers)

    def broadcast_transaction_pool(self, transactions: [Transaction]):
        headers = {'Content-type': 'application/json'}
        for peer in self.peers:
            peer: NodeAddress = peer
            body = {
                'host': self.my_host,
                'port': self.my_port,
                'pool': json.dumps([transaction for transaction in transactions], cls=ComplexEncoder)
            }

            print("Broadcasting transaction to peer: {}".format(peer))
            resp = requests.post("http://{}/receive-transaction".format(peer), json=body, headers=headers)


    def query_entire_chain(self, peer: NodeAddress):
        resp = requests.get("http://{}/blocks".format(peer))
        blocks = resp.json()

        return [Block.from_dict(block) for block in blocks]

    def register_with_peer(self, peer: NodeAddress):
        headers = {'Content-type': 'application/json'}
        body = {"host": self.my_host, "port": self.my_port}
        requests.post("http://{}/peer".format(peer), json=body, headers=headers)

