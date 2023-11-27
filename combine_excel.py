# importing the required modules
import glob
import pandas as pd
 
# specifying the path to csv files
path = r"C:\Users\EkeleOgbadu\Documents\Scout_Data_Edited"
 
# csv files in the path
file_list = glob.glob(path + r"\*.xlsx")
 
# list of excel files we want to merge.
# pd.read_excel(file_path) reads the  
# excel data into pandas dataframe.
excl_list = []
 
for file in file_list:
    excl_list.append(pd.read_excel(file))
 
# concatenate all DataFrames in the list
# into a single DataFrame, returns new 
# DataFrame.
excl_merged = pd.concat(excl_list, ignore_index=True)
 
# exports the dataframe into excel file
# with specified name.
excl_merged.to_excel('oneandtwo.xlsx', index=False)
