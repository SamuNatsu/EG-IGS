import spacy

from . import IGS, E_MAP, H_TREE
from .brute_force import IGSBruteForce
from .ts_igs import TSIGS
from ..oracles import Oracle
from ..utils.data import get_list_of_words
from ..utils.message import create_sse_msg
from ..utils.tree import decompose

from spacy import Language
from spacy.tokens.doc import Doc
from treelib import Node, Tree
from typing import Any, AsyncGenerator, Literal, Self


# Types
type NodeFound = tuple[Literal[True], str]
type NodeNotFound = tuple[Literal[False], dict[str, Any]]

# Constants
TAU: float = 0.8
K: int = 20

# Utils
def _get_promising_question_tree(leaves: list[tuple[float, str]]) -> Tree:
  pqt: Tree = Tree()
  pqt.create_node(identifier=H_TREE.root, data=0)

  for leaf in leaves:
    v: Node = H_TREE.get_node(leaf[1])
    path: list[str] = [v.identifier]
    while v.identifier != H_TREE.root:
      u: Node = H_TREE.parent(v.identifier)
      path.append(u.identifier)
      v = u
    path = list(reversed(path))

    for x in path:
      if x in pqt.nodes:
        u: Node = pqt.get_node(x)
        if u.data < leaf[0]:
          u.data = leaf[0]
        continue
      p: Node = H_TREE.parent(x)
      pqt.create_node(identifier=x, parent=p.identifier, data=leaf[0])

  return pqt

def _compress_promising_question_tree(pqt: Tree) -> Tree:
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

async def _binary_search(
  path: list[str],
  left: int,
  right: int,
  hierarchy: Tree,
  oracle: Oracle,
  entity: str
) -> AsyncGenerator[NodeFound | NodeNotFound, None]:
  while left < right:
    mid: int = (left + right) >> 1
    u: Node = hierarchy.parent(path[mid])
    concept: str = path[mid].replace(f"{u.identifier}-", "")

    result, msg = await oracle.ask(entity, path[mid])
    msg = msg.replace(path[mid], concept)
    yield (False, { "result": result, "msg": msg })

    if result:
      left = mid + 1
    else:
      right = mid

  yield (True, path[left - 1])

# IGS
class EGIGS(IGS):
  async def search(self: Self, oracle: Oracle, entity: str) -> AsyncGenerator[str, None]:
    yield create_sse_msg("desc", entity)

    nlp: Language = spacy.load("en_core_web_sm")
    desc: str = " ".join(get_list_of_words(entity))
    desc_nlp: Doc = nlp(desc)

    similarity: list[tuple[float, str]] = []
    for k, v in E_MAP.items():
      v_nlp: Doc = nlp(v)
      x: float = desc_nlp.similarity(v_nlp)
      if x > TAU:
        similarity.append((x, k))
    similarity = sorted(similarity, key=lambda x: x[0], reverse=True)[:K]
    for x in similarity:
      print(x[0], x[1])

    pqt: Tree = _get_promising_question_tree(similarity)
    cpqt: Tree = _compress_promising_question_tree(pqt)
    pqt.save2file("./tmp1.txt")
    cpqt.save2file("./tmp2.txt")

    base: IGSBruteForce = IGSBruteForce(as_module=True, hierarchy=cpqt)
    async for msg in base.search(oracle, entity):
      yield msg

    if len(cpqt.children(base.target)) == 0:
      yield create_sse_msg(
        "result",
        { "cost": oracle.get_total_cost(), "target": base.target }
      )
      return

    u: str = base.target
    found: bool = False
    children: list[Node] = sorted(pqt.children(u), key=lambda x: x.data, reverse=True)
    for v in children:
      if u == pqt.root:
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

    children = cpqt.children(base.target)
    subs: dict[str, Node] = pqt.subtree(u).nodes
    maxf: float = 0
    maxn: str = ""
    for child in children:
      if child.identifier in subs and maxf < child.data:
        maxf = child.data
        maxn = child.identifier

    path: list[str] = [maxn]
    while maxn != u:
      print(path)
      p: Node = pqt.parent(maxn)
      path.append(p.identifier)
      maxn = p.identifier
    print(path)
    path = list(reversed(path))

    async for result in _binary_search(path, 1, len(path), pqt, oracle, entity):
      if result[0]:
        u = result[1]
        break
      else:
        yield create_sse_msg("msg", result[1])

    subtree: Tree = H_TREE.subtree(u)
    base: TSIGS = TSIGS(hierarchy=subtree, path_tree=decompose(subtree))
    async for msg in base.search(oracle, entity):
      yield msg
