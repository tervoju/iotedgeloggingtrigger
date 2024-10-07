import logging
import os
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, BlobPermissions
from dev.dm_requests import IOT_HUB_CONNECTION_STRING


SUBSCRIPTION_ID = 'ae92e392-3813-45dd-9c54-fe320939f03c'
RG_NAME = 'rg-iotopc-tervo'
BLOB_ACCOUNT_URL = 'https://devtwineventhandler.blob.core.windows.net'
BLOB_CONTAINER_NAME = 'edgemodulelogs'


def get_blob_sas_token(account_url, container_name):
    """
    Get a SAS token for the blob.
    """
    from datetime import timedelta

    logging.info(f"Getting SAS token for blob container {container_name}")
    # Create a BlobServiceClient object using the connection string

    # Generate a SAS token for the container with read permission
    # The token expires in 1 hour, and is valid for 1 minute before expiration
    # The start time is 1 minute before expiration to ensure that the token is valid for the duration of the request

    # Note: Replace 'account_url' and 'container_name' with your actual blob storage account URL and container name

    # Generate the SAS token for the blob container
    # This token can be used to access blobs in the container with read permission

    # The SAS token expires in 1 hour, and is valid for 1 minute before expiration
    # The start time is 1 minute before expiration to ensure that the token is valid for the duration of the request

    # Note: Replace 'account_url'
    try:
        blob_service_client = BlobServiceClient(account_url)

        blob_client = blob_service_client.get_blob_client(container=container_name)
        sas_token = blob_client.generate_shared_access_signature(
            permission=BlobPermissions(read=True),
            expiry=datetime.now(datetime.now.utc) + timedelta(hours=1),
            start=datetime.now(datetime.now.utc)- timedelta(minutes=1),
        )
        sas_url = f"{blob_client.url}?{sas_token}"
        logging.info(f"SAS URL: {sas_url}")
        return sas_url
    except Exception as e:
        logging.info("Error: %s", str(e))
        return None
    
    if __name__ == "__main__":
        get_blob_sas_token(BLOB_ACCOUNT_URL, BLOB_CONTAINER_NAME)