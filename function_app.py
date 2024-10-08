import logging
import os
from datetime import datetime, timedelta
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.iot.hub import IoTHubRegistryManager
from azure.mgmt.iothub import IotHubClient
from azure.storage.blob import BlobServiceClient, generate_container_sas, ContainerSasPermissions
from dev.dm_requests import IOT_HUB_CONNECTION_STRING
from uploadlogs import upload_mi_module_logs_to_blob

app = func.FunctionApp()

SUBSCRIPTION_ID = 'ae92e392-3813-45dd-9c54-fe320939f03c'
RG_NAME = 'rg-iotopc-tervo'
BLOB_ACCOUNT_NAME = 'devtwineventhandler'
BLOB_CONTAINER_NAME = 'edgemodulelogs'


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
        # Get the shared access policies
        policies = client.iot_hub_resource.list_keys(resource_group_name, iot_hub_name)

        # Find the iothubowner policy
        for policy in policies:
            if policy.key_name == 'iothubowner':
                logging.info(f"Policy Name: {policy.key_name}")
                #logging.info(f"Primary Key: {policy.primary_key}")
                #print(f"Secondary Key: {policy.secondary_key}")
                #logging.info(f"Rights: {policy.rights}")
                return policy.primary_key
    
        logging.error('No authorization policies found for IoT Hub: %s', iot_hub_name)
        return None
    except Exception as e:
        logging.error('Error getting IoT Hub connection string with default credential: %s', e)
        return None
    
def get_blob_sas_token(account_name, container_name):
    """
    Get a SAS token for the blob.
    """
   
    # Create a BlobServiceClient object using the connection string

    # Generate a SAS token for the container with read permission
    # The token expires in 1 hour, and is valid for 1 minute before expiration
    # The start time is 1 minute before expiration to ensure that the token is valid for the duration of the request
    # Generate the SAS token for the blob container
    # This token can be used to access blobs in the container with read permission

    # The SAS token expires in 1 hour, and is valid for 1 minute before expiration
    # The start time is 1 minute before expiration to ensure that the token is valid for the duration of the request

    credential = DefaultAzureCredential()
    logging.info(f"Getting SAS token for blob container {container_name}")

    try:
        # Use Managed Identity to authenticate with Azure Storage
        credential = DefaultAzureCredential()
        blob_service_client = BlobServiceClient(account_url=f"https://{account_name}.blob.core.windows.net", credential=credential)
    
        # Get the container client
        container_client = blob_service_client.get_container_client(container_name)
    
        logging.info(f"container account key: {container_client.credential.account_key}")
        # Generate a SAS token for the blob
        sas_token = generate_container_sas(
            account_name=container_client.account_name,
            container_name=container_client.container_name,
            account_key=container_client.credential.account_key,
            permission=ContainerSasPermissions(write=True),
            expiry=datetime.now.datetime.utc() + timedelta(hours=1)
        )
        logging.info(f"SAS URL: {sas_token}")
        # Construct the full URL to the blob including the SAS token
        sas_url = f"https://{account_name}.blob.core.windows.net/{container_name}?{sas_token}"
        return sas_url
    except Exception as e:
        logging.info("Error: %s", str(e))
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
    except Exception as e:
        logging.error('Error processing device connected event: %s', e)
        return

    IOT_HUB_CONNECTION_KEY = get_iot_hub_connection_string(hubName, SUBSCRIPTION_ID, RG_NAME)
    IOT_HUB_CONNECTION_STRING = f"HostName={hubName}.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey={IOT_HUB_CONNECTION_KEY}"

    if IOT_HUB_CONNECTION_STRING is None:
        logging.error('Failed to get IoT Hub connection string')
        return
    
    sas_url = get_blob_sas_token(BLOB_ACCOUNT_NAME, BLOB_CONTAINER_NAME)
    if sas_url is None:
        logging.error('Failed to get SAS URL for blob storage')
        return

    try:
        tags = get_device_twin_tags(IOT_HUB_CONNECTION_STRING, device_id)
        logging.info('Device twin %s tags: %s', device_id, tags)

        logging_on = tags.get("logging")
        if logging_on == "on":
            logging.info(f'Device logging is enabled: {device_id}')
            status, payload = upload_mi_module_logs_to_blob(IOT_HUB_CONNECTION_STRING,
                hubName, sas_url, device_id, "6", ".*", "0 days 15 minutes", "100")
            logging.info('Logs retrieval status: %s', status)
    except Exception as e:
        logging.error(f'Error processing device twin tags: {e} for device: {device_id}')
