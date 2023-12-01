import boto3
from mturk.config import access_id, secret_key, my_region_name
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

    return client

def create_indices(indices_count, df):
    
    random_indices = random.sample(range(0, len(df)), indices_count)

    return random_indices

def shuffle_indices(random_indices):
    random.shuffle(random_indices)
    
    return random_indices

def create_hit_type(client):
    # Create a new HIT type 
    my_hit_type = client.create_hit_type(
        Title = 'Select the best response to the instruction',
        Description = 'Read this instruction and select select the most appropriate response or action from the list provided: turn, move, send image, stop, or explore',
        Reward = '0.05',
        AssignmentDurationInSeconds = 600,
        AutoApprovalDelayInSeconds = 172800,
        Keywords = 'text, quick, labeling',
        QualificationRequirements=[]
    )

    # save the hit type id
    hit_type_id = my_hit_type['HITTypeId']

    return hit_type_id

def create_hits(client,hit_type_id, number_hits, random_indices,is_image_included = True):
    
    # read the pair data df
    df = read_pair_data() 
    
    images_folder = 'images'  # Replace this with your folder's path
    images_folder_path = os.listdir(images_folder)
    
    # create a count variable
    i = 0

    # stop looping when you get through entire df or if you exceed the number hits
    while ( (i < len(random_indices)) and (len(os.listdir(images_folder)) < number_hits) ):  
        print("i inside loop:", i)
        print("len(random_indices):",len(random_indices))
        print("len(images_folder_path):", len(os.listdir(images_folder)))
        print("number hits:",number_hits)

        #Iterate through random indices and select the index
        random_index = random_indices[i]
        
        #Extract the command from the pair table
        random_row = df.iloc[random_index]
        
        # Encode the image using the random index to find the image file path
        encoded_image = encode_image(df, random_index)

        # Only create hits when an image can be encoded
        if encoded_image: 
            
            # Read the question file
            question = open(file ='mturk/question.xml',mode='r').read()

            #Extract the template string 
            template_string = '"Text to Replace"'

            command_string = random_row['Commander']

            new_question = question.replace(template_string, command_string)
            
            question_image = question.replace('YOUR_IMAGE_DATA', encoded_image) 

            # Log or print the length of the generated XML
            #print("Length of QuestionXML:", len(question_image))

            # Print or log the XML content for inspection
            #print("QuestionXML Content:")
            #print(question_image)  # Log the XML content itself
            
            question_image = new_question

            """# Create the second hit with the image
            yes_image_hit = client.create_hit_with_hit_type(
                HITTypeId=hit_type_id,
                MaxAssignments=1,
                LifetimeInSeconds=172800,
                Question = question_image
            )"""

            # Print out the HIT related info
            print("A new IMAGE HIT has been created. You can preview it here:")
            """print ("https://workersandbox.mturk.com/mturk/preview?groupId=" + yes_image_hit['HIT']['HITGroupId'])
            print ("HITID = " + yes_image_hit['HIT']['HITId'] + " (Use to Get Results)")"""
            # Remember to modify the URL above when you're publishing
            # HITs to the live marketplace.
            # Use: https://worker.mturk.com/mturk/preview?groupId="""

            # String literal of image div in question xml
            image_instruction = r"You may be provided an image for additional context."
                
                # remove the image instruction description string
            question_no_image = new_question.replace(image_instruction, "")

                # String literal of image div in question xml
            image_div = r"<img src='data:image/jpeg;base64,YOUR_IMAGE_DATA' alt='Image Placeholder' width='300' height='200'>"
                
                # remove the image div string
            question_no_image = question_no_image.replace(image_div, "")

            """# Create the new hit
            no_image_hit = client.create_hit_with_hit_type(
                HITTypeId=hit_type_id,
                MaxAssignments=1,
                LifetimeInSeconds=172800,
                Question = question_no_image
            )"""

            # Print out the HIT related info
            print("A new TEXT HIT has been created. You can preview it here:")
            """print ("https://workersandbox.mturk.com/mturk/preview?groupId=" + no_image_hit['HIT']['HITGroupId'])
            print ("HITID = " + no_image_hit['HIT']['HITId'] + " (Use to Get Results)")"""
            # Remember to modify the URL above when you're publishing
            # HITs to the live marketplace.
            # Use: https://worker.mturk.com/mturk/preview?groupId=

        i += 1
            

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

    if expr_nbr == 1:
        # Get the video file name that we intend to get frames from
        video_filename = expr_month + "_" + expr_day + "_experiment_" + participant_nbr + "_" + expr_location + "_navigator.ogv"
        print(f"experiment: {expr_nbr}")
    else:
        # Get the video file name that we intend to get frames from
        video_filename = expr_month + "_" + expr_day + "_" + temp1 + "_" + participant_nbr + "_" + expr_location + "_navigator.ogv"

    # Get the full path to the video
    video_path = os.path.join(VIDEOS_PATH, temp1, temp2, "Screen_recorder", video_filename)
    
    # Get the frames
    timestamp = df_row["Timestamp"]
    image_filename = expr_month + "_" + expr_day + "_experiment_" + participant_nbr + "_" + expr_location + "_" + f'{timestamp:.2f}' + "_navigator.jpg"

    screen_recorder_path = os.path.join(VIDEOS_PATH, temp1, temp2, "Screen_recorder")
    
    if not(os.path.exists(screen_recorder_path)):
       print("Video folder does not exist for experiment")
    
    is_frame_extracted = gf.GetFrames(timestamp, video_path, image_filename)

    # try to get the frame
    if not (is_frame_extracted):
        video_filename = expr_year + "_" + expr_month + "_" + expr_day + "_" + temp1 + "_" + participant_nbr + "_" + expr_location + "_navigator.ogv"
        
        # Get the full path to the video
        video_path = os.path.join(VIDEOS_PATH, temp1, temp2, "Screen_recorder", video_filename)

        # Now re-input the video_path
        is_frame_extracted = gf.GetFrames(timestamp, video_path, image_filename)

    if not(is_frame_extracted):
        print("navigator file may not exist for experiment")
        return False

    return image_filename

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
        encoded_image = base64.b64encode(image_bytes).decode('utf-8')    
        
        # Read and encode each image as base 64
        #with open(image_path, "rb") as image_file:
        #    return base64.b64encode(image_file.read()).decode("utf-8")
        
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
       
        # Create random indices needed for the entire df
        random_indices = create_indices(len(df), df)

        hit_type_id = create_hit_type(client)

        # create hits without image included
        create_hits(client,hit_type_id,number_hits,random_indices,is_image_included = False)
        
        # shuffle the indices
        #shuffle_indices(random_indices)
    
        # create hits with image included
        #create_hits(client,hit_type_id,random_indices,is_image_included = True)
        
    # Otherwise request images path input
    else:
       print(f"Please provide the number of hits you would like to generate",
              "'python create_tasks.py <number>'")

       
