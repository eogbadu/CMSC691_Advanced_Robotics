# importing the required modules
import glob
import pandas as pd
 
# specifying the path to csv files
path = r"C:\Users\EkeleOgbadu\Documents\Scout_Data_Experiment"
 
# csv files in the path
file_list = glob.glob(path + r"\*.xlsx")
 
# list of excel files we want to merge.
# pd.read_excel(file_path) reads the  
# excel data into pandas dataframe.
excl_list = []
 
for file in file_list:
    excl_list.append(pd.read_excel(file))
 

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
df.to_excel('oneandtwowithfilepath.xlsx', index=False)
