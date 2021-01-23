import aiomysql
from json import load as json_load
from re import match as re_match
from typing import Union
import time


CYCLE_ADDRESS_HEX = "0000000000000000000000000000000000000000000000000000000000000002"

CYCLE_ADDRESS = bytes.fromhex(CYCLE_ADDRESS_HEX)
ISSUE_FEES = 100 * 10 ** 6  # Micronyzos
MINT_FEES = 1
START_HEIGHT = 10650000

ISSUE_FEES_DISPLAY = "100"
MINT_FEES_DISPLAY = "0.000001"


FEES = [{"height": START_HEIGHT, "issue_fees": ISSUE_FEES, "mint_fees": MINT_FEES}]

TOKENS_INFO_CACHE = {}


class Db:
    def __init__(self, db_config_file: str):
        self.pool = None
        self.config_file = db_config_file

    async def init_loop(self, loop) -> None:
        with open(self.config_file) as f:
            config = json_load(f)
        self.pool = await aiomysql.create_pool(host=config["host"], port=config["port"],
                                               user=config["user"], password=config["password"],
                                               db=config["db"], loop=loop, autocommit=True)

    async def get(self, query: str, args: tuple=None) -> list:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, args=args)
                result = await cur.fetchall()
        return result

    async def get_one(self, query: str, args: tuple=None) -> list:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, args=args)
                result = await cur.fetchone()
        return result

    async def execute(self, query: str, args: tuple=None) -> None:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, args=args)

    async def close(self) -> None:
        self.pool.close()
        await self.pool.wait_closed()


