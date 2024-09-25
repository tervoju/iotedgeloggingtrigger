# edge module logs to blob storage when device is connected


## usage
./re_upload_logs.py devarcedge01 edgeAgent 6 *. "0 days 15 minutes" 100


## steps

1) create a storage account
2) create a blob container 
3) event grid
4) iot hub
5) iot edge device
6) device connected trigger
7) edge module to create logs
8) azure function to upload logs to blob storage

any when device is connected, the logs are written to the blob storage (if needed)

what edge device
what module



logs


1) device connected trigger
   -> use 
   -> https://learn.microsoft.com/en-us/azure/iot-edge/how-to-retrieve-iot-edge-logs?view=iotedge-1.5
   -> https://learn.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-direct-methods?view=iotedge-1.5



az iot hub generate-sas-token -n <iothubName> --du <duration>


#
{
       "schemaVersion": "1.0",
       "sasUrl": "Full path to SAS URL",
       "items": [
          {
             "id": "regex string",
             "filter": {
                "tail": "int",
                "since": "string",
                "until": "string",
                "loglevel": "int",
                "regex": "regex string"
             }
          }
       ],
       "encoding": "gzip/none",
       "contentType": "json/text" 
    }

    az account set --subscription <sub_id>


    https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/iot-edge/troubleshoot.md