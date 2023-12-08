import boto3
from mturk.config import access_id, secret_key, my_region_name, s3_region_name
import os
import base64
import random  # to select a random row from our pair df
import sys 
import pandas as pd
import get_frames as gf
from PIL import Image
from io import BytesIO

# Constants
IMAGES_PATH = 'images'
VIDEOS_PATH = r"D:\SCOUT_RAV"
#VIDEOS_PATH = r"/media/zmarg1/Padlock_DT"
region_name = my_region_name
aws_access_key_id = access_id
aws_secret_access_key = secret_key
ENDPOINT_URL = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com' 
# Uncomment this line to use in production
#ENDPOINT_URL = 'https://mturk-requester.us-east-1.amazonaws.com'
S3_BUCKET_NAME = 'scoutmturk'
S3_REGION = s3_region_name
DAY_IN_SECONDS = 86400
#EXPIRATION_SECONDS = DAY_IN_SECONDS*3 
NAVIGATOR_TYPE = 'navigator'
HIT_TYPE_ID = '3MID1PD49XFUZY6UDB2YCDJUH80WKQ'

# Functions

#
def read_pair_data():
    # Get the current directory
    current_directory = os.getcwd()

    processed_path = os.path.join(current_directory, 'processed_data')

    processed_pairs_file = os.path.join(processed_path,'oneandtwowithfilepath.xlsx')
   
    # Read the file 
    df = pd.read_excel(processed_pairs_file)

    return df


# setup the mturk client
def client_setup():
    client = boto3.client(
        'mturk',
        endpoint_url=ENDPOINT_URL,
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    return client


# setup the s3 bucket client
def bucket_setup():
    # Init the client
    s3_client = boto3.client(
        's3',
        config=boto3.session.Config(signature_version='s3v4'),
        region_name=s3_region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    
    return s3_client


# creates random indices
def create_indices(indices_count, df):
    
    random_indices = random.sample(range(0, len(df)), indices_count)

    return random_indices


# reshuffles the random indices
def shuffle_indices(random_indices):
    
    random.shuffle(random_indices)
    
    return random_indices

# generates the url for the 
def assign_url(bucket_client, image_path, image_name, expiration_seconds):
    
    bucket_name = S3_BUCKET_NAME 

    # Upload the image to the bucket
    with open(image_path, 'rb') as file:
        bucket_client.upload_fileobj(file, bucket_name, image_name)
        
    # Generate a presigned url
    url = bucket_client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': bucket_name,
            'Key': image_name
        },
        # two day expiration time like hit task
        ExpiresIn = expiration_seconds  
    )

    return url


# function to create a hit type
def create_hit_type(client):
    # qualification requirement for hit type
    qualification_requirements = [{
        # replace with correct qualification type id you created 
        'QualificationTypeId': '000000000000000000L0',  # This is the qualification for HIT approval rate
        'Comparator': 'GreaterThan',
        'IntegerValues': [98],
        'RequiredToPreview': True
    }]


    # Create a new HIT type 
    my_hit_type = client.create_hit_type(
        Title = 'Select the best robot response to a human instruction',
        Description = 'Given a human instruction, select the best response from a robot (multiple choice)',
        Reward = '0.05',
        AssignmentDurationInSeconds = 600,
        AutoApprovalDelayInSeconds = DAY_IN_SECONDS *2,
        Keywords = 'text, quick, multiple choice, selection',
        QualificationRequirements=qualification_requirements
    )

    # save the hit type id
    hit_type_id = my_hit_type['HITTypeId']

    return hit_type_id

