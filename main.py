import asyncio

from dotenv import load_dotenv

load_dotenv()

from matcher.extract import run as extract
from matcher.index import build as embed
from matcher.match import run as match
from matcher.score import run as score

def main() -> None:
    asyncio.run(extract())
    asyncio.run(embed())
    asyncio.run(match())
    asyncio.run(score())


if __name__ == "__main__":
    main()
