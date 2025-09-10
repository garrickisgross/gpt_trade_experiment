# GPT Stock Trader

A small toolkit to experiment with GPT-driven trading workflows. Strategies are defined via JSON (validated by Pydantic models), persisted to a SQLite database, and used to generate prompt files (via Jinja2 templates) that you can feed to an LLM for research and trade ideas.

## Features
- Strategy definition and validation (Pydantic v2 models)
- SQLite persistence of strategies and positions
- Prompt generation using Jinja2 templates
- CLI for adding strategies and running daily checkups (scaffolded)
- Output folder per strategy with generated artifacts

## Requirements
- Python 3.10+
- Packages: `pydantic>=2`, `jinja2`

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install pydantic jinja2
```

## Quick Start
1) Create a strategy JSON (example below) and save as `config.json`.
2) Run the CLI to add the strategy and generate the initial prompt.
3) Open the generated markdown under `output/<strategy-name>/initial.md`.

```bash
python main.py --strategy config.json
```

On first run, the SQLite database is created at `db/v1.db`. Output artifacts are written under `output/<strategy-name>/`.

If a strategy with the same name already exists, you will be prompted to either:
- Create a new strategy with a unique suffix, or
- Exit without creating a duplicate

## Strategy JSON Schema (Example)
Minimal example aligning with `models.models.Strategy`:

```json
{
  "name": "midcap_strategy",
  "goal": "maximize alpha",
  "capital": 100.0,
  "universe": "Easily tradible (Preferably U.S. micro-caps...)",
  "risk_params": {
    "general": "Stop-Loss and exit targets required, set trailing stops...",
    "max_per_position": 0.25,
    "max_positions": 5,
    "stop_loss_pct": 0.12,
    "trailing_stops_pct": 0.1
  },
  "benchmarks": ["SPY"]
}
```

Required top-level fields:
- `name` (string)
- `goal` (string)
- `capital` (number)
- `universe` (string)
- `risk_params` (object)
- `benchmarks` (array of strings, optional in the model as `benchmark`)

The model is validated with Pydantic v2; you’ll see a validation error if your JSON doesn’t match the schema.

## Generated Prompts
- Initial prompt template: `prompt_generation/templates/initial.md.j2`
- Renderer: `prompt_generation/render.py`
- The initial prompt file is written to: `output/<strategy-name>/initial.md`

You can customize the template to change the prompt structure, tone, or fields.

## CLI Usage
Top-level entry point: `main.py`

- Add a strategy and generate initial prompt
  ```bash
  python main.py --strategy path/to/strategy.json
  ```

- Daily checkup for all strategies (scaffolded)
  ```bash
  python main.py --daily_checkup all
  ```
  Note: `daily_checkup_flow` and `generate_daily_prompt` are currently stubs; extend `engine/daily.py` to implement daily prompt generation.

- Manage positions for a strategy (scaffolded)
  ```bash
  # Add a position (not yet implemented)
  python main.py --position add <strategy-name> <ticker>

  # Update a position (not yet implemented)
  python main.py --position update <strategy-name> <ticker>
  ```
  Note: `create_new_position` and `update_position` are stubs in `engine/position.py`.

## Data Model
Defined in `models/models.py` (Pydantic v2):

- Strategy
  - `id: UUID` (auto)
  - `name: str`
  - `kind: "strategy"`
  - `goal: str`
  - `capital: float`
  - `universe: str`
  - `risk_params: dict`
  - `benchmark: list[str]` (named `benchmarks` in example JSON)
  - `positions: dict[str, Position]`

- Position
  - `id: UUID` (auto)
  - `name: str`
  - `kind: "position"`
  - `symbol: str`
  - `status: str`
  - `qty: int`
  - `avg_price: float`
  - `stop_loss: float`
  - `thesis: list[str]`
  - `strategy_id: UUID`

Records are serialized as JSON and stored in the `objects` table of `db/v1.db` with columns `(id, kind, name, json)`.

## Project Structure
```
.
├── main.py                          # CLI entry-point
├── config.json                      # Example strategy config
├── db/
│   ├── db.py                        # SQLite helpers (create, insert, update, fetch)
│   └── v1.db                        # Database file (created on first run)
├── engine/
│   ├── strategy.py                  # Strategy creation flow + output scaffolding
│   ├── daily.py                     # Daily checkup (stub)
│   └── position.py                  # Position add/update (stub)
├── models/
│   └── models.py                    # Pydantic v2 models for Strategy/Position
├── prompt_generation/
│   ├── generate.py                  # Orchestrates template rendering
│   ├── render.py                    # Jinja2 renderer
│   └── templates/
│       └── initial.md.j2            # Initial prompt template
└── .gitignore                       # Ignores venv, __pycache__, db/*.db, output/*
```

## Development
- Create a virtualenv and install deps (see Requirements)
- Run `python main.py --strategy config.json` to generate the initial prompt
- Extend stubs in `engine/daily.py` and `engine/position.py` to add functionality
- Outputs under `output/` and the SQLite file under `db/` are ignored by Git

## Roadmap / TODO
- Implement daily prompt generation (`engine/daily.py`)
- Implement position creation/update (`engine/position.py`)
- Enrich prompt templates for weekly and performance reporting
- Add tests and CI
- Optional: scheduler/cron to run daily checkups automatically

## Disclaimer
This project is for experimentation and educational purposes. It does not execute trades and is not financial advice.

