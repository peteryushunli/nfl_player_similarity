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
        display_options, player_mapping = data_loader.get_player_selection_options(season_data)
        return season_data, draft_data, player_bio_data, display_options, player_mapping
    except FileNotFoundError as e:
        st.error(f"Data loading error: {e}")
        st.error("Please ensure all data files are in the data/raw directory.")
        return None, None, None, [], {}

def main():
    """Main application function."""
    st.title('🏈 NFL Player Similarity Analysis')
    st.markdown("---")
    
    # Initialize models
    models = initialize_models()
    
    # Load data
    with st.spinner("Loading data..."):
        season_data, draft_data, player_bio_data, display_options, player_mapping = load_data()
    
    if season_data is None:
        st.error("Failed to load data. Please check the data files.")
        return
    
    # Sidebar for user inputs
    st.sidebar.header("Player Selection")
    
    # Add search functionality
    search_term = st.sidebar.text_input(
        "Search for a player:",
        placeholder="Type player name, position, or year...",
        help="Filter players by name, position, or years active"
    )
    
    # Filter options based on search
    if search_term:
        filtered_options = [
            option for option in display_options 
            if search_term.lower() in option.lower()
        ]
    else:
        filtered_options = display_options
    
    selected_player_display = st.sidebar.selectbox(
        "Select a player to analyze:",
        options=filtered_options,
        index=0 if len(filtered_options) > 0 else None,
        help="Players are shown with their position and years active"
    )
    
    # Get the actual PFR ID from the display string
    target_player_id = player_mapping.get(selected_player_display, selected_player_display)
    
    # Show dataset statistics
    st.sidebar.header("📊 Dataset Info")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Total Players", len(display_options))
    with col2:
        st.metric("Data Years", f"{season_data['Season'].min()}-{season_data['Season'].max()}")
    
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
            target_player_id, 
            season_data, 
            draft_data, 
            models, 
            show_similar_players,
            show_projections,
            show_visualizations
        )

def run_analysis(
    target_player_id: str,
    season_data: pd.DataFrame,
    draft_data: pd.DataFrame,
    models: dict,
    show_similar_players: int,
    show_projections: bool,
    show_visualizations: bool
):
    """Run the complete analysis for a target player."""
    
    # Get player name from ID for display
    target_player_name = season_data[season_data['pfr_id'] == target_player_id]['Player'].iloc[0] if not season_data[season_data['pfr_id'] == target_player_id].empty else target_player_id
    
    st.header(f"Analysis Results for {target_player_name}")
    st.markdown("---")
    
    # Display target player information
    target_info = season_data[season_data['pfr_id'] == target_player_id]
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
            season_data, draft_data, target_player_id
        )
    
    if not similar_players.empty:
        st.write(f"Found {len(similar_players)} similar players")
        
        # Convert IDs to names for display
        similar_players_display = similar_players.copy()
        similar_players_display['Player_Name'] = similar_players_display.index.map(
            lambda x: season_data[season_data['pfr_id'] == x]['Player'].iloc[0] 
            if not season_data[season_data['pfr_id'] == x].empty else x
        )
        
        # Display top similar players with names
        display_df = similar_players_display[['Player_Name', 'Avg']].head(show_similar_players)
        display_df.columns = ['Player', 'Similarity Score']
        st.dataframe(display_df)
        
        if show_visualizations:
            # Create similarity heatmap
            fig = models['viz_utils'].create_similarity_heatmap(
                similar_players.head(10), target_player_name
            )
            st.pyplot(fig)
            plt.close()
    
    # Generate projections
    if show_projections and not similar_players.empty:
        st.subheader("🎯 Fantasy Point Projections")
        
        with st.spinner("Generating projections..."):
            projection_results = models['projection_model'].project_fantasy_points(
                target_player_id, similar_players, season_data
            )
        
        # Check if projections were successful
        if 'error' in projection_results:
            st.warning(f"⚠️ {projection_results['error']}")
            st.info("This may happen when similar players don't have enough historical data for projections.")
        elif projection_results['projection_points'].empty:
            st.warning("⚠️ No projection data available for the selected player and similar players.")
        else:
            # Display projection summary
            summary_text = models['viz_utils'].display_projection_summary(
                projection_results['summary'], target_player_name
            )
            st.markdown(summary_text)
            
            if show_visualizations and not projection_results['weighted_projections'].empty:
                # Create projection plot
                fig = models['viz_utils'].create_projection_plot(
                    projection_results['weighted_projections'],
                    projection_results['point_buckets'],
                    target_player_name,
                    projection_results['num_seasons']
                )
                st.pyplot(fig)
                plt.close()
            elif show_visualizations:
                st.info("📊 No visualization available due to insufficient projection data.")
    
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
                season_data['pfr_id'].isin(top_similar.index)
            ].groupby('Player').agg({
                'Fantasy_Points': ['mean', 'std'],
                'Pos_Rank': 'mean'
            }).round(2)
            st.dataframe(similar_players_stats)

if __name__ == "__main__":
    main()