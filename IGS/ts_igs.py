from . import IGS, H_TREE, P_TREE
from ..oracles import Oracle
from ..utils.message import create_sse_msg
from ..utils.tree import find_next, target_sensitive_binary_search

from treelib import Tree
from typing import AsyncGenerator, Self


# IGS
class TSIGS(IGS):
  def __init__(self: Self, *, hierarchy: Tree = None, path_tree: Tree = None):
    self.hierarchy = hierarchy or H_TREE
    self.path_tree = path_tree or P_TREE

  async def search(
    self: Self,
    oracle: Oracle,
    entity: str
  ) -> AsyncGenerator[str, None]:
    yield create_sse_msg("desc", entity)

    # Get initial path
    for v in self.path_tree.all_nodes_itr():
      if self.hierarchy.root in v.data:
        path: list[str] = v.data
        break

    while True:
      # The path only contains one node
      if len(path) == 1:
        yield create_sse_msg(
          "result",
          { "cost": oracle.get_total_cost(), "target": path[0] }
        )
        break

      # Binary search deepest YES
      async for res1 in target_sensitive_binary_search(self.hierarchy, path, 0, len(path), oracle, entity):
        if res1[0]: # Finished
          # Find next YES
          flag: bool = False
          async for res2 in find_next(self.hierarchy, res1[1], oracle, entity, ignore=path):
            if res2[0]: # Finished
              if res2[1] == None: # Not found next node
                yield create_sse_msg(
                  "result",
                  { "cost": oracle.get_total_cost(), "target": res1[1].identifier }
                )
                return
              else:               # Found next node
                for v in self.path_tree.all_nodes_itr():
                  if res2[1].identifier in v.data:
                    path = v.data
                    break
                flag = True
                break
            else:       # Not finished
              yield create_sse_msg("msg", res2[1])

          # Has new path
          if flag:
            break
        else:       # Not finished
          yield create_sse_msg("msg", res1[1])
