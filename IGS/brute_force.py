from . import IGS, H_TREE
from ..oracles import Oracle
from ..utils.message import create_sse_msg

from treelib import Node, Tree
from typing import AsyncGenerator, Self


# IGS
class IGSBruteForce(IGS):
  def __init__(self: Self, *, as_module: bool = False, hierarchy: Tree = None):
    self.as_module = as_module
    self.hierarchy = hierarchy or H_TREE
    self.target = None

  async def search(self: Self, oracle: Oracle, entity: str) -> AsyncGenerator[str, None]:
    if not self.as_module:
      yield create_sse_msg("desc", entity)

    u: str = self.hierarchy.root
    while True:
      children: list[Node] = self.hierarchy.children(u)
      found: bool = False
      for v in children:
        if u == self.hierarchy.root:
          concept: str = v.identifier
        else:
          concept: str = v.identifier.replace(f"{u}-", "")

        result, msg = await oracle.ask(entity, v.identifier)
        msg = msg.replace(v.identifier, concept)
        yield create_sse_msg("msg", { "result": result, "msg": msg })

        if result:
          u = v.identifier
          found = True
          break

      if not found:
        if self.as_module:
          self.target = u
        else:
          yield create_sse_msg(
            "result",
            { "cost": oracle.get_total_cost(), "target": u }
          )
        return
