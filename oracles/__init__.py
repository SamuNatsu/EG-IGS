from abc import ABC, abstractmethod
from typing import Self


# Interfaces
class Oracle(ABC):
  @abstractmethod
  async def ask(self: Self, entity: str, concept: str) -> tuple[bool, str]:
    raise NotImplementedError()
