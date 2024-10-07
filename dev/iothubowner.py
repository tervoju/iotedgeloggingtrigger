from azure.identity import DefaultAzureCredential
from azure.mgmt.iothub import IotHubClient

# Replace with your subscription ID, resource group name, and IoT Hub name
subscription_id = 'your_subscription_id'
resource_group_name = 'your_resource_group_name'
iothub_name = 'your_iothub_name'

# Authenticate using DefaultAzureCredential
credential = DefaultAzureCredential()

# Initialize the IoT Hub client
client = IotHubClient(credential, subscription_id)

# Get the shared access policies
policies = client.iot_hub_resource.list_keys(resource_group_name, iothub_name)

# Find the iothubowner policy
for policy in policies:
    if policy.key_name == 'iothubowner':
        print(f"Policy Name: {policy.key_name}")
        print(f"Primary Key: {policy.primary_key}")
        print(f"Secondary Key: {policy.secondary_key}")
        print(f"Rights: {policy.rights}")
