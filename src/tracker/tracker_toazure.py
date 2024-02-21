
import os
import uuid

# Import the client object from the SDK library
from azure.storage.blob import BlobClient

# Retrieve the connection string from an environment variable. Note that a
# connection string grants all permissions to the caller, making it less
# secure than obtaining a BlobClient object using credentials.
conn_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]

# Create the client object for the resource identified by the connection
# string, indicating also the blob container and the name of the specific
# blob we want.
blob_client = BlobClient.from_connection_string(
    conn_string,
    container_name="tracking",
    blob_name=f"hour_report-{str(uuid.uuid4())[0:5]}.txt",
)

# Open a local file and upload its contents to Blob Storage
with open("./report.txt", "rb") as data:
    blob_client.upload_blob(data)
    print(f"Uploaded report.txt to {blob_client.url}")