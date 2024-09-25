import requests
import json
import time
from datetime import datetime
from base64 import b64encode, b64decode
from hashlib import sha256
from urllib import parse
from hmac import HMAC
from azure.iot.hub import IoTHubRegistryManager


def generate_sas_token(uri, key, policy_name, expiry=3600):
    ttl = time.time() + expiry
    sign_key = "%s\n%d" % ((parse.quote_plus(uri)), int(ttl))
    print(sign_key)
    signature = b64encode(
        HMAC(b64decode(key), sign_key.encode('utf-8'), sha256).digest())

    rawtoken = {
        'sr':  uri,
        'sig': signature,
        'se': str(int(ttl))
    }
    if policy_name is not None:
        rawtoken['skn'] = policy_name
    return 'SharedAccessSignature ' + parse.urlencode(rawtoken)


print("starting direct method call")

# Load sensitive information from environment variables
IOT_HUB_CONNECTION_STRING = "HostName=iothubtervo01.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=GMKFDqXns9cLz7IOSZpAAKG3Dx4s3RCESAIoTO8gRc0="
DURATION = 600  # Default to 1 hour if not set

# Generate the SAS token
SAS_TOKEN = generate_sas_token("iothubtervo01.azure-devices.net",
                               "GMKFDqXns9cLz7IOSZpAAKG3Dx4s3RCESAIoTO8gRc0=", "iothubowner", DURATION)

# Print the SAS token
#print("SAS Token: {}".format(sas_token))

# https://learn.microsoft.com/en-us/rest/api/iothub/service/modules/invoke-method?view=rest-iothub-service-2021-11-30
# https://<iothubName>.azure-devices.net/twins/<deviceId>/modules/<moduleName>/methods?api-version=2021-04-12
# https://<your-iot-hub-name>.azure-devices.net/twins/<device-id>/methods?api-version=2020-09-30
url = "https://iothubtervo01.azure-devices.net/twins/devarcedge01/module/edgeAgent/methods?api-version=2021-04-12"

payload = json.dumps({
    "methodName": "GetModuleLogs",
    "responseTimeoutInSeconds": 5,

    "payload": {
        "schemaVersion": "1.0",
        "items": [
            {
                "id": "IoTEdgeMetricsCollector",
                "filter": {
                    "tail": 10
                }
            }
        ],
        "encoding": "none",
        "contentType": "text"
    }
})

# upload logs
# SAS URL for uploading logs
SAS_URL = "https://devtwineventhandler.blob.core.windows.net/?sv=2022-11-02&ss=bfqt&srt=c&sp=rwdlacupiyx&se=2024-09-09T15:18:19Z&st=2024-09-09T07:18:19Z&spr=https&sig=bimSCZ4Ebhn2Vvx1tw5JlivsEJKYQMIbl9JnjGiTP6E%3D",

upload_payload = json.dumps({
    "methodName": "uploadModuleLogs",
    "responseTimeoutInSeconds": 5,

    "payload": {
        "schemaVersion": "1.0",
        "sasUrl": SAS_URL,
        "items": [
            {
                "id": "edgeAgent",
                "filter": {
                    "tail": 100,
                    "since": "0 days 15 minutes",
                    "loglevel": 6,
                    "regex": "*"
                }
            }
        ],
        "encoding": "gzip/none",
        "contentType": "json/text"
    }
})

# UploadModuleLogs
headers = {
    'Content-Type': 'application/json',
    'Authorization': SAS_TOKEN,
    'Accept': '*/*'
}

#
for x in range(5):
    timestr = time.strftime("%Y%m%d-%H%M%S")
    start_time = datetime.now().timestamp()
    response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
    
    if response.status_code == 200:
        print(response.text + "200 OK")
        break
    else :
        print(response.text + "Error: " + str(response.status_code))



    end_time = datetime.now().timestamp()
    print(response.text + ", " + str(end_time - start_time))
    time.sleep(1)
