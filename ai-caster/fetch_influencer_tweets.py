import time
import requests
from requests.structures import CaseInsensitiveDict
import os
import json
from dotenv import load_dotenv
load_dotenv()

# Twitter API認証情報
BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

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
def fetch_new_tweets(user_id, username, influencers):
    url = f"https://api.twitter.com/2/users/{user_id}/tweets"
    headers = create_headers()
    params = {
        'max_results': 5,
        'expansions': 'author_id',
        'tweet.fields': 'created_at',
        'user.fields': 'username',
        'exclude': 'replies,retweets'  # リプライとリツイートを除外する
    }
    since_id = influencers[username]
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
            influencers[username] = max(influencers[username] or 0, int(tweet['id']))

    return tweets, influencers

influencers = json.load(open('influencers.json', 'r'))
for username in influencers.keys():
    user_id = get_user_id(username)
    new_tweets, influencers = fetch_new_tweets(user_id, username, influencers)
    if new_tweets:
        print(f"New tweets from {username}:")
        for tweet in new_tweets:
            message = f"{username}: {tweet['text']} \nhttps://twitter.com/{username}/status/{tweet['id']}"
            print(message)
    with open('influencers.json', 'w') as f:
        json.dump(influencers, f)
    with open(f'{username}_tweets.json', 'w') as f:
        json.dump(new_tweets, f)

# 一定時間ごとに新しいツイートを取得する
# while True:
#     influencers = json.load(open('influencers.json', 'r'))
#     for username in influencers.keys():
#         user_id = get_user_id(username)
#         new_tweets, influencers = fetch_new_tweets(user_id, username, influencers)
#         if new_tweets:
#             print(f"New tweets from {username}:")
#             for tweet in new_tweets:
#                 message = f"{username}: {tweet['text']} \nhttps://twitter.com/{username}/status/{tweet['id']}"
#                 print(message)
#         with open('influencers.json', 'w') as f:
#             json.dump(influencers, f)

#     # 一定時間（ここでは12時間）待機
#     time.sleep(1000)

