# GPT Stock Trader

Small toolkit to experiment with GPT-driven trading workflows. You define strategies in JSON, the app validates and persists them to SQLite, scaffolds an output workspace, and generates prompts via Jinja2 templates for you to feed to an LLM. You can add positions and run a daily checkup that snapshots a prompt and a CSV of position history.

## Highlights
- Strategy definition and validation (Pydantic v2)
- SQLite persistence for strategies and positions
- Prompt generation via Jinja2 templates (initial + daily scaffold)
- Daily checkup writes `daily.md` and `history.csv`
- Output workspace per strategy under `output/<strategy>/`

## Requirements
- Python 3.10+
- Install from `requirements.txt` (pydantic, jinja2, pandas, yfinance, etc.)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Workflow Overview
1) Author a strategy JSON (see schema below).
2) Create the strategy: inserts into SQLite, scaffolds `output/<strategy>/`, copies your JSON, and generates `initial.md`.
3) Add positions as you open them; history for active tickers is fetched via yfinance and stored with the strategy.
4) Run daily checkup to write `daily_prompt/<n>/daily.md` and `history.csv` per run.

On first run, the database is created at `db/v1.db`.

Duplicate strategy names: if a strategy name already exists, you can choose to create a unique suffixed copy or exit.

## Quick Start
```bash
# 1) Create a strategy JSON (example below) as config.json
# 2) Generate initial prompt and workspace
python main.py --strategy config.json

# 3) Add a position from JSON (example below)
python main.py --position add pos.json

# 4) Run daily checkup for all strategies
python main.py --daily_checkup all
```

Artifacts are created under `output/<strategy>/`:
- `initial.md` – initial deep-research prompt
- `daily_prompt/<n>/daily.md` – daily prompt snapshot per run
- `daily_prompt/<n>/history.csv` – CSV of position price history
- copy of your strategy JSON

## CLI Usage
Entry point: `main.py`

- Create strategy from JSON and generate `initial.md`
  ```bash
  python main.py --strategy path/to/strategy.json
  ```

- Daily checkup for all or a single strategy
  ```bash
  python main.py --daily_checkup all
  python main.py --daily_checkup <strategy-name>
  ```

- Manage positions (JSON file must match Position schema)
  ```bash
  # Add a position to a strategy
  python main.py --position add path/to/pos.json

  # Update a position (placeholder; not yet implemented)
  python main.py --position update path/to/pos.json
  ```

Notes:
- Adding a position will prompt if the ticker already exists; you can choose to update instead or cancel.
- Daily checkup increments a numeric folder under `output/<strategy>/daily_prompt/` starting at `1`.

## Strategy JSON Schema (Example)
Aligns with `models/models.py::Strategy`.

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
  "benchmark": ["SPY"]
}
```

Required fields:
- `name: str`
- `goal: str`
- `capital: float`
- `universe: str`
- `risk_params: object`
- `benchmark: list[str]` (named `benchmark` in the model)

Validation errors are raised if JSON doesn’t match the schema.

## Position JSON Schema (Example)
Aligns with `models/models.py::Position`.

```json
{
  "name": "IOBT",
  "status": "active",
  "qty": 13,
  "avg_price": 1.81,
  "stop_loss": 1.58,
  "target": 9.00,
  "thesis": [
    "... bullets ..."
  ],
  "strategy_name": "midcap_strategy"
}
```

Notes:
- `strategy_name` associates the position to an existing strategy.
- When adding a position, active tickers are fetched via yfinance to build a history snapshot stored with the strategy.

## Generated Prompts & Templates
- Renderer: `prompt_generation/render.py`
- Orchestration: `prompt_generation/generate.py`
- Initial template: `prompt_generation/templates/initial.md.j2`
- Daily template (placeholder): `prompt_generation/templates/daily.md.j2`

Outputs:
- Initial prompt written to `output/<strategy>/initial.md`
- Daily prompt written to `output/<strategy>/daily_prompt/<n>/daily.md`

Current behavior:
- `generate_daily_prompt` currently renders using `initial.md.j2`. The `daily.md.j2` file is provided as a scaffold to switch to a dedicated daily template.

## Data Model & Persistence
Defined in `models/models.py` (Pydantic v2):

- Strategy
  - `id: UUID`
  - `name: str`
  - `kind: "strategy"`
  - `goal: str`
  - `capital: float`
  - `universe: str`
  - `risk_params: Dict[str, Any]`
  - `benchmark: List[str]`
  - `positions: List[Position]`
  - `position_history: pandas.DataFrame` (serialized to CSV string in DB)

- Position
  - `id: UUID`
  - `name: str` (ticker)
  - `kind: "position"`
  - `status: str`
  - `qty: int`
  - `avg_price: float`
  - `stop_loss: float`
  - `target: float`
  - `thesis: List[str]`
  - `strategy_name: str`

Storage:
- All objects are stored as JSON in SQLite table `objects(id, kind, name, json)` within `db/v1.db`.
- `position_history` is serialized/deserialized automatically by the model.

## Project Structure
```
.
├── main.py                           # CLI entry-point
├── config.json                       # Example strategy config
├── pos.json                          # Example position config
├── db/
│   ├── db.py                         # SQLite helpers (create, insert, update, fetch)
│   └── v1.db                         # Database (created on first run)
├── engine/
│   ├── strategy.py                   # Strategy creation flow + output scaffolding
│   ├── position.py                   # Add/update position flows (update is placeholder)
│   ├── daily.py                      # Daily checkup: prompt + CSV per run
│   └── history.py                    # yfinance fetch + CSV writer
├── models/
│   └── models.py                     # Pydantic v2 models for Strategy/Position
├── prompt_generation/
│   ├── generate.py                   # Orchestrates template rendering
│   ├── render.py                     # Jinja2 renderer
│   └── templates/
│       ├── initial.md.j2             # Initial prompt template
│       └── daily.md.j2               # Daily template scaffold
├── output/                           # Per-strategy outputs (gitignored)
└── requirements.txt                  # Python dependencies
```

## Development Notes
- Create a virtualenv and install dependencies.
- Use `--strategy` to seed a new strategy; outputs and DB records are created atomically.
- Use `--position add` to append positions; active-ticker history is refreshed and stored.
- Use `--daily_checkup` to generate a dated snapshot prompt and `history.csv` per run.
- `output/` and `db/*.db` are ignored by Git.

## Roadmap / TODO
- Switch daily rendering to `daily.md.j2` and flesh out the template.
- Implement `update_position` flow and reconcile with existing positions.
- Enrich templates for weekly and performance reporting.
- Add tests and CI.
- Optional: scheduler/cron for daily checkups.

## Disclaimer
This project is for experimentation and educational purposes. It does not execute trades and is not financial advice.
