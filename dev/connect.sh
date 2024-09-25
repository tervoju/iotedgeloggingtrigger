#
az iot hub device-identity connection-string show --device-id "devarcedge01" --hub-name "iothubtervo01.azure-devices.net"

#disconnect device from Azure
az iot hub device-identity update --device-id "devarcedge01" --hub-name "iothubtervo01.azure-devices.net" --set status=disabled

# connect to Azure
az iot hub device-identity update --device-id "devarcedge01" --hub-name "iothubtervo01.azure-devices.net" --set status=enabled
