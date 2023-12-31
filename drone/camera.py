# Camera sensor that reports 1 if it has 'captured' something of interest and 0 otherwise
# In practice, this is pure RNG
# Main contributors - Emmet McDonald, Siddesh Bangar

import asyncio
import logging
import os
import random
import sys
import tcdicn


async def main():

    # Get parameters or defaults
    file = open("constants.txt","r")
    id = file.readline().strip()
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
        id+"_CAM", port, [id+"_camera"],
        server_host, server_port,
        net_ttl, net_tpf, net_ttp)

    # Publish random data to a random tag every couple of seconds
    async def run_sensor():
        while True:
            await asyncio.sleep(random.uniform(1, 2))
            camera = 0
            if(random.randint(1,5) == 5):
                camera = 1
            logging.info(f"Publishing {id}_camera = {camera}...")
            cameraStr = tcdicn.encrypt(camera,key)
            try:
                await client.set(f"{id}_camera", cameraStr)
            except OSError as e:
                logging.error(f"Failed to publish: {e}")


    # Initialise execution of the sensor logic as a coroutine
    logging.info("Starting camera...")
    sensor = run_sensor()

    # Wait for the client to shutdown while executing the sensor coroutine
    both_tasks = asyncio.gather(client.task, sensor)
    try:
        await both_tasks
    except asyncio.exceptions.CancelledError:
        logging.info("Client has shutdown.")


if __name__ == "__main__":
    asyncio.run(main())

