FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY . /code/

# Create directory for SQLite database
RUN mkdir -p /code/db_data

# エントリーポイントスクリプトをコピーして実行可能にする
COPY entrypoint.sh /code/
RUN chmod +x /code/entrypoint.sh

# エントリーポイントスクリプトを使用
ENTRYPOINT ["/code/entrypoint.sh"]