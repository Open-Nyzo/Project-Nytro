# Nytro Tokens types

The Nytro protocol does support two different kind of tokens, for different use cases.  

Make sure to define what you will use them for, since all issuances are final: There can be no fix if you made an error or change your mind.

**REPEAT**: All tokens issuance, name, supply, decimals are **FINAL**. Think twice before you issue a token.
Nyzo tokens are for life. 

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
  
