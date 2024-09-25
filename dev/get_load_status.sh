az iot hub invoke-module-method --method-name 'GetTaskStatus' -n 'iothubtervo01.azure-devices.net'  -d 'devarcedge01' -m '$edgeAgent' --method-payload '
    {
      "schemaVersion": "1.0",
      "correlationId": "'$1'"
    }'
