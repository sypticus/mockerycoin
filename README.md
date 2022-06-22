# mockerycoin
A fully functional Python Flask implementation of lhartikk's naivecoin.
https://lhartikk.github.io/

Also took some inspiration from https://github.com/benpankow/naivecoin-python and https://github.com/adi2381/py-blockchain

## Running the nodes

- Clone the project from https://github.com/sypticus/mockerycoin
- pip install -r requirements.txt

### Run a single node
- ```python3 node.py -p 8001```

### Start a second node
- ```python3 node.py -p 8002```

As many nodes can be run as you like.
Each time a node starts up you will need to register it with the other nodes. In the future I would like this to happen automatically.

-```curl http://localhost:8001/peer -H 'Content-Type: application/json' -d '{"host":"localhost", "port": 8002}'```

This will register 8002 with 8001, and 8001 with 8002. The nodes will also send each other their current blockchain and transaction pool

## Mine some coins
-```curl http://localhost:8002/mine-block -H 'Content-Type: application/json' -X POST```

This will mine a new block, which will add the coinbase value of 50 coins. Each time you mine the nodes will speak to eachother and shre their versions of the block chaing
The highest level of "difficulty" will prevail. "Difficulty" will increase as more coins are made in a rapid time, requiring more leading 0's in the hash of the block.

## Get your balance
-```curl http://localhost:8002/balance -H 'Content-Type: application/json'```

This shows how many coins you have in your wallet. Your wallet is identified by a private key living in a file on the node.

## Submit a payment

- First you need to get the pubkey you want to send to. Since this setup currently has a single wallet per node, we will query the other node for its pubkey and send the money there.

```curl http://localhost:8001/pubkey -H 'Content-Type: application/json'```

- Now send a payment request to our 8002 node
- ```curl http://localhost:8002/send-transaction -H 'Content-Type: application/json' -d '{"amount": 22.50, "address": "PUBKEY_FROM_ABOVE"}'```

This doesnt actually complete the transaction, as it still has to be mined by a node. However it does send the transaction to all nodes, so the next time a block is mined, it will contain it.
You can see the list of un-mined transactions for each node should be the same.
```curl http://localhost:8001/transaction-pool -H 'Content-Type: application/json'```

- Mine another block.
```curl http://localhost:8001/mine-block -H 'Content-Type: application/json' -X POST```
This will complete the transaction, as well as give the reward coinbase to 8001 for mining. You can now see the correct balances in both wallets!

```curl http://localhost:8002/balance -H 'Content-Type: application/json'```

`77.5`

```curl http://localhost:8001/balance -H 'Content-Type: application/json'```

`22.5`

Now all the un-mined transactions are gone from all nodes
```curl http://localhost:8001/transaction-pool -H 'Content-Type: application/json'```


## Running tests
Just run `pytest` from root.
