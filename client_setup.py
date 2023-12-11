import boto3
from mturk.config import access_id, secret_key, my_region_name
from botocore.exceptions import NoCredentialsError

region_name = my_region_name
aws_access_key_id = access_id
aws_secret_access_key = secret_key
ENDPOINT_URL = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com' 
# Uncomment this line to use in production
#ENDPOINT_URL = 'https://mturk-requester.us-east-1.amazonaws.com'

def setup_mturk_client():
    try:
        client = boto3.client(
        'mturk',
        endpoint_url=ENDPOINT_URL,
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        )
        
        return client

    except NoCredentialsError:
        print("Credentials not found or invalid.")