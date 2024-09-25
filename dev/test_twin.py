import logging
import sys
import json
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod

IOT_HUB_CONNECTION_SAS = "GMKFDqXns9cLz7IOSZpAAKG3Dx4s3RCESAIoTO8gRc0="

def get_device_twin_tags(iot_hub, iot_hub_sas, device_id):

    # Replace with your IoT Hub connection string
    IOT_HUB_CONNECTION_STRING = "HostName=" + iot_hub +".azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey="+iot_hub_sas
    # Initialize the IoTHubRegistryManager
    print(f'Device twin tags: {device_id}')
    registry_manager = IoTHubRegistryManager(IOT_HUB_CONNECTION_STRING)
    # Get the device twin
    twin = registry_manager.get_twin(device_id)
    print(f'Device twin tags: {twin}')
    # Convert the twin object to a dictionary
    twin_dict = twin.as_dict()
    # I need to get the tags from the twin json object. there is no get method
    print(f'Device twin tags: {twin_dict["tags"]}')
    return twin_dict["tags"]

if __name__ == "__main__":
    device_tags = get_device_twin_tags("iothubtervo01", IOT_HUB_CONNECTION_SAS, "devarcedge01")
    # I need to get the tags from the twin json object. there is no get method
    logging_on = device_tags["logging"]
    print(f'Device twin tags - logging on: {logging_on}')
  