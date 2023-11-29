import pandas as pd
import os

# Constants
PROCESSED_DATA_FILE = 'processed_data/pair_data.xlsx' # exp1 and 2 just the 5 commands
SHEET_NAME = 'Sheet1'
COLUMN_TO_EDIT = 'Dialogue Move'
PROCESSED_DATA_PATH = 'processed_data'

# Get the current directory
current_dir = os.path.dirname(__file__)

# Read the processed data file
df = pd.read_excel(PROCESSED_DATA_FILE, sheet_name=SHEET_NAME)

# Select the column to edit
column_to_modify = COLUMN_TO_EDIT

# Remove command substring
df[column_to_modify] = df[column_to_modify].str.replace("command:", "")

#remove hyphen in send image
df[column_to_modify] = df[column_to_modify].str.replace("send-image", "send image")

#Create a path to the processed_data folder
processed_path = os.path.join(current_dir, PROCESSED_DATA_PATH)

# Save the processed data 
df.to_excel(os.path.join(processed_path,"pair_data_processed.xlsx"), index=False)
