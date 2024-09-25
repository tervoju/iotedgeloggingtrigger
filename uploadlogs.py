import logging

from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod

def get_edge_device_modules(iot_hub, iot_hub_sas, device_id):
    """
    Get the modules of an edge device.
    """
    iot_hub_connection_string = (
        "HostName=" + iot_hub + ".azure-devices.net;"
        "SharedAccessKeyName=iothubowner;"
        "SharedAccessKey=" + iot_hub_sas
    )
    registry_manager = IoTHubRegistryManager(iot_hub_connection_string)
    modules = registry_manager.get_modules(device_id)
    return modules

def get_module_twin_tags(iot_hub, iot_hub_sas, device_id, module_id):
    """
    Get the tags from the module twin.
    """
    iot_hub_connection_string = (
        "HostName=" + iot_hub + ".azure-devices.net;"
        "SharedAccessKeyName=iothubowner;"
        "SharedAccessKey=" + iot_hub_sas
    )
    logging.info('module twin tags of module: %s', module_id)
    registry_manager = IoTHubRegistryManager(iot_hub_connection_string)
    twin = registry_manager.get_module_twin(device_id, module_id)
    logging.info('Module module twin: %s', twin)
    try:
        twin_dict = twin.as_dict()
        return twin_dict["tags"]
    except Exception as e:
        logging.info("Error: %s", str(e))
        return  {}

def upload_module_logs_to_blob(iot_hub, iot_hub_sas, sas_url, device_id, log_level, regex, since, tail):
    """
    Upload module logs to blob storage.
    """
    logging.info(
        "upload_module_logs_to_blob: %s, %s, %s, %s, %s, %s, %s, %s",
        iot_hub, iot_hub_sas, sas_url, device_id, log_level, regex, since, tail
    )

    iot_hub_connection_string = (
        "HostName=" + iot_hub + ".azure-devices.net;"
        "SharedAccessKeyName=iothubowner;"
        "SharedAccessKey=" + iot_hub_sas
    )
    registry_manager = IoTHubRegistryManager(iot_hub_connection_string)
    module_id = "$edgeAgent"
    method_name = "UploadModuleLogs"

    try:
        modules = get_edge_device_modules(iot_hub, iot_hub_sas, device_id)
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
                twin_tags = get_module_twin_tags(iot_hub, iot_hub_sas, device_id, module.module_id)
                logging.info("Module twin tags: %s", twin_tags)
                if twin_tags and twin_tags["logging"] == "on":
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
    iot_hub_sas = "GMKFDqXns9cLz7IOSZpAAKG3Dx4s3RCESAIoTO8gRc0="
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

    upload_module_logs_to_blob(iot_hub, iot_hub_sas, sas_url, device_id, log_level, regex, since, tail)
    '''
    print("This is the upload logs module")