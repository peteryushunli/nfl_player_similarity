"""Data loading utilities for NFL player similarity analysis."""

import pandas as pd
from pathlib import Path
from typing import Tuple, Optional
from .player_mapping import PlayerIDMapper, PlayerDataManager


class DataLoader:
    """Handles loading and preprocessing of NFL data."""
    
    def __init__(self, data_dir: str = "data/raw"):
        """Initialize the data loader.
        
        Args:
            data_dir: Path to the directory containing raw data files
        """
        self.data_dir = Path(data_dir)
        self.id_mapper = PlayerIDMapper()
        self.data_manager = PlayerDataManager(self.id_mapper)
        
    def load_season_data(self, filename: str = "Season_Stats_2000_22.csv") -> pd.DataFrame:
        """Load seasonal statistics data.
        
        Args:
            filename: Name of the season data file
            
        Returns:
            DataFrame containing seasonal statistics with PFR IDs
        """
        file_path = self.data_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Season data file not found: {file_path}")
            
        raw_data = pd.read_csv(file_path)
        
        # Process data to include PFR IDs
        data = self.data_manager.process_season_data(raw_data)
        
        return data
    
    def load_draft_data(self, filename: str = "1994_to_2022_draftclass.csv") -> pd.DataFrame:
        """Load draft data.
        
        Args:
            filename: Name of the draft data file
            
        Returns:
            DataFrame containing draft information with PFR IDs
        """
        file_path = self.data_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Draft data file not found: {file_path}")
            
        raw_data = pd.read_csv(file_path)
        
        # Process data to include PFR IDs
        data = self.data_manager.process_draft_data(raw_data)
        
        return data
    
    def load_player_bio_data(self, filename: str = "player_bio_2019_2023.csv") -> pd.DataFrame:
        """Load player biographical data.
        
        Args:
            filename: Name of the player bio data file
            
        Returns:
            DataFrame containing player biographical information
        """
        file_path = self.data_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Player bio data file not found: {file_path}")
            
        return pd.read_csv(file_path)
    
    def load_all_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, Optional[pd.DataFrame]]:
        """Load all available data sources.
        
        Returns:
            Tuple of (season_data, draft_data, player_bio_data)
        """
        season_data = self.load_season_data()
        draft_data = self.load_draft_data()
        
        # Try to load player bio data if available
        try:
            player_bio_data = self.load_player_bio_data()
        except FileNotFoundError:
            player_bio_data = None
            
        return season_data, draft_data, player_bio_data
    
    def get_unique_players(self, season_data: pd.DataFrame) -> list:
        """Get list of unique players from season data.
        
        Args:
            season_data: DataFrame containing seasonal statistics
            
        Returns:
            List of unique player names
        """
        return season_data['Player'].unique().tolist()
    
    def get_player_selection_options(self, season_data: pd.DataFrame) -> Tuple[list, dict]:
        """Get player selection options with position and years active.
        
        Args:
            season_data: DataFrame containing seasonal statistics
            
        Returns:
            Tuple of (display_options, player_mapping)
            - display_options: List of formatted player strings for dropdown
            - player_mapping: Dictionary mapping display strings to PFR IDs
        """
        return self.data_manager.get_player_selection_options(season_data) 