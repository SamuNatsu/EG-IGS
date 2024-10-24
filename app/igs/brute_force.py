from . import IGS, H_TREE
from ..oracles import Oracle
from ..utils.message import MessageBuilder
from ..utils.tree import find_next

from treelib import Node, Tree
from typing import AsyncGenerator, Self


# IGS
class BruteForceIGS(IGS):
  def __init__(
    self: Self,
    *,
    as_module: bool | None = False,
    hierarchy: Tree | None = None
  ):
    self.as_module = as_module or False
    self.hierarchy = hierarchy or H_TREE
    self.target = None

  async def search(
    self: Self,
    oracle: Oracle,
    entity: str
  ) -> AsyncGenerator[str, None]:
    if not self.as_module:
      yield MessageBuilder().event("desc").data(entity).build()

    u: Node = self.hierarchy.get_node(self.hierarchy.root)
    flag: bool = True
    while flag:
      yield (
        MessageBuilder()
          .event("dbg")
          .title("Find next")
          .children(self.hierarchy, u)
          .build()
      )
      async for res in find_next(self.hierarchy, u, oracle, entity):
        if res[0]: # Finished
          if res[1] == None: # Not found next node
            flag = False
          else:              # Found next node
            u = res[1]
          break
        else:      # Not finished
          yield MessageBuilder().event("msg").data(res[1]).build()

    if self.as_module:
      self.target = u
    else:
      yield (
        MessageBuilder()
          .event("res")
          .data({ "cost": oracle.get_total_cost(), "target": u.identifier })
          .build()
      )
