# simple-api

FastAPI と SQLite で Chinook の楽曲データを取得する学習用 API です。初回起動時に `data/chinook.sql` を `data/chinook.db` へ読み込みます。データは [Chinook Database](https://github.com/lerocha/chinook-database) v1.4.5 で、曲 3,503 件、アーティスト 275 件、アルバム 347 件を含みます。配布元の [MIT License](https://github.com/lerocha/chinook-database/blob/master/LICENSE.md) を `data/LICENSE-Chinook.txt` に同梱しています。

## 起動

```powershell
cd tools/simple-api
uv sync
uv run simple-api
```

コード変更時は自動で再起動します。 / The server automatically reloads when source files change.

Swagger UI (`/docs`) と ReDoc (`/redoc`) の説明は日本語・英語を併記しています。 / The Swagger UI (`/docs`) and ReDoc (`/redoc`) documentation is provided in both Japanese and English.

## エンドポイント / Endpoints

- `GET /tracks?limit=5&offset=0` — 曲一覧をページ指定で取得（`limit`: 1〜100） / List tracks with pagination (`limit`: 1–100).
- `GET /tracks?q=love` — 曲名の部分一致検索 / Search track names by partial match.
- `GET /tracks?artist_id=1&genre_id=1` — アーティストやジャンルで絞り込み / Filter by artist and genre.
- `GET /tracks/1` — ID で曲を 1 件取得（存在しない ID は 404） / Get one track by ID (404 if not found).

一覧レスポンスには `items`, `total`, `limit`, `offset` が含まれ、各曲に `id`, `name`, `artist_id`, `genre_id` などを含みます。 / The list response contains `items`, `total`, `limit`, and `offset`; each track includes fields such as `id`, `name`, `artist_id`, and `genre_id`.

HTTPX リクエスト例 / HTTPX request example:

```python
import httpx

with httpx.Client(base_url="http://127.0.0.1:8000") as client:
    page = client.get(
        "/tracks", params={"q": "love", "limit": 5}
    ).raise_for_status().json()
    print(page["total"], page["items"])
    if page["items"]:
        track = client.get(
            f"/tracks/{page['items'][0]['id']}"
        ).raise_for_status().json()
        print(track)
```
