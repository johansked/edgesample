from azure.iot.device.aio import IoTHubModuleClient
from azure.iot.device import Message
import asyncio
import json
import datetime

from logger import logger

class EdgeModuleClient:
  listeners = None
  module_client = None
  def __init__(self, twin_update_callback, input_callback, input_name):
    self.module_client = IoTHubModuleClient.create_from_edge_environment()
    self.twin_update_callback = twin_update_callback
    self.input_callback = input_callback
    self.input_name = input_name

  def __del__(self):
    if self.listeners is not None:
      self.listeners.cancel()
    if self.module_client is not None:
      self.module_client.disconnect()

  async def start(self):
    await self.module_client.connect()

    desired_properties = await self.__get_twin_desired_properties()
    self.twin_update_callback(desired_properties)
    await self.__report_properties(desired_properties)

    # Schedule task for C2D Listener
    self.listeners = asyncio.gather(self.__twin_listener(), self.__input_listener())

  async def send_json_message_to_output(self, payload, output_name):
    message = Message(bytearray(json.dumps(payload), "utf8"), content_type = "application/json", content_encoding = "utf-8")
    await self.module_client.send_message_to_output(message, output_name)

  async def __twin_listener(self):
    while True:
      try:
        desired_properties = await self.module_client.receive_twin_desired_properties_patch() #Blocking
        version = desired_properties.pop('$version')

        logger.info(f'Twin patch desired version {version}: {desired_properties}')

        self.twin_update_callback(desired_properties)
        await self.__report_properties(desired_properties)
      except Exception as e:
        logger.exception(e)

  async def __report_properties(self, properties):
    properties["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    await self.module_client.patch_twin_reported_properties(properties)

  async def __get_twin_desired_properties(self):
    twin = await self.module_client.get_twin()
    desired = twin.get('desired')
    # Remove version
    version = desired.pop('$version')

    logger.info(f'Twin desired version {version}: {desired}')

    return desired
    
  async def __input_listener(self):
    while True:
      message = await self.module_client.receive_message_on_input(self.input_name)
      await self.input_callback(message)