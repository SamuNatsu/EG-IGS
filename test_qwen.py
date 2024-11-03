import asyncio
import dotenv
import os

from app.oracles.qwen import QwenOracle


# Load dotenv
dotenv.load_dotenv()

# Constants
ENTITY: str = "It's a cat"
CONCEPT: str = "appliances"
CONCEPTS: list[str] = ["animal", "mammal", "virus", "plants"]


# Async entry
async def main():
  oracle: QwenOracle = QwenOracle(api_key=os.getenv("QWEN_API_KEY"), model="qwen-turbo")

  print(await oracle.ask(ENTITY, CONCEPT))
  print(await oracle.multi_ask(ENTITY, CONCEPTS))


# Main entry
if __name__ == "__main__":
  asyncio.run(main())
