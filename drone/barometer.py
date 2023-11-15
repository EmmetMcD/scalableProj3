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
        id, port, ["pressure","depth"],
        server_host, server_port,
        net_ttl, net_tpf, net_ttp)

    # Publish random data to a random tag every couple of seconds
    async def run_sensor():
        depth = random.randint(0,100)
        while True:
            await asyncio.sleep(random.uniform(1, 2))
            depth = depth + random.uniform(-5,5)
            if(depth < 0):
                depth = 0
            pressure = depth * 10
            logging.info(f"Publishing Pressure = {pressure}...")
            try:
                await client.set("pressure", pressure)
            except OSError as e:
                logging.error(f"Failed to publish: {e}")
            logging.info(f"Publishing Depth = {depth}...")
            try:
                await client.set("depth", depth)
            except OSError as e:
                logging.error(f"Failed to publish: {e}")


    # Initialise execution of the sensor logic as a coroutine
    logging.info("Starting barometer...")
    sensor = run_sensor()

    # Wait for the client to shutdown while executing the sensor coroutine
    both_tasks = asyncio.gather(client.task, sensor)
    try:
        await both_tasks
    except asyncio.exceptions.CancelledError:
        logging.info("Client has shutdown.")


if __name__ == "__main__":
    asyncio.run(main())

