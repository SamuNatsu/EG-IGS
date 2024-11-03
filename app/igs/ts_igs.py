from . import IGS, H_TREE, P_TREE
from ..oracles import Oracle
from ..utils.message import MessageBuilder
from ..utils.tree import find_next, target_sensitive_binary_search

from treelib import Tree
from typing import AsyncGenerator, Self


# IGS
class TargetSensitiveIGS(IGS):
  def __init__(
    self: Self,
    *,
    as_module: bool | None = None,
    hierarchy: Tree | None = None,
    path_tree: Tree | None = None,
  ):
    self.as_module = as_module or False
    self.hierarchy = hierarchy or H_TREE
    self.path_tree = path_tree or P_TREE
    self.target = None

  async def search(
    self: Self, oracle: Oracle, entity: str
  ) -> AsyncGenerator[str, None]:
    if not self.as_module:
      yield MessageBuilder().event("desc").data(entity).build()

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
          yield (
            MessageBuilder()
            .event("res")
            .data({"cost": oracle.get_total_cost(), "target": path[0]})
            .build()
          )
        break

      # Binary search deepest YES
      yield (
        MessageBuilder()
        .event("dbg")
        .title("Target sensitive binary search")
        .path(path)
        .build()
      )
      async for res1 in target_sensitive_binary_search(
        self.hierarchy, path, 0, len(path), oracle, entity
      ):
        if res1[0]:  # Finished
          # Find next YES
          flag: bool = False
          yield (
            MessageBuilder()
            .event("dbg")
            .title("Find next")
            .children(self.hierarchy, res1[1])
            .build()
          )
          async for res2 in find_next(
            self.hierarchy, res1[1], oracle, entity, ignore=path
          ):
            if res2[0]:  # Finished
              if res2[1] is None:  # Not found next node
                if self.as_module:
                  self.target = res1[1]
                else:
                  yield (
                    MessageBuilder()
                    .event("res")
                    .data(
                      {"cost": oracle.get_total_cost(), "target": res1[1].identifier}
                    )
                    .build()
                  )
                return
              else:  # Found next node
                for v in self.path_tree.all_nodes_itr():
                  if res2[1].identifier in v.data:
                    path = v.data
                    break
                flag = True
                break
            else:  # Not finished
              yield MessageBuilder().event("msg").data(res2[1]).build()

          # Has new path
          if flag:
            break
        else:  # Not finished
          yield MessageBuilder().event("msg").data(res1[1]).build()
