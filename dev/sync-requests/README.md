# sync-requests

`async-httpx` と同じ `.env`、`sample/input.xlsx`、`TrackQuery`、Excel 入出力を使い、同期 HTTP 呼び出しだけ標準ライブラリの `urllib` に置き換えた比較用クライアントです。依存関係は `async-httpx` から `httpx` だけを除いています。

API は別ターミナルで起動します。

```powershell
uv run --project tools/simple-api simple-api
```

同期実行と所要時間の確認:

```powershell
uv run --project dev/sync-requests python dev/sync-requests/main.py
uv run --project dev/sync-requests pytest -s -v dev/sync-requests/tests
```

pytest は同じ `input.xlsx` の先頭 10 件を順番に検索して合計時間を表示します。100 件の同期測定は 90 秒を超えても実行中だったため、テストは短い比較用にしています。async 側も同じ条件で比較できます。
