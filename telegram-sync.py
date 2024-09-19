################################################################### Import Zone

import os           # Import the os module for interacting with the operating system
import time         # Import the time module for time-related functions
import http.client  # Import the http.client module for HTTP connections
import mimetypes    # Import the mimetypes module for guessing the MIME type of a file
import argparse     # Import the argparse module for parsing command-line arguments

################################################################### Constants

BOUNDARY = '----WebKitFormBoundary7MA4YWxkTrZu0gW'  # Define the boundary for the multipart/form-data request
CHECK_INTERVAL = 30                                 # Define the interval (in seconds) to check the folder for new files
LOG_FILE = 'sent_videos.log'                        # Define the log file to keep track of sent videos
WATCHED_FOLDER = '/mnt/ArloExposed/arlo/000000'     # Define the folder to watch for new video files

#################################################################### Argument Parser

parser = argparse.ArgumentParser()              # Create an ArgumentParser object to handle command-line arguments

parser.add_argument('api_token', type=str)      # Add an argument for the API token of the bot

parser.add_argument('chat_id', type=str)        # Add an argument for the chat ID where the videos will be sent

args = parser.parse_args()                      # Parse the command-line arguments

#################################################################### Bot Init

# Store the API token from the parsed arguments
API_TOKEN = args.api_token

# Store the chat ID from the parsed arguments
CHAT_ID = args.chat_id

# Construct the Telegram API URL for sending videos
TELEGRAM_API_URL = f'https://api.telegram.org/bot{API_TOKEN}/sendVideo'

#################################################################### Functions / Main

# Function to load the list of sent videos from the log file
def load_sent_videos():
    
    if os.path.exists(LOG_FILE):                    # Check if the log file exists
        with open(LOG_FILE, 'r') as file:           # Open the log file in read mode           
            return set(file.read().splitlines())    # Read the file and return a set of sent video filenames                   
    return set()                                    # If the log file does not exist, return an empty set

# Function to save a sent video filename to the log file
def save_sent_video(filename):
    with open(LOG_FILE, 'a') as file:               # Open the log file in append mode
        file.write(f'{filename}\n')                 # Write the filename to the log file

# Function to send a video file to the Telegram bot
def send_video(file_path):
 
    conn = http.client.HTTPSConnection("api.telegram.org")     # Create an HTTPS connection to the Telegram API
    payload = (                                                # Construct the payload for the request
        f'--{BOUNDARY}\r\n'
        f'Content-Disposition: form-data; name="chat_id"\r\n\r\n{CHAT_ID}\r\n'
        f'--{BOUNDARY}\r\n'
        f'Content-Disposition: form-data; name="video"; filename="{os.path.basename(file_path)}"\r\n'
        f'Content-Type: {mimetypes.guess_type(file_path)[0]}\r\n\r\n'
    )

    # Open the video file in binary read mode
    try:
        with open(file_path, 'rb') as video:
            payload += video.read().decode('latin-1')          # Read the video file and append its content to the payload
    except IOError as e:
        print(f'Error reading file {file_path}: {e}')
        return

    # Close the payload
    payload += f'\r\n--{BOUNDARY}--'
    
    headers = {'Content-type': f'multipart/form-data; boundary={BOUNDARY}'}    # Define the headers for the request

    # Send the request to the Telegram API
    try:
        conn.request("POST", f"/bot{API_TOKEN}/sendVideo", payload, headers)
        res = conn.getresponse()
        data = res.read()
    except Exception as e:
        print(f'Error sending video {file_path}: {e}')
        return

    # Check the response status
    if res.status == 200:
        print(f'Successfully sent video: {file_path}')
        save_sent_video(os.path.basename(file_path))
    else:
        print(f'Failed to send video: {file_path}, error: {data.decode("utf-8")}')

# Main entry point of the script
if __name__ == '__main__':
    processed_files = load_sent_videos()                                       # Load the list of sent videos
    while True:
        for filename in os.listdir(WATCHED_FOLDER):                            # Iterate over the files in the watched folder
            if filename.endswith('.mp4') and filename not in processed_files:  # Check if the file is a new video file
                file_path = os.path.join(WATCHED_FOLDER, filename)             # Send the video file
                send_video(file_path)
                processed_files.add(filename)                                  # Add the file to the list of processed files
       
        time.sleep(CHECK_INTERVAL)                                             # Wait for the next check interval
