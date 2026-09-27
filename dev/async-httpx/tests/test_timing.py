import asyncio
import os
from pathlib import Path
from time import perf_counter

import pandas as pd
from dotenv import load_dotenv

from async_httpx.core.httpx_client import get_tracks
from async_httpx.schema.input import TrackQuery

PROJECT_DIR = Path(__file__).resolve().parents[1]


def test_input_workbook_concurrent_duration() -> None:
    load_dotenv(PROJECT_DIR / ".env")
    base_url = os.getenv("endpoint", "http://localhost:8000")
    if "://" not in base_url:
        base_url = f"http://{base_url}"
    frame = pd.read_excel(
        PROJECT_DIR / "sample" / "input.xlsx",
        sheet_name="Sheet1",
        engine="openpyxl",
    )
    words = frame["word"].dropna().astype(str).head(10)
    queries = [TrackQuery(q=word) for word in words]

    started = perf_counter()
    results = asyncio.run(get_tracks(base_url, queries, concurrency=10))
    elapsed = perf_counter() - started

    assert len(results) == len(queries)
    print(f"async-httpx: {len(results)} requests in {elapsed:.3f}s (concurrency=10)")
