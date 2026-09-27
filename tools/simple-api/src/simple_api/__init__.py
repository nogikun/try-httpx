from pathlib import Path


def main() -> None:
    import uvicorn

    uvicorn.run(
        "simple_api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[str(Path(__file__).resolve().parent)],
    )
