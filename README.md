# AI Evolutionary Algorithm

An evolutionary code optimization engine that uses LLM API calls to iteratively improve Python search algorithms. Built with async concurrency for parallel code generation.

---

## Quick Start

### 1. Clone & Environment

```bash
git clone <repo-url>
cd AI-evolutionary-algorithm
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. API Key

This project uses [Google AI Studio](https://aistudio.google.com/apikey) (Gemini) — free, no credit card required.

```bash
cp config.example.yaml config.yaml
```

Open `config.yaml` and paste your key:

```yaml
api-key: "your-key-here"
```

> **Do not commit `config.yaml`.** It is already in `.gitignore`.

### 3. Run

```bash
python api.py
```

---

## Usage from Another File

Import and call `main()` from any Python file:

```python
import asyncio
from api import main

# Default — generates 10 variations of the starter code
results = asyncio.run(main())

# Custom — pass up to 10 code strings to improve
results = asyncio.run(main(code_list=["def foo(): ...", "def bar(): ..."]))
```

`main()` returns a `list[list[str]]` — one list of results per iteration.

---

## Configuration

| Variable | Location | Description |
|---|---|---|
| `api-key` | `config.yaml` | Your Google AI Studio API key |
| `NUM_OF_ITERATIONS` | `api.py` | How many evolutionary passes to run |
| `NUM_BEST` | `api.py` | Top N results to keep per generation |
| `MAX_NUM` | `api.py` | Total candidates per generation |
| `API_SEMAPHORE` | `api.py` | Max concurrent API requests (default: 5) |

---

## Rate Limits

The Gemini free tier has a low RPM (requests per minute). The project handles this with:

> **Gemini 3.1 Flash Lite**
> - 15 requests/min (RPM)
> - 500 requests/day (RPD)
- **Semaphore** — caps concurrent requests
- **Staggered launches** — 2s gap between each call
- **Exponential backoff** — auto-retries on 429 errors with increasing delay
- **Cooldown** — 60s pause between iterations

If you're consistently rate limited, lower `API_SEMAPHORE` to `3` or increase the stagger delay.

---

## Project Structure

```
├── api.py                  # Async LLM calls & prompt construction
├── simulation.py           # Simulation runner & evaluation
├── config.yaml             # Your API key (git-ignored)
├── config.example.yaml     # Template — copy this
├── requirements.txt        # Python dependencies
└── README.md
```

---

## Troubleshooting

**`config.yaml not found`**
→ Copy `config.example.yaml` to `config.yaml` and add your key.

**`429 Rate Limit` errors**
→ Normal on the free tier. The retry logic handles it automatically. If persistent, reduce `API_SEMAPHORE`.

**`ModuleNotFoundError`**
→ Make sure your venv is activated and run `pip install -r requirements.txt`.

**Hanging with no output**
→ Check your API key is valid at [aistudio.google.com](https://aistudio.google.com). Console logs show retry status per task.

---

## License

MIT

