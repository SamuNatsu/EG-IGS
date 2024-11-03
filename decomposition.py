import pickle

from app.utils.tree import decompose
from treelib import Tree


# Constants
DATASET: str = "amazon"
T: Tree = pickle.load(open(f"./app/data/{DATASET}_hierarchy", "rb"))

# Main entry
if __name__ == "__main__":
  p: Tree = decompose(T)

  # Export decomposed path tree
  p.save2file("ptree.txt")
  pickle.dump(p, open(f"./{DATASET}_path_tree", "wb"))
