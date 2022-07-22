# alert-lambda

Lambda 関数から CloudWatchLogs の Errors と Throttles を取得して Slack に通知するサービスです。
モニタリングしたいリージョンごとにデプロイします。
システムの仕様上、東京リージョン(ap-northeast-1)はモニタリングしたい Lambda 関数がない場合でも必ずデプロイしてください。
セットアップ後、デプロイ済みのリージョンで、モニタリングされてない Lambda 関数は日次で追加されます。

# セットアップ手順

## 事前準備

初回実行時に必要な準備を記載します。既に設定済のものはスキップしてください。

### npm

端末に npm をインストールします。

- [Configuring your local environment | npm](https://docs.npmjs.com/getting-started/configuring-your-local-environment)

簡単にですが、Homebrew から npm をインストールする例を紹介しています。

[Serverless Framework 用の端末設定メモ | Takaaki Kakei](https://zenn.dev/t_kakei/scraps/8675d5b86ffc4f)

### Pipenv

端末に Pipenv をインストールします。

- [さぁ今すぐこれから Pipenv をインストール! | Pipenv](https://pipenv-ja.readthedocs.io/ja/translate-ja/#install-pipenv-today)

以下は、Homebrew でインストールする場合のコマンド例です。

```bash
$ brew install pipenv
```

### Serverless Framework

端末に Serverless Framework をインストールします。

- [Setting Up Serverless Framework With AWS | Serverless](https://www.serverless.com/framework/docs/getting-started)

以下は、npm でインストールする場合のコマンド例です。

```bash
$ npm install -g serverless
```

デプロイ先の AWS 環境で、Serverless Framework が利用する IAM ユーザーとアクセスキーを作成します。
また端末で、デプロイ時に利用する AWS プロファイルの設定をします。

- [AWS Credentials | Serverless](https://www.serverless.com/framework/docs/providers/aws/guide/credentials)

なお、AWS プロファイルは AWS Vault で管理することを推奨します。

- [AWS Vault で端末内の AWS アクセスキー平文保存をやめてみた](https://dev.classmethod.jp/articles/aws-vault/)


## 端末でのプロジェクトのセットアップ

プロジェクトのディレクトリで以下のコマンドを実行します。

```bash
$ npm ci # 必要なプラグインのインストール
$ pipenv install # 必要なパッケージのインストール
```

## AWS Chatbot の設定

マネジメントコンソールの AWS Chatbot サービスにアクセスします。
以下を参考にして、AWS Chatbot から Slack への接続を確立します。
Slack チャンネル ID とワークスペース ID を後で利用するのでメモします。

- [Serverless Framework で AWS Chatbot と Amazon SNS のリソースを作成してみた](https://dev.classmethod.jp/articles/serverless-framework-resources-chatbot-sns/#toc-4)

## AWS Systems Manager の設定

マネジメントコンソールの AWS Systems Manager サービスにアクセスします。
機微な情報はコード内に直接書きたくないので、AWS Systems Manager のパラメータストアに保存します。
モニタリングするリージョンごとに設定を行います。
パラメータ名はそれぞれ以下で保存します。

- Slack チャンネル ID
    - 名前： /alert-lambda/ステージ名/SLACK_CHANNEL_ID
        - 例： /alert-lambda/dev/SLACK_CHANNEL_ID
    - 値（例）： C01U80K9KPD
- ワークスペース ID
    - 名前： /alert-lambda/ステージ名/SLACK_WORKSPACE_ID
        - 例： /alert-lambda/dev/SLACK_WORKSPACE_ID
    - 値（例）： T01UXHUCRMW


## プロジェクトのデプロイ

東京リージョン(ap-northeast-1)を含む、モニタリングしたい Lambda 関数があるリージョンにデプロイします。
プロジェクトのディレクトリで以下のコマンドでデプロイします。

東京リージョン: ap-northeast-1
オレゴンリージョン: us-west-2

```bash
aws-vault exec プロファイル名 -- sls deploy --stage ステージ名 --region リージョン名
```

以下のリソースは、東京リージョン(ap-northeast-1)でのみ作成されます。
そのため、東京リージョン(ap-northeast-1)にモニタリングしたい Lambda 関数がない場合でも必ずデプロイしてください。

- AWS Chatbot SlackChannelConfiguration
- AWS Chatbot の IAM Role

## AWS Chatbot に Amazon SNS トピックの追加

マネジメントコンソールの AWS Chatbot サービスにアクセスします。
対象の設定済みのクライアントを開きます。
設定名が AlertLambdaChatbot-dev のリソースにチェックをつけて、編集ボタンを押します。
[通知 - オプション]の SNS トピックに、本ツールで作成した Amazon SNS トピックを追加して保存します。

- リージョン：デプロイしたリージョン
- トピック: AlertLambdaTopic-ステージ名-リージョン名

## 備考

アラームの設定内容をなどを変更する場合は、以下のステップが必要です。

1. 変更デプロイ
2. アラーム一括削除
3. アラーム再作成

これでセットアップ完了です。お疲れ様でした！
