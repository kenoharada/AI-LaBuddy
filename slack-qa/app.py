import os
from slack_bolt import App
from slack_sdk.errors import SlackApiError
from slack_bolt.adapter.socket_mode import SocketModeHandler
import openai
import tiktoken
SLACK_CHANNEL_ID = os.environ["SLACK_CHANNEL_ID"]
log_dir = os.path.join('log', SLACK_CHANNEL_ID)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

openai.api_key = os.environ["OPENAI_API_KEY"]
# https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
encoding = tiktoken.get_encoding("cl100k_base")



# スレッド内の全メッセージを取得する関数
def get_thread_messages(channel_id, thread_ts):
    thread_messages = []
    try:
        result = app.client.conversations_replies(
            channel=channel_id,
            ts=thread_ts,
            limit=1000
        )
        thread_messages = result["messages"]
    except SlackApiError as e:
        print("Error getting thread messages: {}".format(e))
    return thread_messages


def create_gpt_message(thread_messages):
    if len(thread_messages) == 1:
        # 会話の始まり
        prompt = "あなたは人工知能・機械学習の研究をしている優秀な博士課程学生で、優秀なプログラマーです。技術的な質問や研究に関する質問に対しては分かりやすく丁寧に回答し、雑談のような問いかけには楽しく陽気に回答して下さい"
        last_message = thread_messages[0]['text']
        gpt_message = [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": last_message},
                ]
        free_token_num = 4000 - (len(encoding.encode(prompt)) + len(encoding.encode(last_message)))
        response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=gpt_message,
                temperature=0,
                max_tokens=free_token_num
            )['choices'][0]['message']['content']
        with open(os.path.join(log_dir, f"{thread_messages[0]['ts']}_{thread_messages[0]['ts']}_prompt.txt"), 'w') as f:
            f.write(prompt)
        with open(os.path.join(log_dir, f"{thread_messages[0]['ts']}_{thread_messages[0]['ts']}_lastmessage.txt"), 'w') as f:
            f.write(last_message)
        with open(os.path.join(log_dir, f"{thread_messages[0]['ts']}_{thread_messages[0]['ts']}_response.txt"), 'w') as f:
            f.write(response)
        return response
    elif len(thread_messages) == 0:
        return ""
    else:
        # for thread_message in thread_messages:
        history = ""
        for thread_message in thread_messages:
            if 'bot_id' in thread_message:
                history += f"あなた: {thread_message['text']}\n"
            else:
                user_id = thread_message["user"]
                user_name = app.client.users_info(user=user_id)["user"]["profile"]["display_name"]
                history += f"{user_name}さん: {thread_message['text']}\n"
                last_message = f"{user_name}さん: {thread_message['text']}\nあなた: "
        if len(encoding.encode(history)) > 3072:
            summary_prompt = f"以下は会話のやり取りです。やり取りを200文字程度に要約して下さい。\n\n{history}"
            free_token_num = 4000 - len(encoding.encode(summary_prompt))
            summarized_history = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": summary_prompt}],
                temperature=0,
                max_tokens=free_token_num
            )['choices'][0]['message']['content']
            # TODO: 最後何個かの会話は残して良いかも
            prompt =  f"以下は今までの会話の要約です。\n\n{summarized_history}\n\nあなたは人工知能・機械学習の研究をしている優秀な博士課程学生で、優秀なプログラマーです。技術的な質問や研究に関する質問に対しては分かりやすく丁寧に回答し、雑談のような問いかけには楽しく陽気に回答して下さい。"
        else:
            prompt =  f"以下は今までの会話です。\n\n{history}\n\nあなたは人工知能・機械学習の研究をしている優秀な博士課程学生で、優秀なプログラマーです。技術的な質問や研究に関する質問に対しては分かりやすく丁寧に回答し、雑談のような問いかけには楽しく陽気に回答して下さい。"
        
    gpt_message = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": last_message},
        ]
    with open(os.path.join(log_dir, f"{thread_messages[0]['thread_ts']}_{thread_messages[-1]['ts']}_prompt.txt"), 'w') as f:
        f.write(prompt)
    with open(os.path.join(log_dir, f"{thread_messages[0]['thread_ts']}_{thread_messages[-1]['ts']}_lastmessage.txt"), 'w') as f:
        f.write(last_message)
    
    free_token_num = 4000 - (len(encoding.encode(prompt)) + len(encoding.encode(last_message)))
    response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=gpt_message,
                temperature=0,
                max_tokens=free_token_num
            )['choices'][0]['message']['content']
    with open(os.path.join(log_dir, f"{thread_messages[0]['thread_ts']}_{thread_messages[-1]['ts']}_response.txt"), 'w') as f:
        f.write(response)
    return response


# ボットトークンとソケットモードハンドラーを使ってアプリを初期化します
app = App(token=os.environ["SLACK_BOT_TOKEN"])

# メッセージを受信した時の処理
@app.event("message")
def handle_message(event, say):
    try:
        print(event)
        channel_id = event["channel"]

        if channel_id == SLACK_CHANNEL_ID:
            if "thread_ts" in event.keys():
                thread_ts = event["thread_ts"]
                thread_messages = get_thread_messages(channel_id, thread_ts)
                response = create_gpt_message(thread_messages)
            else:
                thread_ts = event["ts"]
                thread_messages = [event]
                response = create_gpt_message(thread_messages)
            print(thread_messages)
            print(response)
            say(text=response, thread_ts=thread_ts)
        else:
            pass
    except Exception as e:
        print(e)


# アプリを起動します
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()