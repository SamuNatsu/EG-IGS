import json
import logging
import re

from aiohttp import ClientSession
from bs4 import BeautifulSoup, ResultSet, Tag
from typing import Any


# Constants
HEADERS: dict[str, str] = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}
KEYWORDS: list[str] = ["Product description", "About this item"]
CLOTHING_SELECTOR: str = "#productFactsDesktopExpander :first-child"
BOOK_SELECTOR: str = "#bookDescription_feature_div"

# Logger
logger: logging.Logger = logging.getLogger("uvicorn.error")

# Functions
def extract_desc_1(soup: BeautifulSoup) -> str | None:      # Extractor for general
  text: str = soup.get_text()
  lines: list[str] = text.split("\n")
  lines: list[str] = [line for line in lines if line != ""]

  for line in lines:
    for keyword in KEYWORDS:
      if line.find(keyword) >= 0 and len(line) > 50:
        return line.strip()
  return None

def extract_desc_2(soup: BeautifulSoup) -> str | None:       # Extractor for clothing
  tag: ResultSet[Tag] = soup.select(CLOTHING_SELECTOR, limit=1)
  if len(tag) == 0:
    return None

  text: str = tag[0].get_text()
  pos: int = text.find("About this item")
  text = text[pos:].replace("\n", "").strip()
  return text if len(text) > 50 else None

def extract_desc_3(soup: BeautifulSoup) -> str | None:      # Extractor for books
  tag: ResultSet[Tag] = soup.select(BOOK_SELECTOR, limit=1)
  if len(tag) == 0:
    return None

  text: str = tag[0].get_text()[:2000]
  return text if len(text) > 50 else None

async def fetch_amazon_description(url: str) -> str | None:
  try:
    async with ClientSession() as s:
      async with s.get(url, headers=HEADERS, allow_redirects=True) as r:
        html: str = await r.text()
        soup: BeautifulSoup = BeautifulSoup(html, "html.parser")
        return (
          extract_desc_1(soup) or
          extract_desc_2(soup) or
          extract_desc_3(soup)
        )
  except Exception as e:
    logger.error(e)
    return None

def create_sse_msg(event: str, data: Any) -> str:
  return f"event: {event}\ndata: {json.dumps(data)}\n\n"
