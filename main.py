import asyncio

from dotenv import load_dotenv

load_dotenv()

from matcher.extract import run as extract


def main() -> None:
    asyncio.run(extract())


if __name__ == "__main__":
    main()
