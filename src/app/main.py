"""Main Streamlit application for NFL Player Similarity Analysis."""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data.loader import DataLoader
from models.similarity import PlayerSimilarityModel
from models.projection import FantasyProjectionModel
from utils.visualization import VisualizationUtils

# Configure pandas
pd.options.mode.chained_assignment = None

# Configure Streamlit page
st.set_page_config(
    page_title="NFL Player Similarity Analysis", 
    page_icon="🏈", 
    initial_sidebar_state="expanded",
    layout="wide"
)

# Initialize models and utilities
@st.cache_resource
def initialize_models():
    """Initialize all models and utilities."""
    return {
        'data_loader': DataLoader(),
        'similarity_model': PlayerSimilarityModel(),
        'projection_model': FantasyProjectionModel(),
        'viz_utils': VisualizationUtils()
    }

# Load data with caching
@st.cache_data
def load_data():
    """Load all required data."""
    data_loader = DataLoader()
    try:
        season_data, draft_data, player_bio_data = data_loader.load_all_data()
        unique_players = data_loader.get_unique_players(season_data)
        return season_data, draft_data, player_bio_data, unique_players
    except FileNotFoundError as e:
        st.error(f"Data loading error: {e}")
        st.error("Please ensure all data files are in the data/raw directory.")
        return None, None, None, []

def main():
    """Main application function."""
    st.title('🏈 NFL Player Similarity Analysis')
    st.markdown("---")
    
    # Initialize models
    models = initialize_models()
    
    # Load data
    with st.spinner("Loading data..."):
        season_data, draft_data, player_bio_data, unique_players = load_data()
    
    if season_data is None:
        st.error("Failed to load data. Please check the data files.")
        return
    
    # Sidebar for user inputs
    st.sidebar.header("Player Selection")
    target_player = st.sidebar.selectbox(
        "Select a player to analyze:",
        options=unique_players,
        index=0 if len(unique_players) > 0 else None
    )
    
    # Analysis options
    st.sidebar.header("Analysis Options")
    show_similar_players = st.sidebar.number_input(
        "Number of similar players to show:",
        min_value=1,
        max_value=20,
        value=10
    )
    
    show_projections = st.sidebar.checkbox("Show fantasy point projections", value=True)
    show_visualizations = st.sidebar.checkbox("Show visualizations", value=True)
    
    # Main analysis button
    if st.sidebar.button('🚀 Run Analysis', type="primary"):
        run_analysis(
            target_player, 
            season_data, 
            draft_data, 
            models, 
            show_similar_players,
            show_projections,
            show_visualizations
        )

def run_analysis(
    target_player: str,
    season_data: pd.DataFrame,
    draft_data: pd.DataFrame,
    models: dict,
    show_similar_players: int,
    show_projections: bool,
    show_visualizations: bool
):
    """Run the complete analysis for a target player."""
    
    st.header(f"Analysis Results for {target_player}")
    st.markdown("---")
    
    # Display target player information
    target_info = season_data[season_data['Player'] == target_player]
    if not target_info.empty:
        st.subheader("📊 Player Information")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Position", target_info['Pos'].iloc[0])
        with col2:
            st.metric("Age Range", f"{target_info['Age'].min()}-{target_info['Age'].max()}")
        with col3:
            st.metric("Seasons", len(target_info['Season'].unique()))
        
        # Show recent stats
        st.subheader("📈 Recent Performance")
        recent_stats = target_info.sort_values('Season', ascending=False).head(3)
        st.dataframe(recent_stats[['Season', 'Age', 'Fantasy_Points', 'Pos_Rank']])
    
    # Find similar players
    st.subheader("🔍 Similar Players Analysis")
    with st.spinner("Finding similar players..."):
        similar_players = models['similarity_model'].find_similar_players(
            season_data, draft_data, target_player
        )
    
    if not similar_players.empty:
        st.write(f"Found {len(similar_players)} similar players")
        
        # Display top similar players
        st.dataframe(similar_players.head(show_similar_players))
        
        if show_visualizations:
            # Create similarity heatmap
            fig = models['viz_utils'].create_similarity_heatmap(
                similar_players.head(10), target_player
            )
            st.pyplot(fig)
            plt.close()
    
    # Generate projections
    if show_projections and not similar_players.empty:
        st.subheader("🎯 Fantasy Point Projections")
        
        with st.spinner("Generating projections..."):
            projection_results = models['projection_model'].project_fantasy_points(
                target_player, similar_players, season_data
            )
        
        # Display projection summary
        summary_text = models['viz_utils'].display_projection_summary(
            projection_results['summary'], target_player
        )
        st.markdown(summary_text)
        
        if show_visualizations:
            # Create projection plot
            fig = models['viz_utils'].create_projection_plot(
                projection_results['weighted_projections'],
                projection_results['point_buckets'],
                target_player,
                projection_results['num_seasons']
            )
            st.pyplot(fig)
            plt.close()
    
    # Additional insights
    if not similar_players.empty:
        st.subheader("💡 Key Insights")
        
        # Similar players summary
        top_similar = similar_players.head(5)
        avg_similarity = top_similar['Avg'].mean()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Similarity Score", f"{avg_similarity:.3f}")
        with col2:
            st.metric("Most Similar Player", top_similar.index[0])
        with col3:
            st.metric("Similarity Range", f"{top_similar['Avg'].min():.3f} - {top_similar['Avg'].max():.3f}")
        
        # Show similar players' performance
        if show_projections:
            st.write("**Top Similar Players' Historical Performance:**")
            similar_players_stats = season_data[
                season_data['Player'].isin(top_similar.index)
            ].groupby('Player').agg({
                'Fantasy_Points': ['mean', 'std'],
                'Pos_Rank': 'mean'
            }).round(2)
            st.dataframe(similar_players_stats)

if __name__ == "__main__":
    main()