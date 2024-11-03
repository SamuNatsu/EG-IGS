from . import IGS, H_TREE, P_TREE
from ..oracles import Oracle
from ..utils.message import MessageBuilder
from ..utils.tree import binary_search, find_next

from typing import AsyncGenerator, Self


# IGS
class StateOfTheArtIGS(IGS):
  async def search(
    self: Self, oracle: Oracle, entity: str
  ) -> AsyncGenerator[str, None]:
    yield MessageBuilder().event("desc").data(entity).build()

    # Get initial path
    for v in P_TREE.all_nodes_itr():
      if H_TREE.root in v.data:
        path: list[str] = v.data
        break

    while True:
      # The path only contains one node
      if len(path) == 1:
        yield (
          MessageBuilder()
          .event("res")
          .data({"cost": oracle.get_total_cost(), "target": path[0]})
          .build()
        )
        break

      # Binary search deepest YES
      yield (MessageBuilder().event("dbg").title("Binary search").path(path).build())
      async for res1 in binary_search(H_TREE, path, 1, len(path), oracle, entity):
        if res1[0]:  # Finished
          # Find next YES
          flag: bool = False
          yield (
            MessageBuilder()
            .event("dbg")
            .title("Find next")
            .children(H_TREE, res1[1])
            .build()
          )
          async for res2 in find_next(H_TREE, res1[1], oracle, entity, ignore=path):
            if res2[0]:  # Finished
              if res2[1] is None:  # Not found next node
                yield (
                  MessageBuilder()
                  .event("res")
                  .data({"cost": oracle.get_total_cost(), "target": res1[1].identifier})
                  .build()
                )
                return
              else:  # Found next node
                for v in P_TREE.all_nodes_itr():
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
