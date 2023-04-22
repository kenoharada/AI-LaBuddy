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
        # TODO: 拡張子に応じた処理
        filename = ydl.prepare_filename(info_dict).replace('.webm', f'.{language}.vtt').replace('.mkv', f'.{language}.vtt')
        title = filename.split('.')[0]
        print("Human ##########")
        print('filename: ', filename)
        print('title: ', title)
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
        # TODO: 拡張子に応じた処理
        filename = ydl.prepare_filename(info_dict).replace('.webm', f'.{language}.vtt').replace('.mkv', f'.{language}.vtt')
        title = filename.split('.')[0]
        print("AUTO ##########")
        print('filename: ', filename)
        print('title: ', title)
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