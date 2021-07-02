# Nyzo Tokens Quick start

Nyzo tokens are managed via carefully crafted regular Nyzo transactions, obeying to strict rules concerning recipient, amount and data.

You can use Nytro enabled clients and tools to handle them in a safe way.    
See nytro_enabled.md for current list.

Current version of the Tokens protocol - since June 30, 2021 - is v1.1  
NFT upgraded protocol - v2.0 - has been released on July 2, 2010 and has its own reference, but no implementation yet. 

## Wallet and address

A regular Nyzo address is all you need to receive and handle Nyzo tokens.  
As per core Nyzo rules, a newly created address has to hold at least 10 Nyzos. This is not Nytro specific.

The same address (`id__?????` or raw `00000...0000`) is a Nyzo account and can be used for Nyzo main currency as for tokens.  
The Nyzo balance is handled by the core consensus and balances, while the Tokens balances are handled by the Nytro protocol.

**tl;dr:** If you already have a Nyzo address, this can be used right away as a Nyzo Token address as well.

## Test drive the tokens

### Get free tokens

In order to ease the tests and allow everyone to play with tokens, we issued several TEST Nyzo tokens.  
A faucet was also coded to distribute them for free at everyone requests.

Head over to https://tokens.nyzo.today/faucet/ to request some.

> If you plan to also offer a faucet service, just ask us for a bunch of TEST tokens.

### See your tokens balance

At launch, the reference explorer is https://tokens.nyzo.today/

Since we also provide an open source reference implementation of the protocol, we hope more explorers will be available.  
They will be referenced on nytro_enabled.md

The explorer covers the basics: List of tokens, transactions, balances, tokens info...

### Send tokens to someone

NyzoCli command line client is the first Nyzo wallet to natively support the Nyzo Tokens.  
However, you don't need a specific wallet to send Token transactions.

Since all you need is proper recipient, amount and data, any current wallet will do, including the web wallet at https://nyzo.co.

We released online helpers to make sure you can send correct Token transactions.  
They are available at https://tokens.nyzo.today/helpers/ 

Select "Balance transfer" and fill in the form.   
You will be given a `pre__` nyzostring, as well as the full transaction details.

You just have to send that exact transaction, using any wallet.

Take care of all items:
- Sender
- Recipient
- Amount
- Data

If you use the `pre__` string, then `recipient` and `data` are encoded, but you will still need to send it from the correct wallet, and use the correct Nyzo amount.

For a token transfer, the minimal amount of 0.000001 nyzo is enough.  

> Yes, you can send One Million Tokens transactions for a total fee of 1 Nyzo.

#### Using Nyzo.co wallet:
 
- Fill in the form on the helper
- Click the `pre__` string to have it copied 
- Paste that string as recipient on nyzo.co wallet, this will fill recipient and data
- Enter Nyzo amount, that is 0.000001 for a token transfer, 100 for a token issuance
- Send the transaction

Once the transaction is frozen, it will appear on the token explorer if valid.

#### Using Nyzocli

Example command: `./NyzoCli token send id_xxxx 10 TEST`

