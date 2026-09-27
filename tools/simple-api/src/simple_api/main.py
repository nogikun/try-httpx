from contextlib import asynccontextmanager
from pathlib import Path
import sqlite3
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel

PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_DIR / "data"
DATABASE_PATH = DATA_DIR / "chinook.db"
SEED_PATH = DATA_DIR / "chinook.sql"

TRACK_FROM = """
FROM Track AS t
JOIN Album AS al ON al.AlbumId = t.AlbumId
JOIN Artist AS ar ON ar.ArtistId = al.ArtistId
LEFT JOIN Genre AS g ON g.GenreId = t.GenreId
"""
TRACK_FIELDS = """
SELECT t.TrackId AS id, t.Name AS name, al.Title AS album,
       ar.ArtistId AS artist_id, ar.Name AS artist,
       g.GenreId AS genre_id, g.Name AS genre,
       t.Milliseconds AS milliseconds, t.UnitPrice AS unit_price
"""


class Track(BaseModel):
    id: int
    name: str
    album: str
    artist_id: int
    artist: str
    genre_id: int | None
    genre: str | None
    milliseconds: int
    unit_price: float


class TrackPage(BaseModel):
    items: list[Track]
    total: int
    limit: int
    offset: int


def initialize_database() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE_PATH) as db:
        initialized = db.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='Track'"
        ).fetchone()
        if not initialized:
            db.executescript(SEED_PATH.read_text(encoding="utf-8"))


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


def get_db():
    # FastAPI may create, use, and close this request-scoped connection in different worker threads.
    db = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    db.row_factory = sqlite3.Row
    try:
        yield db
    finally:
        db.close()


app = FastAPI(
    title="Chinook 楽曲 API / Chinook Track API",
    description=(
        "Chinook の楽曲データを検索・取得する学習用 API です。\n\n"
        "A learning API for searching and retrieving Chinook track data."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.get(
    "/tracks",
    response_model=TrackPage,
    summary="曲一覧・検索 / List and search tracks",
    description=(
        "曲をページ単位で取得します。`q` は曲名の部分一致検索、"
        "`artist_id` と `genre_id` は任意の絞り込み条件です。\n\n"
        "Returns tracks in pages. `q` performs a partial match on track names; "
        "`artist_id` and `genre_id` are optional filters."
    ),
    response_description="曲の一覧とページ情報 / Track items and pagination details",
)
def list_tracks(
    db: Annotated[sqlite3.Connection, Depends(get_db)],
    limit: Annotated[
        int, Query(ge=1, le=100, description="1ページの件数 / Items per page")
    ] = 20,
    offset: Annotated[
        int, Query(ge=0, description="読み飛ばす件数 / Number of items to skip")
    ] = 0,
    q: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=100,
            description="曲名の部分一致キーワード / Partial track-name keyword",
        ),
    ] = None,
    artist_id: Annotated[
        int | None,
        Query(gt=0, description="アーティスト ID / Artist ID filter"),
    ] = None,
    genre_id: Annotated[
        int | None,
        Query(gt=0, description="ジャンル ID / Genre ID filter"),
    ] = None,
) -> TrackPage:
    filters = []
    params: list[object] = []
    if q:
        filters.append("t.Name LIKE ?")
        params.append(f"%{q}%")
    if artist_id is not None:
        filters.append("ar.ArtistId = ?")
        params.append(artist_id)
    if genre_id is not None:
        filters.append("g.GenreId = ?")
        params.append(genre_id)
    where = f"WHERE {' AND '.join(filters)}" if filters else ""

    total = db.execute(
        f"SELECT COUNT(*) {TRACK_FROM} {where}", params
    ).fetchone()[0]
    rows = db.execute(
        f"{TRACK_FIELDS} {TRACK_FROM} {where} ORDER BY t.TrackId LIMIT ? OFFSET ?",
        [*params, limit, offset],
    )
    return TrackPage(
        items=[Track(**dict(row)) for row in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@app.get(
    "/tracks/{track_id}",
    response_model=Track,
    summary="曲の詳細取得 / Get a track",
    description=(
        "ID を指定して曲を 1 件取得します。該当する曲がない場合は 404 を返します。\n\n"
        "Returns one track by ID. Returns 404 when the track does not exist."
    ),
    response_description="曲の詳細 / Track details",
    responses={404: {"description": "曲が見つかりません / Track not found"}},
)
def get_track(
    track_id: int,
    db: Annotated[sqlite3.Connection, Depends(get_db)],
) -> Track:
    row = db.execute(
        f"{TRACK_FIELDS} {TRACK_FROM} WHERE t.TrackId = ?", (track_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Track not found")
    return Track(**dict(row))
