import yt_dlp
import os

def download_subtitle(video_url, language='en'):
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        # 'writeautomaticsub': True,
        'subtitleslangs': [language],
        'subtitlesformat': 'vtt',
        'outtmpl': '%(title)s.%(ext)s',
        # 'restrictfilenames': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        title = info_dict.get('title', None)
        filename = f"{title}.{language}.vtt"
        ydl.download([video_url])

    if os.path.exists(filename):
        return filename, title
    else:
        return None, None


import webvtt
def extract_text_from_vtt(vtt_file_path):
    captions = webvtt.read(vtt_file_path)
    extracted_text = ""

    for caption in captions:
        extracted_text += caption.text + "\n"

    return extracted_text


from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from dotenv import load_dotenv
load_dotenv()
def summarize(text, title):
    chat = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    chat.openai_api_key = os.environ['OPENAI_API_KEY']
    prompt = f"""
    ###
    {text}
    ###
    The above ##-encircled area is the presentation given under the title {title}. Please summarize the main points in bullet points.
    """
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content=prompt),
    ]
    response = chat(messages)
    # print(response)
    print(response.content)
    return response.content


from langchain.text_splitter import RecursiveCharacterTextSplitter
def split_text(text):
    separators = [".", " "]
    splitter = RecursiveCharacterTextSplitter(separators=separators, chunk_size=3072, chunk_overlap=0)
    return splitter.split_text(text)

if __name__ == '__main__':
    video_url = 'https://www.youtube.com/watch?v=zFZrkCIc2Oc'  # 動画のURLを入れてください
    vtt_file_path, title = download_subtitle(video_url, language='en')  # 'en' を希望する言語のコードに変更してください
    if vtt_file_path:
        extracted_text = extract_text_from_vtt(vtt_file_path)
        print(extracted_text)
    else:
        print("Failed to download subtitle.")
    text = extracted_text.replace('\n', ' ')
    text_splits = split_text(text)
    print(len(text_splits))
    if not os.path.exists(title):
        os.makedirs(title)
    for idx, text_split in enumerate(text_splits):
        print(text_split)
        summary = summarize(text_split, title)
        with open(f"{title}/summary_{idx}.txt", "w") as f:
            f.write(summary)
        with open(f"{title}/summary.txt", "a") as f:
            f.write(summary)
            f.write('\n')
