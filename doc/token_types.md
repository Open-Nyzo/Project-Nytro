# Nytro Tokens types

The Nytro protocol does support two different kind of tokens, for different use cases.  

Make sure to define what you will use them for, since all issuances are final: There can be no fix if you made an error or change your mind.

**REPEAT**: All tokens issuance, name, supply, decimals are **FINAL**. Think twice before you issue a token.
Nyzo tokens are for all eternity. 

Don't issue critical names just for fun, with no use case in mind: They would be useless and valueless if they are of the wrong type for instance...


## Regular tokens

Regular tokens have a fixed supply. This is a strong guarantee.  
Let say you issue a "ART" token with no decimals and 10 as supply, there will only be 10 of these tokens ever, no matter what.

Use these when you need a fixed supply, for scarce and potentially valuable things, or in flows where a fixed total supply is required.

### Regular tokens properties 
 
- Fixed supply
- Fixed decimals

### Regular tokens Supported operations:

- TI: Token Issuance  
  Initial definition of the token and emission of the full supply to the issuer.
  
- TT: Token Transfer  
  Transfer of token units from sender to recipient.
  

## Mintable tokens

Mintable tokens have an elastic supply. They can be minted and burned at will.
  
A typical use of this token type is for wrapped tokens.    
Say you want to wrap "ETH" into a "NETH" Nyzo token.  
You would issue a NETH Token with 18 decimals (same as ETH native decimals).
Then, you'd need to make sure the NETH supply is 1:1 with the real ETHs you keep in custody.

By minting and burning NETH as you receive and send real ETH, you can prove you operate in a fair way. 

Other creative uses of mintable tokens are also possible ;)

Mintable tokens come with "Ownership" - that is the right to mint that token.    
This ownership can be transfered to anyone for free.

### Mintable tokens properties 
 
- Elastic supply
- Fixed decimals

### Mintable tokens Supported operations:

- TI: Token Issuance  
  Initial definition of the token, supply defined as '-1' by convention, initial supply is null.  
  The issuer becomes the first Owner of the token mint rights.
  
- TT: Token Transfer  
  Transfer of token units from sender to recipient, just like a regular token.

- TM: Token Mint  
  Current owner can mint any number of token units, adds to supply.

- TB: Token Burn  
  Destroy token units from the sender balance, remove from supply.

- TO: Token Ownership change  
  Transfers ownership (mint rights) to the recipient.
  

## NFT Tokens

NFT Tokens will be available once Nytro v2 has activated. Further info will follow.

NFT are "classes" of tokens - sharing common properties - from whom you can mint individual NFT, with their own properties as well.  
They can have limited or unlimited max supply.  

NFT names are recognizable from their name, beginning with a lowercap n.

Ex: `nNFT` is a NFT class  
`nNFT:824fg6` is a unique, non fungible instance of the `nNFT` class.

### NFT Properties

A given NFT instance can have 3 kind of stored properties

- Class properties, defined by the current NFT class owner, that apply to all instances of that class
- individual NFT properties, defined by the current NFT class owner, that apply to a single instance only
- individual NFT properties, defined by the current NFT owner, that apply to a single instance only

### NFT Tokens supported operations:

> This is an overview only. The full specs will define these operations precisely.

- NI: NFT Class issuance    
  Initial definition of a NFT class, with an optional maximal supply.  
  The issuer becomes the class Owner (token mint and admin data rights on that class).
  
- NM: NFT Token Mint  
  Current class owner can mint an instance of the class, defines the UID of that specific NFT.
  
- NT: NFT Transfer  
  Transfer of a given NFT instance from sender to recipient, just like a regular token.
 
- NO: NFT class Ownership change  
  Transfers class ownership (mint and class properties rights) to the recipient.

- NB: NFT Token Burn  
  Destroys The given NFT.        
  
- NA: NFT Token Admin Data    
  Adds owner protected data to an NFT class or a given NFT     
  
- ND: NFT Token User Data    
  Adds user data to a given NFT. Only available to current NFT instance owner.  
  
 
### A note about NFT properties and data storage      

Nyzo is **not** fit for large data storage.  
Data field for a single transaction is 32 bytes max compared to 186 bytes of a transaction with empty data.  
This means storing 32 data bytes really stores 186 + 32 = 218 bytes.  
See http://tech.nyzo.co/dataFormats/transaction  
Recipient address is 32 bytes as well, and can be used in some cases, see protocol detail.

Encoding of the payloads into these 32 bytes is left to every app dev.   
We will provide some examples as guidelines only.  
We urge you not to abuse the system with many transactions for larger payloads. This would be a significant waste of resource, and go against Nyzo aim for efficiency.

If you need a large payload, the logic would be to use ipfs hash for instance.   
Since a sha256 ipfs hash is 32 bytes, it can go into a single transaction data, and hold larger data in a ipfs hosted json for instance.

A Nyzo specific distributed data storage service could emerge later on.
