import logging
import datetime

from azure.identity import DefaultAzureCredential
from azure.iot.hub import IoTHubRegistryManager
from azure.mgmt.iothub import IotHubClient
from azure.iot.hub.models import CloudToDeviceMethod
from azure.storage.blob import BlobServiceClient, generate_container_sas, ContainerSasPermissions

# Define your storage account and container details
account_url = "https://devtwineventhandler.blob.core.windows.net/edgemodulelogs"
container_name = "<your-container-name>"
blob_name = "<your-blob-name>"

def get_blob_sas_token(account_url, container_name, blob_name):
    """
    Get a SAS token for the blob.
    """
    # Create a BlobServiceClient using DefaultAzureCredential
    credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(account_url, credential=credential)
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)

    try:
        # Generate a user delegation SAS token for the container
        sas_token = generate_container_sas(
            account_name=blob_service_client.account_name,
            container_name=container_name,
            permission=ContainerSasPermissions(read=True, write=True, list=True),
            expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            user_delegation_key=blob_service_client.get_user_delegation_key(
                key_start_time=datetime.datetime.utcnow(),
                key_expiry_time=datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            )
        )
        sas_url = f"{blob_client.url}?{sas_token}"
        logging.info(f"SAS URL: {sas_url}")
        return sas_url

    except Exception as e:
        logging.info("Error: %s", str(e))
        return None


def get_edge_device_modules(iot_hub_connection_string, iot_hub, device_id):
    """
    Get the modules of an edge device.
    """
    credential = DefaultAzureCredential()
    registry_manager = IoTHubRegistryManager(iot_hub_connection_string, credential)
    modules = registry_manager.get_modules(device_id)
    return modules

def get_module_twin_tags(iot_hub_connection_string, iot_hub, device_id, module_id):
    """
    Get the tags from the module twin.
    """
    credential = DefaultAzureCredential()
    logging.info('module twin tags of module: %s', module_id)
    registry_manager = IoTHubRegistryManager(iot_hub_connection_string, credential)
    twin = registry_manager.get_module_twin(device_id, module_id)
    logging.info('Module module twin: %s', twin)
    try:
        twin_dict = twin.as_dict()
        return twin_dict["tags"]
    except Exception as e:
        logging.info("Error: %s", str(e))
        return {}

def upload_mi_module_logs_to_blob(iot_hub_connection_string, iot_hub, sas_url, device_id, log_level, regex, since, tail):
    """
    Upload module logs to blob storage using Managed Identity.
    """
    logging.info(
        "upload_module_logs_to_blob: %s, %s, %s, %s, %s, %s, %s",
        iot_hub, sas_url, device_id, log_level, regex, since, tail
    )

    credential = DefaultAzureCredential()
    registry_manager = IoTHubRegistryManager(iot_hub_connection_string, credential)
    module_id = "$edgeAgent"
    method_name = "UploadModuleLogs"

    sas_url = get_blob_sas_token(account_url, container_name, blob_name)

    if sas_url is None:
        logging.info("Error getting SAS URL")
        return

    try:
        modules = get_edge_device_modules(iot_hub_connection_string, iot_hub, device_id)
        items = []
        logging.info("module logs - getting items")
        for module in modules:
            if module.module_id in {"$edgeAgent", "$edgeHub"}:
                log_module_id = module.module_id[1:]
                logging.info("Logging is enabled for module: %s", module_id)
                items.append({
                    "id": log_module_id,
                    "filter": {
                        "tail": tail,
                        "since": since,
                        "loglevel": log_level,
                        "regex": ".*"
                    }
                })
            else:
                logging.info("Module ID: %s, Status: %s", module.module_id, module.connection_state)
                twin_tags = get_module_twin_tags(iot_hub_connection_string, iot_hub, device_id, module.module_id)
                logging.info("Module twin tags: %s", twin_tags)
                if twin_tags and twin_tags.get("logging") == "on":
                    logging.info("Logging is enabled for module: %s", module.module_id)
                    items.append({
                        "id": module.module_id,
                        "filter": {
                            "tail": tail,
                            "since": since,
                            "loglevel": log_level,
                            "regex": ".*"
                        }
                    })
                else:
                    logging.info("no Logging for module: %s", module.module_id)
        payload = {
            "schemaVersion": "1.0",
            "sasUrl": sas_url,
            "items": items,
            "encoding": "none",
            "contentType": "json"
        }

    except Exception as e:
        logging.info("Error invoking direct method: %s", e)
        raise e

    logging.info("creating logging method request")
    direct_method_request = CloudToDeviceMethod(
        method_name=method_name,
        payload=payload,
        response_timeout_in_seconds=30,
        connect_timeout_in_seconds=30
    )
    try:
        response = registry_manager.invoke_device_module_method(
            device_id,
            module_id,
            direct_method_request
        )
    except Exception as e:
        logging.info("Error invoking direct method: %s", e)
        raise e

    logging.info("Response status: %s", response.status)
    logging.info("Response payload: %s", response.payload)
    return response.status, response.payload

if __name__ == "__main__":
    '''
    iot_hub = "iothubtervo01"
    sas_url = (
        "https://devtwineventhandler.blob.core.windows.net/edgelogs?"
        "sp=racw&st=2024-09-13T06:43:26Z&se=2024-11-08T15:43:26Z&spr=https&"
        "sv=2022-11-02&sr=c&sig=QNbmd23%2BOk9i81owPkgMs87utp6s0cXJC%2BXYUUdkrQI%3D"
    )
    device_id = "devarcedge01"
    log_level = "6"
    regex = ".*"
    since = "0 days 15 minutes"
    tail = "100"

    upload_module_logs_to_blob(iot_hub, sas_url, device_id, log_level, regex, since, tail)
    '''
    print("This is the upload logs module")