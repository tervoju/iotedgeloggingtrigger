import logging
import azure.functions as func


app = func.FunctionApp()

@app.event_grid_trigger(arg_name="azeventgrid")
def EventGridTrigger(azeventgrid: func.EventGridEvent):

    logging.info('Python EventGrid trigger processed an IoT HUb device event')
    logging.info('new device, device deleted, status change')
    logging.info(azeventgrid)
    # i need the content of the eventgrid topic message
    # i need to know the event type
    # i need to know the device id
    content = azeventgrid.get_json()
    event_type = azeventgrid.event_type
 
    logging.info(event_type)
    if event_type == 'Microsoft.Devices.DeviceCreated':
        logging.info('new device')
        device_id = content.get('deviceId')
        logging.info(device_id)

    if event_type == 'Microsoft.Devices.DeviceDeleted':
        logging.info('device deleted')
        device_id = content.get('deviceId')
        logging.info(device_id) 