import asyncio

from dotenv import load_dotenv

load_dotenv()

from matcher.extract import run as extract
from matcher.embed import build as embed

def main() -> None:
    asyncio.run(extract())
    asyncio.run(embed())


if __name__ == "__main__":
    main()
