import os
import spacy

from . import H_TREE, IGS
from .brute_force import IGSBruteForce
from .ts_igs import TSIGS
from ..oracles import Oracle
from ..utils.data import DOC_MAP, NLP, get_list_of_words
from ..utils.message import create_sse_msg
from ..utils.tree import (
  binary_search,
  compress_promising_question_tree,
  decompose,
  find_next,
  get_promising_question_tree
)

from spacy.tokens.doc import Doc
from treelib import Node, Tree
from typing import AsyncGenerator, Self


# IGS
class EGIGS(IGS):
  def __init__(self) -> None:
    self.tau = float(os.getenv("EG_IGS_TAU"))
    self.k = int(os.getenv("EG_IGS_K"))

  async def search(
    self: Self,
    oracle: Oracle,
    entity: str
  ) -> AsyncGenerator[str, None]:
    yield create_sse_msg("desc", entity)

    # Compute similarity
    desc: str = " ".join(get_list_of_words(entity))
    desc_nlp: Doc = NLP(desc)

    similarity: list[tuple[float, str]] = []
    for k, v in DOC_MAP.items():
      x: float = desc_nlp.similarity(v)
      if x > self.tau:
        similarity.append((x, k))
    similarity = sorted(similarity, key=lambda x: x[0], reverse=True)[:self.k]
    for x in similarity:
      print(x[0], x[1])

    # Get PQT and CPQT
    pqt: Tree = get_promising_question_tree(H_TREE, similarity)
    cpqt: Tree = compress_promising_question_tree(pqt)
    pqt.save2file("./tmp1.txt")
    cpqt.save2file("./tmp2.txt")

    # Brute force find u_cap on CPQT
    base: IGSBruteForce = IGSBruteForce(as_module=True, hierarchy=cpqt)
    async for msg in base.search(oracle, entity):
      yield msg
    u_cap: Node = base.target
    print("u_cap", u_cap.identifier)

    # If reach at leaf
    if u_cap.is_leaf():
      yield create_sse_msg(
        "result",
        { "cost": oracle.get_total_cost(), "target": u_cap.identifier }
      )
      return

    # Find v on PQT
    children: list[Node] = sorted(
      pqt.children(u_cap.identifier),
      key=lambda x: x.data,
      reverse=True
    )
    async for res in find_next(pqt, u_cap, oracle, entity, children=children):
      if res[0]:
        if res[1] == None:
          yield create_sse_msg(
            "result",
            { "cost": oracle.get_total_cost(), "target": u_cap.identifier }
          )
          return
        else:
          v: Node = res[1]
      else:
        yield create_sse_msg("msg", res[1])
    print("v", v.identifier)

    # Find v_cap in CPQT
    children = cpqt.children(u_cap.identifier)
    subs: dict[str, Node] = pqt.subtree(v.identifier).nodes
    maxf: float = 0
    v_cap: Node | None = None
    for child in children:
      if child.identifier in subs and maxf < child.data:
        maxf = child.data
        v_cap = child.identifier
    print("v_cap", v_cap)

    yield create_sse_msg("err", "End")
    return

    # Get path from v to v_cap
    path: list[str] = [maxn]
    while maxn != u.identifier:
      print(path)
      p: Node = pqt.parent(maxn)
      path.append(p.identifier)
      maxn = p.identifier
    print(path)
    path = list(reversed(path))

    async for res in binary_search(pqt, path, 1, len(path), oracle, entity):
      if res[0]:
        u = res[1]
        break
      else:
        yield create_sse_msg("msg", result[1])

    subtree: Tree = H_TREE.subtree(u.identifier)
    base: TSIGS = TSIGS(hierarchy=subtree, path_tree=decompose(subtree))
    async for msg in base.search(oracle, entity):
      yield msg
