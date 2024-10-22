import json

from typing import Any


def create_sse_msg(event: str, data: Any) -> str:
  return f"event: {event}\ndata: {json.dumps(data)}\n\n"
