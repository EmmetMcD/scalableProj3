import asyncio
import logging
import os
import random
import sys
import tcdicn


async def main():

    # Get parameters or defaults
    id = os.environ.get("TCDICN_ID")
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
        id+"_POS", port, [id+"_xpos",id+"_ypos"],
        server_host, server_port,
        net_ttl, net_tpf, net_ttp)

    # Publish random data to a random tag every couple of seconds
    async def run_sensor():
        xpos = random.randint(0,100)
        ypos = random.randint(0,100)
        while True:
            await asyncio.sleep(random.uniform(1, 2))
            xpos = xpos + random.uniform(-3,3)
            ypos = ypos + random.uniform(-3,3)
            if(xpos < 0):
                xpos = 0
            elif (xpos > 100):
                xpos = 100
            if (ypos < 0):
                ypos = 0
            elif (ypos > 100):
                ypos = 100
            logging.info(f"Publishing {id}_ypos = {ypos}...")
            try:
                await client.set(id+"_ypos", ypos)
            except OSError as e:
                logging.error(f"Failed to publish: {e}")
            logging.info(f"Publishing {id}_xpos = {xpos}...")
            try:
                await client.set(id+"_xpos", xpos)
            except OSError as e:
                logging.error(f"Failed to publish: {e}")


    # Initialise execution of the sensor logic as a coroutine
    logging.info("Starting positioning...")
    sensor = run_sensor()

    # Wait for the client to shutdown while executing the sensor coroutine
    both_tasks = asyncio.gather(client.task, sensor)
    try:
        await both_tasks
    except asyncio.exceptions.CancelledError:
        logging.info("Client has shutdown.")


if __name__ == "__main__":
    asyncio.run(main())

