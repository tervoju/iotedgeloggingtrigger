import sys
import json
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod

# Replace with your IoT Hub connection string
IOT_HUB_CONNECTION_STRING = "HostName=iothubtervo01.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=GMKFDqXns9cLz7IOSZpAAKG3Dx4s3RCESAIoTO8gRc0="

# SAS URL for uploading logs
SAS_URL = "https://devtwineventhandler.blob.core.windows.net/edgelogs?sp=racw&st=2024-09-13T06:43:26Z&se=2024-11-08T15:43:26Z&spr=https&sv=2022-11-02&sr=c&sig=QNbmd23%2BOk9i81owPkgMs87utp6s0cXJC%2BXYUUdkrQI%3D"
# Initialize the IoTHubRegistryManager
registry_manager = IoTHubRegistryManager(IOT_HUB_CONNECTION_STRING)

# command example
''' 
upload_logs.py devarcedge01 edgeAgent 6 *. "0 days 15 minutes" 100
'''

# Arguments for the python script: module_id, log_level, regex, since, tail
device_id = sys.argv[1]  # "devarcedge01"
module_log_id = sys.argv[2]  # IoT Edge module ID
log_level = sys.argv[3]  # 0, 1, 2, 3, 4, 5, 6, 7
regex = sys.argv[4]  # e.g .*
since = sys.argv[5]  # e.g. 0 days 15 minutes
tail = sys.argv[6]  # e.g. 100

module_id = "$edgeAgent"

# Create a CloudToDeviceMethod object
method_name = "UploadModuleLogs"

# Define the payload
payload = {
    "schemaVersion": "1.0",
    "sasUrl": SAS_URL,
    "items": [
        {
            "id": "edgeHub",
            "filter": {
                "tail": tail,
                "since": since,
                "loglevel": log_level,
                "regex": ".*"
            }
        },
        {
            "id": "edgeAgent",
            "filter": {
                "tail": tail,
                "since": since,
                "loglevel": log_level,
                "regex": ".*"
            }
        }
    ],
    "encoding": "none",
    "contentType": "json"
}
trial = {
    "items": [
        {
            "id": 'edgeAgent', 
            'filter': {
                'tail': '100', 
                'since': '0 days 15 minutes', 
                'loglevel': '6', 
                'regex': '.*'
                }
        },
         {'id': 'edgeHub', 'filter': {'tail': '100', 'since': '0 days 15 minutes', 'loglevel': '6', 'regex': '.*'}}]}

# Convert payload to JSON string

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
