from utils import download_subtitle, download_subtitle_auto, extract_text_from_vtt
import os

video_urls = [
    'https://www.youtube.com/watch?v=jGwO_UgTS7I',
    'https://www.youtube.com/watch?v=4b4MUYve_U8',
    'https://www.youtube.com/watch?v=het9HFqo1TQ',
    'https://www.youtube.com/watch?v=iZTeva0WSTQ',
    'https://www.youtube.com/watch?v=nt63k3bfXS0',
    'https://www.youtube.com/watch?v=lDwow4aOrtg',
    'https://www.youtube.com/watch?v=8NYoQiRANpg',
    'https://www.youtube.com/watch?v=rjbkWSTjHzM',
    'https://www.youtube.com/watch?v=iVOxMcumR4A',
    'https://www.youtube.com/watch?v=wr9gUr-eWdA',
    'https://www.youtube.com/watch?v=MfIjxPh6Pys',
    'https://www.youtube.com/watch?v=zUazLXZZA2U',
    'https://www.youtube.com/watch?v=ORrStCArmP4',
    'https://www.youtube.com/watch?v=rVfZHWTwXSA',
    'https://www.youtube.com/watch?v=tw6cmL5STuY',
    'https://www.youtube.com/watch?v=YQA9lLdLig8',
    'https://www.youtube.com/watch?v=d5gaWTo6kDM',
    'https://www.youtube.com/watch?v=QFu5nuc-S0s',
    'https://www.youtube.com/watch?v=0rt2CsEQv6U',
    'https://www.youtube.com/watch?v=pLhPQynL0tY',
]

save_dir = 'data'
for video_url in video_urls:
    # TODO: whisperとか使う場合は音声認識の処理を入れる
    vtt_file_path, title = download_subtitle(video_url, language='en')
    print(vtt_file_path, title)
    if vtt_file_path:
        extracted_text = extract_text_from_vtt(vtt_file_path)
    else:
        vtt_file_path, title = download_subtitle_auto(video_url, language='en')
        print(vtt_file_path, title)
        if vtt_file_path:
            extracted_text = extract_text_from_vtt(vtt_file_path)
        else:
            print("Failed to download subtitle.")
            continue
    text = extracted_text.replace('\n', ' ')
    if not os.path.exists(os.path.join(save_dir, title)):
        os.makedirs((os.path.join(save_dir, title)))
    with open (os.path.join(save_dir, title, 'text.txt'), "w") as f:
        f.write(text)