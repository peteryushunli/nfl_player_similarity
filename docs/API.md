# API Documentation

## Overview

The NFL Player Similarity Analysis package provides a comprehensive suite of tools for analyzing NFL player similarities and generating fantasy point projections.

## Core Modules

### Data Loading (`src.data.loader`)

#### `DataLoader`

The main class for loading and preprocessing NFL data.

```python
from src.data.loader import DataLoader

# Initialize with custom data directory
loader = DataLoader(data_dir="path/to/data")

# Load all data sources
season_data, draft_data, player_bio_data = loader.load_all_data()

# Load individual data sources
season_data = loader.load_season_data()
draft_data = loader.load_draft_data()
player_bio_data = loader.load_player_bio_data()

# Get unique players
unique_players = loader.get_unique_players(season_data)
```

**Methods:**
- `load_season_data(filename: str) -> pd.DataFrame`: Load seasonal statistics
- `load_draft_data(filename: str) -> pd.DataFrame`: Load draft data
- `load_player_bio_data(filename: str) -> pd.DataFrame`: Load player biographical data
- `load_all_data() -> Tuple[pd.DataFrame, pd.DataFrame, Optional[pd.DataFrame]]`: Load all data sources
- `get_unique_players(season_data: pd.DataFrame) -> list`: Get list of unique players

### Similarity Analysis (`src.models.similarity`)

#### `PlayerSimilarityModel`

Handles player similarity calculations using multiple metrics.

```python
from src.models.similarity import PlayerSimilarityModel

model = PlayerSimilarityModel()

# Find similar players
similar_players = model.find_similar_players(
    season_data, draft_data, target_player
)
```

**Methods:**
- `calculate_euclidean_distance(df, target_player, age) -> pd.DataFrame`: Calculate Euclidean distances
- `compare_euclidean_distances(peer_df, target_player) -> pd.DataFrame`: Compare distances across ages
- `calculate_fantasy_point_similarity(peer_df, target_player) -> pd.DataFrame`: Calculate fantasy point similarities
- `calculate_draft_similarity(peer_draft, draft_df, target_player) -> pd.DataFrame`: Calculate draft similarities
- `find_similar_players(season_df, draft_df, target_player) -> pd.DataFrame`: Find similar players

### Projection Analysis (`src.models.projection`)

#### `FantasyProjectionModel`

Handles fantasy point projections based on similar players.

```python
from src.models.projection import FantasyProjectionModel

model = FantasyProjectionModel()

# Generate projections
projection_results = model.project_fantasy_points(
    target_player, similar_players, season_data
)
```

**Methods:**
- `get_projection_stats(target_player, similar_players, season_df) -> pd.DataFrame`: Get projection statistics
- `create_point_buckets(target_player, season_df) -> pd.DataFrame`: Create point buckets for ranking
- `clean_projection_data(proj_points) -> pd.DataFrame`: Clean projection data
- `create_weighted_projections(proj_points, similar_players) -> pd.DataFrame`: Create weighted projections
- `project_fantasy_points(target_player, similar_players, season_df) -> Dict[str, Any]`: Generate comprehensive projections

### Visualization (`src.utils.visualization`)

#### `VisualizationUtils`

Handles visualization of similarity analysis and projections.

```python
from src.utils.visualization import VisualizationUtils

viz = VisualizationUtils()

# Create projection plot
fig = viz.create_projection_plot(
    weighted_projections, point_buckets, target_player, num_seasons
)

# Create similarity heatmap
fig = viz.create_similarity_heatmap(similar_players, target_player)
```

**Methods:**
- `create_projection_plot(weighted_projections, point_buckets, target_player, num_seasons) -> plt.Figure`: Create projection box plot
- `create_similarity_heatmap(similar_players, target_player) -> plt.Figure`: Create similarity heatmap
- `create_player_comparison_chart(target_stats, similar_stats, target_player) -> plt.Figure`: Create comparison chart
- `create_draft_similarity_chart(draft_scores, target_player) -> plt.Figure`: Create draft similarity chart
- `display_projection_summary(summary, target_player) -> str`: Create formatted summary

## Data Formats

### Season Data
Expected columns:
- `Player`: Player name
- `Season`: Season year
- `Pos`: Position
- `Age`: Player age
- `Fantasy_Points`: Fantasy points scored
- Additional statistical columns

### Draft Data
Expected columns:
- `Player`: Player name
- `Season`: Draft year
- `Pos`: Position
- `Pick`: Overall draft pick
- `Position_Pick`: Position-specific draft pick

## Usage Examples

### Basic Similarity Analysis

```python
from src.data.loader import DataLoader
from src.models.similarity import PlayerSimilarityModel

# Load data
loader = DataLoader()
season_data, draft_data, _ = loader.load_all_data()

# Find similar players
model = PlayerSimilarityModel()
similar_players = model.find_similar_players(
    season_data, draft_data, "Tom Brady"
)

print(similar_players.head())
```

### Generate Projections

```python
from src.models.projection import FantasyProjectionModel

# Generate projections
proj_model = FantasyProjectionModel()
projections = proj_model.project_fantasy_points(
    "Tom Brady", similar_players, season_data
)

print(projections['summary'])
```

### Create Visualizations

```python
from src.utils.visualization import VisualizationUtils

# Create visualizations
viz = VisualizationUtils()
fig = viz.create_projection_plot(
    projections['weighted_projections'],
    projections['point_buckets'],
    "Tom Brady",
    projections['num_seasons']
)
plt.show()
```

## Error Handling

The package includes comprehensive error handling:

- **FileNotFoundError**: Raised when data files are missing
- **ValueError**: Raised for invalid input parameters
- **KeyError**: Raised when required columns are missing from data

## Performance Considerations

- Data loading is cached using Streamlit's `@st.cache_data` decorator
- Models are cached using `@st.cache_resource` decorator
- Large datasets are processed efficiently using pandas operations
- Memory usage is optimized for typical fantasy football datasets 