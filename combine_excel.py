# importing the required modules
import glob
import pandas as pd
import os

# Get the current directory
current_dir = os.path.dirname(__file__)

# Create path to the raw_data folder
data_path = os.path.join(current_dir, 'raw_data')

#Create a path to the processed_data folder
processed_path = os.path.join(current_dir, 'processed_data')

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

    # clean-up file name
    file_name = file_name.replace("_annotated-transcript.xlsx", "")

    # Create a new column and set all values to the file name
    df_temp["File Name"] = file_name

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
 
# exports the dataframe into excel file
# with specified name.
df.to_excel(os.path.join(processed_path,'oneandtwowithfilepath.xlsx'), index=False)
