# importing the required modules
import glob
import pandas as pd
import numpy as np
import os
import get_frames as gf

# Get the current directory
current_dir = os.path.dirname(__file__)

# Create path to the raw_data folder
data_path = os.path.join(current_dir, 'raw_data')

#Create a path to the processed_data folder
processed_path = os.path.join(current_dir, 'processed_data')

#Create a path to the images directory
image_path = r"D:\SCOUT_RAV"

# specifying the path to csv files
#path = r"C:\Users\EkeleOgbadu\Documents\Scout_Data_Edited"

# Grab the experiment one pattern
pattern_one = os.path.join(data_path, 'exp1*.xlsx')

# Grab the experiment second pattern
pattern_two = os.path.join(data_path, 'exp2*.xlsx')

# grab the exp1 and exp2 data
file_list = glob.glob(pattern_one) + glob.glob(pattern_two)
 
# list of excel files we want to merge.
#pd.read_excel(file_path) reads the  
#excel data into pandas dataframe.
excl_list = []
for file in file_list:
    # Read the file 
    df_temp = pd.read_excel(file)

    # Extract the file name
    file_name = os.path.basename(file)
    file_names = []

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
    video_file_name = expr_month + "_" + expr_day + "_experiment_" + participant_nbr + "_" + expr_location + "_navigator.ogv"

    # Get the full path to the video
    temp_pattern = os.path.join(image_path, temp1, temp2, "Screen_recorder", video_file_name)

    # Get the frames and print out the image file name to the excel file
    temp_timestamp = df_temp["Timestamp"]
    for i in temp_timestamp:
        img_file = expr_month + "_" + expr_day + "_experiment_" + participant_nbr + "_" + expr_location + "_" + f'{i:.2f}' + "_navigator.jpg"
        gf.GetFrames(i, temp_pattern, img_file)
        file_names.append(img_file)




    # Create a new column and set all values to the file name
    df_temp["File Name"] = np.array(file_names)

    file_names.clear()
    #append the new dataframe to the full df
    excl_list.append(df_temp)

df = pd.concat(excl_list, ignore_index=True)

# Remove words from the specified column
df['Dialogue Move'] = df['Dialogue Move'].replace("ready", pd.NA)
df['Dialogue Move'] = df['Dialogue Move'].replace("yes", pd.NA)
df['Dialogue Move'] = df['Dialogue Move'].replace("direction", pd.NA)
df['Dialogue Move'] = df['Dialogue Move'].replace("acknowledge", pd.NA)
df['Dialogue Move'] = df['Dialogue Move'].replace("describe:plan", pd.NA)
df['Dialogue Move'] = df['Dialogue Move'].replace("describe:scene", pd.NA)
df['Dialogue Move'] = df['Dialogue Move'].replace("no", pd.NA)
df['Dialogue Move'] = df['Dialogue Move'].replace("request-info:scene", pd.NA)
df['Dialogue Move'] = df['Dialogue Move'].replace("request-info:confirm", pd.NA)
df['Dialogue Move'] = df['Dialogue Move'].replace("clarify:target", pd.NA)
df['Dialogue Move'] = df['Dialogue Move'].replace("distance", pd.NA)
df['Dialogue Move'] = df['Dialogue Move'].replace("request-info:map", pd.NA)
df['Dialogue Move'] = df['Dialogue Move'].replace("standby", pd.NA)

# The following lines (till line 45) were taken or inspired from my teammates', Zachary Marguilies, original code.
# Remove command substring
df['Dialogue Move'] = df['Dialogue Move'].str.replace("command:", "")
df['Dialogue Move-2'] = df['Dialogue Move-2'].str.replace("command:", "")

#remove hyphen in send image
df['Dialogue Move'] = df['Dialogue Move'].str.replace("send-image", "send image")
df['Dialogue Move-2'] = df['Dialogue Move-2'].str.replace("send-image", "send image")

# Remove all rows where the cell in the specified column is empty
df.dropna(subset=['Dialogue Move'], inplace=True)

# Combine all DataFrames in the list
# into one DataFrame
df.drop(labels=['DM->RN', 'RN', 'DM->CMD', 'Transaction', 'Antecedent', 'Relation', 'Contextual Info', 'Notes', 'Parameter Type'], axis=1, inplace=True)
 
# Set the 5 control signals
control_signals = ['explore', 'move', 'send image', 'stop', 'turn']

# Select rows where the signals are present
df = df[df['Dialogue Move'].isin(control_signals)]

# exports the dataframe into excel file
# with specified name.
df.to_excel(os.path.join(processed_path,'oneandtwowithfilepath.xlsx'), index=False)
