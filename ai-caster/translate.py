import re
import json
import openai
import os
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# MODEL_NAME = 'gpt-3.5-turbo-16k'
MODEL_NAME = 'gpt-4'

data = json.load(open('techcrunch.json', 'r', encoding='utf-8'))

for news in data:
    response = openai.ChatCompletion.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": "You are a professional translator. translate the following text into Japanese."},
                        {"role": "user", "content": news['title']}
                    ],
                    temperature=0.7,
                )['choices'][0]['message']['content']
    news['title_ja'] = response

# save
with open('techcrunch.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False)