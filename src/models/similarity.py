"""Player similarity analysis models."""

import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist
from typing import List, Dict, Any


class PlayerSimilarityModel:
    """Handles player similarity calculations using multiple metrics."""
    
    def __init__(self):
        """Initialize the similarity model."""
        pass
    
    def calculate_euclidean_distance(
        self, 
        df: pd.DataFrame, 
        target_player: str, 
        age: int
    ) -> pd.DataFrame:
        """Calculate Euclidean distance between target player and peers.
        
        Args:
            df: DataFrame containing player data
            target_player: Name of the target player
            age: Age to filter by
            
        Returns:
            DataFrame with Euclidean distances
        """
        target = df.loc[df.Player == target_player]
        non_target = df.loc[df.Player != target_player]
        
        # Extract scaled feature data
        target_features = target.loc[:, target.columns.str.endswith("_Scaled")]
        non_target_features = non_target.loc[:, target.columns.str.endswith("_Scaled")]
        
        # Calculate Euclidean distance
        euclid_distances = cdist(non_target_features, target_features, 'euclid')
        euclid_distances = euclid_distances.round(decimals=2)
        
        # Create result DataFrame
        names = non_target.Player
        col_name = f'Age_{age}'
        result_df = pd.DataFrame(
            data=euclid_distances, 
            index=names, 
            columns=[col_name]
        )
        
        return result_df
    
    def compare_euclidean_distances(
        self, 
        peer_df: pd.DataFrame, 
        target_player: str
    ) -> pd.DataFrame:
        """Compare Euclidean distances across all ages for a target player.
        
        Args:
            peer_df: DataFrame containing peer player data
            target_player: Name of the target player
            
        Returns:
            DataFrame with average Euclidean distances
        """
        age_range = sorted(peer_df.Age.unique())
        
        # Calculate distances for each age
        age_dfs = {}
        for age in age_range:
            age_data = peer_df.loc[peer_df.Age == age]
            age_dfs[f'euclid_{age}'] = self.calculate_euclidean_distance(
                df=age_data, 
                target_player=target_player, 
                age=int(age)
            )
        
        # Start with the minimum age DataFrame
        base_df = age_dfs[f'euclid_{min(age_range)}']
        
        # Join all age DataFrames
        for age in age_range[1:]:
            age_df = age_dfs[f'euclid_{age}']
            base_df = pd.merge(base_df, age_df, how='inner', on='Player')
        
        # Calculate average distance
        base_df['Avg'] = round(base_df.mean(axis=1), 2)
        return base_df.sort_values(by='Avg', ascending=True)
    
    def calculate_fantasy_point_similarity(
        self, 
        peer_df: pd.DataFrame, 
        target_player: str
    ) -> pd.DataFrame:
        """Calculate fantasy point similarity between players.
        
        Args:
            peer_df: DataFrame containing peer player data
            target_player: Name of the target player
            
        Returns:
            DataFrame with fantasy point similarities
        """
        # Remove duplicates and pivot data
        peer_df = peer_df.drop_duplicates(subset=['Player', 'Age'], keep='first')
        peer_pivot = peer_df.pivot(
            index='Player', 
            columns='Age', 
            values='Fantasy_Points'
        ).dropna(axis=0)
        
        # Calculate relative differences
        reference_row = peer_pivot.loc[peer_pivot.index == target_player].iloc[0]
        peer_fantasy = round(abs(peer_pivot.sub(reference_row) / reference_row), 2)
        
        # Rename columns and calculate average
        peer_fantasy.columns = 'Age_' + peer_fantasy.columns.astype(int).astype(str)
        peer_fantasy['Avg'] = round(peer_fantasy.mean(axis=1), 2)
        peer_fantasy = peer_fantasy.loc[peer_fantasy.index != target_player]
        peer_fantasy.sort_values(by='Avg', ascending=True, inplace=True)
        
        return peer_fantasy
    
    def calculate_draft_similarity(
        self, 
        peer_draft: pd.DataFrame, 
        draft_df: pd.DataFrame, 
        target_player: str
    ) -> pd.DataFrame:
        """Calculate draft position similarity scores.
        
        Args:
            peer_draft: DataFrame containing draft data for peer players
            draft_df: Full draft dataset
            target_player: Name of the target player
            
        Returns:
            DataFrame with draft similarity scores
        """
        # Identify target player's draft position
        target_draft = peer_draft.loc[peer_draft.Player == target_player].iloc[0]
        
        # Calculate absolute pick differences
        peer_draft.loc[:, 'Pick_Diff_Abs'] = abs(peer_draft['Pick'] - target_draft['Pick'])
        peer_draft.loc[:, 'Pos_Pick_Diff_Abs'] = abs(
            peer_draft['Position_Pick'] - target_draft['Position_Pick']
        )
        peer_draft.loc[:, 'Pick_Diff_Weight'] = round(
            1 - peer_draft['Pick_Diff_Abs'] / (32 * 7), 2
        )
        
        # Calculate average players drafted per position
        agg = draft_df.groupby(by=['Season', 'Pos'], as_index=False).count()
        agg = agg.groupby('Pos').mean()
        agg['Avg_Players_Drafted'] = round(agg['Player'], 0)
        draft_avg = agg['Avg_Players_Drafted']
        
        # Calculate positional pick difference
        position = peer_draft.Pos.mode()[0]
        pos_pick_num = draft_avg.loc[draft_avg.index == position][0]
        peer_draft.loc[:, 'Pos_Pick_Diff_Weight'] = round(
            1 - peer_draft['Pos_Pick_Diff_Abs'] / pos_pick_num, 2
        )
        
        # Calculate final pick score
        peer_draft.loc[:, 'Pick_Score'] = round(
            (peer_draft['Pos_Pick_Diff_Weight'] + peer_draft['Pick_Diff_Weight']) / 2, 2
        )
        peer_draft.sort_values(by='Pick_Score', ascending=False, inplace=True)
        
        peer_score = peer_draft[['Player', 'Pick_Score']]
        peer_score.set_index('Player', inplace=True)
        
        return peer_score.applymap(lambda x: max(0, x))
    
    def weight_draft_scores(
        self, 
        output_df: pd.DataFrame, 
        peer_score: pd.DataFrame
    ) -> pd.DataFrame:
        """Weight draft scores based on seasons played.
        
        Args:
            output_df: DataFrame with similarity scores
            peer_score: DataFrame with draft similarity scores
            
        Returns:
            DataFrame with weighted scores
        """
        seasons_played = len(output_df.columns) - 1
        
        # Weight the similarity scores with draft scores
        peer_score_similarity = round(
            output_df.div(output_df.join(peer_score)['Pick_Score'], axis=0), 2
        )
        output_df2 = round(
            (output_df * seasons_played + peer_score_similarity) / (seasons_played + 1), 2
        )
        output_df2.sort_values(by='Avg', ascending=True, inplace=True)
        
        return output_df2
    
    def find_similar_players(
        self, 
        season_df: pd.DataFrame, 
        draft_df: pd.DataFrame, 
        target_player: str
    ) -> pd.DataFrame:
        """Find players most similar to the target player.
        
        Args:
            season_df: DataFrame containing seasonal statistics
            draft_df: DataFrame containing draft data
            target_player: Name of the target player
            
        Returns:
            DataFrame with similarity scores for similar players
        """
        # Filter for peer players
        target_df = season_df.loc[season_df.Player == target_player]
        position = target_df.Pos.iloc[0]
        min_age = target_df.Age.min()
        max_age = target_df.Age.max()
        
        peer_df = season_df.loc[
            (season_df.Age >= min_age) & 
            (season_df.Age <= max_age) & 
            (season_df.Pos == position)
        ]
        
        # Calculate fantasy point similarity
        fantasy_similarity = self.calculate_fantasy_point_similarity(peer_df, target_player)
        
        # Calculate Euclidean distance similarity
        euclid_similarity = self.compare_euclidean_distances(peer_df, target_player)
        
        # Aggregate and average the two metrics
        output_df = (fantasy_similarity + euclid_similarity) / 2
        output_df.sort_values(by='Avg', ascending=True, inplace=True)
        
        # Add draft similarity scores
        peer_draft = self._get_peer_draft_data(output_df, draft_df, target_player)
        peer_score = self.calculate_draft_similarity(peer_draft, draft_df, target_player)
        final_output = self.weight_draft_scores(output_df, peer_score)
        
        # Clean up results
        final_output.dropna(subset=['Avg'], inplace=True)
        final_output = final_output.loc[final_output.Avg < 1]
        
        return final_output
    
    def _get_peer_draft_data(
        self, 
        output_df: pd.DataFrame, 
        draft_df: pd.DataFrame, 
        target_player: str
    ) -> pd.DataFrame:
        """Get draft data for peer players.
        
        Args:
            output_df: DataFrame with similarity scores
            draft_df: Full draft dataset
            target_player: Name of the target player
            
        Returns:
            DataFrame with draft data for peer players
        """
        name_list = output_df.index.tolist()
        name_list.append(target_player)
        
        return draft_df.loc[draft_df.Player.isin(name_list)] 