class Tokens:
    def __init__(self):
        self.db = None

    async def init_db(self, loop, db_config_file: str) -> None:
        self.db = Db(db_config_file)
        await self.db.init_loop(loop)

        await self.db.execute("CREATE TABLE IF NOT EXISTS transactions(token VARCHAR(30), type VARCHAR(2), "
                              "block_height BIGINT(20), canonical INT(11), timestamp BIGINT(20), sender BINARY(32), "
                              "recipient BINARY(32), amount DECIMAL(64, 0), signature BINARY(64) PRIMARY KEY)")
        await self.db.execute("CREATE TABLE IF NOT EXISTS balances(token VARCHAR(30), address BINARY(32), "
                              "balance DECIMAL(64, 0), PRIMARY KEY (token, address))")
        await self.db.execute("CREATE TABLE IF NOT EXISTS tokens(token VARCHAR(30) PRIMARY KEY, issuer BINARY(32), "
                              "owner BINARY(32), supply DECIMAL(64, 0), mintable BOOL, decimals TINYINT(4), "
                              "block_height BIGINT(20), canonical INT(11), timestamp BIGINT(20), signature BINARY(64))")

    async def clear_db(self):
        """test purpose only"""
        await self.db.execute("DELETE FROM transactions")
        await self.db.execute("DELETE FROM balances")
        await self.db.execute("DELETE FROM tokens")

    async def insert_token_tx(self, tx_type: str, token: str, sender: bytes, recipient: bytes, amount: int,
                              block_height: int, canonical: int, timestamp: int, signature: bytes,
                              update_balances: bool=True) -> None:

        await self.db.execute("INSERT INTO transactions(token, type, block_height, canonical, timestamp, sender, "
                              "recipient, amount, signature) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                              (token, tx_type, block_height, canonical, timestamp, sender, recipient,
                               amount, signature))

        if update_balances:
            if sender != b'':
                await self.update_balance(token, sender, -amount)

            if recipient != b'':
                await self.update_balance(token, recipient, amount)

    async def update_balance(self, token: str, address: bytes, amount: int) -> None:
        await self.db.execute("REPLACE INTO balances SET token=%s, address=%s, "
                              "balance=COALESCE((SELECT balance from "
                              "(select * from balances where token=%s and address=%s) as a), 0) + (%s)",
                              (token, address, token, address, amount))

    async def update_supply(self, token: str, amount: int) -> None:
        await self.db.execute("UPDATE tokens SET supply=(select supply from (select * from tokens where token=%s) as a)"
                              " + (%s) WHERE token=%s",
                              (token, amount, token))

    async def issue_token(self, token: str, address: bytes, supply: int, mintable: bool, decimals: int,
                          block_height: int, canonical: int, timestamp: int, signature: bytes) -> None:
        await self.db.execute("INSERT INTO tokens(token, issuer, owner, supply, mintable, decimals, block_height, "
                              "canonical, timestamp, signature) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                              (token, address, address, supply, mintable, decimals, block_height, canonical,
                               timestamp, signature))

    async def change_ownership(self, token: str, address: bytes) -> None:
        await self.db.execute("UPDATE tokens SET owner=%s WHERE token=%s", (address, token))

    async def remove_token_tx(self, signature: bytes) -> None:  # unused
        """
        Should remove the tx, update the balances,
        and remove the corresponding token from the list if the tx is an issue
        """
        pass

    async def test_nyzo_tx(self, nyzo_tx: list) -> True:
        while len(nyzo_tx) <= 7:
            nyzo_tx.append(None)

        return await self.parse_nyzo_tx(nyzo_tx, save_tx=False)

    async def parse_nyzo_tx(self, nyzo_tx: list, save_tx: bool=False) -> True:
        """
        nyzo_tx: [sender: bytes, recipient: bytes, data: bytes, amount: int, timestamp: int, block_height: int,
        canonical: int, signature: bytes]
        """
        sender, recipient, data, amount, timestamp, block_height, canonical, signature = nyzo_tx

        try:
            data = data.replace(b"\x00", b"").decode("utf-8", "strict")
        except UnicodeDecodeError:
            raise ValueError("data is not valid utf-8")

        if not data:
            raise ValueError("data is empty")

        if save_tx and not sender:
            raise ValueError("no sender address")

        segments = data.split(":")
        if len(segments[0]) != 2 or segments[0][0] != "T":
            raise ValueError("segment0 is not 'TX'")

        if save_tx and (await self.signature_exists(signature)):
            raise ValueError("Duplicated transaction")

        if segments[0] == "TI":
            if len(segments) != 4:  # TI_R0
                raise ValueError("TI_R0")

            if not self.is_token_name_valid(segments[1]):  # TI_R1a
                raise ValueError("TI_R1a")

            if await self.token_exists(segments[1]):  # TI_R1b
                raise ValueError("TI_R1b")

            if not len(segments[2]) or not re_match("^d[0-9]{2}", segments[2]):  # TI_R2a
                raise ValueError("TI_R2a")

            decimals = int(segments[2][1:])
            if decimals > 18:  # TI_R2b
                raise ValueError("TI_R2b")

            if segments[3] == "-1":
                supply = -1
            else:
                supply = await self.str_to_int(segments[3], decimals)
                if supply == -1 or supply == 0:  # TI_R3a TI_R3b TI_R3c
                    raise ValueError("TI_R3a TI_R3b TI_R3c")

            if recipient != CYCLE_ADDRESS:  # TI_R4a
                raise ValueError("TI_R4a")

            if amount < ISSUE_FEES:  # TI_R4b
                raise ValueError("TI_R4b")

            mintable = False
            if supply == -1:
                supply = 0
                mintable = True

            if save_tx:
                await self.issue_token(segments[1], sender, supply, mintable, decimals, block_height, canonical,
                                       timestamp, signature)

                await self.insert_token_tx("TI", segments[1], b'', sender, supply, block_height, canonical,
                                           timestamp, signature)

        elif segments[0] == "TT":
            if len(segments) != 3:  # TT_R0
                raise ValueError("TT_R0")

            if not self.is_token_name_valid(segments[1]):  # TT_R1a
                raise ValueError("TT_R1a")

            token_amount = await self.str_to_int(segments[2], token=segments[1])
            if token_amount == -1:  # TT_R2a TT_R2b
                raise ValueError("TT_R2a TT_R2b")

            if token_amount == 0 or (sender and token_amount > (await self.get_token_balance(segments[1], sender))):
                raise ValueError("TT_R2c")  # TT_R2c

            if save_tx:
                await self.insert_token_tx("TT", segments[1], sender, recipient, token_amount, block_height, canonical,
                                           timestamp, signature)

        elif segments[0] == "TM":
            if len(segments) != 3:  # TM_R0
                raise ValueError("TM_R0")

            if not self.is_token_name_valid(segments[1]):  # TM_R1a
                raise ValueError("TM_R1a")

            if sender and sender != (await self.get_token_owner(segments[1])):  # TM_R1b
                raise ValueError("TM_R1b")

            if not (await self.is_token_mintable(segments[1])):  # TM_R1c
                raise ValueError("TM_R1c")

            token_amount = await self.str_to_int(segments[2], token=segments[1])
            if token_amount == -1:  # TM_R2a TM_R2b
                raise ValueError("TM_R2a TM_R2b")

            if token_amount == 0:  # TM_R2c
                raise ValueError("TM_R2c")

            if recipient != CYCLE_ADDRESS:  # TM_R3a
                raise ValueError("TM_R3a")

            if amount < MINT_FEES:  # TM_R3b
                raise ValueError("TM_R3b")
            if save_tx:
                await self.insert_token_tx("TM", segments[1], b'', sender, token_amount, block_height, canonical,
                                           timestamp, signature)
                await self.update_supply(segments[1], token_amount)

        elif segments[0] == "TB":
            if len(segments) != 3:  # TB_R0
                raise ValueError("TB_R0")

            if not self.is_token_name_valid(segments[1]):  # TB_R1a
                raise ValueError("TB_R1a")

            if not (await self.is_token_mintable(segments[1])):  # TB_R1b
                raise ValueError("TB_R1b")

            token_amount = await self.str_to_int(segments[2], token=segments[1])
            if token_amount == -1:  # TB_R2a TB_R2b
                raise ValueError("TB_R2a TB_R2b")

            if token_amount == 0 or (sender and token_amount > (await self.get_token_balance(segments[1], sender))):
                raise ValueError("TB_R2c")  # TB_R2c

            if recipient != CYCLE_ADDRESS:  # TB_R3
                raise ValueError("TB_R3")

            if save_tx:
                await self.insert_token_tx("TB", segments[1], sender, b'', token_amount, block_height, canonical,
                                           timestamp, signature)
                await self.update_supply(segments[1], - token_amount)

        elif segments[0] == "TO":
            if len(segments) != 2:  # TO_R0
                raise ValueError("TO_R0")

            if not self.is_token_name_valid(segments[1]):  # TO_R1a
                raise ValueError("TO_R1a")

            if not (await self.is_token_mintable(segments[1])):  # TO_R1b
                raise ValueError("TO_R1b")

            if sender and sender != (await self.get_token_owner(segments[1])):  # TO_R2
                raise ValueError("TO_R2")

            if save_tx:
                await self.change_ownership(segments[1], recipient)
                await self.insert_token_tx("TO", segments[1], sender, recipient, 0, block_height, canonical,
                                           timestamp, signature)
        else:
            raise ValueError("Unknown command")
        return True

    async def parse_nyzo_txs(self, nyzo_txs: list) -> None:
        for nyzo_tx in nyzo_txs:
            try:
                await self.parse_nyzo_tx(nyzo_tx, save_tx=True)
                print("transaction inserted: ", nyzo_tx)
            except ValueError as e:
                print("insertion failed: ", nyzo_tx, e)
                pass

    async def get_token_balance(self, token: str, address: bytes) -> int:
        return (await self.db.get_one("SELECT "
                                      "COALESCE((SELECT balance FROM balances WHERE token=%s AND address=%s), 0)",
                                      (token, address)))[0]

    async def get_token_decimals(self, token: str) -> int:
        return (await self.db.get_one("SELECT COALESCE((SELECT decimals FROM tokens WHERE token=%s), -1)",
                                      (token, )))[0]

    async def get_token_owner(self, token: str) -> bytes:
        return (await self.db.get_one("SELECT COALESCE((SELECT owner FROM tokens WHERE token=%s), 0)",
                                      (token, )))[0]

    async def get_token_supply(self, token: str) -> int:
        return (await self.db.get_one("SELECT COALESCE((SELECT supply FROM tokens WHERE token=%s), 0)",
                                      (token, )))[0]

    async def signature_exists(self, signature: bytes) -> bool:
        return bool((await self.db.get_one("SELECT COUNT(*) FROM transactions WHERE signature=%s LIMIT 1",
                                           (signature, )))[0])

    async def is_token_mintable(self, token: str) -> bool:
        return (await self.db.get_one("SELECT COALESCE((SELECT mintable FROM tokens WHERE token=%s), 0)",
                                      (token, )))[0]

    @staticmethod
    def is_token_name_valid(token: str) -> bool:
        return len(token) >= 3 and re_match("^[A-Z0-9_]*$", token)

    async def token_exists(self, token: str) -> bool:
        return bool((await self.db.get_one("SELECT count(token) from tokens WHERE token=%s", (token, )))[0])

    async def str_to_int(self, amount: str, decimals: int=0, token: str="") -> int:
        if token:
            decimals = await self.get_token_decimals(token)
        segments = amount.split(".")
        if len(segments) == 1:
            segments.append("")
        if len(segments) != 2:
            return -1

        if not segments[0].isdigit() or (segments[1] and not segments[1].isdigit()):
            return -1
        if len(segments[1]) > decimals:
            return -1
        segments[1] += "0" * (decimals - len(segments[1]))

        return int(segments[0] + segments[1])

    async def async_int_to_str(self, amount: int, decimals: int = 0, token: str = "") -> str:
        if token:
            decimals = await self.get_token_decimals(token)
        result = str(amount).zfill(decimals + 1)
        if decimals:
            return result[:-decimals] + "." + result[-decimals:]
        return result

    @staticmethod
    def int_to_str(amount: int, decimals: int) -> str:
        result = str(amount).zfill(decimals + 1)
        if decimals:
            return result[:-decimals] + "." + result[-decimals:]
        return result

    async def get_address_transactions(self, address: bytes, as_dictlist: bool=False) -> list:
        data = await self.db.get("SELECT timestamp, type, block_height, token, sender, recipient, amount, signature "
                                 "FROM transactions WHERE sender=%s OR recipient=%s "
                                 "ORDER BY block_height DESC, canonical DESC LIMIT 50",
                                 (address, address))
        if as_dictlist:
            result = []
            for line in data:
                result.append({"sender": line[4].hex(), "recipient": line[5].hex(), "token": line[3],
                               "amount": self.int_to_str(line[6], (await self.get_cached_token_info(line[3]))[3]),
                               "amount_int": int(line[6]), "type": line[1], "timestamp": line[0],
                               "block_height": line[2], "signature": line[7].hex()})
            return result
        else:
            return data

    async def get_token_transactions(self, token: str) -> list:
        return await self.db.get("SELECT timestamp, type, block_height, token, sender, recipient, amount, signature "
                                 "FROM transactions WHERE token=%s "
                                 "ORDER BY block_height DESC, canonical DESC LIMIT 50",
                                 (token, ))

    async def get_signature_transactions(self, signature: bytes) -> list:
        return await self.db.get("SELECT timestamp, type, block_height, token, sender, recipient, amount, signature "
                                 "FROM transactions WHERE signature=%s "
                                 "ORDER BY block_height DESC, canonical DESC LIMIT 50",
                                 (signature, ))

    async def get_height_transactions(self, height: int) -> list:
        return await self.db.get("SELECT timestamp, type, block_height, token, sender, recipient, amount, signature "
                                 "FROM transactions WHERE block_height=%s "
                                 "ORDER BY block_height DESC, canonical DESC LIMIT 50",
                                 (height, ))

    async def get_latest_transactions(self) -> list:
        return await self.db.get("SELECT timestamp, type, block_height, token, sender, recipient, amount, signature "
                                 "FROM transactions ORDER BY block_height DESC, canonical DESC LIMIT 50")

    async def get_address_balances(self, address: bytes, as_dict: bool=False) -> Union[list, dict]:
        balances = await self.db.get("SELECT token, balance, "
                                     "address=(SELECT owner FROM tokens WHERE tokens.token=balances.token LIMIT 1) "
                                     "FROM balances WHERE address=%s",
                                     (address, ))
        if as_dict:
            return {item[0]: {"amount": self.int_to_str(item[1], (await self.get_cached_token_info(item[0]))[3]),
                              "amount_int": int(item[1])} for item in balances}
        else:
            return balances

    async def get_token_balances(self, token: str, as_dictlist: bool=False) -> list:
        balances = await self.db.get("SELECT address, balance FROM balances WHERE token=%s ORDER BY balance DESC",
                                     (token, ))
        if as_dictlist:
            return [{"address": item[0].hex(),
                     "balance": self.int_to_str(item[1], (await self.get_cached_token_info(token))[3]),
                     "balance_int": int(item[1])} for item in balances]
        else:
            return balances

    async def get_all_balances(self, as_dict: bool=False) -> Union[list, dict]:
        balances = await self.db.get("SELECT token, address, balance FROM balances")
        if as_dict:
            result = {}
            for token, address, balance in balances:
                if token not in result:
                    result[token] = {}
                result[token][address.hex()] = int(balance)
            return result
        else:
            return balances

    async def get_token_info(self, token: str) -> list:
        return await self.db.get_one("SELECT issuer, supply, mintable, decimals, block_height, "
                                     "timestamp, signature, owner, token "
                                     "FROM tokens WHERE token=%s LIMIT 1",
                                     (token, ))

    async def get_address_info(self, address: bytes) -> tuple:
        return ((await self.db.get_one("SELECT COUNT(*) FROM balances WHERE address=%s AND balance != 0",
                                       (address, )))[0],
                (await self.db.get_one("SELECT COUNT(*) FROM tokens WHERE issuer=%s",
                                       (address, )))[0],
                (await self.db.get_one("SELECT COUNT(*) FROM tokens WHERE owner=%s AND mintable",
                                       (address, )))[0])

    async def get_all_tokens_info(self, as_dict: bool=False) -> Union[list, dict]:
        data = await self.db.get("SELECT issuer, supply, mintable, decimals, block_height, "
                                 "timestamp, signature, owner, token FROM tokens")
        if as_dict:
            result = {}
            for line in data:
                result[line[8]] = {"issuer": line[0].hex(), "owner": line[7].hex(), "signature": line[6].hex(),
                                   "supply": self.int_to_str(line[1], line[3]), "supply_int": int(line[1]),
                                   "mintable": bool(line[2]), "decimals": line[3], "block_height": line[4],
                                   "timestamp": line[5]}
            return result
        else:
            return data

    async def get_highest_height(self) -> int:
        return max((await self.db.get_one("SELECT COALESCE(MAX(block_height), 0) FROM transactions"))[0], START_HEIGHT)

    async def get_network_stats(self) -> list:
        return await self.db.get_one("SELECT COUNT(DISTINCT(token)), COUNT(DISTINCT(recipient)), COUNT(*) "
                                     "FROM transactions")

    async def get_current_state(self) -> dict:
        return {"tokens": await self.get_all_tokens_info(as_dict=True),
                "balances": await self.get_all_balances(as_dict=True)}

    async def get_cached_token_info(self, token: str) -> list:
        if token not in TOKENS_INFO_CACHE:
            TOKENS_INFO_CACHE[token] = await self.get_token_info(token)
        return TOKENS_INFO_CACHE[token]


