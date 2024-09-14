import os
import time
import http.client
import mimetypes

########################################################### Argument Parser

parser = argparse.ArgumentParser(description='Send clips to your Telegram bot.')
parser.add_argument('api_token', type=str, help='Token API of the bot created with BotFather')
parser.add_argument('chat_id', type=str, help='Chat id of the chat where the videos will be sent')
args = parser.parse_args()

########################################################### Bot Configuration

API_TOKEN = args.api_token
CHAT_ID = args.chat_id
TELEGRAM_API_URL = f'https://api.telegram.org/bot{API_TOKEN}/sendVideo'

########################################################### Folder to watch

WATCHED_FOLDER = '/mnt/ArloExposed/arlo/000000'
CHECK_INTERVAL = 30  #second refresh
LOG_FILE = 'sent_videos.log'

########################################################### Main Sender

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
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    payload = f'--{boundary}\r\nContent-Disposition: form-data; name="chat_id"\r\n\r\n{CHAT_ID}\r\n--{boundary}\r\nContent-Disposition: form-data; name="video"; filename="{os.path.basename(file_path)}"\r\nContent-Type: {mimetypes.guess_type(file_path)[0]}\r\n\r\n'
    
    with open(file_path, 'rb') as video:
        payload += video.read().decode('latin-1')
    
    payload += f'\r\n--{boundary}--'
    
    headers = {
        'Content-type': f'multipart/form-data; boundary={boundary}'
    }
    
    conn.request("POST", f"/bot{API_TOKEN}/sendVideo", payload, headers)
    res = conn.getresponse()
    data = res.read()
    
    if res.status == 200:
        print(f'Successfully sent video: {file_path}')
        save_sent_video(os.path.basename(file_path))
    else:
        print(f'Failed to send video: {file_path}, error: {data.decode("utf-8")}')

def monitor_folder():
    processed_files = load_sent_videos()
    while True:
        for filename in os.listdir(WATCHED_FOLDER):
            if filename.endswith('.mp4') and filename not in processed_files:
                file_path = os.path.join(WATCHED_FOLDER, filename)
                send_video(file_path)
                processed_files.add(filename)
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    monitor_folder()
