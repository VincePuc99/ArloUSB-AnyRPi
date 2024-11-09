import os
import http.client
import mimetypes
import argparse
import time
from datetime import datetime
import json

# Constants
BOUNDARY = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
LOG_FILE = '/var/log/telegram_video_sender.log'  # Log dei video inviati
BASE_FOLDER = '/mnt/ArloExposed/arlo/'

# Argument Parser per ottenere API_TOKEN e CHAT_ID
parser = argparse.ArgumentParser()
parser.add_argument('api_token', type=str, help='Telegram API token')
parser.add_argument('chat_id', type=str, help='Telegram chat ID')
args = parser.parse_args()

# Bot Init
API_TOKEN = args.api_token
CHAT_ID = args.chat_id
TELEGRAM_API_URL = f'https://api.telegram.org/bot{API_TOKEN}/sendVideo'
TELEGRAM_API_URL_TEXT = f'https://api.telegram.org/bot{API_TOKEN}/sendMessage'

def load_sent_videos():
    """Carica i video già inviati dal file di log."""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as file:
            return set(file.read().splitlines())
    return set()

def save_sent_video(filename):
    """Salva il nome del file inviato nel log."""
    with open(LOG_FILE, 'a') as file:
        file.write(f'{filename}\n')

def handle_rate_limit(response):
    """Gestisce il rate limit di Telegram, aspettando il tempo indicato da 'retry_after'."""
    if response.status == 429:
        try:
            # Decodifica la risposta come JSON
            data = json.loads(response.read().decode("utf-8"))
            retry_after = data.get('parameters', {}).get('retry_after', 0)
            
            if retry_after > 0:
                print(f"Rate limited. Retrying after {retry_after} seconds.")
                time.sleep(retry_after)  # Aspettiamo il tempo indicato
                return True
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing rate limit response: {e}")
            return False
    return False

def send_message(text):
    """Invia un messaggio di testo su Telegram gestendo il rate limit."""
    conn = http.client.HTTPSConnection("api.telegram.org")
    payload = f'chat_id={CHAT_ID}&text={text}'
    headers = {'Content-type': 'application/x-www-form-urlencoded'}

    try:
        conn.request("POST", f"/bot{API_TOKEN}/sendMessage", payload, headers)
        res = conn.getresponse()

        # Gestione del rate limit
        if handle_rate_limit(res):
            # Se siamo rate limited, ritenta l'invio del messaggio
            conn.request("POST", f"/bot{API_TOKEN}/sendMessage", payload, headers)
            res = conn.getresponse()

        data = res.read()

    except Exception as e:
        print(f'Error sending message: {e}')
        return

    if res.status == 200:
        print(f'Successfully sent message: {text}')
    else:
        print(f'Failed to send message: {text}, error: {data.decode("utf-8")}')

def send_video(file_path):
    """Invia il video a Telegram, insieme al messaggio di testo formattato."""
    filename = os.path.basename(file_path)
    
    try:
        # Rimuovere il suffisso '.mp4' dal nome del file prima di estrarlo
        if filename.endswith('.mp4'):
            filename = filename[:-4]  # Rimuove '.mp4'
        
        # Proviamo a dividere il nome del file in base al delimitatore "_"
        parts = filename.split('_')
        
        # Verifica che ci siano almeno 4 parti (includendo il prefisso e il suffisso)
        if len(parts) < 4:
            raise ValueError(f"Il nome del file non è nel formato atteso: {filename}")
        
        # Estrazione data e ora (il formato è: date_str + time_str)
        date_str = parts[2]  # YYYYMMDD
        time_str = parts[3]  # HHMMSS
        
        # Convertiamo la data e ora in formato leggibile
        date_obj = datetime.strptime(date_str + time_str, "%Y%m%d%H%M%S")
        formatted_datetime = date_obj.strftime("%d/%m/%Y %H:%M")
    
    except Exception as e:
        print(f"Error parsing filename {filename}: {e}")
        return

    # Prima inviamo il messaggio con la data e l'ora
    message = f"Video received on {formatted_datetime}"
    send_message(message)

    # Creazione del payload per inviare il video
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

        # Gestione del rate limit (per l'invio dei video)
        if handle_rate_limit(res):
            conn.request("POST", f"/bot{API_TOKEN}/sendVideo", payload, headers)
            res = conn.getresponse()

        data = res.read()

    except Exception as e:
        print(f'Error sending video {file_path}: {e}')
        return

    if res.status == 200:
        print(f'Successfully sent video: {file_path}')
        save_sent_video(os.path.basename(file_path))
    elif res.status == 429:
        # Gestione della rate limit di Telegram (errore 429)
        print("Error: Rate limited. Check the response for retry time.")
    else:
        print(f'Failed to send video: {file_path}, error: {data.decode("utf-8")}')

def process_videos():
    """Controlla tutte le sottocartelle in BASE_FOLDER e invia i video non ancora inviati."""
    processed_files = load_sent_videos()

    while True:
        # Scansiona tutte le sottocartelle di BASE_FOLDER
        for root, dirs, files in os.walk(BASE_FOLDER):
            for filename in files:
                if filename.endswith('.mp4') and filename not in processed_files:
                    file_path = os.path.join(root, filename)
                    send_video(file_path)
                    processed_files.add(filename)  # Aggiungi al set dei video già inviati
        
        time.sleep(30)  # Pausa di 30 secondi tra un controllo e l'altro

if __name__ == '__main__':
    process_videos()
