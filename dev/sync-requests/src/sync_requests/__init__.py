import argparse
import os
from pathlib import Path
import sys
from urllib.error import URLError

import pandas as pd
from dotenv import load_dotenv

from sync_requests.client import get_tracks
from sync_requests.schema.input import TrackQuery

PROJECT_DIR = Path(__file__).resolve().parents[2]


def main() -> None:
    load_dotenv(PROJECT_DIR / ".env")

    parser = argparse.ArgumentParser(description="Search tracks sequentially")
    parser.add_argument(
        "--input",
        type=Path,
        default=PROJECT_DIR / "sample" / "input.xlsx",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_DIR / "sample" / "output.xlsx",
    )
    parser.add_argument(
        "--endpoint",
        default=os.getenv("endpoint", "http://localhost:8000"),
        help="API base URL; /tracks is appended",
    )
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--artist-id", type=int)
    parser.add_argument("--genre-id", type=int)
    args = parser.parse_args()

    if args.input.resolve() == args.output.resolve():
        parser.error("--output must not overwrite --input")

    endpoint = args.endpoint
    if "://" not in endpoint:
        endpoint = f"http://{endpoint}"

    frame = pd.read_excel(args.input, sheet_name="Sheet1", engine="openpyxl")
    if "word" not in frame.columns:
        parser.error("the input sheet must contain a 'word' column")

    rows = frame.index[frame["word"].notna()]
    queries = [
        TrackQuery(
            q=str(word),
            limit=args.limit,
            offset=args.offset,
            artist_id=args.artist_id,
            genre_id=args.genre_id,
        )
        for word in frame.loc[rows, "word"]
    ]

    try:
        results = get_tracks(endpoint, queries)
    except URLError as exc:
        print(f"Request failed: {type(exc).__name__}", file=sys.stderr)
        raise SystemExit(1) from None

    if "res" not in frame.columns:
        frame["res"] = pd.Series(index=frame.index, dtype="object")
    frame.loc[rows, "res"] = results
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_excel(args.output, sheet_name="Sheet1", index=False, engine="openpyxl")
    print(f"Saved results to {args.output}")
