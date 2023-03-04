# slack-qa

https://slack.dev/bolt-python/ja-jp/tutorial/getting-started  
上記を参考に SLACK_BOT_TOKEN、SLACK_APP_TOKEN を発行

## 準備

```sh
# 環境変数を設定して実行

export SLACK_CHANNEL_ID=
# Slack連携用
export SLACK_BOT_TOKEN=xoxb-
export SLACK_APP_TOKEN=xapp-
# Open AIのAPI
export OPENAI_API_KEY=sk-
```

```sh
pip install slack_bolt openai tiktoken
python3 app.py
```
