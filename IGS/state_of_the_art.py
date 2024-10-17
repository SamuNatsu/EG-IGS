from . import IGS, H_TREE, P_TREE
from ..oracles import Oracle
from ..utils import create_sse_msg

from treelib import Node
from typing import Any, AsyncGenerator, Self


async def _binary_search(
  path: list[str],
  left: int,
  right: int,
  oracle: Oracle,
  entity: str
) -> AsyncGenerator[tuple[False, dict[str, Any]] | tuple[True, int, str], None]:
  cost: int = 0
  while left < right:
    mid: int = (left + right) >> 1
    if path[mid] == H_TREE.root:
      concept: str = path[mid]
    else:
      u: Node = H_TREE.parent(path[mid])
      concept: str = path[mid].replace(f"{u.identifier}-", "")

    result, msg = await oracle.ask(entity, concept)
    cost += 1
    yield (False, { "result": result, "msg": msg })

    if result:
      left = mid + 1
    else:
      right = mid

  yield (True, cost, path[left - 1])

class IGSStateOfTheArt(IGS):
  async def search(self: Self, oracle: Oracle, entity: str) -> AsyncGenerator[str, None]:
    yield create_sse_msg("desc", entity)

    for v in P_TREE.all_nodes_itr():
      if H_TREE.root in v.data:
        pth: list[str] = v.data
        break
  
    stop: bool = False
    while not stop:
      async for result in _binary_search(pth, 0, len(pth), oracle, entity):
        if result[0]:
          stop = True
          break
        else:
          yield create_sse_msg("msg", result[1])

    yield create_sse_msg("result", { "cost": -1, "target": "None" })
