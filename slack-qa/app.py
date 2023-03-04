import os
from slack_bolt import App
from slack_sdk.errors import SlackApiError
from slack_bolt.adapter.socket_mode import SocketModeHandler
import openai

CHANNEL_ID = os.environ.get("CHANNEL_ID")
log_dir = os.path.join('log', CHANNEL_ID)
if not os.path.exists(CHANNEL_ID):
    os.makedirs(log_dir)

openai.api_key = os.environ.get("OPENAI_API_KEY")


# スレッド内の全メッセージを取得する関数
def get_thread_messages(channel_id, thread_ts):
    messages = []
    try:
        result = app.client.conversations_replies(
            channel=channel_id,
            ts=thread_ts
        )
        messages = result["messages"]
    except SlackApiError as e:
        print("Error getting thread messages: {}".format(e))
    return messages


def create_response(messages):
    response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0,
                max_tokens=4096
            )
    return response['choices'][0]['message']['content']


# ボットトークンとソケットモードハンドラーを使ってアプリを初期化します
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# メッセージを受信した時の処理
@app.event("message")
def handle_message(event, say):
    query = event["text"]
    channel_id = event["channel"]
    thread_ts = event["ts"]
    print(channel_id)
    if channel_id == os.environ.get("CHANNEL_ID"):
        thread_messages = get_thread_messages(channel_id, thread_ts)
        response = create_response(query, thread_ts)
        say(text=response, thread_ts=thread_ts)
    else:
        pass


# アプリを起動します
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()