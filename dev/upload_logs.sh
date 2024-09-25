az iot hub invoke-module-method --method-name UploadModuleLogs -n 'iothubtervo01.azure-devices.net' -d 'devarcedge01' -m \$edgeAgent --method-payload \
'
    {
        "schemaVersion": "1.0",
        "sasUrl": "https://devtwineventhandler.blob.core.windows.net/?sv=2022-11-02&ss=bfqt&srt=c&sp=rwdlacupiyx&se=2024-09-09T15:18:19Z&st=2024-09-09T07:18:19Z&spr=https&sig=bimSCZ4Ebhn2Vvx1tw5JlivsEJKYQMIbl9JnjGiTP6E%3D",
        "items": [
            {
                "id": ".*",
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