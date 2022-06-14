import unittest
from unittest.mock import patch

import requests_mock

import blockchain
from node import app
import node
from p2p import P2P


class NodeTestCase(unittest.TestCase):

    def setUp(self):
        node.port = 8001  # Todo: This should be configurable
        node.host = 'localhost'
        node.p2p = P2P(node.host, node.port)
        node.blockchain = blockchain.Blockchain()

    def test_status(self):
        with app.test_client() as test_client:
            response = test_client.get('/status')

            json = response.json
            self.assertEqual(json['host'], 'localhost')  # add assertion here
            self.assertEqual(json['port'], 8001)  # add assertion here

    @patch('transactions.process_transactions')  # Dont want to test Transactions here, just the blockchain
    def test_mine_blocks(self, transactions_mock):
        with app.test_client() as test_client:
            transactions_mock.return_value.transactions_mock.return_value = []
            headers = {'Content-type': 'application/json'}
            response = test_client.post('/mine-block', json={'block_data': 'block 1'}, headers=headers)

            json = response.json
            self.assertEqual(json['data'], 'block 1')

            #Get latest block and confirm it matches
            response = test_client.get('/latest-block', headers=headers)
            self.assertEqual(response.json, json)


            #Mine a few more blocks
            test_client.post('/mine-block', json={'block_data': 'block 2'}, headers=headers)
            test_client.post('/mine-block', json={'block_data': 'block 3'}, headers=headers)
            test_client.post('/mine-block', json={'block_data': 'block 4'}, headers=headers)

            #Call for the full chain
            response = test_client.get('/blocks', headers=headers)

            full_chain = response.json
            print(full_chain)
            self.assertEqual(len(full_chain), 5)

            self.assertEqual(full_chain[0]['data'], 'my genesis block!!')
            self.assertEqual(full_chain[1]['data'], 'block 1')
            self.assertEqual(full_chain[2]['data'], 'block 2')
            self.assertEqual(full_chain[3]['data'], 'block 3')
            self.assertEqual(full_chain[4]['data'], 'block 4')


    @requests_mock.mock()
    def test_add_peer_no_new_blocks(self, m):
        genesis_block = {'data': 'my genesis block!!', 'hash': '2ed4d17ce6cca7550d4024bba70be5287ee71cc871853ccf9379e68558f4b1ca', 'index': 0, 'previous_hash': None, 'timestamp': 1465154705}
        with app.test_client() as test_client:
            m.get('http://testhost:8002/latest-block', json=genesis_block)
            headers = {'Content-type': 'application/json'}
            response = test_client.post('/peer', json={'host': 'testhost', 'port': 8002}, headers=headers)


            # Call for the full chain
            response = test_client.get('/blocks', headers=headers)
            full_chain = response.json

            # genesis block returned, so no change in our chain
            self.assertEqual(len(full_chain), 1)

            # Call for the list of peers
            response = test_client.get('/peers', headers=headers)
            peers = response.json
            self.assertEqual(len(peers), 1)
            self.assertEqual(peers[0]['host'], 'testhost')


    @requests_mock.mock()
    @patch('transactions.process_transactions')  # Dont want to test Transactions here, just the blockchain
    def test_add_peer_1_new_block(self, m, transactions_mock):
        transactions_mock.return_value.transactions_mock.return_value = []
        new_block = {'data': 'block_2',
                         'hash': 'ff51f5f4f0719e898068a207527f04f7b8dfaef9cbaa04a228f179ee905fb091', 'index': 1,
                         'previous_hash': blockchain.genesis_block.hash, 'timestamp': 1465154705, 'nonce': 0, 'difficulty': 0}




        with app.test_client() as test_client:
            m.get('http://testhost:8002/latest-block', json=new_block)
            headers = {'Content-type': 'application/json'}
            response = test_client.post('/peer', json={'host': 'testhost', 'port': 8002}, headers=headers)

            # Call for the full chain
            response = test_client.get('/blocks', headers=headers)
            full_chain = response.json

            # block after genesis block returned, so we added it to our chain
            self.assertEqual(len(full_chain), 2)
            self.assertEqual(full_chain[1]['data'], 'block_2')


    @requests_mock.mock()
    def test_add_peer_replace_chain(self, m):
        full_chain = [
            {'data': 'my genesis block!!', 'hash': '2ed4d17ce6cca7550d4024bba70be5287ee71cc871853ccf9379e68558f4b1ca',
             'index': 0, 'previous_hash': None, 'timestamp': 1465154705, 'nonce': 0, 'difficulty': 0},
            {'data': 'block 1', 'hash': '56a251be770d2859bfa9677f77496d59c32a1486074559bcd186269c237a009e', 'index': 1,
             'previous_hash': '2ed4d17ce6cca7550d4024bba70be5287ee71cc871853ccf9379e68558f4b1ca',
             'timestamp': 1652975062, 'nonce': 0, 'difficulty': 0},
            {'data': 'block 2', 'hash': '2ad34364df30644b9ba6754d23ff50bdc584b311bc9743c29bc98d4578132850', 'index': 2,
             'previous_hash': '56a251be770d2859bfa9677f77496d59c32a1486074559bcd186269c237a009e',
             'timestamp': 1652975062, 'nonce': 0, 'difficulty': 0},
            {'data': 'block 3', 'hash': 'b0d6462436e5a08cc6f0d03c4e20e5f217e2cd1fc8557fb8140d88cdcfbb20a2', 'index': 3,
             'previous_hash': '2ad34364df30644b9ba6754d23ff50bdc584b311bc9743c29bc98d4578132850',
             'timestamp': 1652975062, 'nonce': 0, 'difficulty': 0},
            {'data': 'block 4', 'hash': '66a138c8e64ffc1258f45e2a6300b0cd21dfd7a5470d715f8c38466a9cea5d05', 'index': 4,
             'previous_hash': 'b0d6462436e5a08cc6f0d03c4e20e5f217e2cd1fc8557fb8140d88cdcfbb20a2',
             'timestamp': 1652975062, 'nonce': 0, 'difficulty': 0}]

        new_block = {'data': 'block_3',
                         'hash': 'ff51f5f4f0719e898068a207527f04f7b8dfaef9cbaa04a228f179ee905fb091', 'index': 2,
                         'previous_hash': '14f2979fcf2e3a1144d40b4561659169b838b948dda3478b72af7f2f50acca42', 'timestamp': 1465154705, 'nonce': 0, 'difficulty': 0}

        with app.test_client() as test_client:
            m.get('http://testhost:8002/latest-block', json=new_block)
            m.get('http://testhost:8002/blocks', json=full_chain)

            headers = {'Content-type': 'application/json'}
            response = test_client.post('/peer', json={'host': 'testhost', 'port': 8002}, headers=headers)

            # Call for the full chain
            response = test_client.get('/blocks', headers=headers)
            full_chain = response.json

            # unknown block was returned, so we replaced the full chain from the new peer
            self.assertEqual(full_chain[0]['data'], 'my genesis block!!')
            self.assertEqual(full_chain[1]['data'], 'block 1')
            self.assertEqual(full_chain[2]['data'], 'block 2')
            self.assertEqual(full_chain[3]['data'], 'block 3')
            self.assertEqual(full_chain[4]['data'], 'block 4')


#TODO: Tests for Adjusted Difficulty

if __name__ == '__main__':
    unittest.main()
