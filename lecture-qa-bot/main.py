# imports
import os
import openai  # for calling the OpenAI API
import pandas as pd  # for storing text and embeddings data
import tiktoken  # for counting tokens
from scipy import spatial  # for calculating vector similarities for search

from dotenv import load_dotenv
load_dotenv()
# models
EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-3.5-turbo"
openai.api_key = os.environ["OPENAI_API_KEY"]

import pandas as pd
import pickle
from dataclasses import dataclass
from typing import List

@dataclass
class Video:
    video_name: str
    text: str
    embedding: List[float]
@dataclass
class Page:
    page_number: int
    text: str
    embedding: List[float]


# ファイルパスとファイル名を定義
notes_path = 'lecture_notes.pickle'
videos_path = 'lecture_videos.pickle'

# pickleファイルを読み込み、DataFrameに変換
with open(notes_path, 'rb') as f:
    data = pickle.load(f)
note_df = pd.DataFrame(data)

with open(videos_path, 'rb') as f:
    data = pickle.load(f)
video_df = pd.DataFrame(data)

# DataFrameの中身を確認
# print(note_df.head())
# print(video_df.head())
filtered_note_df = note_df[note_df['text'].str.len() >= 200]
filtered_video_df = video_df[video_df['text'].str.len() >= 200]

# https://github.com/openai/openai-cookbook/blob/main/examples/Question_answering_using_embeddings.ipynb
# search function
def strings_ranked_by_relatedness(
    query: str,
    df: pd.DataFrame,
    relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
    top_n: int = 10,
    source: str = 'note',
) -> tuple[list[str], list[float]]:
    """Returns a list of strings and relatednesses, sorted from most related to least."""
    query_embedding_response = openai.Embedding.create(
        model=EMBEDDING_MODEL,
        input=query,
    )
    query_embedding = query_embedding_response["data"][0]["embedding"]
    strings_and_relatednesses = [
        (row["text"], relatedness_fn(query_embedding, row["embedding"]), row['page_number'] if source == 'note' else row['video_name'])
        for i, row in df.iterrows()
    ]
    strings_and_relatednesses.sort(key=lambda x: x[1], reverse=True)
    strings, relatednesses, sources = zip(*strings_and_relatednesses)
    return strings[:top_n], relatednesses[:top_n], sources[:top_n]


# strings, relatednesses = strings_ranked_by_relatedness("What is reinforcement learning?", filtered_note_df, top_n=3)
# for string, relatedness in zip(strings, relatednesses):
#     print(f"{relatedness=:.3f}")
#     print(string)


# strings, relatednesses = strings_ranked_by_relatedness("What is reinforcement learning?", filtered_video_df, top_n=3)
# for string, relatedness in zip(strings, relatednesses):
#     print(f"{relatedness=:.3f}")
#     print(string)


def num_tokens(text: str, model: str = GPT_MODEL) -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def query_message(
    query: str,
    df: pd.DataFrame,
    model: str,
    token_budget: int,
    source: str = 'note',
) -> str:
    """Return a message for GPT, with relevant source texts pulled from a dataframe."""
    strings, relatednesses, sources = strings_ranked_by_relatedness(query=query, df=df, source=source)
    introduction = 'Use the below notes or transcription on Lectures of Machine Learning to answer the subsequent question. If the answer cannot be found in the articles, write "I could not find an answer."'
    question = f"\n\nQuestion: {query}"
    message = introduction
    source = ''
    for idx, string in enumerate(strings):
        next_article = f'\n\nnotes or transcription:\n"""\n{string}\n"""'
        if (
            num_tokens(message + next_article + question, model=model)
            > token_budget
        ):
            break
        else:
            message += next_article
            source += f'{sources[idx]}\n{string}\n\n'
    return message + question, source


def ask(
    query: str,
    df: pd.DataFrame,
    model: str = GPT_MODEL,
    token_budget: int = 4096 - 500,
    print_message: bool = False,
    source: str = 'note',
) -> str:
    """Answers a query using GPT and a dataframe of relevant texts and embeddings."""
    message, source = query_message(query=query, df=df, source=source, model=model, token_budget=token_budget)
    if print_message:
        print(message)
    messages = [
        {"role": "system", "content": "You answer questions about machine learning."},
        {"role": "user", "content": message},
    ]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0
    )
    response_message = response["choices"][0]["message"]["content"]
    return response_message, source


# question = '決定木とロジスティック回帰の使い分けを教えて下さい'
# messages = [
#         {"role": "system", "content": "You are a professional translator. Translate the following question on Machine learning into English. If the question is already in English, just return the original question."},
#         {"role": "user", "content": question},
#     ]
# response = openai.ChatCompletion.create(
#     model=GPT_MODEL,
#     messages=messages,
#     temperature=0
# )
# response_message = response["choices"][0]["message"]["content"]
# print(response_message)
# answer, source = ask(response_message, df=filtered_video_df, source='video')
# messages = [
#         {"role": "system", "content": "You are a professional translator. Translate the following answer on Machine learning into Japanese."},
#         {"role": "user", "content": answer},
#     ]
# response = openai.ChatCompletion.create(
#     model=GPT_MODEL,
#     messages=messages,
#     temperature=0
# )
# answer_jp = response["choices"][0]["message"]["content"]

