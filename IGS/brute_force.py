from . import IGS, H_TREE
from ..oracles import Oracle
from ..utils.message import create_sse_msg
from ..utils.tree import find_next

from treelib import Node, Tree
from typing import AsyncGenerator, Self


# IGS
class IGSBruteForce(IGS):
  def __init__(self: Self, *, as_module: bool = False, hierarchy: Tree = None):
    self.as_module = as_module
    self.hierarchy = hierarchy or H_TREE
    self.target = None

  async def search(
    self: Self,
    oracle: Oracle,
    entity: str
  ) -> AsyncGenerator[str, None]:
    if not self.as_module:
      yield create_sse_msg("desc", entity)

    u: Node = self.hierarchy.get_node(self.hierarchy.root)
    flag: bool = True
    while flag:
      async for res in find_next(self.hierarchy, u, oracle, entity):
        if res[0]: # Finished
          if res[1] == None: # Not found next node
            flag = False
          else:              # Found next node
            u = res[1]
          break
        else:      # Not finished
          yield create_sse_msg("msg", res[1])

    if self.as_module:
      self.target = u
    else:
      yield create_sse_msg(
        "result",
        { "cost": oracle.get_total_cost(), "target": u.identifier }
      )

