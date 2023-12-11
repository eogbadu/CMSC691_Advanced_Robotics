from mturk.config import access_id, secret_key, my_region_name
from create_tasks import get_endpoint, client_setup
import os
import xmltodict
import pandas as pd
import string
import random
import nltk
import plotly.express as px

# Uncomment and run this line to download the NLTK words corpus if you haven't already
#nltk.download('words')

region_name = my_region_name
aws_access_key_id = access_id
aws_secret_access_key = secret_key
SANDBOX_URL = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
LIVE_URL = 'https://mturk-requester.us-east-1.amazonaws.com'
S3_BUCKET_NAME = 'scoutmturk'
DAY_IN_SECONDS = 86400
HIT_TYPE_ID = '3MID1PD49XFUZY6UDB2YCDJUH80WKQ'


def get_results(client, hit_type_id, answer_key):
   # Iterate over each item in list hits
   rows_to_append = []
   
   # iterate over each item in list hits
   for item in client.list_hits()['HITs']:
      # retrieve the hit id
      hit_id = item['HITId']
      hit_type = item['HITTypeId']  # Fetch the HIT Type ID for comparison
      print('HITId:', hit_id)
   
      # Check if the HIT matches the provided hit_type_id
      if hit_type == hit_type_id:
   
         worker_results = client.list_assignments_for_hit(
            HITId=hit_id, AssignmentStatuses=['Submitted'])

         if worker_results['NumResults'] > 0:
                        
            for assignment in worker_results['Assignments']:
               xml_doc = xmltodict.parse(assignment['Answer'])

               print("Worker's answer was:")
              # Find matching hit_id in 'yes_image' column
               matching_hit = answer_key[answer_key['hitid_yes_image'] == hit_id]
               with_image = True 
               
               if matching_hit.empty:
                  # Find matching hit_id in "no image" column 
                  matching_hit = answer_key[answer_key['hitid_no_image'] == hit_id]
                  with_image = False
               
               if not matching_hit.empty:
                  command = matching_hit.iloc[0]['Commander']
                  real_output = matching_hit.iloc[0]['Dialogue Move']
                  submitted_answer = xml_doc['QuestionFormAnswers']['Answer']['FreeText']
                  is_correct = check_correct(real_output,submitted_answer)
                  
                  print("Command: " + command)
                  print("Correct Answer :" + real_output)
                  print("Submitted answer: " + submitted_answer)
                  print("Matching: "+ str(is_correct)) 

                  # Store the row to append to the DataFrame
                  rows_to_append.append({
                     'hitid': hit_id,
                     'command': command,
                     'real_output': real_output,
                     'submitted_answer': submitted_answer,
                     'with_image': int(with_image),
                     'matching': int(is_correct)
                  })
               else:
                  print("HIT ID not found in answer_key")

         else:
            print("No results ready yet")
   
   # Append all collected rows to the results DataFrame
   rows_df = pd.DataFrame(rows_to_append)
   
   # initialize a results dataframe
   results_df = init_results_df()

   #populate the results df
   updated_results_df = pd.concat([results_df, rows_df], ignore_index=True)
   
   return updated_results_df 

def export_results(results_df):
   # Get the current directory
   current_directory = os.getcwd()

   processed_path = os.path.join(current_directory, 'processed_data')

   #create excel from the results_df
   results_df.to_excel(os.path.join(processed_path,'mturk_results.xlsx'), index=False)


def check_correct(real_output, submitted_answer):
   
   # Convert strings to lowercase and split into lists 
   real_output_words = real_output.lower().split()
   submitted_answer_words = submitted_answer.lower().split()

   # Check if both lists are non-empty
   if real_output_words and submitted_answer_words:
   # Compare the first word of each string
      return real_output_words[0] == submitted_answer_words[0]
   return False


def get_key():
   current_directory = os.getcwd()

   processed_path = os.path.join(current_directory, 'processed_data')

   answer_key = os.path.join(processed_path,'answer_key.xlsx')

   # Read the file 
   df = pd.read_excel(answer_key)

   return df


def init_results_df():
   columns = ['hitid', 'command', 'real_output', 'submitted_answer', 'with_image', 'matching']

   data_types = {
        'hitid': 'object',
        'command': 'object',
        'real_output': 'object',
        'submitted_answer': 'object',
        'with_image': 'int64',
        'matching': 'int64'
   }
   
   results_df = pd.DataFrame(columns=columns)

   results_df = results_df.astype(data_types)
   return results_df


