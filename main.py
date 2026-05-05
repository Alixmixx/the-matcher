import asyncio

from dotenv import load_dotenv

load_dotenv()

from matcher.extract import run as extract
from matcher.embed import build as embed
from matcher.match import run as match

def main() -> None:
    asyncio.run(extract())
    asyncio.run(embed())
    asyncio.run(match())


if __name__ == "__main__":
    main()
