# NFL Player Similarity Analysis

A fantasy football analytics platform that identifies similar NFL players based on statistical profiles and career trajectories.

## Features

- **Player Similarity Analysis**: Find players with similar statistical profiles using weighted metrics
- **Career Trajectory Comparison**: Visualize how players' careers compare year-over-year
- **Fantasy Point Projections**: Projections based on similar players' historical performance
- **Player Headshots**: Visual player identification
- **Interactive Web Interface**: Modern React frontend with search and filtering

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React + TypeScript + Vite
- **Database**: SQLite
- **Styling**: Tailwind CSS

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+

### Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the API server
uvicorn src.api.main:app --reload --port 8000
```

The API will be available at http://localhost:8000 with documentation at http://localhost:8000/docs.

### Frontend Setup

```bash
cd web

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at http://localhost:5173.

### Production Build

```bash
# Build the frontend
cd web && npm run build

# Run the API (serves both API and frontend)
uvicorn src.api.main:app --port 8000
```

## Project Structure

```
nfl_player_similarity/
├── src/
│   ├── api/                # FastAPI application
│   │   ├── main.py         # App entry point
│   │   ├── routers/        # API route handlers
│   │   └── schemas/        # Pydantic models
│   ├── db/                 # Database layer
│   ├── models/             # Similarity and projection logic
│   ├── data/               # Data loading utilities
│   └── app/                # Legacy Streamlit app
├── web/                    # React frontend
│   └── src/
│       ├── components/     # React components
│       ├── api/            # API client
│       └── types/          # TypeScript types
├── data/                   # Data files
├── notebooks/              # Jupyter notebooks for analysis
└── tests/                  # Unit tests
```

## API Endpoints

- `GET /api/v1/players/` - List all players
- `GET /api/v1/players/search` - Search players by name
- `GET /api/v1/similarity/{player_id}` - Get similar players
- `GET /health` - Health check

## Development

```bash
# Run tests
pytest tests/

# Run linting
ruff check src/
```
