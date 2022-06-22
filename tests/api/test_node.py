import json
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

    def test_mine_blocks_no_transactions(self):
        with app.test_client() as test_client:
            headers = {'Content-type': 'application/json'}
            response = test_client.post('/mine-block', headers=headers)
            self.assertEqual(response.status_code, 200)
            json = response.json


            #Get latest block and confirm it matches
            response = test_client.get('/latest-block', headers=headers)
            self.assertEqual(response.json, json)

            #Mine a few more blocks
            test_client.post('/mine-block', headers=headers)
            test_client.post('/mine-block', headers=headers)
            test_client.post('/mine-block', headers=headers)

            #Call for the full chain
            response = test_client.get('/blocks', headers=headers)

            full_chain = response.json
            print(full_chain)
            self.assertEqual(len(full_chain), 5)

            self.assertEqual(full_chain[0]['data'], [])

    @requests_mock.mock()
    def test_send_transaction(self, m):
        with app.test_client() as test_client:
            register_w_peer_post = m.post('http://testhost:8002/peer')
            send_block_to_peer_post = m.post('http://testhost:8002/receive-block')
            send_transaction_to_peer_post = m.post('http://testhost:8002/receive-transactions')

            m.get('http://testhost:8002/transaction-pool', json=[])
            headers = {'Content-type': 'application/json'}

            #add a peer
            genesis_block = {'data': [],
                             'hash': '2ed4d17ce6cca7550d4024bba70be5287ee71cc871853ccf9379e68558f4b1ca', 'index': 0,
                             'previous_hash': None, 'nonce':0, 'timestamp': 1465154705, 'difficulty': 0}

            m.get('http://testhost:8002/latest-block', json=genesis_block)
            response = test_client.post('/peer', json={'host': 'testhost', 'port': 8002}, headers=headers)
            self.assertEqual(response.status_code, 200)

            #mine a block so we have some coins
            headers = {'Content-type': 'application/json'}
            response = test_client.post('/mine-block', headers=headers)
            self.assertEqual(response.status_code, 200)


            # Get the balance, should be 50 from the coinbase block
            response = test_client.get('/balance', headers=headers)
            self.assertEqual(response.json, 50)

            #Now we want to send one coin to an address
            json_body = {"address": "00048ef1ddedf42ca1d0461149cdc7d50502da8eb2f5976296b0752a0771ff8c023bfb8dd8b13880d6eb210141844fe06c0cac357222081d4e4709fb9224ea00fc21",
                       'amount': 1}

            response = test_client.post('/send-transaction', json=json_body, headers=headers)
            self.assertEqual(response.status_code, 200)

            #Now make sure the transaction is there.
            response = test_client.get('/transaction-pool', headers=headers)
            transactions = response.json
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(transactions), 1)


    @requests_mock.mock()
    def test_mine_blocks_transaction_pool(self, m):
        with app.test_client() as test_client:
            m.post('http://testhost:8002/peer')
            m.post('http://testhost:8002/receive-block')
            m.post('http://testhost:8002/receive-transactions')
            headers = {'Content-type': 'application/json'}
            transaction_pool = {'host': 'localhost', 'port': 8001, 'pool': '[{"tx_ins": [{"tx_out_id": "d72773cd3c39988e9a1ebf40ba9c3dcee5ec2738482ebc4c38c22aac91942f12", "tx_out_index": 0, "signature": "304602210098945858b615896a711a3a4c36858fd7fe041dcd126a7bd501e9c04e5e48c086022100aa4fba9bee7d8e100bc3d019cd21c36a308aed5bf570466269d99ce5142c8060"}], "tx_outs": [{"amount": 1, "address": "00048ef1ddedf42ca1d0461149cdc7d50502da8eb2f5976296b0752a0771ff8c023bfb8dd8b13880d6eb210141844fe06c0cac357222081d4e4709fb9224ea00fc21"}, {"amount": 49, "address": "000455c273c248ac9eb9045b689603fcda9863fb9b01fb9a2abb97a93783043aedecc9305d301db9dcb36af547fdf59835404ffc40f13173b190fda55afabf0471f8"}], "id": "2c90d70e52896ecb29daa9fa4015303d90079507eb5e7a185d36a8f789f23558"}]'}

            # mine a block so we have some coins
            headers = {'Content-type': 'application/json'}
            response = test_client.post('/mine-block', headers=headers)

            # Now we want to send one coin to an address
            json_body = {
                "address": "00048ef1ddedf42ca1d0461149cdc7d50502da8eb2f5976296b0752a0771ff8c023bfb8dd8b13880d6eb210141844fe06c0cac357222081d4e4709fb9224ea00fc21",
                'amount': 1}

            response = test_client.post('/send-transaction', json=json_body, headers=headers)
            self.assertEqual(response.status_code, 200)

            #Mine a block
            test_client.post('/mine-block', headers=headers)
            self.assertEqual(response.status_code, 200)

            #Call for the full chain
            response = test_client.get('/blocks', headers=headers)

            full_chain = response.json
            print(full_chain)
            self.assertEqual(len(full_chain), 3)




    @requests_mock.mock()
    def test_add_peer_no_new_blocks(self, m):
        genesis_block = {'data': [], 'hash': '2ed4d17ce6cca7550d4024bba70be5287ee71cc871853ccf9379e68558f4b1ca', 'index': 0, 'previous_hash': None, 'timestamp': 1465154705, 'nonce': 0, 'difficulty': 0}
        with app.test_client() as test_client:
            m.get('http://testhost:8002/latest-block', json=genesis_block)
            m.get('http://testhost:8002/transaction-pool', json=[])
            headers = {'Content-type': 'application/json'}
            register_w_peer_post = m.post('http://testhost:8002/peer')

            response = test_client.post('/peer', json={'host': 'testhost', 'port': 8002}, headers=headers)
            self.assertEqual(response.status_code, 200)

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

    def test_mine_blocks_with_transaction(self):
        with app.test_client() as test_client:
            #First mine a block so we have some COINBASE
            headers = {'Content-type': 'application/json'}
            response = test_client.post('/mine-block', headers=headers)
            self.assertEqual(response.status_code, 200)

            #Get the balance, should be 50 from the coinbase block
            response = test_client.get('/balance', headers=headers)
            self.assertEqual(response.json, 50)

            headers = {'Content-type': 'application/json'}
            response = test_client.post('/mine-transaction',  json={'address': '00048ef1ddedf42ca1d0461149cdc7d50502da8eb2f5976296b0752a0771ff8c023bfb8dd8b13880d6eb210141844fe06c0cac357222081d4e4709fb9224ea00fc21', 'amount': 20}, headers=headers)
            self.assertEqual(response.status_code, 200)

            json = response.json
            self.assertEqual(len(json['data']), 2)

            response = test_client.get('/balance', headers=headers)
            self.assertEqual(response.json, 80)   #50 initial coins, 50 coins on transaction mine, -20 sent away == 80


    @requests_mock.mock()
    @patch('transactions.process_transactions')  # Dont want to test Transactions here, just the blockchain
    def test_add_peer_1_new_block(self, m, transactions_mock):
        transactions_mock.return_value.transactions_mock.return_value = []
        new_block = {'data': [],
                         'hash': '8d4ddc782ce04450dd5cdb65667bd1dbbe39858584cef264c6aa26d77674e57d', 'index': 1,
                         'previous_hash': blockchain.genesis_block.hash, 'timestamp': 1465154705, 'nonce': 0, 'difficulty': 0}




        with app.test_client() as test_client:
            m.get('http://testhost:8002/latest-block', json=new_block)
            register_w_peer_post = m.post('http://testhost:8002/peer')
            m.get('http://testhost:8002/transaction-pool', json=[])
            headers = {'Content-type': 'application/json'}
            response = test_client.post('/peer', json={'host': 'testhost', 'port': 8002}, headers=headers)
            self.assertEqual(response.status_code, 200)

            self.assertEqual(register_w_peer_post.last_request.json(), {'host': 'localhost', 'port': 8001})

            # Call for the full chain
            response = test_client.get('/blocks', headers=headers)
            full_chain = response.json

            # block after genesis block returned, so we added it to our chain
            self.assertEqual(len(full_chain), 2)
            self.assertEqual(full_chain[1]['data'], [])


    @requests_mock.mock()
    def test_add_peer_replace_chain(self, m):
        full_chain = [
            {'data': [], 'hash': '2ed4d17ce6cca7550d4024bba70be5287ee71cc871853ccf9379e68558f4b1ca',
             'index': 0, 'previous_hash': None, 'timestamp': 1465154705, 'nonce': 0, 'difficulty': 0},
            {'data': [], 'hash': 'ba8eda44f270fb8d63d09fefc8059440a27a5406fc51714db8d29f86b244d30b', 'index': 1,
             'previous_hash': '2ed4d17ce6cca7550d4024bba70be5287ee71cc871853ccf9379e68558f4b1ca',
             'timestamp': 1652975062, 'nonce': 0, 'difficulty': 0},
            {'data': [], 'hash': 'a9db9c5b04d60e3739ff38d32193f820b1112cc7ddf4d63424d02b65e3a72156', 'index': 2,
             'previous_hash': 'ba8eda44f270fb8d63d09fefc8059440a27a5406fc51714db8d29f86b244d30b',
             'timestamp': 1652975062, 'nonce': 0, 'difficulty': 0},
            {'data': [], 'hash': '5e1f689fed5395bb3a8c82ce93b745ed4ee9cff6ac1ac7df5e5bff95c4ba0b47', 'index': 3,
             'previous_hash': 'a9db9c5b04d60e3739ff38d32193f820b1112cc7ddf4d63424d02b65e3a72156',
             'timestamp': 1652975062, 'nonce': 0, 'difficulty': 0},
            {'data': [], 'hash': 'c82c09528207d6e96b7e5e5c23ce27d69b44918f4c8308d6eb78b889807456f3', 'index': 4,
             'previous_hash': '5e1f689fed5395bb3a8c82ce93b745ed4ee9cff6ac1ac7df5e5bff95c4ba0b47',
             'timestamp': 1652975062, 'nonce': 0, 'difficulty': 0}]

        new_block = {'data': [],
                         'hash': 'ff51f5f4f0719e898068a207527f04f7b8dfaef9cbaa04a228f179ee905fb091', 'index': 2,
                         'previous_hash': '14f2979fcf2e3a1144d40b4561659169b838b948dda3478b72af7f2f50acca42', 'timestamp': 1465154705, 'nonce': 0, 'difficulty': 0}

        with app.test_client() as test_client:
            m.get('http://testhost:8002/latest-block', json=new_block)
            m.get('http://testhost:8002/blocks', json=full_chain)
            m.get('http://testhost:8002/transaction-pool', json=[])
            register_w_peer_post = m.post('http://testhost:8002/peer')

            headers = {'Content-type': 'application/json'}
            response = test_client.post('/peer', json={'host': 'testhost', 'port': 8002}, headers=headers)
            self.assertEqual(response.status_code, 200)

            # Call for the full chain
            response = test_client.get('/blocks', headers=headers)
            full_chain = response.json

            # unknown block was returned, so we replaced the full chain from the new peer
            self.assertEqual(len(full_chain), 5)


#TODO: Tests for Adjusted Difficulty

if __name__ == '__main__':
    unittest.main()
