# GenAiFlowMaster

GenAiFlowMasterは、AIを活用したワークフローの作成、実行、管理を簡単にする革新的なプラットフォームです。直感的なインターフェースと強力な機能を組み合わせることで、AIの力を最大限に引き出し、ビジネスプロセスを効率化します。

## 特徴

- **ビジュアルフロー作成**: ユーザーフレンドリーなドラッグ＆ドロップインターフェースを使用して、複雑なAIワークフローを設計できます。
![フローの定義](https://github.com/sinjorjob/GenAiFlowMaster/blob/main/gif/flow-editor.gif)

- **マルチモデルサポート**: OpenAI、AzureOpenAI、Claudeなど、さまざまなAIモデルと統合できます。
- **リアルタイム実行監視**: ワークフローの進行状況をリアルタイムで追跡できます。

![フローの実行](https://github.com/sinjorjob/GenAiFlowMaster/blob/main/gif/flow-run.gif
)


- **カスタマイズ可能なノード**: 各ノードに特定の指示、システムプロンプト、AIモデル設定を構成できます。
- **実行履歴**: 過去のワークフロー実行の詳細なログを確認できます。


## はじめに

### 前提条件

- Docker
- Docker Compose

### クイックスタート

1. リポジトリをクローンします：
   ```
   git clone https://github.com/sinjorjob/GenAiFlowMaster.git
   cd genaiflowmaster
   ```

2. Dockerを使用してアプリケーションを起動します：
   ```
   docker-compose up --build -d
   ```

3. スーパーユーザーアカウントを作成します：
   ```
   docker-compose exec web python manage.py createsuperuser
   ```

4. 開発サーバーを実行します：
   ```
   docker-compose exec web python manage.py runserver 0.0.0.0:8000
   ```

5. `http://localhost:8000` でアプリケーションにアクセスします。

## 使用方法

1. **新しいフローの作成**: 「新規フロー作成」ボタンをクリックし、フローに名前を付けます。
2. **ノードの追加**: 「ノードを追加」ボタンを使用して、フローに新しいノードを挿入します。
3. **ノードの設定**: 各ノードをクリックして、ノード名、システムプロンプト、指示内容、AIモデル設定などのプロパティを設定します。
4. **ノードの接続**: ノード間をドラッグして接続し、実行の流れを定義します。
5. **フローの実行**: 「フローを実行」ボタンをクリックし、必要に応じて初期入力を提供し、フローの動作を確認します。

## AIモデルの設定

「モデル設定」メニューから、使用するAIモデル（OpenAI、AzureOpenAI、Claude）のAPIキーを設定します。


## ライセンス

このプロジェクトはMITライセンスの下でライセンスされています。

