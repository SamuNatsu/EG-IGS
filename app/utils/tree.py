import os

from ..oracles import Oracle

from treelib import Node, Tree
from typing import Any, AsyncGenerator, Literal


# Types
type Finished    = tuple[Literal[True], Node | None]
type NotFinished = tuple[Literal[False], dict[str, Any]]

# Functions
def decompose(t: Tree) -> Tree:
  p: Tree = Tree()
  stk: list[str] = [t.root]
  acc: int = 1
  pth: list[str] = []

  while len(stk) > 0:
    # Pop stack
    u: str = stk.pop()
    if len(pth) == 0:
      pth.append(u)

    # Maintain path tree
    if len(t.children(u)) == 0:
      if len(p.nodes) == 0:
        p.create_node(identifier=acc, data=pth)
      else:
        tmp: str = t.parent(pth[0]).identifier
        for v in p.all_nodes_itr():
          if tmp in v.data:
            pnt: Node = v
            break
        p.create_node(identifier=acc, data=pth, parent=pnt.identifier)
      acc += 1
      pth = []
      continue

    # Find heavy child
    mxs: int = 0
    mxn: str | None = None
    for v in t.children(u):
      sz: int = len(t.subtree(v.identifier))
      if mxs < sz:
        mxs = sz
        mxn = v.identifier

    # Maintain recursive stack
    for v in t.children(u):
      if v.identifier != mxn:
        stk.append(v.identifier)
    stk.append(mxn)
    pth.append(mxn)

  return p

async def find_next(
  t: Tree,
  u: Node,
  oracle: Oracle,
  entity: str,
  ignore: list[str] | None = None,
  children: list[Node] | None = None
) -> AsyncGenerator[Finished | NotFinished, None]:
  for v in children or t.children(u.identifier):
    if ignore is not None and v.identifier in ignore:
      continue

    res, msg = await oracle.ask(entity, v.identifier)
    yield (False, { "result": res, "msg": msg })

    if res:
      yield (True, v)
      return

  yield (True, None)

async def binary_search(
  t: Tree,
  path: list[str],
  left: int,
  right: int,
  oracle: Oracle,
  entity: str
) -> AsyncGenerator[Finished | NotFinished, None]:
  while left < right:
    mid: int = (left + right) >> 1
    result, msg = await oracle.ask(entity, path[mid])
    yield (False, { "result": result, "msg": msg })

    if result:
      left = mid + 1
    else:
      right = mid

  yield (True, t.get_node(path[left - 1]))

async def target_sensitive_binary_search(
  t: Tree,
  path: list[str],
  left: int,
  right: int,
  oracle: Oracle,
  entity: str
) -> AsyncGenerator[Finished | NotFinished, None]:
  i: int = 1
  flag: bool = False
  while left < right:
    if right - left == 1:
      break

    nxt: int = min(left + (1 << i) - 1, right - 1)
    if nxt == right - 1:
      flag = True

    result, msg = await oracle.ask(entity, path[nxt])
    yield (False, { "result": result, "msg": msg })

    if result:
      i += 1
      if flag:
        left = nxt
    else:
      right = nxt
      left += (1 << (i - 1)) - 1
      i = 1
      flag = False

  yield (True, t.get_node(path[left]))

async def target_sensitive_binary_search_ex(
  t: Tree,
  path: list[str],
  left: int,
  right: int,
  oracle: Oracle,
  entity: str
) -> AsyncGenerator[Finished | NotFinished, None]:
  batch: int = int(os.getenv("TARGET_SENSITIVE_BATCH"))

  while left < right:
    if right - left == 1:
      break

    concepts: list[dict[str, Any]] = []
    i: int = 1
    while True:
      pos: int = min(left + (1 << i) - 1, right - 1)
      concepts.append({ "pos": pos, "i": i })
      i += 1
      if pos == right - 1:
        break

    chunks: list[list[dict[str, Any]]] = []
    for i in range(0, len(concepts), batch):
      chunks.append(concepts[i:i + batch])

    flag: bool = True
    for chunk in chunks:
      asks: list[str] = list(map(lambda x: path[x["pos"]], chunk))
      results, msg = await oracle.multi_ask(entity, asks)
      yield (False, { "msg": msg })

      if all(results):
        continue

      tmp: dict[str, Any] = chunk[results.index(False)]
      right = tmp["pos"]
      left += (1 << (tmp["i"] - 1)) - 1
      flag = False
      break
    if flag:
      yield (True, t.get_node(path[concepts[-1]["pos"]]))
      return

  yield (True, t.get_node(path[left]))

def get_promising_question_tree(
  t: Tree,
  examples: list[tuple[float, str]]
) -> Tree:
  pqt: Tree = Tree()
  pqt.create_node(identifier=t.root, data=0)

  for similarity, example in examples:
    v: Node = t.get_node(example)
    path: list[str] = [v.identifier]
    while v.identifier != t.root:
      u: Node = t.parent(v.identifier)
      path.append(u.identifier)
      v = u
    path = list(reversed(path))

    for x in path:
      if x in pqt.nodes:
        u: Node = pqt.get_node(x)
        if u.data < similarity:
          u.data = similarity
        continue
      p: Node = t.parent(x)
      pqt.create_node(identifier=x, parent=p.identifier, data=similarity)

  return pqt

def compress_promising_question_tree(pqt: Tree) -> Tree:
  cpqt: Tree = Tree(pqt, deep=True)
  for u in cpqt.all_nodes():
    if u.identifier not in cpqt.nodes:
      continue
    if u.identifier == cpqt.root:
      continue
    children_cnt: int = len(cpqt.children(u.identifier))
    if children_cnt == 0 or children_cnt >= 2:
      continue
    cpqt.link_past_node(u.identifier)

  return cpqt
