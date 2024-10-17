import dotenv
import os

from .IGS import IGS
from .IGS.IGS_brute_force import IGSBruteForce

from .oracles import Oracle
from .oracles.qwen import QwenOracle

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
  )
}

# Supported methods
SUPPORTED_METHODS: dict[str, Callable[[], IGS]] = {
  "brute-force": lambda: IGSBruteForce()
}
