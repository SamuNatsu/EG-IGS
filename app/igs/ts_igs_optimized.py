from . import IGS, H_TREE, P_TREE
from ..oracles import Oracle
from ..utils.message import create_sse_msg
from ..utils.tree import find_next, target_sensitive_binary_search_ex

from treelib import Tree
from typing import AsyncGenerator, Self


# IGS
class TargetSensitiveIGSOptimized(IGS):
  def __init__(
    self: Self,
    *,
    as_module: bool | None = None,
    hierarchy: Tree | None = None,
    path_tree: Tree | None = None
  ):
    self.as_module = as_module or False
    self.hierarchy = hierarchy or H_TREE
    self.path_tree = path_tree or P_TREE
    self.target = None

  async def search(
    self: Self,
    oracle: Oracle,
    entity: str
  ) -> AsyncGenerator[str, None]:
    if not self.as_module:
      yield create_sse_msg("desc", entity)

    # Get initial path
    for v in self.path_tree.all_nodes_itr():
      if self.hierarchy.root in v.data:
        path: list[str] = v.data
        break

    while True:
      # The path only contains one node
      if len(path) == 1:
        if self.as_module:
          self.target = self.hierarchy.get_node(path[0])
        else:
          yield create_sse_msg(
            "result",
            { "cost": oracle.get_total_cost(), "target": path[0] }
          )
        break

      # Binary search deepest YES
      async for res1 in target_sensitive_binary_search_ex(self.hierarchy, path, 0, len(path), oracle, entity):
        if res1[0]: # Finished
          # Find next YES
          flag: bool = False
          async for res2 in find_next(self.hierarchy, res1[1], oracle, entity, ignore=path):
            if res2[0]: # Finished
              if res2[1] == None: # Not found next node
                if self.as_module:
                  self.target = res1[1]
                else:
                  yield create_sse_msg(
                    "result",
                    {
                      "cost": oracle.get_total_cost(),
                      "target": res1[1].identifier
                    }
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
