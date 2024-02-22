"""Script that processed the raw data from the experiments"""
import os
import glob
import pandas as pd

# Constants
RAW_FOLDER_NAME = 'raw_data'
PROCESSED_FOLDER_NAME = 'processed_data'
PROCESSED_FILE_NAME = 'oneandtwowithfilepath.xlsx'


def process_data(raw_folder_name, processed_folder_name):
    """
    Processes data from Excel files in 'raw_data' folder and outputs a combined file.

    Output:
    An Excel file in the processed data folder containing the processed data.

    Returns: None
    """
    # Get the directory of where the current file is located
    current_dir = os.path.dirname(__file__)

    # Create path to the raw_data folder
    data_path = os.path.join(current_dir, raw_folder_name)

    # Create a path to the processed_data folder
    processed_path = os.path.join(current_dir, processed_folder_name)

    # Create a file name path pattern for experiment 1
    pattern_one = os.path.join(data_path, 'exp1*.xlsx')

    # Create a file name path pattern for experiment 2
    pattern_two = os.path.join(data_path, 'exp2*.xlsx')

    # grab the exp1 and exp2 data
    file_list = glob.glob(pattern_one) + glob.glob(pattern_two)

    # list of excel files we want to merge.
    excl_list = []

    # Loop through the file list and add each file's contents to list of excel dfs
    for file in file_list:

        # Save each file's contents to a df
        df_temp = pd.read_excel(file)

        # Extract the file name
        file_name = os.path.basename(file)

        # Create a new column and set all values to the file name
        df_temp["File Name"] = file_name

        # append the new dataframe to the full df
        excl_list.append(df_temp)

    # combine each df into a single df
    df = pd.concat(excl_list, ignore_index=True)

    words_to_remove = ["ready", "yes", "direction", "acknowledge", "describe:plan",
                       "describe:scene", "no", "request-info:scene", "request-info:confirm",
                       "clarify:target", "distance", "request-info:map", "standby"]

    # Remove all of the words that are in the removal list
    df['Dialogue Move'] = df['Dialogue Move'].replace(words_to_remove, pd.NA)

    # Remove command substring
    df['Dialogue Move'] = df['Dialogue Move'].str.replace("command:", "")
    df['Dialogue Move-2'] = df['Dialogue Move-2'].str.replace("command:", "")

    # Remove hyphen in send image
    df['Dialogue Move'] = df['Dialogue Move'].str.replace(
        "send-image", "send image")
    df['Dialogue Move-2'] = df['Dialogue Move-2'].str.replace(
        "send-image", "send image")

    # Remove all rows where the cell in the specified column is empty
    df.dropna(subset=['Dialogue Move'], inplace=True)

    # Remove unneeded columns(axis 1)
    df.drop(labels=['DM->RN', 'RN', 'DM->CMD', 'Transaction', 'Antecedent',
            'Relation', 'Contextual Info', 'Notes', 'Parameter Type'], axis=1, inplace=True)

    # Set the 5 control signals
    control_signals = ['explore', 'move', 'send image', 'stop', 'turn']

    # Select rows where the signals are present
    df = df[df['Dialogue Move'].isin(control_signals)]

    # exports the dataframe into excel file with specified name.
    df.to_excel(os.path.join(processed_path, PROCESSED_FILE_NAME), index=False)


if __name__ == "__main__":
    process_data(RAW_FOLDER_NAME, PROCESSED_FOLDER_NAME)
