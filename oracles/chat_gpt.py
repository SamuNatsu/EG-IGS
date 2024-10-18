import asyncio
import logging

from . import Oracle
from openai import AsyncOpenAI
from openai.types.chat.chat_completion import ChatCompletion
from typing import Self


# Logger
logger: logging.Logger = logging.getLogger("uvicorn.error")

# Oracle
class ChatGPTOracle(Oracle):
  def __init__(self: Self, *, api_key: str, model: str):
    self.model = model
    self.cost = 0
    self.client = AsyncOpenAI(api_key=api_key)

  async def ask(self: Self, entity: str, concept: str) -> tuple[bool, str]:
    logger.info(f"[ChatGPT:{self.model}] Ask: concept={concept}")
    self.cost += 1

    if concept == "root":
      return (True, "")

    msg: str = (
      f"{entity}. Based on the description above, is it an item in category {concept}? Please start with \"Yes\" or \"No\" to answer the question, then follows your reason."
    )
    failed: int = 0
    while True:
      try:
        completion: ChatCompletion = await self.client.chat.completions.create(
          model=self.model,
          messages=[
            {
              "role": "system",
              "content": "You are a helpful assistant. You should respond to the user in English."
            },
            {
              "role": "user",
              "content": msg
            }
          ],
        )
        break
      except Exception as e:
        logger.error(e)
        failed += 1
        if failed > 5:
          raise Exception("Fail to retry asking")
        await asyncio.sleep(1)

    reply: str = completion.choices[0].message.content
    return (
      reply.find("Yes") >= 0,
      f"Is it an item in category {concept}?\n{reply}"
    )
  
  def get_total_cost(self: Self):
    return self.cost
