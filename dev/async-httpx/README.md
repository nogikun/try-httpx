# async-httpx

`sample/input.xlsx` の `Sheet1` にある `word` 列を `GET /tracks` の `q` に渡し、応答本文を `res` 列に入れた `sample/output.xlsx` を作ります。

`.env` の `endpoint` には API のベース URL を設定します。クライアントが `/tracks` を追加します。

```dotenv
endpoint=http://localhost:8000
```

```powershell
uv run --project dev/async-httpx python dev/async-httpx/main.py
```

`--concurrency` は同時リクエスト数（既定値 10）、`--limit` と `--offset` はページ指定です。`--artist-id` と `--genre-id` で絞り込めます。入出力ファイルは `--input` と `--output` で変更できます。

同期版と同じ入力 10 件で所要時間を測る pytest:

```powershell
uv run --project dev/async-httpx pytest -s -v dev/async-httpx/tests
```
