import time
import requests
from requests.structures import CaseInsensitiveDict
import os
from dotenv import load_dotenv
load_dotenv()
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SLACK_CHANNEL_ID = os.environ['SLACK_CHANNEL_ID']
SLACK_API_URL = "https://slack.com/api/chat.postMessage"


# Twitter API認証情報
BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

# 対象アカウントの設定
TARGET_ACCOUNTS = ['_akhaliq', 'johnjnay', 'omarsar0', 'shota7180']

# 最後に取得したツイートのIDを保存する辞書
last_tweet_id = {username: None for username in TARGET_ACCOUNTS}

def create_headers():
    headers = CaseInsensitiveDict()
    headers["Authorization"] = f"Bearer {BEARER_TOKEN}"
    headers["Content-Type"] = "application/json"
    return headers

# ユーザーIDを取得する関数
def get_user_id(username):
    url = f"https://api.twitter.com/2/users/by?usernames={username}"
    headers = create_headers()
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Request failed: {response.text}")
    user_data = response.json()
    return user_data['data'][0]['id']

# 新しいツイートを取得する関数
def fetch_new_tweets(user_id, username, since_id=None):
    url = f"https://api.twitter.com/2/users/{user_id}/tweets"
    headers = create_headers()
    params = {
        'max_results': 20,
        'expansions': 'author_id',
        'tweet.fields': 'created_at',
        'user.fields': 'username'
    }
    if since_id is not None:
        params['since_id'] = since_id

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Request failed: {response.text}")
    
    tweets_data = response.json()
    tweets = []

    if 'data' in tweets_data:
        for tweet in tweets_data['data']:
            tweets.append(tweet)
            last_tweet_id[username] = max(last_tweet_id[username] or 0, int(tweet['id']))

    return tweets


def post_to_slack(token, channel_id, message):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    data = {"channel": channel_id, "text": message}
    response = requests.post(SLACK_API_URL, headers=headers, json=data)
    
    if response.status_code != 200:
        raise Exception(f"Error posting to Slack: {response.status_code}")

# 一定時間ごとに新しいツイートを取得する
while True:
    for username in TARGET_ACCOUNTS:
        user_id = get_user_id(username)
        new_tweets = fetch_new_tweets(user_id, username, last_tweet_id[username])
        if new_tweets:
            print(f"New tweets from {username}:")
            for tweet in new_tweets:
                message = f"{username}: {tweet['text']} \nhttps://twitter.com/{username}/status/{tweet['id']}"
                post_to_slack(SLACK_BOT_TOKEN, SLACK_CHANNEL_ID, message)
                time.sleep(5)

    # 一定時間（ここでは12時間）待機
    time.sleep(60 * 60 * 12)

