import json

from treelib import Node, Tree
from typing import Any, Self


class MessageBuilder:
  def __init__(self: Self):
    self._event: str | None = None
    self._title: str | None = None
    self._content: Any | None = None

  def event(self: Self, ev: str) -> Self:
    self._event = ev
    return self

  def title(self: Self, title: str) -> Self:
    self._title = title
    return self

  def data(self: Self, data: Any) -> Self:
    self._content = data
    return self

  def path(self: Self, path: list[str]) -> Self:
    self._content = "<br/>".join(path)
    return self

  def children(self: Self, tree: Tree, parent: Node) -> Self:
    self._content = (
      "<br/>".join(map(lambda x: x.identifier,tree.children(parent.identifier)))
    )
    return self
  
  def similarity(self: Self, similarity: list[tuple[float, str]]) -> Self:
    self._content = (
      "<br/>".join(map(lambda x: f"<b>{x[0]}</b> {x[1]}", similarity))
    )
    return self

  def tree(self: Self, tree: Tree) -> Self:
    self._content = "<pre>" + json.dumps(tree.to_dict(), indent=2) + "</pre>"
    return self

  def build(self: Self) -> str:
    assert self._event != None and self._content != None

    packet: dict[str, Any] = { "content": self._content }
    if self._title != None:
      packet["title"] = self._title

    return f"event: {self._event}\ndata: {json.dumps(packet)}\n\n"
