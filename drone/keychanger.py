# Keychanger device that tries to update network key every 10s to simulate key expiry
# Admitedly hacky solution, and not incredibly secure, but slightly more secure vs. never updating the key.
# THIS DOES NOT WORK, so it's broadcast key is not used by any devices. 
# The issue is down to encoding, I think, but I'm implementing this pretty close to the deadline
# and don't believe I'd get it working in time.
# The Code here remains for posterity, so the grader has an idea of what we were going for.

# Main Contributor - Emmet McDonald
import asyncio
import logging
import os
import random
import sys
import tcdicn
from cryptography.fernet import Fernet
key = ""

async def main():

    # Get parameters or defaults
    file = open("constants.txt","r")
    id = file.readline().strip()
    global key
    key = open("key","rb").read()
    port = int(os.environ.get("TCDICN_PORT", random.randint(33334, 65536)))
    server_host = os.environ.get("TCDICN_SERVER_HOST", "localhost")
    server_port = int(os.environ.get("TCDICN_SERVER_PORT", 33335))
    net_ttl = int(os.environ.get("TCDICN_NET_TTL", 180))
    net_tpf = int(os.environ.get("TCDICN_NET_TPF", 3))
    net_ttp = float(os.environ.get("TCDICN_NET_TTP", 0))
    if id is None:
        sys.exit("Please give your client a unique ID by setting TCDICN_ID")

    # Logging verbosity
    logging.basicConfig(
        format="%(asctime)s.%(msecs)04d [%(levelname)s] %(message)s",
        level=logging.INFO, datefmt="%H:%M:%S:%m")

    # Start the client as a background task
    logging.info("Starting client...")
    client = tcdicn.Client(
        "KEYCHANGER", port, ["keychange"],
        server_host, server_port,
        net_ttl, net_tpf, net_ttp)

    # Publish random data to a random tag every couple of seconds
    async def run_sensor():
        global key
        while True:
            await asyncio.sleep(10)
            newKey = Fernet.generate_key();
            # Obviously this shouldn't actually be printed like this, but it's useful for viewing the simulation
            logging.info(f"Publishing keychange = {newKey}...")
            newKeyEnc = tcdicn.encrypt(newKey,key)
            try:
                await client.set("keychange", newKeyEnc)
            except OSError as e:
                logging.error(f"Failed to publish: {e}")
            key = newKey


    # Initialise execution of the sensor logic as a coroutine
    logging.info("Starting keychanger...")
    sensor = run_sensor()

    # Wait for the client to shutdown while executing the sensor coroutine
    both_tasks = asyncio.gather(client.task, sensor)
    try:
        await both_tasks
    except asyncio.exceptions.CancelledError:
        logging.info("Client has shutdown.")


if __name__ == "__main__":
    asyncio.run(main())