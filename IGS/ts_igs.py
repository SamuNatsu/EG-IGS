from . import IGS, H_TREE, P_TREE
from ..oracles import Oracle
from ..utils import create_sse_msg

from treelib import Node
from typing import Any, AsyncGenerator, Literal, Self


# Types
type NodeFound = tuple[Literal[True], str]
type NodeNotFound = tuple[Literal[False], dict[str, Any]]

# Utils
async def _ts_binary_search(
  path: list[str],
  left: int,
  right: int,
  oracle: Oracle,
  entity: str
) -> AsyncGenerator[NodeFound | NodeNotFound, None]:
  while left < right:
    mid: int = (left + right) >> 1
    u: Node = H_TREE.parent(path[mid])
    concept: str = path[mid].replace(f"{u.identifier}-", "")

    result, msg = await oracle.ask(entity, path[mid])
    msg = msg.replace(path[mid], concept)
    yield (False, { "result": result, "msg": msg })

    if result:
      left = mid + 1
    else:
      right = mid

  yield (True, path[left - 1])

async def _find_next(
  u: str,
  path: list[str],
  oracle: Oracle,
  entity: str
) -> AsyncGenerator[NodeFound | NodeNotFound, None]:
  for v in H_TREE.children(u):
    if v.identifier in path:
      continue
    concept: str = v.identifier.replace(f"{u}-", "")

    result, msg = await oracle.ask(entity, v.identifier)
    msg = msg.replace(v.identifier, concept)
    yield (False, { "result": result, "msg": msg })

    if result:
      yield (True, v.identifier)
      break

# Oracle
class TSIGS(IGS):
  async def search(self: Self, oracle: Oracle, entity: str) -> AsyncGenerator[str, None]:
    yield create_sse_msg("desc", entity)

    # Get initial path
    for v in P_TREE.all_nodes_itr():
      if H_TREE.root in v.data:
        pth: list[str] = v.data
        break

    while True:
      # The path only contains one node
      if len(pth) == 1:
        yield create_sse_msg(
          "result",
          { "cost": oracle.get_total_cost(), "target": pth[0] }
        )
        break

      async for result in _ts_binary_search(pth, 1, len(pth), oracle, entity):
        if result[0]: # If binary found
          # Find next YES child
          flag: bool = False
          async for rnext in _find_next(result[1], pth, oracle, entity):
            if rnext[0]: # If child found
              # Update current path
              for v in P_TREE.all_nodes_itr():
                if rnext[1] in v.data:
                  pth = v.data
                  break
              flag = True
              break
            else:
              yield create_sse_msg("msg", rnext[1])
          if flag:
            break

          # Not found
          yield create_sse_msg(
            "result",
            { "cost": oracle.get_total_cost(), "target": result[1] }
          )
          return
        else:
          yield create_sse_msg("msg", result[1])