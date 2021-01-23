"""
Reference implementation test
"""

import asyncio
from tokens import Tokens
import json
token_instance = Tokens()

SAVE_RESULTS = False


async def test(loop):
    await token_instance.init_db(loop, "tokens_db_config.json")

    for vector in range(1, 6):
        # Clear DB before each vector
        await token_instance.clear_db()
        with open("../../test_vectors/vector{}_state.json".format(vector)) as f:
            # Final state reference
            target_state = json.load(f)

        with open("../../test_vectors/vector{}.txt".format(vector)) as f:
            # Event stream
            f.readline()  # First line is header
            count = 0
            for line in f.readlines():
                if not line or line == "\n":
                    continue
                line = line.replace("\n", "")
                data = list(line.split("\t"))
                data[0] = bytes.fromhex(data[0])
                data[1] = bytes.fromhex(data[1])
                data[3] = data[3].encode("utf-8")
                data[2] = int(float(data[2]) * 10 ** 6)
                try:
                    result = await token_instance.parse_nyzo_tx([data[0], data[1], data[3], data[2],
                                                                 0, 0,
                                                                 count, str(count).encode("utf-8")],
                                                                save_tx=True)
                except ValueError as e:
                    if data[4] == "1":
                        print(vector, count, e, "|", line)
                else:
                    if data[4] == "0":
                        print(vector, count, result, "|", line)
                count += 1
            state = await token_instance.get_current_state()

            if target_state != state:
                print("Wrong final state: {} instead of {}".format(state, target_state))
            else:
                print("Vector #{} is correct".format(vector))

            if SAVE_RESULTS:
                with open("../../test_vectors/vector{}_state.json".format(vector), "w") as f2:
                    json.dump(state, f2)
    await token_instance.clear_db()


aioloop = asyncio.get_event_loop()
aioloop.run_until_complete(test(aioloop))
