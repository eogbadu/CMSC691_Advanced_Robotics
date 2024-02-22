import pandas as pd


# Global constants
PROCESSED_DATA_PATH = 'processed_data'
ANALYSIS_PATH = 'analysis'

# read in the raw SCOUT data
df = pd.read_excel(f"{PROCESSED_DATA_PATH}/oneandtwowithfilepath.xlsx")

# Split the data into features and labels
Y = df["Dialogue Move"]
features = df["Commander"]


