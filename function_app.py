import logging
import json
import os
import azure.functions as func
from azure.iot.hub import IoTHubRegistryManager
from uploadlogs import upload_module_logs_to_blob

app = func.FunctionApp()

def get_device_twin_tags(iot_hub, iot_hub_sas, device_id):
    # Replace with your IoT Hub connection string
    IOT_HUB_CONNECTION_STRING = "HostName=" + iot_hub +".azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey="+iot_hub_sas
    # Initialize the IoTHubRegistryManager
    logging.info('Device twin tags: {}'.format(device_id))
    registry_manager = IoTHubRegistryManager(IOT_HUB_CONNECTION_STRING)
    # Get the device twin
    twin = registry_manager.get_twin(device_id)
    logging.info(f'Device twin tags: {twin}')
    # Convert the twin object to a dictionary
    twin_dict = twin.as_dict()
    # I need to get the tags from the twin json object. there is no get method
    logging.info(f'Device twin tags: {twin_dict["tags"]}')
    return twin_dict["tags"]


def device_logging_on(hubName, device_id):
    try:
        tags = get_device_twin_tags(hubName, os.environ['IOT_HUB_CONNECTION_SAS'], device_id)
        # Implement the logic to process device twin tags and trigger an action based on the tags
        logging.info(f'Device twin tags: {tags}')
    
        logging_on = tags["logging"]
        if logging_on == "on":
            # Implement the logic to retrieve logs from IoT Edge module and upload to Blob storage
            logging.info(f'Device logging is enabled: {device_id}')
            # Retrieve the logs from IoT Edge module
            return True
        else:
            return False
    except Exception as e:
        logging.error(f'Error processing device twin tags: {e}')
        return False

@app.event_grid_trigger(arg_name="azeventgrid")
def EventGridTrigger(azeventgrid: func.EventGridEvent):
    logging.info('Python EventGrid trigger processed an device connected event')
    try:
        content = azeventgrid.get_json()
        hubName = content.get('hubName')
        device_id = content.get('deviceId')
        # Implement the logic to get device twin tags from IoT Hub
        logging.info(f'Device connected event received from device: {device_id}')
    except Exception as e:
        logging.error(f'Error processing device connected event: {e}')
    
    try:
        tags = get_device_twin_tags(hubName, os.environ['IOT_HUB_CONNECTION_SAS'], device_id)
        # Implement the logic to process device twin tags and trigger an action based on the tags
        logging.info(f'Device twin tags: {tags}')
        logging_on = tags["logging"]
        if logging_on == "on":
            # Implement the logic to retrieve logs from IoT Edge module and upload to Blob storage
            logging.info(f'Device logging is enabled: {device_id}')
            # Retrieve the logs from IoT Edge module
            status, payload = upload_module_logs_to_blob(hubName,
                                 os.environ['IOT_HUB_CONNECTION_SAS'],
                                 os.environ['BLOB_SAS'],
                                 device_id,
                                 "6",
                                 "'*.'",
                                 "0 days 15 minutes",
                                 "100")
            logging.info('Logs retrieval status: %s', status)

    except Exception as e:
        logging.error(f'Error processing device twin tags: {e}')
    


