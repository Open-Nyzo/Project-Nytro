# Nyzo.today API

Tokens and  NFT explorer features are available as an API

## API Endpoint

API Endpoint: `https://tokens.nyzo.today/api`  
Called by a simple get request with parameters in the URL, returns Json.

## Tokens Specific endpoints

### Tokens list
`/tokens_list`  
All tokens with their current properties

ex: `https://tokens.nyzo.today/api/tokens_list` 

### Balances
`/balances/{address}`  
All tokens owned by address with their balance

### Rich list
`/richlist/{token_name}`  
All current owners of that token and associated balance, sorted by amount desc

### Last transactions
`/transactions/{address}`  
Last 50 tokens transactions for that address  
Returns last 50 tokens transactions for all addresses if address is empty.

### Validity check
`/check_tx/{sender}/{recipient}/{amount_nyzo}/{data}`  
Token transaction tester, tests that tx and returns ok or specific error code.

### Token Fees
`/fees`  
Fees history: list of { “block height”: {“issue_fees”: micronyzo_fees, “mint_fees”: micronyzo_fees}}  

## NFT Specific endpoints

### NFT list
`/nft_list`  
All NFT classes with their current properties.

### NFT data
`/nft_data/{nft_class}/{(optional) nft_id}`  
Returns data relative to the nft_id instance and the nft_class class, or only nft_class data if nft_id is not given.  
Will return an empty list if no data transactions have been made for this instance/class, or if the instance/class does not exist.

### nft instances list
`/nft_instances/{nft_class}`  
Lists all existing instances of the given nft_class.  
Will return an empty list if there are no instances of this class, or if the class does not exist.


## Swagger Documentation

A Swagger Doc is in progress, but the use of the API is simple enough (just an http get!) this should not be an obstacle.
