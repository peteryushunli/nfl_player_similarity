"""Visualization utilities for NFL player similarity analysis."""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, Any


class VisualizationUtils:
    """Handles visualization of similarity analysis and projections."""
    
    def __init__(self):
        """Initialize visualization utilities."""
        # Set default style
        sns.set_style("whitegrid")
    
    def create_projection_plot(
        self, 
        weighted_projections: pd.DataFrame, 
        point_buckets: pd.DataFrame, 
        target_player: str,
        num_seasons: int
    ) -> plt.Figure:
        """Create a box plot showing fantasy point projections.
        
        Args:
            weighted_projections: DataFrame with weighted projection data
            point_buckets: DataFrame with point buckets for ranking
            target_player: Name of the target player
            num_seasons: Number of seasons to project
            
        Returns:
            Matplotlib figure object
        """
        # Check if we have data to plot
        if weighted_projections.empty:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, 'No projection data available', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title(f"Fantasy Points Projection for {target_player}")
            return fig
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create box plot
        sns.boxplot(data=weighted_projections, palette="Set2", ax=ax)
        
        # Set y-axis limits based on point buckets
        ax.set_ylim(point_buckets.Fantasy_Points.min(), point_buckets.Fantasy_Points.max())
        ax.set_ylabel('Fantasy Points')
        
        # Create twin axis for ranking
        ax2 = ax.twinx()
        ax2.set_ylim(ax.get_ylim())
        ax2.set_yticks(ax.get_yticks())
        ax2.set_yticklabels(point_buckets['Avg_Rank'])
        ax2.set_ylabel('Positional Rank')
        
        # Add median value labels
        medians = weighted_projections.median().values
        median_labels = [f'{val:.2f}' for val in medians]
        pos = range(len(medians))
        
        for tick, label in zip(pos, ax.get_xticklabels()):
            ax.text(
                pos[tick], 
                medians[tick] + 2.5, 
                median_labels[tick],
                horizontalalignment='center', 
                size='x-small', 
                color='black', 
                weight='semibold'
            )
        
        # Add title
        plt.title(f"Fantasy Points and Rank Projection for {target_player} over the next {num_seasons} seasons")
        
        return fig
    
    def create_similarity_heatmap(
        self, 
        similar_players: pd.DataFrame, 
        target_player: str
    ) -> plt.Figure:
        """Create a heatmap showing similarity scores.
        
        Args:
            similar_players: DataFrame with similarity scores
            target_player: Name of the target player
            
        Returns:
            Matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Prepare data for heatmap
        heatmap_data = similar_players.head(10).copy()
        
        # Create heatmap
        sns.heatmap(
            heatmap_data, 
            annot=True, 
            cmap='RdYlBu_r', 
            center=0.5,
            ax=ax
        )
        
        plt.title(f"Similarity Scores for {target_player}")
        plt.xlabel("Age Groups")
        plt.ylabel("Similar Players")
        
        return fig
    
    def create_player_comparison_chart(
        self, 
        target_stats: pd.DataFrame, 
        similar_stats: pd.DataFrame, 
        target_player: str
    ) -> plt.Figure:
        """Create a comparison chart between target player and similar players.
        
        Args:
            target_stats: DataFrame with target player statistics
            similar_stats: DataFrame with similar players' statistics
            target_player: Name of the target player
            
        Returns:
            Matplotlib figure object
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Fantasy points comparison
        fantasy_data = pd.concat([
            target_stats['Fantasy_Points'].rename(f'{target_player}'),
            similar_stats['Fantasy_Points'].rename('Similar Players Avg')
        ], axis=1)
        
        fantasy_data.plot(kind='bar', ax=ax1)
        ax1.set_title('Fantasy Points Comparison')
        ax1.set_ylabel('Fantasy Points')
        ax1.tick_params(axis='x', rotation=45)
        
        # Position rank comparison
        rank_data = pd.concat([
            target_stats['Pos_Rank'].rename(f'{target_player}'),
            similar_stats['Pos_Rank'].rename('Similar Players Avg')
        ], axis=1)
        
        rank_data.plot(kind='bar', ax=ax2)
        ax2.set_title('Position Rank Comparison')
        ax2.set_ylabel('Position Rank')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        return fig
    
    def create_draft_similarity_chart(
        self, 
        draft_scores: pd.DataFrame, 
        target_player: str
    ) -> plt.Figure:
        """Create a chart showing draft position similarities.
        
        Args:
            draft_scores: DataFrame with draft similarity scores
            target_player: Name of the target player
            
        Returns:
            Matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create bar chart of draft similarity scores
        draft_scores.head(10).plot(kind='bar', ax=ax)
        ax.set_title(f'Draft Position Similarity Scores for {target_player}')
        ax.set_ylabel('Similarity Score')
        ax.set_xlabel('Players')
        ax.tick_params(axis='x', rotation=45)
        
        return fig
    
    def display_projection_summary(
        self, 
        summary: pd.DataFrame, 
        target_player: str
    ) -> str:
        """Create a formatted summary of projections.
        
        Args:
            summary: DataFrame with projection summary statistics
            target_player: Name of the target player
            
        Returns:
            Formatted summary string
        """
        if summary.empty:
            return f"## Projection Summary for {target_player}\n\n⚠️ No projection data available for this player."
        
        summary_text = f"## Projection Summary for {target_player}\n\n"
        
        for age in summary.columns:
            summary_text += f"**Age {age}:**\n"
            summary_text += f"- 75th percentile: {summary.loc['75%', age]:.1f} points\n"
            summary_text += f"- Median: {summary.loc['50%', age]:.1f} points\n"
            summary_text += f"- 25th percentile: {summary.loc['25%', age]:.1f} points\n\n"
        
        return summary_text 