from .igs import IGS
from .config import SUPPORTED_METHODS, SUPPORTED_MODELS
from .oracles import Oracle
from .utils.amazon import fetch_desc
from .utils.message import create_sse_msg

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pathlib import Path
from typing import Generator


# FastAPI instance
app: FastAPI = FastAPI()

# Routes
@app.get("/api/igs")
async def start_IGS(model: str, method: str, link: str) -> StreamingResponse:
  # Validate parameters
  if model not in SUPPORTED_MODELS:
    def not_support() -> Generator[str, None, None]:
      yield create_sse_msg("err", "Model not supported")
    return StreamingResponse(not_support(), media_type="text/event-stream")
  if method not in SUPPORTED_METHODS:
    def not_support() -> Generator[str, None, None]:
      yield create_sse_msg("err", "Method not supported")
    return StreamingResponse(not_support(), media_type="text/event-stream")

  # Try fetch description
  desc: str | None = await fetch_desc(link)
  if desc == None:
    def no_desc() -> Generator[str, None, None]:
      yield create_sse_msg("err", "Product has no description")
    return StreamingResponse(no_desc(), media_type="text/event-stream")

  # Start searching
  oracle: Oracle = SUPPORTED_MODELS[model]()
  igs: IGS = SUPPORTED_METHODS[method]()
  return StreamingResponse(
    igs.search(oracle, desc),
    media_type="text/event-stream"
  )

app.mount(
  "/",
  StaticFiles(directory=Path(__file__).parent / "public", html=True)
)
