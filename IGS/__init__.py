import pickle

from ..oracles import Oracle
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Self
from treelib import Tree


# Preload data
H_TREE: Tree = pickle.load(open("./data/amazon_hierarchy", "rb"))
P_TREE: Tree = pickle.load(open("./data/amazon_path_tree", "rb"))
E_MAP: dict[str, str] = pickle.load(open("./data/amazon_pre_mined", "rb"))

# Interfaces
class IGS(ABC):
  @abstractmethod
  async def search(self: Self, oracle: Oracle, entity: str) -> AsyncGenerator[str, None]:
    raise NotImplementedError()
