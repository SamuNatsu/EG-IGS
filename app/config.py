import dotenv
import os

from .igs import IGS
from .igs.brute_force import BruteForceIGS
from .igs.state_of_the_art import StateOfTheArtIGS
from .igs.ts_igs import TargetSensitiveIGS
from .igs.eg_igs import ExampleGuidedIGS
from .igs.ts_igs_optimized import TargetSensitiveIGSOptimized
from .igs.eg_igs_optimzed import ExampleGuidedIGSOptimized

from .oracles import Oracle
from .oracles.qwen import QwenOracle
from .oracles.chat_gpt import ChatGPTOracle

from typing import Callable


# Load dotenv
dotenv.load_dotenv()

# Supported models
SUPPORTED_MODELS: dict[str, Callable[[], Oracle]] = {
  "qwen-turbo": (
    lambda: QwenOracle(api_key=os.getenv("QWEN_API_KEY"), model="qwen-turbo")
  ),
  "qwen-plus": (
    lambda: QwenOracle(api_key=os.getenv("QWEN_API_KEY"), model="qwen-plus")
  ),
  "gpt-3.5-turbo": (
    lambda: ChatGPTOracle(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-3.5-turbo")
  ),
  "gpt-4o-mini": (
    lambda: ChatGPTOracle(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini")
  ),
  "gpt-4o": (
    lambda: ChatGPTOracle(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o")
  ),
}

# Supported methods
SUPPORTED_METHODS: dict[str, Callable[[], IGS]] = {
  "brute-force": lambda: BruteForceIGS(),
  "state-of-the-art": lambda: StateOfTheArtIGS(),
  "ts-igs": lambda: TargetSensitiveIGS(),
  "eg-igs": lambda: ExampleGuidedIGS(),
  "ts-igs-opt": lambda: TargetSensitiveIGSOptimized(),
  "eg-igs-opt": lambda: ExampleGuidedIGSOptimized(),
}
