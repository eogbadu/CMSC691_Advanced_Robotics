import boto3
from mturk.config import access_id, secret_key, my_region_name
import os
import base64
import random  # to select a random row from our pair df
import sys 
import pandas as pd
import get_frames as gf

# Constants
IMAGES_PATH = 'images'
VIDEOS_PATH = r"D:\SCOUT_RAV"
region_name = my_region_name
aws_access_key_id = access_id
aws_secret_access_key = secret_key
ENDPOINT_URL = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com' 
# Uncomment this line to use in production
#ENDPOINT_URL = 'https://mturk-requester.us-east-1.amazonaws.com'

def read_pair_data():
    # Get the current directory
    current_directory = os.getcwd()

    processed_path = os.path.join(current_directory, 'processed_data')

    processed_pairs_file = os.path.join(processed_path,'oneandtwowithfilepath.xlsx')
   
    # Read the file 
    df = pd.read_excel(processed_pairs_file)

    return df

def client_setup():
    client = boto3.client(
        'mturk',
        endpoint_url=ENDPOINT_URL,
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    # This will return $10,000.00 in the MTurk Developer Sandbox
    print("I have $" + client.get_account_balance()['AvailableBalance'] + " in my Sandbox account")

    return client

def create_indices(number_hits, df):
    
    random_indices = random.sample(range(0, len(df)), number_hits)

    print(random_indices)

    return random_indices

def shuffle_indices(random_indices):
    random.shuffle(random_indices)
    
    return random_indices

def create_hit_type(client):
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

    return hit_type_id

def create_hits(client,hit_type_id,random_indices,is_image_included = False):
    
    # read the pair data df
    df = read_pair_data() 
    
    # Read the question file
    question = open(file ='mturk/question.xml',mode='r').read()

    #Extract the template string 
    template_string = '"Text to Replace"'

    number_hits = len(random_indices)

    for i in range(number_hits):
        #Iterate through random indices and select the index
        random_index = random_indices[i]
        
        #Extract the command from the pair table
        random_row = df.iloc[random_index]
        
        command_string = random_row['Commander']

        # when we want the image included find the path
        if is_image_included:
            # Encode the image using the random index to find the image file path
            #uncomment when this function is ready
            encoded_image = encode_image(df, random_index)

            # Replace the with the real image
            question = question.replace('YOUR_IMAGE_DATA', encoded_image) 
        #Otherwise, remove the image display in the xml file
        else:
            # String literal of image div in question xml
            image_instruction = r"You may be provided an image for additional context."
            
            # remove the image instruction description string
            question = question.replace(image_instruction, "")

            # String literal of image div in question xml
            image_div = r"<img src='data:image/jpeg;base64,YOUR_IMAGE_DATA' alt='Image Placeholder' width='300' height='200'>"
            
            # remove the image div string
            question = question.replace(image_div, "")

        """# Create the new hit
        new_hit = client.create_hit_with_hit_type(
            HITTypeId=hit_type_id,
            MaxAssignments=1,
            LifetimeInSeconds=172800,
            Question = question.replace(template_string, command_string)
        )"""

        # Create a second hit with the image included

        # Print out the HIT related info
        print("A new HIT has been created. You can preview it here:")
"""        print ("https://workersandbox.mturk.com/mturk/preview?groupId=" + new_hit['HIT']['HITGroupId'])
        print ("HITID = " + new_hit['HIT']['HITId'] + " (Use to Get Results)")"""
        # Remember to modify the URL above when you're publishing
        # HITs to the live marketplace.
        # Use: https://worker.mturk.com/mturk/preview?groupId=

def get_image(df_row):
    file_name = df_row['File Name']

    # Break up file name into parts
    expr_location = ""
    expr_nbr = file_name[3:4]
    expr_year = file_name[16:20]
    expr_month = file_name[12:15]
    expr_day = file_name[9:11]
    participant_nbr = file_name[6:8]

    # Convert month to full name
    if expr_month == "apr":
        expr_month = "april"
    elif expr_month == "mar":
        expr_month = "march"
    elif expr_month == "feb":
        expr_month = "february"

    # Set the location of the experiment
    if "alley" in file_name:
        expr_location = "alley"
    elif "house1" in file_name:
        expr_location = "house1"
    elif "house2" in file_name:
        expr_location = "house2"

    # define the experiment number
    temp1 = "experiment" + expr_nbr 
    temp2 = expr_year + "_" + expr_month + "_" + expr_day + "_" + temp1 + "_" + participant_nbr

    # Get the video file name that we intend to get frames from
    video_filename = expr_month + "_" + expr_day + "_experiment_" + participant_nbr + "_" + expr_location + "_navigator.ogv"

    # Get the full path to the video
    video_path = os.path.join(VIDEOS_PATH, temp1, temp2, "Screen_recorder", video_filename)

    # Get the frames
    timestamp = df_row["Timestamp"]
    image_filename = expr_month + "_" + expr_day + "_experiment_" + participant_nbr + "_" + expr_location + "_" + f'{timestamp:.2f}' + "_navigator.jpg"

    gf.GetFrames(timestamp, video_path, image_filename)

    return image_filename

def encode_image(df, df_index):
    # comment out to replace placeholder cat once we get images folder
    #image_path = os.path.abspath("cat.jpg")

    #Uncommment once you are connected to the SCOUT Box
    #Extract the command from the pair table
    random_row = df.iloc[df_index]

    image_filename = get_image(random_row)

    # Get the current directory
    current_directory = os.getcwd()

    # get the images directory
    images_dir = os.path.join(current_directory, IMAGES_PATH)

    # set the image_path
    image_path =  os.path.join(images_dir, image_filename)
            
    # Read and encode each image as base 64
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
    
    return encoded_image

if __name__ == "__main__":
    #check if user passes data folder argument
    if len(sys.argv) > 1:
        # accept the second argument as the number hits
        number_hits = int(sys.argv[1])
       
        # setup the client
        client = client_setup()

        # import the pair data df
        df = read_pair_data()
       
        # Create random indices needed
        random_indices = create_indices(number_hits, df)

        hit_type_id = create_hit_type(client)

        # create hits without image included
        create_hits(client,hit_type_id,random_indices,is_image_included = False)
        
        # shuffle the indices
        shuffle_indices(random_indices)
    
        # create hits with image included
        create_hits(client,hit_type_id,random_indices,is_image_included = True)
        
    # Otherwise request images path input
    else:
       print(f"Please provide the number of hits you would like to generate",
              "'python create_tasks.py <number>'")

       
