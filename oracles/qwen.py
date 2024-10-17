import asyncio
import functools
import logging

from . import Oracle
from dashscope import Generation
from dashscope.api_entities.dashscope_response import GenerationResponse
from typing import Self


# Logger
logger: logging.Logger = logging.getLogger("uvicorn.error")

# Oracle
class QwenOracle(Oracle):
  def __init__(self: Self, *, api_key: str, model: str):
    self.api_key = api_key
    self.model = model

  async def ask(self: Self, entity: str, concept: str) -> tuple[bool, str]:
    if concept == "root":
      return (True, "")

    msg: str = (
      f"{entity}. Based on the description above, is it an item in category {concept}? Please start with \"Yes\" or \"No\" to answer the question, then follows your reason."
    )
    while True:
      try:
        response: GenerationResponse = await (
          asyncio.get_running_loop().run_in_executor(
            None,
            functools.partial(
              Generation.call,
              api_key=self.api_key,
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
              result_format="message"
            )
          )
        )

        if response.status_code != 200:
          raise Exception(f"fail to query: {response.message}")
        if response.output.choices[0].finish_reason != "stop":
          raise Exception(
            f"unexpected finish reason: {response.output.choices[0].finish_reason}"
          )
        break
      except Exception as e:
        logger.error(e)
        await asyncio.sleep(1)

    reply: str = response.output.choices[0].message.content
    return (
      reply.find("Yes") >= 0,
      f"Is it an item in category {concept}?\n{reply}"
    )
