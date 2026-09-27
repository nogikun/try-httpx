import asyncio
from collections.abc import Sequence

import httpx

from async_httpx.schema.input import TrackQuery


async def get_tracks(
    base_url: str,
    queries: Sequence[TrackQuery],
    concurrency: int = 10, # 同時実行数
) -> list[str]:
    if concurrency < 1:
        raise ValueError("concurrency must be at least 1")

    endpoint = f"{base_url.rstrip('/')}/tracks"
    semaphore = asyncio.Semaphore(concurrency)
    limits = httpx.Limits(
        max_connections=concurrency,
        max_keepalive_connections=concurrency,
    )

    async with httpx.AsyncClient(timeout=30.0, limits=limits) as client:
        async def get(query: TrackQuery) -> str:
            async with semaphore:
                response = await client.get(
                    endpoint,
                    params=query.model_dump(exclude_none=True),
                )
                response.raise_for_status()
                return response.text

        tasks = [asyncio.create_task(get(query)) for query in queries]
        try:
            return await asyncio.gather(*tasks)
        except BaseException:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            raise
