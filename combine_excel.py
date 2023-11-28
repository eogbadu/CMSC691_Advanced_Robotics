# importing the required modules
import glob
import pandas as pd
import os

# Get the current directory
current_dir = os.path.dirname(__file__)

# Create path to the csv data folder
data_path = os.path.join(current_dir, 'data')

# specifying the path to csv files
#path = r"C:\Users\EkeleOgbadu\Documents\Scout_Data_Edited"

# grab the exp1 and exp2 data
file_list = glob.glob(data_path + 'exp1*.xlsx') + glob.glob(data_path, 'exp2*.xlsx'))
 
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
excl_merged.to_excel('oneandtwo.xlsx', index=False)