# Makes a bunch of dummy data 
def create_dummy(num_rows):
   results_df = init_results_df()
   
   rows_to_append = []
   
   # Create lists to store generated data
   hitid_list = []
   predefined_commands = ['Turn', 'Move', 'Send photo', 'Stop', 'Explore']
   
   # Using NLTK to get words from its corpus and create a random command
   words = nltk.corpus.words.words()
   random_command = ' '.join(random.choices(words, k=random.randint(1, 3)))

   real_output_list = ['Turn', 'Move', 'Send image', 'Stop', 'Explore']
   submitted_answer_list = ['Turn', 'Move', 'Send photo', 'Stop', 'Explore', 'None of the above']
   with_image_list = [0, 1]

   for i in range(num_rows):
      hitid = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
      hitid_list.append(hitid)

      # Initialize with a predefined command
      random_command = random.choice(predefined_commands)

      # Generate random command 10% of the time
      if random.random() < 0.1:
         words = nltk.corpus.words.words()
         random_command = ' '.join(random.choices(words, k=random.randint(1, 3)))
      
      row = {
         'hitid': hitid,
         'command': random_command,
         'real_output': random.choice(real_output_list),
         'submitted_answer': random.choice(submitted_answer_list),
         'with_image': random.choice(with_image_list),
         'matching': 0
      }

      row['matching'] = int(check_correct(row['real_output'], row['submitted_answer']))
      rows_to_append.append(row)
      
   # Append all collected rows to the results DataFrame
   rows_df = pd.DataFrame(rows_to_append)

   #update the results df
   updated_results_df = pd.concat([results_df, rows_df], ignore_index=True)
      
   return updated_results_df

def read_results():
   # Get the current directory
   current_directory = os.getcwd()

   processed_path = os.path.join(current_directory, 'processed_data')

   #create excel from the results_df
   results_df = pd.read_excel(os.path.join(processed_path,'mturk_results.xlsx'))
   
   return results_df

def analyze_results(mturk_results):
   # Count the total number of entries with and without images
   total_with_image = mturk_results[mturk_results['with_image'] == 1]['matching'].count()
   total_without_image = mturk_results[mturk_results['with_image'] == 0]['matching'].count()

   # Count the number of matches with and without images
   matches_with_image = mturk_results[(mturk_results['with_image'] == 1) & (mturk_results['matching'] == 1)]['matching'].count()
   matches_without_image = mturk_results[(mturk_results['with_image'] == 0) & (mturk_results['matching'] == 1)]['matching'].count()

   # Calculate the percentage of matches for entries with images
   percentage_matches_with_image = 0
   if total_with_image > 0:
      percentage_matches_with_image = (matches_with_image / total_with_image) * 100

   # Calculate the percentage of matches for entries without images
   percentage_matches_without_image = 0
   if total_without_image > 0:
      percentage_matches_without_image = (matches_without_image / total_without_image) * 100

   # Display the results
   print("Total entries with image:", total_with_image)
   print("Total entries without image:", total_without_image)
   print("Matches with image:", matches_with_image)
   print("Matches without image:", matches_without_image)
   print("Percentage of matches with image:", percentage_matches_with_image)
   print("Percentage of matches without image:", percentage_matches_without_image)

   # Calculate standard errors
   error_with_image = (percentage_matches_with_image / 100) * ((total_with_image - matches_with_image) / total_with_image)**0.5 if total_with_image > 0 else 0
   error_without_image = (percentage_matches_without_image / 100) * ((total_without_image - matches_without_image) / total_without_image)**0.5 if total_without_image > 0 else 0

   # Create a DataFrame for plotting
   data = {
      'Category': ['With Image', 'Without Image'],
      'Percentage of Matches': [percentage_matches_with_image, percentage_matches_without_image],
      'Error': [error_with_image, error_without_image]
   }
   df = pd.DataFrame(data)

   # Create a bar plot with error bars using Plotly
   fig = px.bar(df, x='Category', y='Percentage of Matches', error_y='Error', color='Category',
               labels={'Percentage of Matches': 'Percentage of Matches', 'Category': 'Category'},
               title='Comparison of Matches with and without Images')
   
   fig.update_traces(error_x=dict(visible=False), width=0.5)  # Hiding x-axis error bars and adjusting bar width
   fig.show()

   # Save the plot as a static image (e.g., PNG)
   #fig.write_image("static_plot.png")

   # Save the plot as an HTML file
   fig.write_html("mturk_analysis.html")

if __name__ == "__main__":    
   # accept the second argument as the number hits
   url_type = input("'sandbox' or 'live'?: ")

   # determine if you want to sandbox or live
   while (url_type != 'sandbox' and url_type != 'live'):
      url_type = input("restate entry: ")

   endpoint_url = get_endpoint(url_type)

   # setup the client
   client = client_setup(endpoint_url)

   # hit_type_id = create_hit_type(client)
   hit_type_id = HIT_TYPE_ID

   answer_key = get_key()

   # dummy data section
   data_type = input ("Real or dummy data? ")

   while (data_type != 'dummy' and data_type != 'real'):
      data_type = input ("Real or dummy data? ")
   
   if data_type == 'dummy':
      num_rows = int(input("How many rows of dummy data? (0 for no new data): "))
      
      if num_rows > 0:
         print("Creating" + num_rows + "rows of dummy data")
         updated_results_df = create_dummy(num_rows)
         export_results(updated_results_df)
      elif num_rows == 0:
         print('No new rows added to the dummy data')
      else:
         print("Invalid entry")
   else:
      print("processing data from mturk and exporting ...")
      updated_results_df = get_results(client, hit_type_id,answer_key)
      export_results(updated_results_df)

   # Now read the results from the mturk results file
   mturk_results = read_results()

   #Analyze results
   analyze_results(mturk_results)





   
