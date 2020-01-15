# line2slack

LINE@の情報を、API使って取得するよ。

## コマンド

### 環境変数を指定して実行
python ./line2slack.py production

## 設定関連
conf/conf.yml

production:
  database:
    host: 'localhost'
    db: 'database'
    user: 'user'
    password: 'password'
    charset: 'utf8'
  slack-token: 'slack-token'
