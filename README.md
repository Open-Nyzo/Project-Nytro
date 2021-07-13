# Project-Nytro
Project Nytro is bringing ERC-20 like tokens to Nyzo blockchain.  
7 seconds block time, fast finality and very low fees.

## About Nyzo

Nyzo is a unique blockchain with unique features, based upon a cycle relying on Proof of Diversity.

Its architecture brings some strong guarantees vs usual blockchains.

Read more at:  
https://nyzo.co  
https://nyzo.io  
https://nyzo.net

## Tokens and NFTs on Nyzo

Nyzo does not come with embedded smart contract - and may not need their overhead.   
However, it has a convenient "data" field that can be used for anything.

Leveraging experience with Bismuth execution model, Iyomisc and NyzoSy proposed to specify and implement a layer-2 protocol on top of Nyzo, so Tokens could be issued and managed.  
This was NCFP-17 https://forum.nyzo.community/t/ncfp-17-draft-tokens-on-nyzo/354 

Relying on a layer-2 protocol means:
- No change needed to the verifiers code, they continue to process transactions as usual
- Inherit the speed of final transactions Nyzo comes with
- Ability to send transactions with minimal fees, 0.000001 Nyzo

The first technical document and reference implementation was released on January 23, 2021. One month after its approval.  
It came with a full featured Tokens explorer, Online Helpers, APIs, Faucet and a command line wallet support.  

More than expected, a full ecosystem from day One! 

## The Nytro protocol 

We designed the protocol to be as simple as possible, while maximizing the possible use cases and compatibility.  
While not using smart contract language, we kept most of the ERC-20 features.

- See https://github.com/Open-Nyzo/Project-Nytro/blob/main/doc/nytro_protocol.pdf for the most complete reference doc, mainly targeting developers.  
- **New:** See https://github.com/Open-Nyzo/Project-Nytro/blob/main/doc/nft_protocol_v20.pdf for the NFT complete reference doc, mainly targeting developers.  
- See https://github.com/Open-Nyzo/Project-Nytro/blob/main/doc/quickstart.md if you want to use tokens right away  
- see https://github.com/Open-Nyzo/Project-Nytro/blob/main/doc/token_types.md for the 2 main token types and their possible uses.  
- see https://github.com/Open-Nyzo/Project-Nytro/blob/main/doc/nytro_enabled.md for the current list of Nytro Enabled tools and services.  
- see https://github.com/Open-Nyzo/Project-Nytro/blob/main/doc/reserved_tokens.md for the reserved tokens and the reason why.  
- see https://github.com/Open-Nyzo/Project-Nytro/blob/main/doc/nyzo_today_api.md for an easy to use API.  

The https://github.com/Open-Nyzo/Project-Nytro/tree/main/doc directory will also grow with more info. 

## Integration

We are willing to help anyone willing to integrate the Nytro protocol.   
See implementations/tokens for a reference Python implementation and test tool.  
We will happily reference alternate implementations.   

Test vectors are also provided, see /test_vectors.

## Changelog

V2.1 - 2021-07-13 - NFT Protocol document, Release v2.01 - Update to helpers and initial fees.  
NFT Class issuance fee is set as 300 Nyzo.

V2.0 - 2021-07-02 - NFT Protocol document, First Version released

V1.1 - 2021-06-30 - Limit Max len of token name to 10 chars, add optional comment to somme commands, allow burn to any Nyzo address.

Draft - 2020-06-10 - NFTs Draft
 
V1.0 - 2020-12-23 - Initial release

## FAQs

The FAQ section will be created and updated with user questions.    
You can reach us on the Nyzo Discord, @Iyomisc and @NyzoSy.  
Please do not use the github as discussion or question support, and reserve it for development, code, integration support.

We plan to run an AMA on the discord ASAP.


## Thanks

Thanks to z0rn and Gigison who supported and helped during development, as well as all Nyzo users and cycle owner so quickly voting for NCFP-17.

We are confident project Nytro will trigger interest in Nyzo and give birth to new use cases and exposure.  

Your help - yes, yours, whoever you are - is crucial to have Nyzo and its features known to a wider audience.   
Talk about Nyzo, communicate over use cases and Nyzo specifics: You are the voice of Nyzo, Nyzo needs all of you and may reward you!
