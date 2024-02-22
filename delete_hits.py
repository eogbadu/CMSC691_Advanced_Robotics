import boto3
from mturk.config import access_id, secret_key, my_region_name
import datetime
import client_setup

region_name = my_region_name
aws_access_key_id = access_id
aws_secret_access_key = secret_key
ENDPOINT_URL = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com' 
# Uncomment this line to use in production
#ENDPOINT_URL = 'https://mturk-requester.us-east-1.amazonaws.com'

"""def client_setup():
    client = boto3.client(
        'mturk',
        endpoint_url=ENDPOINT_URL,
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    return client"""

def delete_hits(client):
    client = client_setup.setup_mturk_client()

    #Set an expiration time
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)  


    # iterate over each item in list hits
    for item in client.list_hits()['HITs']:
        
        # retrieve the hit id
        hit_id=item['HITId']
        print('HITId:', hit_id)


        # Get the hit status
        status = client.get_hit(HITId=hit_id)['HIT']['HITStatus']
        print('HITStatus:', status)

        # update the expiration time of hit            
        client.update_expiration_for_hit(HITId=hit_id,
            ExpireAt=yesterday
        )        

        # Delete hit
        try:
            client.delete_hit(HITId=hit_id)
        except:
            print('Not deleted')
        else:
            print('Deleted')

if __name__ == "__main__":
    user_confirm = input("Are you sure you want to delete all hits? Type Y to confirm: ")
    
    if user_confirm == 'Y':
        client = client_setup()
        delete_hits(client)