"""Player mapping system for Pro Football Reference IDs."""

import pandas as pd
import requests
import time
from typing import Dict, Optional, Tuple
import json
from pathlib import Path


class PlayerIDMapper:
    """Handles mapping player names to Pro Football Reference IDs."""
    
    def __init__(self, cache_file: str = "data/processed/player_id_mapping.json"):
        """Initialize the player ID mapper.
        
        Args:
            cache_file: Path to cache file for player ID mappings
        """
        self.cache_file = Path(cache_file)
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.mapping = self._load_cached_mapping()
    
    def _load_cached_mapping(self) -> Dict[str, str]:
        """Load cached player ID mapping."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def _save_cached_mapping(self):
        """Save player ID mapping to cache."""
        with open(self.cache_file, 'w') as f:
            json.dump(self.mapping, f, indent=2)
    
    def get_pfr_id(self, player_name: str) -> Optional[str]:
        """Get Pro Football Reference ID for a player name.
        
        Args:
            player_name: Name of the player
            
        Returns:
            PFR ID if found, None otherwise
        """
        # Check cache first
        if player_name in self.mapping:
            return self.mapping[player_name]
        
        # Try to find PFR ID
        pfr_id = self._search_pfr_id(player_name)
        
        if pfr_id:
            self.mapping[player_name] = pfr_id
            self._save_cached_mapping()
        
        return pfr_id
    
    def _search_pfr_id(self, player_name: str) -> Optional[str]:
        """Search for PFR ID using the player name.
        
        This is a simplified version. In a real implementation, you would:
        1. Use PFR's search API or scrape their search results
        2. Handle name variations and disambiguation
        3. Implement proper rate limiting
        
        Args:
            player_name: Name of the player
            
        Returns:
            PFR ID if found, None otherwise
        """
        # This is a placeholder implementation
        # In practice, you would need to implement actual PFR API calls
        # For now, we'll create a simple mapping based on common patterns
        
        # Common name variations and their PFR IDs
        # This would be populated from actual PFR data
        name_to_id = {
            "Tom Brady": "B/BradTo00",
            "Aaron Rodgers": "R/RodgAa00",
            "Patrick Mahomes": "M/MahoPa00",
            "Christian McCaffrey": "M/McCaCh01",
            "Saquon Barkley": "B/BarkSa00",
            "Alvin Kamara": "K/KamaAl00",
            "Davante Adams": "A/AdamDa01",
            "Tyreek Hill": "H/HillTy00",
            "Travis Kelce": "K/KelcTr00",
            "George Kittle": "K/KittGe00",
            "A.J. Brown": "B/BrowAJ00",
            "Stefon Diggs": "D/DiggSt00",
            "Justin Jefferson": "J/JeffJu00",
            "Cooper Kupp": "K/KuppCo00",
            "Derrick Henry": "H/HenrDe00",
            "Nick Chubb": "C/ChubNi00",
            "Jonathan Taylor": "T/TaylJo00",
            "Austin Ekeler": "E/EkelAu00",
            "Josh Jacobs": "J/JacoJo00",
            "Dalvin Cook": "C/CookDa00"
        }
        
        # If not in predefined mapping, generate a unique ID
        if player_name not in name_to_id:
            # Generate a unique ID based on player name
            # This is a simple hash-based approach
            import hashlib
            name_hash = hashlib.md5(player_name.encode()).hexdigest()[:8]
            first_letter = player_name.split()[0][0].upper()
            last_letter = player_name.split()[-1][0].upper()
            # Use more of the hash to ensure uniqueness
            unique_id = f"{first_letter}/{last_letter}{name_hash[:4]}"
            return unique_id
        
        return name_to_id.get(player_name)
    
    def get_player_name(self, pfr_id: str) -> Optional[str]:
        """Get player name from PFR ID.
        
        Args:
            pfr_id: Pro Football Reference ID
            
        Returns:
            Player name if found, None otherwise
        """
        # Reverse lookup
        for name, pid in self.mapping.items():
            if pid == pfr_id:
                return name
        return None
    
    def create_id_mapping_from_data(self, season_data: pd.DataFrame, draft_data: pd.DataFrame) -> pd.DataFrame:
        """Create a comprehensive player ID mapping from existing data.
        
        Args:
            season_data: DataFrame with seasonal statistics
            draft_data: DataFrame with draft information
            
        Returns:
            DataFrame with player name to ID mapping
        """
        # Get unique players from both datasets
        season_players = set(season_data['Player'].unique())
        draft_players = set(draft_data['Player'].unique())
        all_players = season_players.union(draft_players)
        
        # Create mapping DataFrame
        mapping_data = []
        used_ids = set()
        
        for player in all_players:
            pfr_id = self.get_pfr_id(player)
            
            # Ensure ID is unique
            if pfr_id and pfr_id not in used_ids:
                used_ids.add(pfr_id)
                mapping_data.append({
                    'player_name': player,
                    'pfr_id': pfr_id,
                    'in_season_data': player in season_players,
                    'in_draft_data': player in draft_players
                })
            elif pfr_id and pfr_id in used_ids:
                # Generate a unique variant
                counter = 1
                while f"{pfr_id}{counter}" in used_ids:
                    counter += 1
                unique_id = f"{pfr_id}{counter}"
                used_ids.add(unique_id)
                mapping_data.append({
                    'player_name': player,
                    'pfr_id': unique_id,
                    'in_season_data': player in season_players,
                    'in_draft_data': player in draft_players
                })
        
        return pd.DataFrame(mapping_data)
    
    def update_data_with_ids(self, df: pd.DataFrame, player_col: str = 'Player') -> pd.DataFrame:
        """Update DataFrame to include PFR IDs.
        
        Args:
            df: DataFrame to update
            player_col: Name of the column containing player names
            
        Returns:
            DataFrame with added PFR ID column
        """
        df_copy = df.copy()
        
        # Get unique players and create mapping
        unique_players = df_copy[player_col].unique()
        player_id_mapping = {}
        used_ids = set()
        
        for player in unique_players:
            pfr_id = self.get_pfr_id(player)
            
            # Ensure ID is unique
            if pfr_id and pfr_id not in used_ids:
                used_ids.add(pfr_id)
                player_id_mapping[player] = pfr_id
            elif pfr_id and pfr_id in used_ids:
                # Generate a unique variant
                counter = 1
                while f"{pfr_id}{counter}" in used_ids:
                    counter += 1
                unique_id = f"{pfr_id}{counter}"
                used_ids.add(unique_id)
                player_id_mapping[player] = unique_id
            else:
                # Generate a completely new ID
                import hashlib
                name_hash = hashlib.md5(player.encode()).hexdigest()[:8]
                first_letter = player.split()[0][0].upper()
                last_letter = player.split()[-1][0].upper()
                unique_id = f"{first_letter}/{last_letter}{name_hash[:4]}"
                
                # Ensure this is also unique
                counter = 1
                while unique_id in used_ids:
                    unique_id = f"{first_letter}/{last_letter}{name_hash[:4]}{counter}"
                    counter += 1
                
                used_ids.add(unique_id)
                player_id_mapping[player] = unique_id
        
        # Apply mapping to DataFrame
        df_copy['pfr_id'] = df_copy[player_col].map(player_id_mapping)
        
        return df_copy
    
    def get_players_with_ids(self, df: pd.DataFrame, player_col: str = 'Player') -> pd.DataFrame:
        """Get only players that have PFR IDs.
        
        Args:
            df: DataFrame to filter
            player_col: Name of the column containing player names
            
        Returns:
            DataFrame with only players that have PFR IDs
        """
        df_with_ids = self.update_data_with_ids(df, player_col)
        return df_with_ids[df_with_ids['pfr_id'].notna()]


class PlayerDataManager:
    """Manages player data with PFR ID integration."""
    
    def __init__(self, mapper: PlayerIDMapper):
        """Initialize the data manager.
        
        Args:
            mapper: PlayerIDMapper instance
        """
        self.mapper = mapper
    
    def process_season_data(self, season_data: pd.DataFrame) -> pd.DataFrame:
        """Process season data to include PFR IDs.
        
        Args:
            season_data: Raw season data
            
        Returns:
            Processed season data with PFR IDs
        """
        # Add PFR IDs
        processed_data = self.mapper.update_data_with_ids(season_data)
        
        # Filter to only include players with IDs
        processed_data = self.mapper.get_players_with_ids(processed_data)
        
        # Create position rank columns by season
        processed_data['Pos_Rank'] = processed_data.groupby(['Pos', 'Season'])['Fantasy_Points'].rank(
            ascending=False, method='min'
        )
        
        return processed_data
    
    def process_draft_data(self, draft_data: pd.DataFrame) -> pd.DataFrame:
        """Process draft data to include PFR IDs.
        
        Args:
            draft_data: Raw draft data
            
        Returns:
            Processed draft data with PFR IDs
        """
        # Add PFR IDs
        processed_data = self.mapper.update_data_with_ids(draft_data)
        
        # Filter to only include players with IDs
        processed_data = self.mapper.get_players_with_ids(processed_data)
        
        return processed_data
    
    def get_player_selection_options(self, season_data: pd.DataFrame) -> Tuple[list, dict]:
        """Get player selection options with position and years active.
        
        Args:
            season_data: DataFrame containing seasonal statistics
            
        Returns:
            Tuple of (display_options, player_mapping)
            - display_options: List of formatted player strings for dropdown
            - player_mapping: Dictionary mapping display strings to PFR IDs
        """
        # Get player summary information
        player_summary = season_data.groupby(['Player', 'pfr_id']).agg({
            'Pos': 'first',
            'Season': ['min', 'max'],
            'Fantasy_Points': 'mean'
        }).round(0)
        
        # Flatten column names
        player_summary.columns = ['Pos', 'Start_Year', 'End_Year', 'Avg_Fantasy_Points']
        player_summary = player_summary.reset_index()
        
        # Create display options and mapping
        display_options = []
        player_mapping = {}
        
        for _, row in player_summary.iterrows():
            player_name = row['Player']
            pfr_id = row['pfr_id']
            position = row['Pos']
            start_year = int(row['Start_Year'])
            end_year = int(row['End_Year'])
            
            # Create display string
            if start_year == end_year:
                years_active = f"{start_year}"
            else:
                years_active = f"{start_year}-{end_year}"
            
            display_string = f"{player_name} ({position}, {years_active})"
            display_options.append(display_string)
            player_mapping[display_string] = pfr_id
        
        # Sort by player name for easier selection
        display_options.sort()
        
        return display_options, player_mapping 