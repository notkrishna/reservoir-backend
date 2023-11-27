from b2sdk.v2 import B2Api
from b2sdk.v2.exception import FileNotPresent
import os
from django.conf import settings


def upload_to_b2(file_data, file_name):
    b2_api = B2Api()
    # b2_api.authorize_account('production', settings.B2_ACCOUNT_ID, settings.B2_APPLICATION_KEY)
    b2_api.authorize_account('production', settings.B2_ACCOUNT_ID, settings.B2_APPLICATION_KEY)

    bucket = b2_api.get_bucket_by_name(settings.B2_BUCKET_NAME)
    # file_data = self.request.data['image']
    file_name = os.path.basename(file_data.name)
    folder_name = 'dp'
    file_path = os.path.join(folder_name,file_name)
    file_data.seek(0)

                # file_size = file_data.size
                
                # with tempfile.NamedTemporaryFile() as temp_file:
                #     # Write the image data to the temporary file
                #     temp_file.write(file_data.read())


    uploaded_file = bucket.upload_bytes(file_data.read(),file_name = file_path)
    
    
    # b2_api = B2Api()
    # b2_api.authorize_account('production', settings.B2_ACCOUNT_ID, settings.B2_APPLICATION_KEY)

    # bucket = b2_api.get_bucket_by_name(settings.B2_BUCKET_NAME)

    # uploaded_file = bucket.upload(file_data, file_name)
    # file_url = uploaded_file.get_download_url()

    # return file_url

def delete_from_b2(file_url):
    b2_api = B2Api()
    b2_api.authorize_account('production', settings.B2_ACCOUNT_ID, settings.B2_APPLICATION_KEY)

    file_name = file_url.split("/")[-1]
    file_path = f"dp/{file_name}"  # Extract the file name from the URL
    bucket = b2_api.get_bucket_by_name(settings.B2_BUCKET_NAME)

    # Get the file ID using file name
    # file_versions = bucket.ls(show_versions=True, file_name=file_path)
    # file_id = file_versions[0]["fileId"]

    # Delete the file from B2
    try:
        bucket.hide_file(file_path)
    except FileNotPresent:
        print("file not present")
