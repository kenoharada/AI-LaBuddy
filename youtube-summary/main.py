import os
import streamlit as st
from pytube import YouTube
import openai
from youtube_transcript_api import YouTubeTranscriptApi
import asyncio
from typing import Any
import tiktoken

GPT_MODEL = "gpt-3.5-turbo"
openai.api_key = os.environ['OPENAI_API_KEY']


def num_tokens(text: str, model: str = GPT_MODEL) -> int:
  """Return the number of tokens in a string."""
  encoding = tiktoken.encoding_for_model(model)
  return len(encoding.encode(text))


async def dispatch_openai_requests(
  messages_list: list[list[dict[str, Any]]],
  model: str,
  temperature: float,
  top_p: float,
) -> list[str]:
  async_responses = [
    openai.ChatCompletion.acreate(
      model=model,
      messages=x,
      temperature=temperature,
      top_p=top_p,
    ) for x in messages_list
  ]
  return await asyncio.gather(*async_responses)


def process_text(text):
  text_chunks = text.split('\n')
  processed_idx = 0
  processing_text = ''
  prompt = (
    'The following section enclosed by ## is a transcription from a YouTube video. Please summarize the important points in bullet points. Please answer in the same language as the language enclosed in ##.\n\n'
    '##\nTranscription content\n##')

  token_budget = 4096 - 512 - num_tokens(prompt)
  messages_list = []
  print(text_chunks)
  if len(text_chunks) == 1:
    if num_tokens(text_chunks[0]) < token_budget:
      prompt = (
        'The following section enclosed by ## is a transcription from a YouTube video. Please summarize the important points in bullet points. Please answer in the same language as the language enclosed in ##.\n\n'
        f'##\n{text_chunks[0]}\n##')
      messages = [
        {
          "role": "user",
          "content": prompt
        },
      ]
      print(messages)
      messages_list.append(messages)
    else:
      prompt = (
        'The following section enclosed by ## is a transcription from a YouTube video. Please summarize the important points in bullet points. Please answer in the same language as the language enclosed in ##.\n\n'
        f'##\n{text_chunks[0][:token_budget]}\n##')
      messages = [
        {
          "role": "user",
          "content": prompt
        },
      ]
      # print(messages)
      messages_list.append(messages)
  else:
    while processed_idx < len(text_chunks):
      if num_tokens(processing_text + ' ' +
                    text_chunks[processed_idx]) < token_budget:
        if processed_idx == 0:
          processing_text += text_chunks[processed_idx]
        else:
          processing_text += ' ' + text_chunks[processed_idx]
        processed_idx += 1
      else:
        prompt = (
          'The following section enclosed by ## is a transcription from a YouTube video. Please summarize the important points in bullet points. Please answer in the same language as the language enclosed in ##.\n\n'
          f'##\n{processing_text}\n##')
        messages = [
          {
            "role": "user",
            "content": prompt
          },
        ]
        # print(messages)
        messages_list.append(messages)
        processing_text = ''
    if len(messages_list) == 0:
      prompt = (
        'The following section enclosed by ## is a transcription from a YouTube video. Please summarize the important points in bullet points. Please answer in the same language as the language enclosed in ##.\n\n'
        f'##\n{processing_text}\n##')
      messages = [
        {
          "role": "user",
          "content": prompt
        },
      ]
      messages_list.append(messages)
  print('API call')
  predictions = asyncio.run(
    dispatch_openai_requests(
      messages_list=messages_list,
      model="gpt-3.5-turbo",
      temperature=0,
      top_p=1.0,
    ))
  summaries = []

  for i, x in enumerate(predictions):
    summaries.append(x['choices'][0]['message']['content'])
  print(summaries)
  print(len(summaries))
  with open('points.txt', 'w') as f:
    f.write('\n'.join(summaries))
  
  messages_list = [[
    {
      "role":
      "system",
      "content":
      "You are a professional translator. Please translate the following text into English if it's not written in English. Just return the original text if it's written in English."
    },
    {
      "role": "user",
      "content": summary
    },
  ] for summary in summaries]

  predictions_en = asyncio.run(
    dispatch_openai_requests(
      messages_list=messages_list,
      model="gpt-3.5-turbo",
      temperature=0,
      top_p=1.0,
    ))

  messages_list = [[
    {
      "role":
      "system",
      "content":
      "You are a professional translator. Please translate the following text into Japanese if it's not written in Japanese. Just return the original text if it's written in Japanese."
    },
    {
      "role": "user",
      "content": summary
    },
  ] for summary in summaries]

  predictions_jp = asyncio.run(
    dispatch_openai_requests(
      messages_list=messages_list,
      model="gpt-3.5-turbo",
      temperature=0,
      top_p=1.0,
    ))
  
  output = '\n'.join([
    prediction['choices'][0]['message']['content']
    for prediction in predictions_en
  ])
  output_jp = '\n'.join([
    prediction['choices'][0]['message']['content']
    for prediction in predictions_jp
  ])

  with open('points_en.txt', 'w') as f:
    f.write(output)
  
  with open('points_jp.txt', 'w') as f:
    f.write(output_jp)


  messages_list = []
  processed_idx = 0
  processing_text = ''
  while processed_idx < len(summaries):
    if num_tokens(processing_text + '\n' +
                  summaries[processed_idx]) < token_budget:
      if processed_idx == 0:
        processing_text += summaries[processed_idx]
      else:
        processing_text += '\n' + summaries[processed_idx]
      processed_idx += 1
    else:
      prompt = (
        'Please provide a single summary in 3-5 sentences, incorporating the key points from the bullet points below. Please answer in the same language as the language enclosed in ##.\n\n'
        f'##\n{processing_text}\n##')
      messages = [
        {
          "role": "user",
          "content": prompt
        },
      ]
      messages_list.append(messages)
      processing_text = ''
  if len(messages_list) == 0:
    prompt = (
      'Please provide a single summary in 3-5 sentences, incorporating the key points from the bullet points below. Please answer in the same language as the language enclosed in ##.\n\n'
      f'##\n{processing_text}\n##')
    messages = [
      {
        "role": "user",
        "content": prompt
      },
    ]
    messages_list.append(messages)

  predictions = asyncio.run(
    dispatch_openai_requests(
      messages_list=messages_list,
      model="gpt-3.5-turbo",
      temperature=0,
      top_p=1.0,
    ))

  messages_list = [[
    {
      "role":
      "system",
      "content":
      "You are a professional translator. Please translate the following text into English if it's not written in English. Just return the original text if it's written in English."
    },
    {
      "role": "user",
      "content": prediction['choices'][0]['message']['content']
    },
  ] for prediction in predictions]
  print(messages_list)

  predictions_en = asyncio.run(
    dispatch_openai_requests(
      messages_list=messages_list,
      model="gpt-3.5-turbo",
      temperature=0,
      top_p=1.0,
    ))

  messages_list = [[
    {
      "role":
      "system",
      "content":
      "You are a professional translator. Please translate the following text into Japanese if it's not written in Japanese. Just return the original text if it's written in Japanese."
    },
    {
      "role": "user",
      "content": prediction['choices'][0]['message']['content']
    },
  ] for prediction in predictions]
  print(messages_list)

  predictions_jp = asyncio.run(
    dispatch_openai_requests(
      messages_list=messages_list,
      model="gpt-3.5-turbo",
      temperature=0,
      top_p=1.0,
    ))

  output = '\n'.join([
    prediction['choices'][0]['message']['content']
    for prediction in predictions_en
  ])
  output_jp = '\n'.join([
    prediction['choices'][0]['message']['content']
    for prediction in predictions_jp
  ])

  return output, output_jp


