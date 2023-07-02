import re
from dotenv.main import load_dotenv
import requests
import os
import json
import time
from dotenv import load_dotenv
load_dotenv()
PLAY_API_KEY = os.environ['PLAY_API_KEY']
PLAY_USER_ID = os.environ['PLAY_USER_ID']
PLAY_URL = "https://play.ht/api/v1/convert"
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "AUTHORIZATION": PLAY_API_KEY,
    "X-USER-ID": PLAY_USER_ID
}
# dialogue_json = 'today_dialogue.json'
dialogue_json = 'news_dialogue_0.json'

dialogue_list = json.load(open(dialogue_json))

for dialogue in dialogue_list:
    print(dialogue)
    if dialogue['person'] == 'アナウンサー':
        payload = {
            "content": [dialogue['text']],
            "voice": "ja-JP-KeitaNeural",
            # "globalSpeed": "130%"
        }
    elif dialogue['person'] == 'アイドル':
        payload = {
            "content": [dialogue['text']],
            "voice": "ja-JP-NanamiNeural",
            # "globalSpeed": "130%"
        }
    response = requests.post(PLAY_URL, json=payload, headers=headers)
    transcriptionId = response.json()['transcriptionId']
    dialogue['transcriptionId'] = transcriptionId

with open(dialogue_json, 'w', encoding='utf-8') as file:
    json.dump(dialogue_list, file, ensure_ascii=False)

dialogue_list = json.load(open(dialogue_json))
if not os.path.exists('audio'):
    os.mkdir('audio')
max_trial = 5
for dialogue in dialogue_list:
    trial = 0
    while True:
        url = f"https://play.ht/api/v1/articleStatus?transcriptionId={dialogue['transcriptionId']}"
        headers = {
            "accept": "application/json",
            "AUTHORIZATION": PLAY_API_KEY,
            "X-USER-ID": PLAY_USER_ID
        }
        response = requests.get(url, headers=headers).json()
        if response["message"] == "Transcription completed":
            dialogue['audioUrl'] = response['audioUrl']
            dialogue['audioDuration'] = response['audioDuration']
            dialogue['converted'] = response['converted']
            # save audio
            # リクエストを送る
            audio_response = requests.get(response['audioUrl'])

            # レスポンスをバイナリ形式として扱う
            filename = f"audio/audiofile_{dialogue['transcriptionId']}.mp3"
            with open(filename, 'wb') as file:
                file.write(audio_response.content)
            dialogue['audioPath'] = filename
            break
        else:
            print('not completed')
            time.sleep(1)
            trial += 1
            if trial >= max_trial:
                break
with open(dialogue_json, 'w', encoding='utf-8') as file:
    json.dump(dialogue_list, file, ensure_ascii=False)
