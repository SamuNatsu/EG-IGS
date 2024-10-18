from . import IGS, H_TREE
from ..oracles import Oracle
from ..utils import create_sse_msg

from treelib import Node
from typing import AsyncGenerator, Self


class IGSBruteForce(IGS):
  async def search(self: Self, oracle: Oracle, entity: str) -> AsyncGenerator[str, None]:
    yield create_sse_msg("desc", entity)

    u: str = H_TREE.root
    while True:
      children: list[Node] = H_TREE.children(u)
      found: bool = False
      for v in children:
        if u == H_TREE.root:
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
        yield create_sse_msg(
          "result",
          { "cost": oracle.get_total_cost(), "target": u }
        )
        return
