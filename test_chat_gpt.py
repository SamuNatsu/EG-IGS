import asyncio
import dotenv
import os

from app.oracles.chat_gpt import ChatGPTOracle


# Load dotenv
dotenv.load_dotenv()

# Constants
ENTITY: str = "It's a cat"
CONCEPT: str = "appliances"

# Async entry
async def main():
  oracle: ChatGPTOracle = ChatGPTOracle(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-3.5-turbo"
  )

  print(await oracle.ask(ENTITY, CONCEPT))

# Main entry
if __name__ == '__main__':
  asyncio.run(main())
