"""Fantasy point projection models."""

import pandas as pd
import numpy as np
import math
from typing import Dict, Any, Optional


class FantasyProjectionModel:
    """Handles fantasy point projections based on similar players."""
    
    def __init__(self):
        """Initialize the projection model."""
        pass
    
    def get_projection_stats(
        self, 
        target_player_id: str, 
        similar_players: pd.DataFrame, 
        season_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Get projection statistics for similar players.
        
        Args:
            target_player_id: PFR ID of the target player
            similar_players: DataFrame with similar players
            season_df: DataFrame containing seasonal statistics
            
        Returns:
            DataFrame with projection statistics
        """
        player_list = [target_player_id] + similar_players.index.tolist()
        
        # Look at performances in subsequent seasons
        projection_stats = season_df[season_df['pfr_id'].isin(player_list)]
        target_age = season_df[season_df['pfr_id'] == target_player_id]['Age'].min()
        projection_stats = projection_stats[projection_stats['Age'] > target_age]
        
        # Group and pivot the data
        grouped_stats = projection_stats.groupby(['pfr_id', 'Age'])['Fantasy_Points'].mean().reset_index()
        proj_points = grouped_stats.pivot(index='pfr_id', columns='Age', values='Fantasy_Points')
        
        return proj_points
    
    def create_point_buckets(
        self, 
        target_player_id: str, 
        season_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Create point buckets for ranking visualization.
        
        Args:
            target_player_id: PFR ID of the target player
            season_df: DataFrame containing seasonal statistics
            
        Returns:
            DataFrame with point buckets and average ranks
        """
        position = season_df.loc[season_df.pfr_id == target_player_id].Pos.min()
        latest_season = season_df.Season.max()
        latest_season_df = season_df.loc[
            (season_df.Season == latest_season) & (season_df.Pos == position)
        ]
        
        point_max = int(latest_season_df.Fantasy_Points.max())
        ceiling = (math.ceil(point_max / 50) * 50) + 1
        points_df = pd.DataFrame({'Fantasy_Points': range(0, ceiling, 50)})
        
        # Group by 50-point increments and calculate mean rank
        latest_season_df['Points_bin'] = pd.cut(
            latest_season_df['Fantasy_Points'], 
            range(0, ceiling, 50)
        )
        avg_rank_df = latest_season_df.groupby('Points_bin')['Pos_Rank'].mean().reset_index()
        
        # Merge DataFrames
        points_df['Avg_Rank'] = round(avg_rank_df['Pos_Rank'], 1)
        return points_df.dropna()
    
    def clean_projection_data(
        self, 
        proj_points: pd.DataFrame
    ) -> pd.DataFrame:
        """Clean projection data by removing insufficient data columns.
        
        Args:
            proj_points: DataFrame with projection points
            
        Returns:
            Cleaned DataFrame
        """
        # Remove columns (ages) where there is insufficient data
        zero_col = None
        for col in proj_points.columns:
            if (proj_points[col] == 0).sum() / len(proj_points) > 0.5:
                zero_col = col
                break
        
        # Remove all columns to the right of the zero column
        if zero_col is not None:
            proj_points = proj_points.loc[:, :zero_col]
        
        return proj_points
    
    def create_weighted_projections(
        self, 
        proj_points: pd.DataFrame, 
        similar_players: pd.DataFrame
    ) -> pd.DataFrame:
        """Create weighted projections based on similarity scores.
        
        Args:
            proj_points: DataFrame with projection points
            similar_players: DataFrame with similarity scores
            
        Returns:
            DataFrame with weighted projections
        """
        # Transform similarity scores to weights
        weights = similar_players.copy()
        weights['Avg'] = 1 - weights['Avg']
        
        # Find common players between projections and weights
        common_players = proj_points.index.intersection(weights.index)
        
        if len(common_players) == 0:
            # If no common players, return empty DataFrame with same structure
            return pd.DataFrame(columns=proj_points.columns)
        
        # Filter both DataFrames to only include common players
        proj_points_filtered = proj_points.loc[common_players]
        weights_filtered = weights.loc[common_players]
        
        # Add weights to projections
        proj_points_filtered['Weight'] = weights_filtered['Avg']
        
        # Create weighted projections
        weighted_proj_points = proj_points_filtered.loc[
            np.repeat(proj_points_filtered.index.values, proj_points_filtered['Weight'])
        ]
        weighted_proj_points.drop(columns='Weight', inplace=True)
        weighted_proj_points = weighted_proj_points[weighted_proj_points != 0]
        
        return weighted_proj_points
    
    def generate_projection_summary(
        self, 
        proj_points: pd.DataFrame
    ) -> pd.DataFrame:
        """Generate summary statistics for projections.
        
        Args:
            proj_points: DataFrame with projection points
            
        Returns:
            DataFrame with summary statistics
        """
        proj_points = proj_points.replace(0.0, np.nan)
        summary = proj_points.describe(percentiles=[0.25, 0.5, 0.75])
        return summary.loc[['max', '75%', '50%', '25%', 'min']]
    
    def project_fantasy_points(
        self, 
        target_player_id: str, 
        similar_players: pd.DataFrame, 
        season_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Generate comprehensive fantasy point projections.
        
        Args:
            target_player_id: PFR ID of the target player
            similar_players: DataFrame with similar players
            season_df: DataFrame containing seasonal statistics
            
        Returns:
            Dictionary containing projection data and metadata
        """
        # Get projection statistics
        proj_points = self.get_projection_stats(target_player_id, similar_players, season_df)
        
        # Check if we have any projection data
        if proj_points.empty:
            return {
                'projection_points': pd.DataFrame(),
                'weighted_projections': pd.DataFrame(),
                'summary': pd.DataFrame(),
                'point_buckets': self.create_point_buckets(target_player_id, season_df),
                'num_seasons': 0,
                'error': 'No projection data available for similar players'
            }
        
        # Clean the data
        proj_points = self.clean_projection_data(proj_points)
        
        # Create weighted projections
        weighted_projections = self.create_weighted_projections(proj_points, similar_players)
        
        # Generate summary
        summary = self.generate_projection_summary(proj_points)
        
        # Create point buckets for visualization
        point_buckets = self.create_point_buckets(target_player_id, season_df)
        
        return {
            'projection_points': proj_points,
            'summary': summary,
            'weighted_projections': weighted_projections,
            'point_buckets': point_buckets,
            'num_seasons': len(proj_points.columns)
        } 