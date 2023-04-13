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
        'restrictfilenames': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        filename = ydl.prepare_filename(info_dict).replace('.webm', f'.{language}.vtt')
        title = filename.split('.')[0]
        ydl.download([video_url])

    if os.path.exists(filename):
        return filename, title
    else:
        return None, None


def download_subtitle_auto(video_url, language='en'):
    ydl_opts = {
        'skip_download': True,
        # 'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': [language],
        'subtitlesformat': 'vtt',
        'outtmpl': '%(title)s.%(ext)s',
        'restrictfilenames': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        filename = ydl.prepare_filename(info_dict).replace('.webm', f'.{language}.vtt')
        title = filename.split('.')[0]
        print(filename, title)
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
    video_urls = [
        'https://www.youtube.com/watch?v=zFZrkCIc2Oc',
        'https://www.youtube.com/watch?v=NcoBAfJ6l2Q',
        'https://www.youtube.com/watch?v=EOLPQdVj5Ac',
        'https://www.youtube.com/watch?v=w8q0C-C1js4',
        'https://www.youtube.com/watch?v=YzP164YANAU',
        'https://www.youtube.com/watch?v=x5trGVMKTdY',
        'https://www.youtube.com/watch?v=jrBhi8wbzPw',
        'https://www.youtube.com/watch?v=WbRDkJ4lPdY',
        'https://www.youtube.com/watch?v=6PWTxRGh_dk',
    ]
    overview = ''
    for video_url in video_urls:
        vtt_file_path, title = download_subtitle(video_url, language='en')  # 'en' を希望する言語のコードに変更してください
        print(vtt_file_path)
        print(title)
        if vtt_file_path:
            extracted_text = extract_text_from_vtt(vtt_file_path)
            print(extracted_text)
        else:
            vtt_file_path, title = download_subtitle_auto(video_url, language='en')  # 'en' を希望する言語のコードに変更してください
            print(vtt_file_path)
            print(title)
            if vtt_file_path:
                extracted_text = extract_text_from_vtt(vtt_file_path)
                print(extracted_text)
            else:
                print("Failed to download subtitle.")
                continue
        text = extracted_text.replace('\n', ' ')
        text_splits = split_text(text)
        if not os.path.exists(title):
            os.makedirs(title)
        with open (f"{title}/text.txt", "w") as f:
            f.write(text)
        total_summary = ''
        for idx, text_split in enumerate(text_splits):
            print(text_split)
            summary = summarize(text_split, title)
            with open(f"{title}/summary_{idx}.txt", "w") as f:
                f.write(summary)
            total_summary += summary
            total_summary += '\n'
        with open(f"{title}/summary.txt", "w") as f:
            f.write(total_summary)
        
        from make_lecture_notes import summarize_to_notes, split_chunk_by_token_nums
        text_splits = split_chunk_by_token_nums(total_summary)
        notes = ''
        for text_split in text_splits:
            note = summarize_to_notes(text_split, title)
            notes += note
            notes += '\n'
        with open(f"{title}/notes.txt", "w") as f:
            f.write(notes)
        overview += f"## {title}\n"
        overview += f"{notes}\n"
    with open("overview.md", "w") as f:
        f.write(overview)
