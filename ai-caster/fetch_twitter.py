import requests
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv
load_dotenv()

# your Twitter API credentials
bearer_token = os.environ['TWITTER_BEARER_TOKEN']

search_url = "https://api.twitter.com/2/tweets/search/recent"


def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


# query_params = {
#         'query': 'GPT lang:en -is:retweet -is:reply',
#         'start_time': start_time_str,
#         'tweet.fields': 'public_metrics',
#         'max_results': 100  # maximum allowed by API per single request
#     }

# tweets = connect_to_endpoint(search_url, query_params)['data']
# print(tweets)
# print(len(tweets))
# tweets = [tweet for tweet in tweets if not tweet['text'].startswith('RT @')]
# print(len(tweets))
# top_tweets = sorted(tweets, key=lambda x: x['public_metrics']['retweet_count'], reverse=True)
# print(top_tweets[:20])

start_time = start_time = datetime.now() - timedelta(hours=12)
start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")

# langs = ['ja', 'en']
# keywords = ['LLM', 'GPT', '"Foundation Model"']
langs = ['ja']
keywords = ['LLM']


all_tweets = []
for keyword in keywords:
    for lang in langs:
        while True:
            query_params = {
                'query': f'{keyword} lang:{lang} -is:retweet -is:reply',
                'start_time': start_time_str,
                'tweet.fields': 'public_metrics',
                'max_results': 100,  # maximum allo wed by API per single request
                'next_token': None,
            }
        
            tweets_data = connect_to_endpoint(search_url, query_params)
            tweets = tweets_data['data']
            all_tweets.extend(tweets)
            if 'next_token' in tweets_data['meta']:
                query_params['next_token'] = tweets_data['meta']['next_token']
            else:
                break
            time.sleep(1)
print(len(all_tweets))
top_tweets = sorted(all_tweets, key=lambda x: x['public_metrics']['retweet_count'], reverse=True)
print(top_tweets[:20])
print(top_tweets[-20:])