def create_hits(client,hit_type_id, number_hits, random_indices,bucket_client):  
    # read the pair data df
    df = read_pair_data() 
    
    images_folder = 'images'  # Replace this with your folder's path
    
    # Add two columns for each hitid
    df['hitid_yes_image'] = None
    df['hitid_no_image'] = None

    # create a count variable
    i = 0

    # stop looping when you get through entire df or if you exceed the number hits
    while ( (i < len(random_indices)) and (len(os.listdir(images_folder)) < number_hits) ):  
        """print("i inside loop:", i)
        print("len(random_indices):",len(random_indices))
        print("len(images_folder_path):", len(os.listdir(images_folder)))
        print("number hits:",number_hits)"""

        #Iterate through random indices and select the index
        random_index = random_indices[i]
        
        #Extract the command from the pair table
        random_row = df.iloc[random_index]
        
        # Encode the image using the random index to find the image file path
        #encoded_image = encode_image(df, random_index)

        video_type = NAVIGATOR_TYPE #decide what type of video you want to pass to get image
        
        # Only create hits when an image can extracted
        image_filename = get_image(random_row,video_type)

        """
        # To test the issues of finding files
        if not image_filename:
            break
        """

        if image_filename: 

            # Read the question file
            question = open(file ='mturk/question.xml',mode='r').read()

            #Extract the template string 
            template_string = '"Text to Replace"'

            command_string = str(random_row['Commander'])

            new_question = question.replace(template_string, command_string)

            expiration_seconds = DAY_IN_SECONDS * 3

            # get the image path
            image_path = os.path.join(IMAGES_PATH,image_filename)

            image_url = assign_url(bucket_client, image_path, image_filename, expiration_seconds)

            # check if the img url correctly generates
            if image_url:
                print("Generated Image URL:", image_url)  # Log or print the generated URL for inspection

                #question_image = question.replace('YOUR_IMAGE_DATA', encoded_image)
                question_image = new_question.replace('YOUR_IMAGE_URL_HERE', image_url) 

                # Log or print the length of the generated XML
                #print("Length of QuestionXML:", len(question_image))

                # Print or log the XML content for inspection
                #print("QuestionXML Content:")
                #print(question_image)  # Log the XML content itself
            
            
                # Create the second hit with the image
                yes_image_hit = client.create_hit_with_hit_type(
                    HITTypeId=hit_type_id,
                    MaxAssignments=1,
                    LifetimeInSeconds=expiration_seconds,
                    Question = question_image
                )

                # Print out the HIT related info
                print("A new IMAGE HIT has been created. You can preview it here:")
                print ("https://workersandbox.mturk.com/mturk/preview?groupId=" + yes_image_hit['HIT']['HITGroupId'])
                print ("HITID = " + yes_image_hit['HIT']['HITId'] + " (Use to Get Results)")
                # Remember to modify the URL above when you're publishing
                # HITs to the live marketplace.
                # Use: https://worker.mturk.com/mturk/preview?groupId="""

                # String literal of image div in question xml
                #image_instruction = r"You will be provided a still image of the robot's video feed from the moment the human issued the instruction."
                #image_please_do = r"<li><strong> Inspect the image showing the robot's video feed.</strong></li>"

                # remove the image instruction description string
                question_no_image = new_question

                    # String literal of image div in question xml
                image_div = r"<img src='YOUR_IMAGE_URL_HERE' alt='Image Placeholder' width='600' height='400'>"
                    
                    # remove the image div string
                question_no_image = question_no_image.replace(image_div, "")

                # Create the new hit
                no_image_hit = client.create_hit_with_hit_type(
                    HITTypeId=hit_type_id,
                    MaxAssignments=1,
                    LifetimeInSeconds=expiration_seconds,
                    Question = question_no_image
                )

                # Print out the HIT related info
                print("A new TEXT HIT has been created. You can preview it here:")
                print ("https://workersandbox.mturk.com/mturk/preview?groupId=" + no_image_hit['HIT']['HITGroupId'])
                print ("HITID = " + no_image_hit['HIT']['HITId'] + " (Use to Get Results)")
                # Remember to modify the URL above when you're publishing
                # HITs to the live marketplace.
                # Use: https://worker.mturk.com/mturk/preview?groupId=

                # add each hit id to the answer key
                df.loc[random_index,'hitid_yes_image'] = yes_image_hit['HIT']['HITId']
                df.loc[random_index,'hitid_no_image'] = no_image_hit['HIT']['HITId']

        i += 1
    
    # Get the current directory
    current_dir = os.path.dirname(__file__)

    #Create a path to the processed_data folder
    processed_path = os.path.join(current_dir, 'processed_data')

    # save answer key to the processed paths
    df.to_excel(os.path.join(processed_path,'answer_key.xlsx'), index=False)


