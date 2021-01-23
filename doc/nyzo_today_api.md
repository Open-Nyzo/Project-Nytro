# Nyzo.today API

Tokens explorer features are available as an API

## API Endpoint

API Endpoint: https://tokens.nyzo.today/api  
Called by a simple get request with parameters in the URLl, returns Json.

### Tokens list
/tokens_list  
All tokens with their current properties

ex: `https://tokens.nyzo.today/api/tokens_list` 

### Balances
/balances/{address}  
All tokens owned by address with their balance

### Rich list
/richlist/{token_name}  
All current owners of that token and associated balance, sorted by amount desc

### Last transactions
/transactions/{address}  
Last 50 tokens transactions for that address  
Returns last 50 tokens transactions for all addresses if address is empty.

### Validity check
/check_tx/{sender}/{recipient}/{amount_nyzo}/{data}  
Token transaction tester, tests that tx and returns ok or specific error code.

### Token Fees
/fees  
Fees history: list of { “block height”: {“issue_fees”: micronyzo_fees, “mint_fees”: micronyzo_fees}}  

## Swagger Documentation

A Swagger Doc is in progress, but the use of the API is simple enough (just an http get!) this should not be an obstacle.
