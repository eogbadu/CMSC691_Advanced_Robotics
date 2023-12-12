import tkinter as tk
import delete_hits
from mturk.config import access_id, secret_key, my_region_name
import boto3
from botocore.exceptions import NoCredentialsError
import datetime
import tkinter.messagebox as messagebox
import tkinter.simpledialog as simpledialog



region_name = my_region_name
aws_access_key_id = access_id
aws_secret_access_key = secret_key
SANDBOX_URL = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com' 
LIVE_URL = 'https://mturk-requester.us-east-1.amazonaws.com'

def set_endpoint():
    choice = simpledialog.askstring("Environment Choice", "Select the environment:\nSandbox or Live?")
    if choice.lower() == 'sandbox':
        return SANDBOX_URL
    elif choice.lower() == 'live':
        return LIVE_URL
    else:
        tk.messagebox.showerror("Invalid Choice", "Please select either 'Sandbox' or 'Live'.")
        return None

def connect_client():    
    endpoint_url = set_endpoint()

    try:
        client = boto3.client(
        'mturk',
        endpoint_url=endpoint_url,
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        )
        
        # Update label text for successful connection
        status_label.config(text="Connected to MTurk!", fg="green")

        return client

    except NoCredentialsError:
        print("Credentials not found or invalid.")
        status_label.config(text="Failed to connect!", fg="red")

def delete_hits():
    mturk_client  = connect_client()

    if mturk_client:
        confirmation = messagebox.askquestion("Confirmation", "Are you sure you want to delete the HITs?")

        if confirmation == 'yes':

            #Set an expiration time
            yesterday = datetime.datetime.now() - datetime.timedelta(days=1)  


            # iterate over each item in list hits
            for item in mturk_client.list_hits()['HITs']:
                
                # retrieve the hit id
                hit_id=item['HITId']
                print('HITId:', hit_id)


                # Get the hit status
                status = mturk_client.get_hit(HITId=hit_id)['HIT']['HITStatus']
                print('HITStatus:', status)

                # update the expiration time of hit            
                mturk_client.update_expiration_for_hit(HITId=hit_id,
                    ExpireAt=yesterday
                )        

                # Delete hit
                try:
                    mturk_client.delete_hit(HITId=hit_id)
                except:
                    print('Not deleted')
                    status_label.config(text="No hit deleted", fg="red")
                else:
                    print('Deleted')
                    status_label.config(text="Deleted the Hit", fg="green")



if __name__ == "__main__":    
    # Create the main window
    root = tk.Tk()
    root.title("Mturk App")

    status_label = tk.Label(root, text="")
    status_label.pack()

    # Create a button
    button1 = tk.Button(root, text="Delete Hits from Mturk", command=delete_hits)
    button1.pack()
    button2 = tk.Button(root, text="Check Client Connection", command=connect_client)
    button2.pack()

    # Run the application
    root.mainloop()