if __name__ == "__main__":
    # Run the file as main script to run the processor (nyzo to tokens)
    nyzo_db_config_file = "nyzo_db_config.json"
    tokens_db_config_file = "tokens_db_config.json"

    async def db_update_loop(loop):
        print("Running db_update_loop")
        nyzo_db = Db(nyzo_db_config_file)
        await nyzo_db.init_loop(loop)
        tokens = Tokens()
        await tokens.init_db(loop, tokens_db_config_file)

        last_height = await tokens.get_highest_height()

        while True:
            try:
                next_height = (await nyzo_db.get_one("SELECT COALESCE(MAX(height), 0) FROM transactions"))[0]
                transactions = await nyzo_db.get("SELECT sender, recipient, data, amount, timestamp, height, "
                                                 "canonical, signature "
                                                 "FROM transactions "
                                                 "WHERE height >= %s AND height < %s AND type=2 "
                                                 "AND data != 0x0000000000000000000000000000000000000000000000000000000000000000",
                                                 (last_height, next_height))
                await tokens.parse_nyzo_txs(transactions)

                last_height = next_height
            except Exception as e:
                print(e)
            time.sleep(10)


    import asyncio
    aioloop = asyncio.get_event_loop()
    aioloop.run_until_complete(db_update_loop(aioloop))
