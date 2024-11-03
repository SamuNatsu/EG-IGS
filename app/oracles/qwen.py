import asyncio
import logging

from . import Oracle
from dashscope.aigc.generation import AioGeneration
from dashscope.api_entities.dashscope_response import GenerationResponse
from typing import Self


# Logger
logger: logging.Logger = logging.getLogger("uvicorn.error")


# Oracle
class QwenOracle(Oracle):
  def __init__(self: Self, *, api_key: str, model: str):
    self.api_key = api_key
    self.model = model
    self.cost = 0
    self.cache = {"root": True}

  async def ask(self: Self, entity: str, concept: str) -> tuple[bool, str]:
    logger.info(f"[QwenOracle:{self.model}] Ask: concept={concept}")

    if concept in self.cache:
      return (
        self.cache[concept],
        f"Is it an item in category {concept}? [Cached Answer]\n[Please see before]",
      )
    self.cost += 1

    msg: str = f'{entity}. Based on the description above, is it an item in category {concept}? Please start with "Yes" or "No" to answer the question, then follows your reason.'
    failed: int = 0
    while True:
      try:
        response: GenerationResponse = await AioGeneration.call(
          api_key=self.api_key,
          model=self.model,
          messages=[
            {
              "role": "system",
              "content": "You are a helpful assistant. You should respond to the user in English.",
            },
            {"role": "user", "content": msg},
          ],
          result_format="message",
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
        failed += 1
        if failed > 5:
          raise Exception("Fail to retry asking")
        await asyncio.sleep(1)

    reply: str = response.output.choices[0].message.content
    result: bool = reply.find("Yes") >= 0

    self.cache[concept] = result
    return (result, f"Is it an item in category {concept}?\n{reply}")

  async def multi_ask(
    self: Self, entity: str, concepts: list[str]
  ) -> tuple[list[bool], str]:
    logger.info(f"[QwenOracle:{self.model}] Multi Ask: concepts={", ".join(concepts)}")

    ret: list[bool | None] = [None] * len(concepts)
    ask: list[str] = []
    pos: list[int] = []
    for i in range(len(concepts)):
      if concepts[i] in self.cache:
        ret[i] = self.cache[concepts[i]]
      else:
        ask.append(concepts[i])
        pos.append(i)
    if len(ask) == 0:
      return (
        ret,
        f"Is it an item in category {", ".join(concepts)}? [Full Cached Answer]\n{", ".join(map(str, ret))}",
      )
    self.cost += 1

    msg: str = f"{entity}. Based on the description above, is it an item in category {", ".join(map(lambda x: f"\"{x}\"", ask))} respectively? Please output the answer of each category with a \"Yes\" or \"No\", split them with a line break."
    failed: int = 0
    while True:
      try:
        response: GenerationResponse = await AioGeneration.call(
          api_key=self.api_key,
          model=self.model,
          messages=[
            {
              "role": "system",
              "content": "You are a helpful assistant. You should respond to the user in English.",
            },
            {"role": "user", "content": msg},
          ],
          result_format="message",
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
        failed += 1
        if failed > 5:
          raise Exception("Fail to retry asking")
        await asyncio.sleep(1)

    replies: list[str] = response.output.choices[0].message.content.splitlines()
    results: list[bool] = list(map(lambda x: x.find("Yes") >= 0, replies))

    for i in range(len(ask)):
      ret[pos[i]] = results[i]

    return (
      ret,
      f"Is it an item in category {", ".join(concepts)}?{"" if len(ask) == len(concepts) else " [Partial Cached Answer]"}\n{", ".join(map(str, ret))}",
    )

  def get_total_cost(self: Self):
    return self.cost
