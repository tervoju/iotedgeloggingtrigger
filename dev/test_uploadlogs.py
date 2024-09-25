import sys
import json
import logging

from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod

BLOB_SAS = "https://devtwineventhandler.blob.core.windows.net/edgelogs?sp=racw&st=2024-09-13T06:43:26Z&se=2024-11-08T15:43:26Z&spr=https&sv=2022-11-02&sr=c&sig=QNbmd23%2BOk9i81owPkgMs87utp6s0cXJC%2BXYUUdkrQI%3D"


def retrieve_logs_from_iot_edge_module2blob():
    # Implement the logic to retrieve logs from IoT Edge module

    # Log the function invocation
    logging.info('Retrieving logs from IoT Edge module')
    # Implement the logic to retrieve logs from IoT Edge module
    status, payload = uploadlogs("iothubtervo01",
                                 "GMKFDqXns9cLz7IOSZpAAKG3Dx4s3RCESAIoTO8gRc0=",
                                 "https://devtwineventhandler.blob.core.windows.net/edgelogs?sp=racw&st=2024-09-09T09:56:20Z&se=2024-09-09T17:56:20Z&spr=https&sv=2022-11-02&sr=c&sig=gF%2Ft683X8ZGdBZqqtrR4%2FBC%2BwDn0Vrgpyhw3IsAy2kQ%3D",
                                 "devarcedge01",
                                 "edgeAgent",
                                 "6",
                                 "*.",
                                 "0 days 15 minutes",
                                 "100")
    logging.info("Running the uploadlogs function")
    return status


def uploadlogs(iot_hub, iot_hub_sas, sasUrl, device_id, log_module_id, log_level, regex, since, tail):

    # Replace with your IoT Hub connection string
    IOT_HUB_CONNECTION_STRING = "HostName=" + iot_hub + \
        ".azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey="+iot_hub_sas

    # SAS URL for uploading logs
    SAS_URL = sasUrl

    # Initialize the IoTHubRegistryManager
    registry_manager = IoTHubRegistryManager(IOT_HUB_CONNECTION_STRING)

    # Logs from edgeAgent module
    module_id = "$edgeAgent"

    # Create a CloudToDeviceMethod object
    method_name = "UploadModuleLogs"

    # Define the payload
    payload = {
        "schemaVersion": "1.0",
        "sasUrl": SAS_URL,
        "items": [{'id': 'iotdb', 'filter': {'tail': 100, 'since': '0 days 15 minutes', 'loglevel': 6, 'regex': '.*'}}, {'id': 'IoTEdgeMetricsCollector', 'filter': {'tail': 100, 'since': '0 days 15 minutes', 'loglevel': 6, 'regex': '.*'}}],
        "encoding": "none",
        "contentType": "json"
    }

    # Define the method parameters
    timeout = 10

    # Create the CloudToDeviceMethod object
    direct_method_request = CloudToDeviceMethod(
        method_name=method_name,
        payload=payload,
        response_timeout_in_seconds=30,
        connect_timeout_in_seconds=30
    )

    try:
        # Invoke the direct method
        response = registry_manager.invoke_device_module_method(
            device_id,
            module_id,
            direct_method_request
        )
    except Exception as e:
        print("Error invoking direct method: {}".format(e))
        raise e

    # Print the response
    print("Response status: {}".format(response.status))
    print("Response payload: {}".format(response.payload))
    return response.status, response.payload


def retrieve_logs_from_iot_edge_module2blob():
    # Implement the logic to retrieve logs from IoT Edge module
    # Log the function invocation
    logging.info('Retrieving logs from IoT Edge module')
    # Implement the logic to retrieve logs from IoT Edge module
    status, payload = uploadlogs("iothubtervo01",
                                 "GMKFDqXns9cLz7IOSZpAAKG3Dx4s3RCESAIoTO8gRc0=",
                                 BLOB_SAS,
                                 "devarcedge01",
                                 "edgeAgent",
                                 "6",
                                 "'*.'",
                                 "0 days 15 minutes",
                                 "100")
    logging.info("Running the uploadlogs function")
    return status


if __name__ == "__main__":

    status = retrieve_logs_from_iot_edge_module2blob()
