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
        id+"_SAM", port, ["scienceList"],
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
        subscribe(id+"_depth")
        logging.info(f"Subscribing to {id}_xpos...")
        subscribe(id+"_xpos")
        logging.info(f"Subscribing to {id}_ypos...")
        subscribe(id+"_ypos")
        logging.info(f"Subscribing to {id}_camera...")
        subscribe(id+"_camera")
        logging.info(f"Subscribing to scienceList...")
        subscribe("scienceList")

        myList = []
        myDepth, myX, myY = 0,0,0

        while True:
            done, tasks = await asyncio.wait(
                tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                tag = task.get_name()
                value = task.result()
                logging.info(f"Received {tag}={value}")
                if("depth" in tag):
                    myDepth = float(tcdicn.decrypt(value,key))
                elif("xpos" in tag):
                    myX = float(tcdicn.decrypt(value,key))
                elif("ypos" in tag):
                    myY = float(tcdicn.decrypt(value,key))
                elif(tag == "scienceList"):
                    newList = (tcdicn.decrypt(value,key)).split()
                    if newList.size >= myList.size:
                        myList = newList
                elif(("camera" in tag) & int(tcdicn.decrypt(value,key))>0):
                    scienceString = str(myDepth)[:5]+","+str(myX)[:5]+","+str(myY)[:5]
                    if(scienceString not in myList):
                        myList.append(scienceString)
                        logging.info(f"Publishing to scienceList = {scienceString}...")
                        listStr = ""
                        listStr += listStr.join(myList)
                        listStr = tcdicn.encrypt(listStr,key)
                        try:
                            await client.set("scienceList", listStr)
                        except OSError as e:
                            logging.error(f"Failed to publish: {e}")
                        logging.info(f"Resubscribing to {tag}...")
                subscribe(tag)

    # Initialise execution of the actuator logic as a coroutine
    logging.info("Starting sampler...")
    actuator = run_actuator()

    # Wait for the client to shutdown while executing the actuator coroutine
    both_tasks = asyncio.gather(client.task, actuator)
    try:
        await both_tasks
    except asyncio.exceptions.CancelledError:
        logging.info("Client has shutdown.")


if __name__ == "__main__":
    asyncio.run(main())

