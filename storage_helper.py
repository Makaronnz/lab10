import os
from azure.storage.blob import BlobServiceClient
from werkzeug.utils import secure_filename
import uuid

def upload_file_to_azure(file):
    try:
        connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        if not connect_str:
            print("Azure Storage Connection String not found.")
            return None

        container_name = "book-covers"
        
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        
        try:
            container_client = blob_service_client.get_container_client(container_name)
            if not container_client.exists():
                container_client.create_container(public_access="blob")
        except Exception as e:
            print(f"Container access error: {e}")
            return None

        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=unique_filename)
        
        file.seek(0)
        blob_client.upload_blob(file, overwrite=True)
        
        return blob_client.url

    except Exception as e:
        print(f"Azure Upload Error: {e}")
        return None
