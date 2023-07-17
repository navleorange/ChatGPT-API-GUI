# ChatGPT-API-GUI
これはChatGPTをAPIでもGUIが使えるようにしたものです。

## 作成した理由
2023-07-18現在、WebでChatGPTを使うと3時間ごとに最大25メッセージしか送れない制限があります。
APIを使えばその制限はないですが、ちょっと試すだけならGUIの方が色々と楽なので作りました。

## 実行前に1度設定する必要があるもの
以下を参考に`.env`を作成してください
```
/res/env.sample
```
<details><summary>詳細</summary><div>

`Organization ID`はOpenAIの`Organization settings`で確認してください
```
OPENAI_ORGANIZATION_3.5 = "ChatGPT3系を使いたいときの請求先のOrganization ID"
OPENAI_ORGANIZATION_4 = "ChatGPT4系を使いたいときの請求先のOrganization ID"
OPENAI_API_KEY = "APIキー"
```

</div></details>

## 実行
Djangoを使用して実装しています。
以下のコマンドでできるはず
```
python3 manage.py runserver
```

## 設定の変更
以下のファイルでChatGPTの設定を変更できます。
```
/res/config.ini
```

<details><summary>詳細</summary><div>

基本は[API Reference](https://platform.openai.com/docs/api-reference/completions/create)に準拠しています。
`generate_num`は`API Reference`で言うところの`n`に該当します。(現在は1にのみ対応)
`model_name`は使いたい物をコメントアウトするか、`API Reference`を参照してください。
```
[log]
path = ./log/

[ChatGPT]
api_key_path = ./res/.env
temperature = 1
to_p = 1
generate_num = 1
stream = true
max_tokens = 512
presence_penalty = 0
frequency_penalty = 0
; model_name = gpt-3.5-turbo
model_name = gpt-3.5-turbo-16k-0613
; model_name = gpt-4-0314
; model_name = gpt-4-0613
```

</div></details>

<!-- フロントエンド初心者なのでご容赦ください(>_<) -->