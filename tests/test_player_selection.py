"""Tests for player selection functionality."""

import pytest
import pandas as pd
from src.data.loader import DataLoader


class TestPlayerSelection:
    """Test cases for player selection functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.data_loader = DataLoader()
        
        # Create test season data
        self.test_season_data = pd.DataFrame({
            'Player': ['Tom Brady', 'Aaron Rodgers', 'Patrick Mahomes', 'Tom Brady'],
            'Season': [2020, 2020, 2021, 2021],
            'Pos': ['QB', 'QB', 'QB', 'QB'],
            'Age': [43, 37, 25, 44],
            'Fantasy_Points': [300, 280, 350, 320]
        })
    
    def test_get_player_selection_options(self):
        """Test getting player selection options with position and years."""
        display_options, player_mapping = self.data_loader.get_player_selection_options(
            self.test_season_data
        )
        
        # Check that we get the expected format
        assert len(display_options) > 0
        assert len(player_mapping) > 0
        
        # Check format of display options
        for option in display_options:
            assert '(' in option
            assert ')' in option
            assert ',' in option
        
        # Check that player mapping works
        for display_string, player_name in player_mapping.items():
            assert player_name in display_string
    
    def test_player_mapping_consistency(self):
        """Test that player mapping is consistent."""
        display_options, player_mapping = self.data_loader.get_player_selection_options(
            self.test_season_data
        )
        
        # All display options should have a mapping
        for option in display_options:
            assert option in player_mapping
        
        # All mappings should have a display option
        for display_string in player_mapping.keys():
            assert display_string in display_options
    
    def test_years_active_formatting(self):
        """Test that years active are formatted correctly."""
        display_options, _ = self.data_loader.get_player_selection_options(
            self.test_season_data
        )
        
        for option in display_options:
            # Should contain position and years
            assert 'QB' in option or 'RB' in option or 'WR' in option or 'TE' in option
            assert '2020' in option or '2021' in option
    
    def test_sorting(self):
        """Test that display options are sorted alphabetically."""
        display_options, _ = self.data_loader.get_player_selection_options(
            self.test_season_data
        )
        
        # Check that options are sorted
        sorted_options = sorted(display_options)
        assert display_options == sorted_options 