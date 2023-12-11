import boto3
from mturk.config import access_id, secret_key, my_region_name

region_name = my_region_name
aws_access_key_id = access_id
aws_secret_access_key = secret_key
ENDPOINT_URL = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com' 
# Uncomment this line to use in production
#ENDPOINT_URL = 'https://mturk-requester.us-east-1.amazonaws.com'

from boto3 import Session
from botocore.exceptions import NoCredentialsError

def setup_mturk_client():
    try:
        # Replace these with your AWS credentials
        aws_access_key_id = 'YOUR_ACCESS_KEY'
        aws_secret_access_key = 'YOUR_SECRET_KEY'
        aws_region_name = 'YOUR_AWS_REGION'

        # Create a session using your credentials
        session = Session(aws_access_key_id=aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key,
                            region_name=aws_region_name)

        # Create an MTurk client and assign it to the class attribute
        mturk_client = session.client('mturk')
        return mturk_client

        # Add your further actions here using self.mturk_client

    except NoCredentialsError:
        print("Credentials not found or invalid.")