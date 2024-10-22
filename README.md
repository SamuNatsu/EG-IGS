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
3. Please manually install `en-core-web-md` package from Spacy for NLP procedure

## Usage

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
