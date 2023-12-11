import tkinter as tk
import delete_hits
from mturk.config import access_id, secret_key, my_region_name
import boto3
from boto3 import Session
from botocore.exceptions import NoCredentialsError
import datetime

region_name = my_region_name
aws_access_key_id = access_id
aws_secret_access_key = secret_key
ENDPOINT_URL = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com' 
# Uncomment this line to use in production
#ENDPOINT_URL = 'https://mturk-requester.us-east-1.amazonaws.com'

def connect_client():
    try:
        # Replace these with your AWS credentials
        aws_access_key_id = access_id
        aws_secret_access_key = secret_key
        aws_region_name = my_region_name

        # Create a session using your credentials
        session = Session(aws_access_key_id=aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key,
                            region_name=aws_region_name)

        # Create an MTurk client and assign it to the class attribute
        session = session.client('mturk')

        # Update label text for successful connection
        status_label.config(text="Connected to MTurk!", fg="green")

        return session
    except NoCredentialsError:
        print("Credentials not found or invalid.")
        status_label.config(text="Failed to connect!", fg="red")


def delete_hits():
    mturk_client  = connect_client()

    if mturk_client:
        # Do something with the MTurk client (e.g., change this to delete client)
        response = mturk_client.get_account_balance()
        balance = response['AvailableBalance']
        status_label.config(text=f"MTurk Account Balance: {balance}", fg="green")


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