# Azure Blob Storage and Excel ingestion utilities
import pandas as pd
from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient
import os

AZURE_STORAGE_ACCOUNT_URL = os.getenv("AZURE_STORAGE_ACCOUNT_URL", "https://yourstorageaccount.blob.core.windows.net/")

async def fetch_excel_from_blob(container_name: str, blob_name: str) -> bytes:
    credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(account_url=AZURE_STORAGE_ACCOUNT_URL, credential=credential)
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)
    stream = await blob_client.download_blob()
    data = await stream.readall()
    await blob_service_client.close()
    return data

def read_excel_to_df(excel_bytes: bytes) -> pd.DataFrame:
    return pd.read_excel(excel_bytes)
