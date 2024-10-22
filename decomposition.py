import pickle

from treelib import Node, Tree


# Constants
DATASET: str = "amazon"
T: Tree = pickle.load(open(f"./data/{DATASET}_hierarchy", "rb"))

# Main entry
if __name__ == '__main__':
  p: Tree = Tree()
  stk: list[str] = [T.root]
  acc: int = 1
  pth: list[str] = []

  while len(stk) > 0:
    # Pop stack
    u: str = stk.pop()
    if len(pth) == 0:
      pth.append(u)

    # Maintain path tree
    if len(T.children(u)) == 0:
      if len(p.nodes) == 0:
        p.create_node(identifier=acc, data=pth)
      else:
        tmp: str = T.parent(pth[0]).identifier
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
    for v in T.children(u):
      sz: int = len(T.subtree(v.identifier))
      if mxs < sz:
        mxs = sz
        mxn = v.identifier

    # Maintain recursive stack
    for v in T.children(u):
      if v.identifier != mxn:
        stk.append(v.identifier)
    stk.append(mxn)
    pth.append(mxn)

  # Export decomposed path tree
  p.save2file("ptree.txt")
  pickle.dump(p, open(f"./{DATASET}_path_tree", "wb"))
