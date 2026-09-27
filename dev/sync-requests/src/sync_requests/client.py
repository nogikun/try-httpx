from collections.abc import Sequence
from urllib.parse import urlencode
from urllib.request import urlopen

from sync_requests.schema.input import TrackQuery


def get_tracks(
    base_url: str,
    queries: Sequence[TrackQuery],
    timeout: float = 30.0,
) -> list[str]:
    endpoint = f"{base_url.rstrip('/')}/tracks"
    results = []

    for query in queries:
        url = f"{endpoint}?{urlencode(query.model_dump(exclude_none=True))}"
        with urlopen(url, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            results.append(response.read().decode(charset))

    return results
