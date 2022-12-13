import os
import sys
import asyncio
import time
import json

from edge_module_client import EdgeModuleClient
from logger import logger


def twin_callback(twin_properties):
    logger.info(twin_properties)
    return

async def process_data(message):
    global module_client
    global data_output_name
    payload = json.loads(message.data) 
    logger.info(payload)
    module_client.send_json_message_to_output(payload, data_output_name)


async def main():
    global module_client
    global data_output_name
    try:
        if not sys.version >= "3.5.3":
            raise Exception("The sample requires python 3.5.3+. Current version of Python: %s" % sys.version)
        logger.info("IoT Hub Client for Python")

        device_id = os.getenv("IOTEDGE_DEVICEID")
        data_input_name = os.getenv("DATA_INPUT_NAME", "input1")
        data_output_name = os.getenv("DATA_OUTPUT_NAME", "output1")

        module_client = None
        try:
            # The client object is used to interact with your Azure IoT hub.
            module_client = EdgeModuleClient(twin_callback, process_data, data_input_name)
            # connect the client.
            await module_client.start()
        except Exception as e:
            logger.exception(e)
            logger.warning('Unable to connect to IoTHub')  
        
        # Run the stdin listener in the event loop
        while True:
            await asyncio.sleep(1000)


    except Exception as e:
        logger.exception(e)
        raise

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    try:
        loop.create_task(main())
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    loop.close()