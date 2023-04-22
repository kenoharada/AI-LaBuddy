import re
import os
import glob
import json
import openai
import tiktoken
import time
from dotenv import load_dotenv
load_dotenv()
# models
EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-3.5-turbo"
openai.api_key = os.environ["OPENAI_API_KEY"]

def replace_newlines(text):
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)  # 1つだけの改行を空白に置換
    text = re.sub(r'\n{2,}', '\n', text)  # 2つ以上の連続する改行を1つの改行に置換
    return text


def num_tokens(text: str, model: str = GPT_MODEL) -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


if __name__ == '__main__':
    process_data = 'process_data'
    save_dir = 'result_data'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    json_path_list = glob.glob(os.path.join(process_data, '*.json'))
    system_message = 'You are a helpful assistant'
    questions = [
        'What is this paper about? What is the main topic/idea/theme?',
        'What makes this paper impressive compared to previous research? What are the novel contributions? What is new compared to previous work? How does it outperform previous research?',
        'What is the core of the technique or method of this paper?',
        'How was this paper\'s effectiveness validated? What experiments were conducted? What are the evaluation methods?',
        'Are there any discussions? What are the limitations of this paper? What are the future works?',
        'What are the next papers to read? What are the related papers?'
    ]
    for json_path in json_path_list:
        with open(json_path, 'r', encoding='utf-8') as f:
            paper = json.load(f)

        for question in questions:
            answers = ''
            for idx, answer in enumerate(paper[question]):
                answers += f'Answer from excerpt No. {idx}: {answer}\n'
            prompt = (
                        f"Paper title: {paper['title']}\n"
                        f"Question: {question}\n"
                        "The following answers are derived from each excerpt chunk from the paper:\n"
                        f"###\n{answers}\n###\n"
                        "Considering the answers above, please provide an aggregated answer statement to the question.\n"
                        )            
            messages = [
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": prompt},
            ]
            response = openai.ChatCompletion.create(
                model=GPT_MODEL,
                messages=messages,
                temperature=0
            )
            response_message = response["choices"][0]["message"]["content"]

            messages = [
                {"role": "system", "content": "You are a professional translator. Please translate the following text into Japanese."},
                {"role": "user", "content": response_message},
            ]
            response = openai.ChatCompletion.create(
                model=GPT_MODEL,
                messages=messages,
                temperature=0
            )
            response_message_jp = response["choices"][0]["message"]["content"]
            paper[question] = response_message
            paper['jp_' + question] = response_message_jp
            print(question)
            print(response_message)
            print(response_message_jp)
        # save data
        save_path = os.path.join(save_dir, os.path.basename(json_path))
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(paper, f, indent=4)