import json
import logging
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod

IOT_HUB_CONNECTION_SAS = "GMKFDqXns9cLz7IOSZpAAKG3Dx4s3RCESAIoTO8gRc0="

# this could be useful for getting the connection string for the iot hub
def get_iot_hub_connection_string(subscription_id, resource_group_name, iot_hub_name):
    credential = DefaultAzureCredential()
    client = IotHubClient(credential, subscription_id)
    iot_hub = client.iot_hub_resource.get(resource_group_name, iot_hub_name)
    connection_string = next(cs.primary_key for cs in iot_hub.properties.authorization_policies if cs.key_name == 'iothubowner')
    return connection_string

def get_edge_device_modules(iot_hub, iot_hub_sas, device_id):
    # Replace with your IoT Hub connection string
    IOT_HUB_CONNECTION_STRING = "HostName=" + iot_hub +".azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey="+iot_hub_sas
    # Initialize the IoTHubRegistryManager
    registry_manager = IoTHubRegistryManager(IOT_HUB_CONNECTION_STRING)
    # Get the device twin
    modules = registry_manager.get_modules(device_id)
    return modules


def get_module_twin_tags(iot_hub, iot_hub_sas, device_id, module_id):
    # Replace with your IoT Hub connection string
    IOT_HUB_CONNECTION_STRING = "HostName=" + iot_hub +".azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey="+iot_hub_sas
    # Initialize the IoTHubRegistryManager
    logging.info(f'Device twin tags of module: {module_id}')
    registry_manager = IoTHubRegistryManager(IOT_HUB_CONNECTION_STRING)
    # Get the device twin
    twin = registry_manager.get_module_twin(device_id,module_id)
    logging.info(f'Device module twin: {twin}')
    try:
        # Convert the twin object to a dictionary
        twin_dict = twin.as_dict()
        # I need to get the tags from the twin json object. there is no get method
        #print(f'Device module twin tags: {twin_dict["tags"]}')
        return twin_dict["tags"]
    except Exception as e:
        logging.info(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    modules = get_edge_device_modules("iothubtervo01", IOT_HUB_CONNECTION_SAS, "devarcedge01")
      # Extract the list of modules
    items = []
    tail = 100
    since = "0 days 15 minutes"
    log_level = 6
    
    for module in modules:
        logging.info(f"Module ID: {module.module_id}, Status: {module.connection_state}")
        twin_tags = get_module_twin_tags("iothubtervo01", IOT_HUB_CONNECTION_SAS, "devarcedge01", module.module_id)
        logging.info("Module twin tags: ", twin_tags)
        if twin_tags and twin_tags["logging"] == "on":
            logging.info(f"Logging is enabled for module: {module.module_id}")
            items.append({"id": module.module_id,
            "filter": {
                "tail": tail,
                "since": since,
                "loglevel": log_level,
                "regex": ".*"
            }})
    print("Items: ", items)