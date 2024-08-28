#!/bin/sh

# マイグレーションの作成
python manage.py makemigrations flow

# データベースのマイグレーション
python manage.py migrate

# 静的ファイルの収集（必要な場合）
python manage.py collectstatic --noinput

# スクリプトの終了
echo "Initialization complete. You can now create a superuser and start the development server."

# コンテナを実行し続ける
tail -f /dev/null