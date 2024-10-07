import logging
import os
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.iot.hub import IoTHubRegistryManager
from azure.mgmt.iothub import IotHubClient
from azure.storage.blob import BlobServiceClient
from uploadlogs import upload_mi_module_logs_to_blob

app = func.FunctionApp()

SUBSCRIPTION_ID = 'ae92e392-3813-45dd-9c54-fe320939f03c'
RG_NAME = 'rg-iotopc-tervo'

def get_iot_hub_connection_string(iot_hub_name, subscription_id, resource_group_name):
    """
    Get the connection string for the IoT Hub.
    """

    try:
        logging.info('Getting IoT Hub connection string for %s', iot_hub_name)
        # Use Managed Identity to authenticate with IoT Hub
        credential = DefaultAzureCredential()
        # how to get IoT Hub connection string using Managed Identity
        client = IotHubClient(credential, subscription_id)
        # Get the IoT Hub description
        iothub_description = client.iot_hub_resource.get(resource_group_name, iot_hub_name)
        # Retrieve the connection string
           # Extract the connection string from the IoT Hub description
        for key in iothub_description.properties.authorization_policies:
            if key.key_name == "iothubowner":
                return key.primary_key
    except Exception as e:
        logging.error('Error getting IoT Hub connection string with default credential: %s', e)
        return None

def get_device_twin_tags(iot_hub_connection_string, device_id):
    """
    Get the tags from the device twin.
    """
    # Use Managed Identity to authenticate with IoT Hub
    credential = DefaultAzureCredential()
    # how to get IoT Hub connection string using Managed Identity

    # Initialize the IoTHubRegistryManager with Managed Identity
    registry_manager = IoTHubRegistryManager(iot_hub_connection_string, credential)

    # Get the device twin
    twin = registry_manager.get_twin(device_id)
    logging.info(f'Device twin: {twin}')

    # Convert the twin object to a dictionary
    twin_dict = twin.as_dict()

    # Access the tags from the twin dictionary
    tags = twin_dict.get("tags", {})
    logging.info(f'Device twin tags: {tags}')

    return tags


'''
def device_logging_on(hubName, device_id):
    try:
        tags = get_device_twin_tags(hubName, device_id)
        logging.info(f'Device twin tags: {tags}')

        logging_on = tags.get("logging")
        if logging_on == "on":
            logging.info(f'Device logging is enabled: {device_id}')
            return True
        else:
            return False
    except Exception as e:
        logging.error(f'Error processing device twin tags: {e}')
        return False
'''

@app.event_grid_trigger(arg_name="azeventgrid")
def EventGridTrigger(azeventgrid: func.EventGridEvent):
    """
    Azure Function triggered by an Event Grid event.
    """
    # Retrieve the logs from IoT Edge modules
    logging.info(
        'Python EventGrid trigger processed an device connected event')
   
    try:
        content = azeventgrid.get_json()
        hubName = content.get('hubName')
        device_id = content.get('deviceId')
        logging.info(
            'Device connected event received from iothub: %s device: %s' ,hubName, device_id)
    except (KeyError, ValueError) as e:
        logging.error('Error processing device connected event: %s', e)
        return

    IOT_HUB_CONNECTION_STRING = get_iot_hub_connection_string(hubName, SUBSCRIPTION_ID, RG_NAME)

    if IOT_HUB_CONNECTION_STRING is None:
        logging.error('Failed to get IoT Hub connection string')
        return

    try:
        tags = get_device_twin_tags(IOT_HUB_CONNECTION_STRING, device_id)
        logging.info(f'Device twin {device_id} tags: {tags}')

        logging_on = tags.get("logging")
        if logging_on == "on":
            logging.info(f'Device logging is enabled: {device_id}')
            status, payload = upload_mi_module_logs_to_blob(IOT_HUB_CONNECTION_STRING,
                hubName, os.environ["BLOB_ACCOUNT_URL"], device_id, "6", ".*", "0 days 15 minutes", "100")
            logging.info('Logs retrieval status: %s', status)
    except Exception as e:
        logging.error(f'Error processing device twin tags: {e} for device: {device_id}')
