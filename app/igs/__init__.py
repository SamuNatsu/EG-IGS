import pickle

from ..oracles import Oracle
from abc import ABC, abstractmethod
from pathlib import Path
from typing import AsyncGenerator, Self
from treelib import Tree


# Preload data
DATA_PATH: Path = Path(__file__).parent.parent / "data"
H_TREE: Tree = pickle.load(open(DATA_PATH / "amazon_hierarchy", "rb"))
P_TREE: Tree = pickle.load(open(DATA_PATH / "amazon_path_tree", "rb"))
E_MAP: dict[str, str] = pickle.load(open(DATA_PATH / "amazon_pre_mined", "rb"))

# Interfaces
class IGS(ABC):
  @abstractmethod
  async def search(
    self: Self,
    oracle: Oracle,
    entity: str
  ) -> AsyncGenerator[str, None]:
    raise NotImplementedError()
