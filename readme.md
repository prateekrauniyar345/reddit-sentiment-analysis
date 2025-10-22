# Reddit Sentiment Analysis - Full Stack Application

A modern, full-stack application for comprehensive Reddit sentiment analysis with advanced analytics, real-time processing, and beautiful visualizations.

## 🚀 Features

### Backend (FastAPI)
- **Async Processing**: Handle 1000+ Reddit posts concurrently
- **Advanced Sentiment Analysis**: LLM-powered sentiment scoring with TextBlob fallback
- **Comprehensive Analytics**: 
  - Temporal analysis and posting patterns
  - Engagement metrics and correlation analysis
  - Subreddit analysis and user behavior patterns
  - Topic modeling and keyword extraction
- **Persistent Storage**: SQLite database for caching and history
- **RESTful API**: Well-documented endpoints with FastAPI auto-docs
- **Real-time Status**: WebSocket-like polling for analysis progress

### Frontend (React + TypeScript)
- **Modern UI**: Material-UI components with smooth animations
- **Interactive Charts**: Multiple visualization types using Recharts
- **Real-time Updates**: Live progress tracking and status updates
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Advanced Filtering**: Subreddit targeting, time filters, and sorting options

### Analytics Dashboard
- **Sentiment Timeline**: Track sentiment changes over time
- **Distribution Analysis**: Pie charts showing sentiment breakdown
- **Engagement Scatter Plots**: Correlation between engagement and sentiment
- **Subreddit Comparison**: Bar charts comparing sentiment across communities
- **Statistical Insights**: Mean, median, volatility, and trend analysis

## 📋 Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Reddit API Credentials** (see setup instructions below)
- **OpenAI/Nebius API Key** for advanced sentiment analysis

## 🛠️ Installation & Setup

### Quick Start (Recommended)

1. **Clone and Navigate**:
   ```bash
   git clone <repository-url>
   cd "reddit sentiment analysis"
   ```

2. **Run the Startup Script**:
   ```bash
   ./start_app.sh
   ```
   
   This script will:
   - Check prerequisites
   - Set up Python virtual environment
   - Install dependencies for both backend and frontend
   - Initialize the database
   - Start both services
   - Open the application in your browser

## Features

- Analyze sentiment of Reddit comments.
- Visualize sentiment trends with graphs and word clouds.
- Identify top positive and negative comments.
- Export results as a CSV file.

---

## Installation

### Prerequisites
- Python 3.8+
- Pip package manager

### Steps

1. Clone the repository:
   ```bash
   git clone "url"
   cd reddit-sentiment-analysis
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   python app.py
   ```

---

## Usage

1. Launch the Gradio interface by running `python app.py`.
2. Input Reddit comments (single or batch upload via CSV).
3. Click "Analyze" to view:
   - Sentiment scores.
   - Sentiment distribution histogram.
   - Word clouds for positive/negative sentiments.
   - Top positive and negative comments.
   - Sentiment trend over time.

---

## Visualization Details

- **Sentiment Distribution**: Histogram showing overall sentiment trends.
- **Word Clouds**: Highlights common words in positive and negative comments.
- **Top Comments**: Most extreme examples of positive and negative sentiments.
- **Trend Over Time**: Rolling average of sentiment scores over time.

---

## Model

This tool uses the **DeepSeek-V3** language model for sentiment analysis. No vision models are used—only text-based analysis.

---

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch and make your changes.
3. Submit a pull request.

---



## Contact

For questions or feedback, contact:

- Email: prateekrauniyar345@gmail.com

---

This version keeps the README simple, focused, and relevant to your project while ensuring all key details are included.