def get_image(df_row, video_type):
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

    video_filename = expr_month + "_" + expr_day + "_" + temp1 + "_" + participant_nbr + "_" + expr_location + "_"+ video_type + ".ogv"

    # Get the full path to the video
    video_path = os.path.join(VIDEOS_PATH, temp1, temp2, "Screen_recorder", video_filename)
    
    # Get the frames
    timestamp = df_row["Timestamp"]
    image_filename = expr_month + "_" + expr_day + "_experiment_" + participant_nbr + "_" + expr_location + "_" + f'{timestamp:.2f}' + "_" + video_type + ".jpg"

    screen_recorder_path = os.path.join(VIDEOS_PATH, temp1, temp2, "Screen_recorder")
    
    if not(os.path.exists(screen_recorder_path)):
       print(f"Screen Recorder folder does not exist for experiment: {screen_recorder_path}")
       return False
    
    # Get the frame needed
    is_frame_extracted = gf.GetFrames(timestamp, video_path, image_filename)

    if not (is_frame_extracted):
        print("checking if adding year name first helps pull the video")

        video_filename_year_check = expr_year + "_" + expr_month + "_" + expr_day + "_" + temp1 + "_" + participant_nbr + "_" + expr_location + "_"+ video_type + ".ogv"
        
        # Get the full path to the video
        video_path_year_check = os.path.join(VIDEOS_PATH, temp1, temp2, "Screen_recorder", video_filename_year_check)

        # Now re-input the video_path
        is_frame_extracted = gf.GetFrames(timestamp, video_path_year_check, image_filename)
    
    # try to get the frame
    if not (is_frame_extracted):
        print("checking if removing exp number from video name")

        video_filename_expnum_check = expr_month + "_" + expr_day + "_" + "experiment" + "_" + participant_nbr + "_" + expr_location + "_"+ video_type + ".ogv"
        
        # Get the full path to the video
        video_path_expnum_check = os.path.join(VIDEOS_PATH, temp1, temp2, "Screen_recorder", video_filename_expnum_check)

        # Now re-input the video_path
        is_frame_extracted = gf.GetFrames(timestamp, video_path_expnum_check, image_filename)

    # try to get the frame
    if not (is_frame_extracted):
        print("checking if adding a period at the end")

        video_filename_period_check = expr_month + "_" + expr_day + "_" + "experiment" + "_" + participant_nbr + "_" + expr_location + "_"+ video_type + "." + ".ogv"
        
        # Get the full path to the video
        video_path_period_check = os.path.join(VIDEOS_PATH, temp1, temp2, "Screen_recorder", video_filename_period_check)

        # Now re-input the video_path
        is_frame_extracted = gf.GetFrames(timestamp, video_path_period_check, image_filename)
    
    if not(is_frame_extracted):
        print("the image is still not extracted")
        return False
    
    # return the image name in the images folder
    image_filename = is_frame_extracted
    
    return image_filename

# delete once we know hosting works
while False:
    def encode_image(df, df_index):
        # comment out to replace placeholder cat once we get images folder
        #image_path = os.path.abspath("cat.jpg")

        #Uncommment once you are connected to the SCOUT Box
        #Extract the command from the pair table
        
        random_row = df.iloc[df_index]

        # only encode if you can get the image first
        if get_image(random_row):

            image_filename = get_image(random_row)

            # Get the current directory
            current_directory = os.getcwd()

            # get the images directory
            images_dir = os.path.join(current_directory, IMAGES_PATH)

            # set the image_path
            image_path =  os.path.join(images_dir, image_filename)

            """# Delete once we know it is safe not to compress the images
            # open the image with pillow
            image = Image.open(image_path)

            max_width = 800 
            max_height = 600
            quality = 85

            # Resize image
            image.thumbnail((max_width, max_height), Image.BICUBIC)

            # Compress the image
            buffered = BytesIO()
            image.save(buffered, format="JPEG", quality=quality)
            image_bytes = buffered.getvalue()

            # Encode the image bytes as base64
            encoded_image = base64.b64encode(image_bytes).decode('utf-8')"""
            
            """# Read and encode each image as base 64
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")"""
            
            #return encoded_image"

if __name__ == "__main__":
    #check if user passes data folder argument
    if len(sys.argv) > 1:
        # accept the second argument as the number hits
        number_hits = int(sys.argv[1])
       
        # setup the client
        client = client_setup()

        # setup bucket client
        bucket_client = bucket_setup()

        # import the pair data df
        df = read_pair_data()
       
        # Create random indices needed for the entire df
        random_indices = create_indices(len(df), df)

        #hit_type_id = create_hit_type(client)
        hit_type_id = HIT_TYPE_ID

        # create hits without image included
        create_hits(client,hit_type_id,number_hits,random_indices,bucket_client)
        
        # shuffle the indices
        #shuffle_indices(random_indices)
    
        # create hits with image included
        #create_hits(client,hit_type_id,random_indices,is_image_included = True)
        
    # Otherwise request images path input
    else:
       print(f"Please provide the number of hits you would like to generate",
              "'python create_tasks.py <number>'")

       
