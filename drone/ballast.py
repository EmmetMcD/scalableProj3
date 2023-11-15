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
    get_ttl = int(os.environ.get("TCDICN_GET_TTL", 180))
    get_tpf = int(os.environ.get("TCDICN_GET_TPF", 3))
    get_ttp = float(os.environ.get("TCDICN_GET_TTP", 0))
    if id is None:
        sys.exit("Please give your client a unique ID by setting TCDICN_ID")

    # Logging verbosity
    logging.basicConfig(
        format="%(asctime)s.%(msecs)04d [%(levelname)s] %(message)s",
        level=logging.INFO, datefmt="%H:%M:%S:%m")

    # Start the client as a background task
    logging.info("Starting client...")
    client = tcdicn.Client(
        id+"_BAL", port, [],
        server_host, server_port,
        net_ttl, net_tpf, net_ttp)

    # Subscribe to random subset of data
    async def run_actuator():
        tasks = set()

        def subscribe(tag):
            getter = client.get(tag, get_ttl, get_tpf, get_ttp)
            task = asyncio.create_task(getter, name=tag)
            tasks.add(task)

        logging.info(f"Subscribing to {id}_depth...")
        subscribe(f"{id}_depth")
        logging.info(f"Subscribing to {id}_power...")
        subscribe(f"{id}_power")

        powerSafe = True
        while True:
            done, tasks = await asyncio.wait(
                tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                tag = task.get_name()
                value = task.result()
                logging.info(f"Received {tag}={value}")
                if("depth" in tag):
                    if(powerSafe):
                        if(value >= 95):
                            logging.info("Depth approaching 100, rising...")
                        elif(value <= 5):
                            logging.info("Depth approaching 0, descending...")
                elif("power" in tag):
                    if(value <= 10):
                        logging.info("Power approaching 0, surfacing...")
                logging.info(f"Resubscribing to {tag}...")
                subscribe(tag)

    # Initialise execution of the actuator logic as a coroutine
    logging.info("Starting ballast...")
    actuator = run_actuator()

    # Wait for the client to shutdown while executing the actuator coroutine
    both_tasks = asyncio.gather(client.task, actuator)
    try:
        await both_tasks
    except asyncio.exceptions.CancelledError:
        logging.info("Client has shutdown.")


if __name__ == "__main__":
    asyncio.run(main())

