import os

from . import H_TREE, IGS
from .brute_force import IGSBruteForce
from .ts_igs import TSIGS
from ..oracles import Oracle
from ..utils.data import DOC_MAP, NLP, get_list_of_words
from ..utils.message import create_sse_msg
from ..utils.tree import (
  Finished,
  NotFinished,
  compress_promising_question_tree,
  decompose,
  find_next,
  get_promising_question_tree,
  target_sensitive_binary_search
)

from spacy.tokens.doc import Doc
from treelib import Node, Tree
from typing import AsyncGenerator, Self


# Utils
async def compress_and_find(
  pqt: Tree,
  oracle: Oracle,
  entity: str
) -> AsyncGenerator[Finished | NotFinished, None]:
  # Step 1
  cpqt: Tree = compress_promising_question_tree(pqt)

  # Step 2
  base: IGSBruteForce = IGSBruteForce(as_module=True, hierarchy=cpqt)
  async for msg in base.search(oracle, entity):
    yield (False, { "raw": msg })
  u_cap: Node = base.target

  # Step 3
  if u_cap.is_leaf():
    yield (True, u_cap)
    return

  # Step 4
  children: list[Node] = sorted(
    pqt.children(u_cap.identifier),
    key=lambda x: x.data,
    reverse=True
  )
  async for res in find_next(pqt, u_cap, oracle, entity, children=children):
    if res[0]:
      if res[1] == None:
        yield (True, u_cap)
        return
      else:
        v: Node = res[1]
    else:
      yield (False, res[1])

  children = cpqt.children(u_cap.identifier)
  subs: dict[str, Node] = pqt.subtree(v.identifier).nodes
  maxf: float = 0
  v_cap: Node | None = None
  for child in children:
    if child.identifier in subs and maxf < child.data:
      maxf = child.data
      v_cap = child

  path: list[str] = [v_cap.identifier]
  while v_cap.identifier != v.identifier:
    p: Node = pqt.parent(v_cap.identifier)
    path.append(p.identifier)
    v_cap = p
  path = list(reversed(path))

  async for res in target_sensitive_binary_search(pqt, path, 0, len(path), oracle, entity):
    if res[0]:
      yield (True, res[1])
      break
    else:
      yield (False, res[1])

# IGS
class EGIGSOptimized(IGS):
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

    # Get PQT
    pqt: Tree = get_promising_question_tree(H_TREE, similarity)

    # Compress and find
    async for res in compress_and_find(pqt, oracle, entity):
      if res[0]:
        u: Node = res[1]
      elif res[1].get("raw") != None:
        yield res[1]["raw"]
      else:
        yield create_sse_msg("msg", res[1])

    # Find in subtree
    print("u", u.identifier)
    subtree: Tree = H_TREE.subtree(u.identifier)
    base: TSIGS = TSIGS(
      as_module=True,
      hierarchy=subtree,
      path_tree=decompose(subtree)
    )
    async for msg in base.search(oracle, entity):
      yield msg

    yield create_sse_msg(
      "result",
      { "cost": oracle.get_total_cost(), "target": base.target.identifier }
    )