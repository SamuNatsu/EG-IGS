# EG-IGS

Reproduction demo for Example-Guided Interactive Graph Search

## Paper Information

_Efficient Example-Guided Interactive Graph Search_  
2024 IEEE 40th International Conference on Data Engineering (ICDE)  
Zhuowei Zhao et. al

DOI 10.1109/ICDE60146.2024.00033  
<https://ieeexplore.ieee.org/document/10597759/>

## Paper's Demo Repository

<https://github.com/alvinzhaowei/EG-IGS-AND-GPT-DEMO>

## Prerequisites

1. Python version >= 3.12
2. Any python package manager that support `pyproject.toml` as dependency file
3. Please manually install `en_core_web_md` package (~31MB) from [spaCy](https://spacy.io/models/en) for NLP procedure

## Usage

### Environment Variables

Some environment variables are quired, you can place a dotenv file in the repository directory

#### QWEN_API_KEY

If you want to use Qwen as an oracle, you should have this variable

#### OPENAI_API_KEY

If you want to use GPTs as an oracle, you should have this variable

#### EG_IGS_TAU

If you want to use EG-IGS, you should have this float variable ranges from 0 to 1 as the threshold of the similarity

#### EG_IGS_K

If you want to use EG-IGS, you should have this positive integer variable as the top-k similarity

### Start up

It uses FastAPI as web service, so it's simple to run the project:

```bash
fastapi run
```

## Folders and Files

### Folders

|     Name      |               What               |
| :-----------: | :------------------------------: |
|    `app/`     |     Web service root package     |
|  `app/data`   |       Premined data folder       |
|   `app/igs`   | Interactive graph search package |
| `app/oravles` |         Oracles package          |
| `app/public`  |      Static web file folder      |
|  `app/utils`  |          Utils package           |

### Files

|        Name        |                       What                       |
| :----------------: | :----------------------------------------------: |
| `decomposition.py` |     Decomposition scripts for hierarchy tree     |
|    `premine.py`    |     Premine scripts for amazon item examples     |
| `test_chat_gpt.py` |         Test scripts for ChatGPT oracle          |
|  `test_fetch.py`   | Test scripts for fetching amazon item desciption |
|   `test_qwen.py`   |           Test scripts for Qwen oracle           |

## License

AGPL-3.0
