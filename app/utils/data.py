import nltk
import spacy

from ..igs import E_MAP
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from pathlib import Path
from spacy.language import Language
from spacy.tokens.doc import Doc


# Initialize NLTK
NLTK_PATH: str = str(Path(__file__).parent.parent / "nltk_data")
nltk.download("stopwords", download_dir=NLTK_PATH, force=True, quiet=True)
nltk.data.path.append(NLTK_PATH)

STOP_WORDS: set[str] = set(stopwords.words("english"))
STAMMER: PorterStemmer = PorterStemmer()

# Initialize Spacy
NLP: Language = spacy.load("en_core_web_md")
DOC_MAP: dict[str, Doc] = dict([(k, NLP(v)) for k, v in E_MAP.items()])


# Functions
def get_list_of_words(str: str) -> list[str]:
  step1: map = map(lambda x: x.lower(), str.split())
  step2: filter = filter(lambda x: x not in STOP_WORDS, step1)
  step3: map = map(lambda x: STAMMER.stem(x), step2)
  return list(step3)