# print(answer)
# print(answer_jp)
# print(source)
# answer, source = ask(response_message, df=filtered_note_df, source='note')

from slack_bolt import App
import re
from slack_bolt.adapter.socket_mode import SocketModeHandler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
@app.event("app_mention")
def handle_app_mentions(body, say):
    if "thread_ts" in body['event'].keys():
        thread_ts = body['event']['thread_ts']
    else:
        thread_ts = body['event']['ts']
    text = body['event']['text']
    user_id = body['event']['user']
    
    # メンションの形式である <@U12345> を削除
    mention_pattern = r'<@\w+>'
    cleaned_text = re.sub(mention_pattern, '', text).strip()
    question = cleaned_text
    
    messages = [
            {"role": "system", "content": "You are a helpful assistant. Answer the following question. Please answer in Japanese. 回答は日本語でお願いします。"},
            {"role": "user", "content": question},
        ]
    response = openai.ChatCompletion.create(
        model=GPT_MODEL,
        messages=messages,
        temperature=0
    )
    naive_answer = response["choices"][0]["message"]["content"]
    slack_message = f'ChatGPTからの回答: \n{naive_answer}'
    say(text=slack_message, thread_ts=thread_ts)

    messages = [
            {"role": "system", "content": "You are a researcher on Machine Learning and Deep Learning. Answer the following question. Please answer in Japanese. 回答は日本語でお願いします。"},
            {"role": "user", "content": question},
        ]
    response = openai.ChatCompletion.create(
        model=GPT_MODEL,
        messages=messages,
        temperature=0
    )
    professional_answer = response["choices"][0]["message"]["content"]
    slack_message = f'機械学習の専門家プロンプトChatGPTからの回答: \n{professional_answer}'
    say(text=slack_message, thread_ts=thread_ts)


    messages = [
            {"role": "system", "content": "You are a professional translator. Translate the following question on Machine learning into English. If the question is already in English, just return the original question."},
            {"role": "user", "content": question},
        ]
    response = openai.ChatCompletion.create(
        model=GPT_MODEL,
        messages=messages,
        temperature=0
    )
    response_message = response["choices"][0]["message"]["content"]
    print(response_message)
    answer_video, source_video = ask(response_message, df=filtered_video_df, source='video')
    messages = [
            {"role": "system", "content": "You are a professional translator. Translate the following answer on Machine learning into Japanese."},
            {"role": "user", "content": answer_video},
        ]
    response = openai.ChatCompletion.create(
        model=GPT_MODEL,
        messages=messages,
        temperature=0
    )
    answer_video_jp = response["choices"][0]["message"]["content"]

    # print(answer)
    # print(answer_jp)
    # print(source)
    # answer, source = ask(response_message, df=filtered_note_df, source='note')
    slack_message = f'講義動画からの回答: \n{answer_video_jp}\n\n{answer_video}'
    say(text=slack_message, thread_ts=thread_ts)
    # say(text=source_video, thread_ts=thread_ts)

    answer_note, source_note = ask(response_message, df=filtered_note_df, source='note')
    messages = [
            {"role": "system", "content": "You are a professional translator. Translate the following answer on Machine learning into Japanese."},
            {"role": "user", "content": answer_note},
        ]
    response = openai.ChatCompletion.create(
        model=GPT_MODEL,
        messages=messages,
        temperature=0
    )
    answer_note_jp = response["choices"][0]["message"]["content"]
    slack_message = f'講義ノートからの回答: \n{answer_note_jp}\n\n{answer_note}'
    say(text=slack_message, thread_ts=thread_ts)
    # say(text=source_note, thread_ts=thread_ts)

    prompt = f"""
    質問: {question}
    上記の質問に対して以下の回答が得られました。
    回答1: {naive_answer}
    回答2: {professional_answer}
    回答3: {answer_video_jp}
    回答4: {answer_note_jp}
    これらの回答を総合的に考慮し、質問に対するより良い回答をして下さい。
    回答: 
    """
    messages = [
            {"role": "system", "content": "You are a researcher on Machine Learning and Deep Learning. Please answer in Japanese. 回答は日本語でお願いします。"},
            {"role": "user", "content": prompt},
        ]
    response = openai.ChatCompletion.create(
        model=GPT_MODEL,
        messages=messages,
        temperature=0
    )
    total_answer = response["choices"][0]["message"]["content"]
    slack_message = f'総合的な回答: \n{total_answer}'
    say(text=slack_message, thread_ts=thread_ts)



if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
