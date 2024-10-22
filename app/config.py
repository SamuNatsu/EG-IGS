import dotenv
import os

from .igs import IGS
from .igs.brute_force import IGSBruteForce
from .igs.state_of_the_art import IGSStateOfTheArt
from .igs.ts_igs import TSIGS
from .igs.eg_igs import EGIGS
from .igs.eg_igs_optimzed import EGIGSOptimized

from .oracles import Oracle
from .oracles.qwen import QwenOracle
from .oracles.chat_gpt import ChatGPTOracle

from typing import Callable


# Load dotenv
dotenv.load_dotenv()

# Supported models
SUPPORTED_MODELS: dict[str, Callable[[], Oracle]] = {
  "qwen-turbo": (
    lambda: QwenOracle(
      api_key=os.getenv("QWEN_API_KEY"),
      model="qwen-turbo"
    )
  ),
  "qwen-plus": (
    lambda: QwenOracle(
      api_key=os.getenv("QWEN_API_KEY"),
      model="qwen-plus"
    )
  ),
  "gpt-3.5-turbo": (
    lambda: ChatGPTOracle(
      api_key=os.getenv("OPENAI_API_KEY"),
      model="gpt-3.5-turbo"
    )
  ),
  "gpt-4o-mini": (
    lambda: ChatGPTOracle(
      api_key=os.getenv("OPENAI_API_KEY"),
      model="gpt-4o-mini"
    )
  ),
  "gpt-4o": (
    lambda: ChatGPTOracle(
      api_key=os.getenv("OPENAI_API_KEY"),
      model="gpt-4o"
    )
  )
}

# Supported methods
SUPPORTED_METHODS: dict[str, Callable[[], IGS]] = {
  "brute-force": lambda: IGSBruteForce(),
  "state-of-the-art": lambda: IGSStateOfTheArt(),
  "ts-igs": lambda: TSIGS(),
  "eg-igs": lambda: EGIGS(),
  "eg-igs-opt": lambda: EGIGSOptimized()
}
