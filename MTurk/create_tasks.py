import boto3
from config import access_id, secret_key, my_region_name
import os
import base64


region_name = my_region_name
aws_access_key_id = access_id
aws_secret_access_key = secret_key
ENDPOINT_URL = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com' 
# Uncomment this line to use in production
#ENDPOINT_URL = 'https://mturk-requester.us-east-1.amazonaws.com'

client = boto3.client(
    'mturk',
    endpoint_url=ENDPOINT_URL,
    region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)

# This will return $10,000.00 in the MTurk Developer Sandbox
print("I have $" + client.get_account_balance()['AvailableBalance'] + " in my Sandbox account")

# Read the question file
question = open(file ='question.xml',mode='r').read()

# Create a new HIT type 
my_hit_type = client.create_hit_type(
    Title = 'Select the best response to the instruction',
    Description = 'Read this instruction and select select the most appropriate response or action from the list provided: turn, move, send image, stop, or explore',
    Reward = '0.10',
    AssignmentDurationInSeconds = 600,
    AutoApprovalDelayInSeconds = 172800,
    Keywords = 'text, quick, labeling',
    QualificationRequirements=[]
)

# save the hit type id
hit_type_id = my_hit_type['HITTypeId']

#Extract the template string 
template_string = '"Text to Replace"'

number_hits = 1
count = 0
for i in range(number_hits):
    # Create a new hit using the hit type
    #Extract the command from the pair table
    command_string = "Turn left 45 degrees"

    #Find the image path
    image_path = os.path.abspath("cat.jpg")

    # Get the image path
    #image_path = '/path/to/your/image_directory/data.jpg'

    # Read and encode each image as base 64
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

    # Replace the with the real image
    question = question.replace('YOUR_IMAGE_DATA', encoded_image) 

    # Create the new hit
    new_hit = client.create_hit_with_hit_type(
        HITTypeId=hit_type_id,
        MaxAssignments=1,
        LifetimeInSeconds=172800,
        Question = question.replace(template_string, command_string)
    )

    # Print out the HIT related info
    print("A new HIT has been created. You can preview it here:")
    print ("https://workersandbox.mturk.com/mturk/preview?groupId=" + new_hit['HIT']['HITGroupId'])
    print ("HITID = " + new_hit['HIT']['HITId'] + " (Use to Get Results)")
    # Remember to modify the URL above when you're publishing
    # HITs to the live marketplace.
    # Use: https://worker.mturk.com/mturk/preview?groupId=

