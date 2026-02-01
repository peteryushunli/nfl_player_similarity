"""Tests for the data loader module."""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import os

from src.data.loader import DataLoader


class TestDataLoader:
    """Test cases for DataLoader class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_loader = DataLoader(self.temp_dir)
        
        # Create test data files
        self.create_test_files()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_test_files(self):
        """Create test data files."""
        # Create season data
        season_data = pd.DataFrame({
            'Player': ['Player A', 'Player B', 'Player C'],
            'Season': [2020, 2020, 2020],
            'Pos': ['QB', 'QB', 'RB'],
            'Age': [25, 26, 24],
            'Fantasy_Points': [300, 280, 250]
        })
        season_data.to_csv(os.path.join(self.temp_dir, 'Season_Stats_2000_22.csv'), index=False)
        
        # Create draft data
        draft_data = pd.DataFrame({
            'Player': ['Player A', 'Player B', 'Player C'],
            'Season': [2018, 2019, 2017],
            'Pos': ['QB', 'QB', 'RB'],
            'Pick': [1, 15, 25],
            'Position_Pick': [1, 2, 5]
        })
        draft_data.to_csv(os.path.join(self.temp_dir, '1994_to_2022_draftclass.csv'), index=False)
    
    def test_load_season_data(self):
        """Test loading season data."""
        data = self.data_loader.load_season_data('Season_Stats_2000_22.csv')
        
        assert isinstance(data, pd.DataFrame)
        assert 'Pos_Rank' in data.columns
        assert len(data) == 3
    
    def test_load_draft_data(self):
        """Test loading draft data."""
        data = self.data_loader.load_draft_data('1994_to_2022_draftclass.csv')
        
        assert isinstance(data, pd.DataFrame)
        assert len(data) == 3
        assert 'Pick' in data.columns
    
    def test_load_all_data(self):
        """Test loading all data sources."""
        season_data, draft_data, player_bio_data = self.data_loader.load_all_data()
        
        assert isinstance(season_data, pd.DataFrame)
        assert isinstance(draft_data, pd.DataFrame)
        assert player_bio_data is None  # No bio data in test
    
    def test_get_unique_players(self):
        """Test getting unique players."""
        season_data = self.data_loader.load_season_data('Season_Stats_2000_22.csv')
        unique_players = self.data_loader.get_unique_players(season_data)
        
        assert isinstance(unique_players, list)
        assert len(unique_players) == 3
        assert 'Player A' in unique_players
    
    def test_file_not_found_error(self):
        """Test handling of missing files."""
        with pytest.raises(FileNotFoundError):
            self.data_loader.load_season_data('nonexistent_file.csv') 