from pydantic import BaseModel, Field


class TrackQuery(BaseModel):
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="1ページの件数 / Items per page",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="読み飛ばす件数 / Number of items to skip",
    )
    q: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="曲名の部分一致キーワード / Partial track-name keyword",
    )
    artist_id: int | None = Field(
        default=None,
        gt=0,
        description="アーティスト ID / Artist ID filter",
    )
    genre_id: int | None = Field(
        default=None,
        gt=0,
        description="ジャンル ID / Genre ID filter",
    )
