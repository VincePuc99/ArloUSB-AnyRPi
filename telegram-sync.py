import os
import time
import http.client
import mimetypes
import argparse

# Constants
BOUNDARY = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
CHECK_INTERVAL = 60  # Interval in seconds to check the folder for new files
LOG_FILE = 'sent_videos.log'
WATCHED_FOLDER = '/mnt/ArloExposed/arlo/000000'

# Argument Parser
parser = argparse.ArgumentParser()
parser.add_argument('api_token', type=str)
parser.add_argument('chat_id', type=str)
args = parser.parse_args()

# Bot Init
API_TOKEN = args.api_token
CHAT_ID = args.chat_id
TELEGRAM_API_URL = f'https://api.telegram.org/bot{API_TOKEN}/sendVideo'

def load_sent_videos():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as file:
            return set(file.read().splitlines())
    return set()

def save_sent_video(filename):
    with open(LOG_FILE, 'a') as file:
        file.write(f'{filename}\n')

def send_video(file_path):
    conn = http.client.HTTPSConnection("api.telegram.org")
    payload = (
        f'--{BOUNDARY}\r\n'
        f'Content-Disposition: form-data; name="chat_id"\r\n\r\n{CHAT_ID}\r\n'
        f'--{BOUNDARY}\r\n'
        f'Content-Disposition: form-data; name="video"; filename="{os.path.basename(file_path)}"\r\n'
        f'Content-Type: {mimetypes.guess_type(file_path)[0]}\r\n\r\n'
    )

    try:
        with open(file_path, 'rb') as video:
            payload += video.read().decode('latin-1')
    except IOError as e:
        print(f'Error reading file {file_path}: {e}')
        return

    payload += f'\r\n--{BOUNDARY}--'
    headers = {'Content-type': f'multipart/form-data; boundary={BOUNDARY}'}

    try:
        conn.request("POST", f"/bot{API_TOKEN}/sendVideo", payload, headers)
        res = conn.getresponse()
        data = res.read()
    except Exception as e:
        print(f'Error sending video {file_path}: {e}')
        return

    if res.status == 200:
        print(f'Successfully sent video: {file_path}')
        save_sent_video(os.path.basename(file_path))
    else:
        print(f'Failed to send video: {file_path}, error: {data.decode("utf-8")}')

if __name__ == '__main__':
    processed_files = load_sent_videos()
    while True:
        for filename in os.listdir(WATCHED_FOLDER):
            if filename.endswith('.mp4') and filename not in processed_files:
                file_path = os.path.join(WATCHED_FOLDER, filename)
                send_video(file_path)
                processed_files.add(filename)
        time.sleep(CHECK_INTERVAL)
