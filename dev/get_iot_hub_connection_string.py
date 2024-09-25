import os
import logging
from azure.identity import DefaultAzureCredential
from azure.mgmt.iothub import IotHubClient

def get_device_connection_string(subscription_id, resource_group_name, iot_hub_name, device_id):
    try:
        # Use DefaultAzureCredential to authenticate
        credential = DefaultAzureCredential()
        # Create an IoT Hub client
        client = IotHubClient(credential, subscription_id=os.getenv('AZURE_SUBSCRIPTION_ID'))
        # Retrieve the IoT Hub connection string
        resource_group_name = os.getenv('RESOURCE_GROUP_NAME')
        iot_hub_name = os.getenv('IOT_HUB_NAME')
        device_id = os.getenv('DEVICE_ID')
        device = client.iot_hub_resource.get_keys_for_key_name(resource_group_name, iot_hub_name, device_id)
        connection_string = device.primary_key
    except Exception as e:
        logging.error(f"Error getting device connection string: {e}")
        connection_string = None

