
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os
from dotenv import load_dotenv

load_dotenv()

def get_blob_service_client_account_key():
    # Replace <storage-account-name> with your actual storage account name
    account_url = "https://<storage-account-name>.blob.core.windows.net"
    shared_access_key = os.getenv("AZURE_STORAGE_ACCESS_KEY")
    credential = shared_access_key

    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient(account_url, credential=credential)

    return blob_service_client

def upload_blob_file(container_name: str, file_name: str, full_file_path: str):
    blob_service_client: BlobServiceClient = get_blob_service_client_account_key()
    container_client = blob_service_client.get_container_client(container=container_name)
    with open(file=full_file_path, mode="rb") as data:
        blob_client = container_client.upload_blob(name=file_name, data=data, overwrite=True)

def download_blob_to_file(container_name: str, file_name: str, full_file_path: str):
    blob_service_client: BlobServiceClient = get_blob_service_client_account_key()
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
    if blob_client.exists():
        with open(file=full_file_path, mode="wb") as blob:
            download_stream = blob_client.download_blob()
            blob.write(download_stream.readall())
            return True
    else:
        return False