import asyncio
import pickle
import urllib.parse

from aiohttp import ClientSession
from bs4 import BeautifulSoup, ResultSet, Tag
from random import sample
from treelib import Node, Tree
from typing import Any, Coroutine
from utils import HEADERS, fetch_amazon_description, get_list_of_words


# Constants
DATASET: str = "amazon"
T: Tree = pickle.load(open(f"./data/{DATASET}_hierarchy", "rb"))

EXAMPLE_COUNT: int = 400

ITEM_SELECTOR: str = ".s-result-list > div:not([data-asin=\"\"])"

# Async main
async def main():
  # Get examples
  example_cnt: int = EXAMPLE_COUNT
  examples: list[Node] = sample(T.leaves(), example_cnt)

  # Subroutes
  async def search_amazon(keywords: str) -> str:
    q: str = urllib.parse.quote_plus(keywords)
    url: str = f"https://www.amazon.com/s?k={q}"
    async with ClientSession() as s:
      async with s.get(url, headers=HEADERS, allow_redirects=True) as r:
        html: str = await r.text()
        soup: BeautifulSoup = BeautifulSoup(html, "html.parser")
        items: ResultSet[Tag] = soup.select(ITEM_SELECTOR)
        links: list[Tag] = list(map(lambda x: x.select("a")[0], items))
        selection: Tag = sample(links, 1)[0]
        href: str = selection.attrs["href"]
        return f"https://www.amazon.com{href}"

  async def get_amazon_words(keywords: str) -> list[str]:
    url: str = await search_amazon(keywords)
    desc: str = await fetch_amazon_description(url)
    return get_list_of_words(desc)

  def get_concept(leaf: Node) -> str:
    p: str = leaf.predecessor(T.identifier)
    return leaf.identifier.replace(f"{p}-", "")

  # Mine descriptions
  data: dict[str, list[str]] = {}
  failed: set[str] = set()
  async def fetch_task(example: Node) -> None:
    concept: str = get_concept(example)
    retry_cnt: int = 0
    while True:
      try:
        result: list[str] = await get_amazon_words(concept)
        data[example.identifier] = " ".join(result)
        break
      except:
        retry_cnt += 1
        if retry_cnt > 5:
          failed.add(example)
          break
    print(f"Progress {len(data)}/{EXAMPLE_COUNT}, failed: {len(failed)}/{example_cnt}")

  while True:
    print(f"Tasks: {len(examples)}")
    tasks: list[Coroutine[Any, Any, None]] = [
      fetch_task(examples[i]) for i in range(example_cnt)
    ]
    await asyncio.gather(*tasks)

    if len(failed) > 0:
      example_cnt = len(failed)
      while True:
        nexamples: list[str] = sample(T.leaves(), example_cnt)
        if len(set(examples) & set(nexamples)) == 0:
          break
      examples = nexamples
      failed = set()
    else:
      break

  pickle.dump(data, open(f"./{DATASET}_pre_mined", "wb"))

# Main entry
if __name__ == '__main__':
  asyncio.run(main())
