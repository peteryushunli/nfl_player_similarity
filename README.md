# NFL Player Similarity Analysis

A comprehensive fantasy football analytics platform that identifies similar NFL players based on statistical profiles and provides fantasy point projections.

## 🏈 Features

- **Player Similarity Analysis**: Find players with similar statistical profiles
- **Fantasy Point Projections**: Weighted projections based on similar players' historical performance
- **Draft Position Integration**: Incorporates draft position data for enhanced similarity scoring
- **Interactive Visualizations**: Box plots showing projected fantasy points and positional rankings
- **Streamlit Web Interface**: User-friendly web application for easy interaction

## 🚀 Quick Start

### Prerequisites

```bash
pip install -r requirements.txt
```

### Running the Application

```bash
streamlit run src/app/main.py
```

## 📁 Project Structure

```
nfl_player_similarity/
├── src/
│   ├── app/                 # Streamlit application
│   ├── core/                # Core business logic
│   ├── data/                # Data loading and processing
│   ├── models/              # Similarity and projection models
│   └── utils/               # Utility functions
├── data/
│   ├── raw/                 # Raw data files
│   └── processed/           # Processed data files
├── notebooks/               # Jupyter notebooks for analysis
├── tests/                   # Unit tests
├── docs/                    # Documentation
├── requirements.txt          # Python dependencies
├── setup.py                 # Package setup
└── README.md               # This file
```

## 🔧 Development

### Setting up the development environment

```bash
# Clone the repository
git clone <repository-url>
cd nfl_player_similarity

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Running tests

```bash
pytest tests/
```

## 📊 Data Sources

- **Seasonal Statistics**: NFL player performance data (2000-2022)
- **Draft Data**: NFL draft information (1994-2022)
- **Player Bios**: Player biographical information (2019-2023)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- NFL data sources for providing comprehensive player statistics
- Streamlit for the web application framework
- The fantasy football community for inspiration and feedback 