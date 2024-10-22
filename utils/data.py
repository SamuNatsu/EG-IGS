import nltk

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from pathlib import Path


# Initialize NLTK
NLTK_PATH: str = str(Path(__file__).parent.parent / "nltk_data")
nltk.download("stopwords", download_dir=NLTK_PATH, force=True, quiet=True)
nltk.data.path.append(NLTK_PATH)

STOP_WORDS: set[str] = set(stopwords.words("english"))
STAMMER: PorterStemmer = PorterStemmer()

# Functions
def get_list_of_words(str: str) -> list[str]:
  step1: map = map(lambda x: x.lower(), str.split())
  step2: filter = filter(lambda x: x not in STOP_WORDS, step1)
  step3: map = map(lambda x: STAMMER.stem(x), step2)
  return list(step3)
