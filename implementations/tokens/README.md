# Reference Nytro Implementation

The "Token" class takes regular Nyzo transactions as input, validates them, updates the tokens states, and stores everything in a SQL database.

**To be updated with Protocol version 1.1** 

## 1. Test Setup

- rename `tokens_db_config.sample.json` to `tokens_db_config.json` and edit to point to your sql instance, user and database  
- install requirements `pip3 install -r requirements.txt`
- run the test vectors `python3 test.py`


**Warning:** This test clears the db since test vectors need to start from a blank state.  
Do not run on a production setup or you will need to rescan all historical transactions again. 

## 2. Integration

Once the test step above is ok, you can integrate for use in your own explorer, service...  

The "tokens" class will feed "tokens", "transactions" and "balances" tables with real time state of the tokens and addresses.


### 2.1. Integration with custom data source 

You can feed the Nyzo transactions, starting from first possible block 10650000 to the 
`def parse_nyzo_tx(self, nyzo_tx: list, save_tx: bool=False) -> True:` method

nyzo_tx is a list, defined as 
```
[
  sender: bytes, 
  recipient: bytes, 
  data: bytes, 
  amount: int, 
  timestamp: int, 
  block_height: int, 
  canonical: int, 
  signature: bytes
]
```

`def parse_nyzo_txs(self, nyzo_txs: list) -> None:` does the same for a list of transactions.


### 2.2. Integration with Open Nyzo Sql Data source

We rely on the sql structure from the Nyzo open db specification, see https://github.com/Open-Nyzo/Open-Nyzo-Projects/tree/master/Open-DB

This database can be filled in by Monk's Go Verifier implementation, see https://github.com/cryptic-monk/go-nyzo  
In that case, the full chain will be validated then kept synced, with all data easily accessed.

You can also rely on tracking verifiers to track Nyzo chain, and poll for frozen blocks then insert converted blocks and transactions into the Open DB. 

Once you have the Nyzo chain as Sql data, you can use the script as is to track and fill the token tables: 

- Make sure to have run the test from "1. Test setup above"
- rename `nyzo_db_config.sample.json` to `nyzo_db_config.json` and edit to point to your Nyzo sql instance, user and database
- Run the tokens script in a screen `python3 tokens.py` , it will start processing old then new Nyzo transactions as they come.



 

   

