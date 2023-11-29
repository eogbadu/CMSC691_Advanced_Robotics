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

# grab the exp1 and exp2 data
file_list = glob.glob(pattern_one)

print(len(file_list))
 
# list of excel files we want to merge.
#pd.read_excel(file_path) reads the  
#excel data into pandas dataframe.
excl_list = []

for file in file_list:
    excl_list.append(pd.read_excel(file))


#concatenate all DataFrames in the list
# into a single DataFrame, returns new 
# DataFrame.
excl_merged = pd.concat(excl_list, ignore_index=True)
 
# exports the dataframe into excel file
# with specified name.
excl_merged.to_excel(os.path.join(processed_path,'oneandtwo.xlsx'), index=False)