def download_subtitles(youtube_url):
  """Download YouTube subtitles in WebVTT format
    
    Args:
        youtube_url (str): URL of YouTube video
    
    Returns:
        str: WebVTT-formatted subtitle text
    """
  # Get video ID from URL
  video_id = YouTube(youtube_url).video_id
  # # Get video title from YouTube webpage
  # title = YouTube(youtube_url).title

  # Get subtitles from API
  transcript_list = YouTubeTranscriptApi.get_transcript(video_id,
                                                        languages=['en', 'ja'])
  subtitle_text = ""
  for transcript in transcript_list:
    if transcript["text"]:
      subtitle_text += transcript["text"] + "\n"

  # If subtitles are not found, write a message and return an empty string
  if not subtitle_text:
    st.write("Subtitles not available.")
    return ""

  return subtitle_text


def main():
  # Title and instructions
  st.title("YouTube summerizer with ChatGPT")
  st.write(
    "要約したいYouTubeのURLを入力してね。 Enter a YouTube video URL and click the button to get started."
  )

  # Get user input
  youtube_url = st.text_input("Enter a YouTube URL:")

  # Download subtitles
  try:
    subtitle_text = download_subtitles(youtube_url)
    print(subtitle_text)
    # print(title)
  except Exception as e:
    st.write(f"Error: {e}")
    return

  # If no subtitles are found, exit early
  if not subtitle_text:
    return

  # Process subtitles with OpenAI GPT-3
  st.write(
    "ChatGPTくんが頑張ってます、少々お待ちを。 Processing subtitles with ChatGPT... (this may take a minute)"
  )
  processed_text, processed_text_jp = process_text(subtitle_text)
  st.write("どうぞ！")
  st.write(processed_text_jp)
  st.write("Here's the summary")
  st.write(processed_text)


if __name__ == '__main__':
  main()
