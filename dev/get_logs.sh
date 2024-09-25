az iot hub invoke-module-method --method-name UploadModuleLogs -n 'iothubtervo01.azure-devices.net' -d 'devarcedge01' -m \$edgeAgent --method-payload \
'
    {
        "schemaVersion": "1.0",
        "items": [
            {
                "id": "IotEdgeIoTEdgeMetricsCollector",
                "filter": {
                    "tail": 100,
                    "since": "0 hours 15 minutes"
                }
            }
        ],
        "encoding": "gzip",
        "contentType": "json"
    }
'