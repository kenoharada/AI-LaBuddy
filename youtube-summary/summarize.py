import argparse
import openai
from dotenv import load_dotenv
load_dotenv()
import os
openai.api_key = os.environ['OPENAI_API_KEY']
from main import process_text, download_subtitles

if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str, required=True)

    args = parser.parse_args()
    # Get user input
    youtube_url = args.url

    # Download subtitles
    try:
        subtitle_text = download_subtitles(youtube_url)
        print(subtitle_text)
        # print(title)
    except Exception as e:
        print(e)

    # If no subtitles are found, exit early
    if not subtitle_text:
        print("No subtitles found")
    
    processed_text, processed_text_jp = process_text(subtitle_text)

    # save to file
    with open("summary.txt", "w") as f:
        f.write(processed_text)
    with open("summary_jp.txt", "w") as f:
        f.write(processed_text_jp)
